import time,datetime,json,os

from . import config
from . import logger
from . import policy_helper

_log = logger.get_logger()

_SAVE_FILE_PATH = "./stock_balance.json"

class SingletonMeta(type):
  _instances = {}

  def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super().__call__(*args, **kwargs)
    return cls._instances[cls]

class AddBalance(metaclass=SingletonMeta):
  def __init__(self):
    self.currency_last_adjust_day = {}
   
    self.stocks = json.loads(config.get_policy_stocks_config())
    self.stocks_by_currency = {}
    for stock_name, stock_attr in self.stocks.items():
      if stock_attr["stock_currency"] not in self.stocks_by_currency:
        self.stocks_by_currency[stock_attr["stock_currency"]] = []
      
      self.stocks_by_currency[stock_attr["stock_currency"]].append(stock_name)
    
    self.currency_reserve = json.loads(config.get_currency_reserve())
    
    self.load_balance_from_file()
  
  def load_balance_from_file(self):
    """从文件加载上次保存的 total_amount_money，并确保不小于 config 预设值"""
    if os.path.exists(_SAVE_FILE_PATH):
      try:
        with open(_SAVE_FILE_PATH, "r") as f:
          saved_data = json.load(f)
        for stock_name, amount in saved_data.items():
          if stock_name in self.stocks:
            self.stocks[stock_name]["total_amount_money"] = max(
              self.stocks[stock_name]["total_amount_money"], amount
            )
        _log.info("成功加载上次保存的 balance 数据")
      except Exception as e:
        _log.error("加载 balance 数据失败: %s", str(e))
  
  def save_balance_to_file(self):
    """将当前的 total_amount_money 持久化到文件"""
    try:
      with open(_SAVE_FILE_PATH, "w") as f:
        json.dump(
          {stock_name: stock_attr["total_amount_money"] for stock_name, stock_attr in self.stocks.items()},
          f,
          indent=4
        )
      _log.info("成功保存 balance 数据到文件")
    except Exception as e:
      _log.error("保存 balance 数据失败: %s", str(e))
                 
  def _do_balance(self,balance,position_list,stock_list,reserve_currency):
    # compose position map
    rest_balance = balance
    if rest_balance <= reserve_currency:
      # no need to adjust
      return True
    else:
      rest_balance -= reserve_currency
    
    stock_position = {}
    for stock in position_list.data:
      if stock["symbol"] in stock_list:
        stock_position[stock["symbol"]] = stock["position"]
    
    for stock_name in stock_list:
      stock_attr = self.stocks[stock_name]
      price_degree_array = policy_helper.calculate_price_groups(stock_attr["max_price"],stock_attr["min_price"],stock_attr["degree"])
      #need to consider reserved stocks
      number_of_stocks = 0 if stock_position[stock_name] < stock_attr["reserve_stocks"] else stock_position[stock_name] - stock_attr["reserve_stocks"]
      money_of_stocks = price_degree_array[-1] * number_of_stocks
      if (money_of_stocks > stock_attr["total_amount_money"]):
        _log.warning("why stock: %s stock money: %s is more than total amount: %s", stock_name,money_of_stocks,stock_attr["total_amount_money"])
        return False
      
      money_need_from_balance = stock_attr["total_amount_money"] - money_of_stocks
      if (rest_balance <= money_need_from_balance):
        # no more balance need to adjust
        # even we didn't adjust the amount, we should return true means we success tried.
        return True
      else:
        rest_balance -= money_need_from_balance
        
    # now we always pick the first one
    #TODO: need policy
    self.stocks[stock_list[0]]["total_amount_money"] += round(rest_balance)
    _log.info("stock %s balance has been adjusted to %s",stock_list[0],self.stocks[stock_list[0]]["total_amount_money"])
    
    self.save_balance_to_file()
    return True
  
  # each day we only adjust once. and when there is no pending order for stocks
  def trigger_add_balance(self,balance,order_list,position_list):
    if not config.get_adjust_balance():
      # adjust balance not allowed
      return
    
    current_day = datetime.date.today().day
    
    # for each currency, calculate the stocks
    for currency,stock_list in self.stocks_by_currency.items():
      #check if already adjusted this day
      last_adjust_day = 0
      if currency not in self.currency_last_adjust_day:
        self.currency_last_adjust_day[currency] = 0
      
      last_adjust_day = self.currency_last_adjust_day[currency]
      if current_day == last_adjust_day:
        # skip this currency
        continue
      
      #check if there are pending orders for this currency
      need_skip = False
      for order in order_list.data["items"]:
        if order["symbol"] in stock_list:
          if order["status"] == "REPORTED" or order["status"] == "PART_CONCLUDED":
            # there is pending order, so do nothing. and wait next time
            need_skip = True
            break
      if need_skip:
        continue
      
      #start to adjust
      currency_balance = 0
      for cash in balance.data["balance_detail_items"]:
        if currency == cash["currency"]:
          currency_balance = cash["cash"]
          break
      
      reserve_currency = 0
      if currency in self.currency_reserve:
        reserve_currency = self.currency_reserve[currency]
        
      if self._do_balance(currency_balance,position_list,stock_list,reserve_currency):
        self.currency_last_adjust_day[currency] = current_day  
        
  # get the new amount for stock
  def get_new_amount(self,stock_symbol):
    _log.debug("return new amount money: %s",self.stocks[stock_symbol]["total_amount_money"])
    return self.stocks[stock_symbol]["total_amount_money"]
  
  # report stock actions. we can depends on those information to decide how to adjust balance for different stocks.
  def report_action(self,buy,stock_symbol,currency,price,quantity):
    pass

