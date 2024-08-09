import shioaji as sj
import os
from dotenv import load_dotenv

# 該腳本不在主邏輯中，其作用請參考以下連結
# Reference: https://sinotrade.github.io/zh_TW/tutor/prepare/terms/

load_dotenv()
shioaji_api_key = os.getenv('SHIOAJI_API_KEY')
shioaji_secret_key = os.getenv('SHIOAJI_SECRET_KEY')

api = sj.Shioaji(simulation=True)

try:
    api.login(
        api_key=shioaji_api_key,
        secret_key=shioaji_secret_key,
    )
    active_result = api.activate_ca(
        ca_path='./Sinopac.pfx',  # 請修改此處為自己的憑證路徑
        ca_passwd='A000000000',   # 請修改此處為自己的憑證密碼
    )
    contract = api.Contracts.Stocks.TSE["2890"]

    # 證券委託單 - 請修改此處
    order = api.Order(
        price=26.5,  # 價格
        quantity=1,  # 數量
        action=sj.constant.Action.Buy,  # 買賣別
        price_type=sj.constant.StockPriceType.LMT,  # 委託價格類別
        order_type=sj.constant.OrderType.ROD,  # 委託條件
        account=api.stock_account  # 下單帳號
    )

    # 下單
    trade = api.place_order(contract, order)
    print(trade)

except Exception as e:
    print(e)
finally:
    api.logout()
    print('logout')




