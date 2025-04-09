import time,datetime

from snbpy.common.domain.snb_config import SnbConfig
from snbpy.snb_api_client import SnbHttpClient
from snbpy.snb_api_client import SecurityType
from snbpy.snb_api_client import OrderSide,Currency

from . import config
from . import logger
from . import types

_log = logger.get_logger()

class SingletonMeta(type):
  _instances = {}

  def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super().__call__(*args, **kwargs)
    return cls._instances[cls]

class SnowBallProxy(metaclass=SingletonMeta):
  CURRENCY_MAP = {"USD":Currency.USD,"HKD":Currency.HKD}
  
  def __init__(self):
    self.client = None
    self.last_ts = 0
    self.sq = 0
    self.last_login_time = None
  
  def get_snowball_client(self) -> SnbHttpClient:
    if self.client is None: 
      conf = SnbConfig()
      conf.sign_type = 'None'
      conf.snb_server = config.get_snowball_server()
      conf.account = config.get_snowball_account()
      conf.key = config.get_snowball_key()
      conf.snb_port = config.get_snowball_port()
      conf.timeout = 1000
      conf.schema = 'https'

      self.client = SnbHttpClient(conf)
      self.client.login()
      self.last_login_time = datetime.datetime.now()
    else:
      current_time = datetime.datetime.now()
      time_elapsed = current_time - self.last_login_time
      if time_elapsed.total_seconds() >= 24*60*60: #24 hours (since client token expire time is 25hours)
        _log.debug("snowball client login again")
        self.client.login()
        self.last_login_time = current_time
      
    return self.client
  
  def gen_order_id(self):
    t = int(time.time())
    if self.last_ts == t:
        if self.sq == 999:
            raise Exception("too many request in one second")
        else:
            self.sq += 1
    else:
        self.last_ts = t
        self.sq = 0
    return "{}{:03}".format(self.last_ts, self.sq)

  def get_position_list(self):
    client = self.get_snowball_client()
    position_res = client.get_position_list()
    if position_res.result_code != "60000":
      raise Exception("get position list failed")

    return position_res
  
  def get_order_list(self):
    client = self.get_snowball_client()
    all_orders = types.OrderListRes()
    page_number = 1
    page_size = 10
    while True:
      current_orders = client.get_order_list(page=page_number,size=page_size)
      if current_orders.result_code != "60000":
        raise Exception("get order faild")
      
      items = current_orders.data["items"]
      if not items or len(items) <= 0:
        break # no more items. exits the loop
      for item in items:
        if item["status"] == "INVALID":
          # something wrong happened today,do nothing today
          raise Exception("invaild order found")
        all_orders.add_order(item)
        
    return all_orders
  
  def get_balance(self):
    client = self.get_snowball_client()
    balance_res = client.get_balance()
    if balance_res.result_code != "60000":
      raise Exception("get balance failed")
  
    return balance_res
  
  def get_transactions(self,min_time=None,max_time=None):
    client = self.get_snowball_client()
    return client.get_transaction_list(order_time_min=min_time,order_time_max=max_time)
  
  def place_order(self,buy,symbol,currency,price,quantity):
    client = self.get_snowball_client()
    order_id = "t"+self.gen_order_id() # t for trade order. orderID should <= 20
    buy_or_sell = OrderSide.BUY if buy else OrderSide.SELL
   
    response = client.place_order(order_id,SecurityType.STK,symbol,"",buy_or_sell,self.CURRENCY_MAP[currency],int(quantity),price)
    #response = client.place_order(order_id,SecurityType.STK,"06862","",OrderSide.BUY,Currency.HKD,4000,12.19)
    if response.result_code != "60000" or "status" not in response.data or response.data["status"] != "REPORTED":
      raise Exception("place order failed")
    
    return response
    
  def cancel_order(self,origin_order_id):
    client = self.get_snowball_client()
    order_id = "x"+self.gen_order_id() # x for cancel order.
    response = client.cancel_order(order_id,origin_order_id)
    if response.result_code != "60000":
      raise Exception("cancel order failed")

    return response
  
  