import time

from snbpy.common.domain.snb_config import SnbConfig
from snbpy.snb_api_client import SnbHttpClient
from snbpy.snb_api_client import SecurityType
from snbpy.snb_api_client import OrderSide,Currency

last_ts = 0
sq = 0

def gen_order_id():
    global last_ts,sq   
    t = int(time.time())
    if last_ts == t:
        if sq == 999:
            raise Exception("too many request in one second")
        else:
            sq += 1
    else:
        last_ts = t
        sq = 0
    return "{}{:03}".format(last_ts, sq)
        
if __name__ == '__main__':
    config = SnbConfig()
    #config.account = "U8211213"
    #config.key = 'wuzm2k01'
    #config.snb_server ='openapi.snbsecurities.com'
    config.sign_type = 'None'
    config.snb_server ='sandbox.snbsecurities.com'
    config.account = "DU1730010"
    config.key = '123456789'
    config.snb_port = '443'
    config.timeout = 1000
    config.schema = 'https'

    client = SnbHttpClient(config)
    client.login()
    
    #time.sleep(3600)
    
    balance_response = client.get_balance()
    print(balance_response.result_code)
    #for cash in balance_response.data["balance_detail_items"]:
    #    print(cash["currency"],cash["cash"])
        
    #order_list_response=client.get_order_list()
    #print(order_list_response.result_code)
    #for order in order_list_response.data["items"]:
    #    print(order["id"],order["status"],order["symbol"],order["side"],order["quantity"],order["price"])
    #print(order_list_response)
    
    #cancel_order_response = client.cancel_order('wuzmcancel0001','1724121600000')
    #cancel_order_response.data
    #cancel_order_response.result_code == "60000"
    #print(cancel_order_response.result_code)
    #print(cancel_order_response.data["id"])
    #print(cancel_order_response.data["status"])
    
    #print(cancel_order_response)
    
    #position_list = client.get_position_list()
    #print(position_list.result_code)
    #for stock in position_list.data:
    #    print(stock["symbol"],stock["position"],stock["market_price"])
    
    #print(position_list)
    
    #details = client.get_security_detail("NCLH")
    #print(details)
    #details = client.get_security_detail("06862")
    #print(details)
    
    #order_id = gen_order_id()
    #order_response = client.place_order(order_id,SecurityType.STK,"NCLH","",OrderSide.SELL,Currency.USD,7000,11.50)
    #order_id = gen_order_id()
    #order_response = client.place_order(order_id,SecurityType.STK,"NCLH","",OrderSide.BUY,Currency.USD,100,16.16)
    #print(order_response)
    #print(order_response.result_code)
    #print(order_response.data["status"]) #must have this attrbute and must be REPORTED
    
    #order_id = "t1724378642003"
    #order_response = client.place_order(order_id,SecurityType.STK,"06862","",OrderSide.BUY,Currency.HKD,1000,11.76)
    #print(order_response.result_code)
    #print(order_response.data["status"]) #must have this attrbute and must be REPORTED
    #print(order_response)
    #if there is no status=reported, then should think the order fail
    
    #place an order
    