from StockAccount import ShioajiStockAccount
from datetime import datetime
from TWStock import TWStock
from GenFigure import PositionFigure
from dotenv import load_dotenv
from glob import glob
import os


if __name__ == '__main__':
    load_dotenv()
    private_output_dir = '.'
    public_output_dir = '.'
    shioaji_api_key = os.getenv('SHIOAJI_API_KEY')
    shioaji_secret_key = os.getenv('SHIOAJI_SECRET_KEY')
    if 'PRIVATE_OUTPUT_DIR' in os.environ:
        private_output_dir = os.getenv('PRIVATE_OUTPUT_DIR')
    if 'PUBLIC_OUTPUT_DIR' in os.environ:
        public_output_dir = os.getenv('PUBLIC_OUTPUT_DIR')

    # init ShioajiStockAccount object
    myAccount = ShioajiStockAccount(
        api_key=shioaji_api_key,
        secret_key=shioaji_secret_key
    )

    try:
        # 帳務：查詢銀行帳戶餘額
        print(f"查詢目前 ({myAccount.account_balance.date}) 銀行帳戶餘額為新台幣 {myAccount.account_balance.acc_balance}")

        # 查詢持倉
        # myPositions = myAccount.list_positions(is_df=True)
        myPositions = myAccount.list_positions_detail(to_csv=True, output_dir=private_output_dir)
        # print(myPositions)

        # 查詢已實現損益
        myLossSummary = myAccount.get_all_loss_summary()
        print(f"統計{min([year for year in myLossSummary.keys() if type(year)==int])}年至今的已實現損益為{myLossSummary['total']['pnl']} ({myLossSummary['total']['pr_ratio']}%)")

        # # 查詢交割資訊
        settlements = myAccount.settlements(is_df=True)
        print('交割資訊如下：')
        print(settlements)

        # 繪製持倉類型各項圖
        myPositionFigure = PositionFigure(myPositions)
        # 定義要顯示的圖表及其布局
        chart_configs = [
            ['position_pie', (0, 0), (1, 1)],
            ['loss_bar_with_type', (0, 1), (1, 1)],
            ['value_bar_chart', (1, 0), (1, 1)],
            ['combined_holdings_and_changes', (1, 1), (1, 1)],
            # ['combined_holdings_and_changes', (2, 0), (1, 1)]  # 新增的方法
        ]

        myPositionFigure.custom_combined_charts(chart_configs, save_path=f'{public_output_dir}/{datetime.now().strftime("%Y%m%d")}_stock_positions.jpg')
        # myPositionFigure.save_individual_charts(chart_configs, save_dir=f'{public_output_dir}/{datetime.now().strftime("%Y%m%d")}_stock_positions', format='jpg')

        # 查詢大盤資訊
        taiex_info = TWStock.get_taiex_info()
        with open(f'{public_output_dir}/{datetime.now().strftime("%Y%m%d")}_caption.txt', 'w') as f:
            date_string = datetime.now().strftime("%Y年%m月%d日")
            string_format = f"{date_string}大盤加權指數：\n開盤{float(taiex_info['指數'])-float(taiex_info['漲跌']):.2f}\n漲跌指數為{taiex_info['漲跌']}({taiex_info['漲跌比例']})\n最後收{taiex_info['指數']}\n今年漲跌幅：{taiex_info['今年表現']}"
            f.write(string_format)
            print(string_format)

        # 產生近七天交易日的大盤文字資訊
        TWSTock_perDay_path = sorted(glob(f'{public_output_dir}/*_caption.txt'), key=os.path.getctime)
        TWSTock_perDay_path.reverse()
        statistics_days = 7
        with open(f'{public_output_dir}/{datetime.now().strftime("%Y%m%d")}_caption_{statistics_days}dsummary.txt', 'w') as f:
            if len(TWSTock_perDay_path) < statistics_days:
                statistics_days = len(TWSTock_perDay_path)
            for p in TWSTock_perDay_path[:statistics_days]:
                with open(p, 'r') as fp:
                    f.write(fp.read())
                    f.write('\n\n')

    except Exception as e:
        print(e)
    finally:
        myAccount.logout()
        print('logout')
