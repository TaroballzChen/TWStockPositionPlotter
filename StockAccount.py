import shioaji as sj
import pandas as pd
from datetime import datetime


class ShioajiStockAccount:
    def __init__(self, api_key, secret_key):
        self.api = sj.Shioaji()
        self.login(api_key, secret_key)
        self.stock_account = self.api.stock_account

    def login(self, api_key, secret_key):
        self.api.login(
            api_key=api_key,
            secret_key=secret_key
        )

    @property
    def account_balance(self):
        return self.api.account_balance()

    def list_positions(self, is_df=False):
        positions = self.api.list_positions(self.api.stock_account, unit=sj.constant.Unit.Share)
        if is_df:
            df = pd.DataFrame(p.__dict__ for p in positions)
            df = df.drop(columns=['direction', 'margin_purchase_amount', 'collateral', 'short_sale_margin', 'interest'])
            df.columns = ['部位代碼', '商品代碼', '數量', '平均價格', '目前股價', '損益', '昨日庫存數量', '商品類型']
            return df

        return positions

    def list_positions_detail(self, to_csv=False, output_dir='.'):
        positions = self.list_positions(is_df=True)

        def product_total_value(current_share_price, quantity):
            return current_share_price * quantity

        from TWStock import ETFCategory
        etf_c = ETFCategory()
        positions['股票類型'] = positions['商品代碼'].apply(lambda x: etf_c.num_to_name(x))
        positions['部位價值'] = positions.apply(lambda x: product_total_value(x['目前股價'], x['數量']), axis=1)
        positions['部位占比'] = positions['部位價值'] / positions['部位價值'].sum() * 100
        if to_csv:
            today = datetime.now().strftime('%Y%m%d')
            positions.to_csv(f'{output_dir}/{today}_positions.csv', index=False)
        return positions

    def get_all_loss_summary(self):
        def year_duration(year):
            start_date = datetime(year, 1, 1).strftime('%Y-%m-%d')
            end_date = datetime(year, 12, 31).strftime('%Y-%m-%d')
            return start_date, end_date

        all_loss_summary = {}
        for year in range(2019, datetime.now().year + 1):
            start_date, end_date = year_duration(year)
            loss_summary_year = self.api.list_profit_loss_summary(self.api.stock_account, start_date, end_date).total
            if str(loss_summary_year):
                all_loss_summary[year] = loss_summary_year
        else:
            total = {'quantity': 0, 'buy_cost': 0, 'sell_cost': 0, 'pnl': 0.0, 'pr_ratio': 0.0}
            for year, loss_summary in all_loss_summary.items():
                total['quantity'] += loss_summary.quantity
                total['buy_cost'] += loss_summary.buy_cost
                total['sell_cost'] += loss_summary.sell_cost
                total['pnl'] += loss_summary.pnl
                total['pr_ratio'] = round(total['pnl'] / total['buy_cost'] * 100, 2) if total['buy_cost'] else 0
            else:
                all_loss_summary['total'] = total
                return all_loss_summary

    def settlements(self, is_df=False):
        settlements = self.api.settlements(self.api.stock_account)
        if is_df:
            df = pd.DataFrame(s.__dict__ for s in settlements).set_index('T')
            return df

        return settlements

    def logout(self):
        self.api.logout()
