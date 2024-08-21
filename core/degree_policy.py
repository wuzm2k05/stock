import traceback

from . import trade_time
from . import snowball_proxy
from . import logger
from . import config

_log = logger.get_logger()

class DegreePolicy:
  def __init__(self):
    pass
  
  def _calculate_price_groups(self,max_price, min_price, num_groups):
    ratio = (min_price / max_price) ** (1 / (num_groups - 1))
    prices = [round(max_price * (ratio ** i), 2) for i in range(num_groups)]
    return prices
  
  def _calculate_stock_num_array(self,price_degree_array,total_money,num_degree,round_stocks):
    balance_each_degree = round(total_money/(num_degree-1))
    stock_num_array = [0]
    stock_left = 0
    for price in price_degree_array[1:]:
      stock_num_price = round(balance_each_degree/price)
      stock_for_this_price = round((stock_num_price + stock_left)/round_stocks)*round_stocks
      stock_left = (stock_num_price + stock_left) - stock_for_this_price
      stock_num_array.append(stock_for_this_price)
      
    return stock_num_array
    
  def _cal_buy_sell_stocks(self,
                           stocks,
                           total_money,
                           max_price,
                           min_price,
                           current_price,
                           num_degree,
                           min_trade_stocks,
                           round_stocks,
                           fraction):
    """
    Des:
      calculate the stocks we need to buy or sell based on the input information.
    Argument:
      stocks: how many stocks the account have right now.
      total_money: how much money the accoutn used for this stock.
      max_price:
      min_price:
      num_degree:
      min_trade_stocks: minmum trade stocks. that means if sell or buy stock num is less than this num, shoud not trade.
      round_stocks: 
      fraction: the price fraction. for example, if the degree price is 10$, then we will buy when the price is (10-0.05)$, 
        and sell when the price is (10+0.05)$
    """
    price_degree_array = self._calculate_price_groups(max_price,min_price,num_degree)
    stock_num_array = self._calculate_stock_num_array(price_degree_array,total_money,num_degree,round_stocks)
    _log.debug("price_degree_array: %s",price_degree_array)
    _log.debug("stock_num_array: %s",stock_num_array)
    
    # calculate how many stock we should have
    stock_willing_for_buy = 0
    stock_willing_for_sell = 0
    for i in range(len(price_degree_array)):
      price = price_degree_array[i]
      if current_price < price-fraction:
        stock_willing_for_buy += stock_num_array[i]
      
      if i > 0 and current_price <= price_degree_array[i-1]+fraction:
        stock_willing_for_sell += stock_num_array[i]
      
    if stock_willing_for_buy > stocks:
      buy_stock_num = ((stock_willing_for_buy - stocks)/round_stocks)*round_stocks
      buy_stock_num = buy_stock_num if buy_stock_num > min_trade_stocks else 0
      return True, buy_stock_num
    
    if stocks > stock_willing_for_sell:
      sell_stock_num = ((stocks-stock_willing_for_sell)/round_stocks)*round_stocks
      sell_stock_num = sell_stock_num if sell_stock_num > min_trade_stocks else 0
      return False, sell_stock_num
    
    return True, 0
  
  def run_policy_for_stock(self,stock_name:str, stock_attr:dict,balance_res,order_list_res,position_list_res):
    try:
      need_exit = False
      #cancel any unfinished order for this stock
      proxy = snowball_proxy.SnowBallProxy()
      for order in order_list_res.data["items"]:
        if order["symbol"] == stock_name and (order["status"] == "REPORTED" or order["status"] == "PART_CONCLUDED"):
          proxy.cancel_order(order["id"])
          need_exit = True
      
      if need_exit:
        _log.debug("stock %s cannot be run since there are some pending order need be canncelled",stock_name)
        # if we need to cancel order, need to wait next time run policy. since the balance and stocks may not accurate.
        return
      
      #find the balance
      account_balance = 0
      for cash in balance_res.data["balance_detail_items"]:
        if stock_attr["stock_currency"] == cash["currency"]:
          account_balance = cash["cash"]
          break
      
      #find how many stocks we have from position list response
      stocks = 0
      current_price = 0
      for stock in position_list_res.data:
        if stock["symbol"] == stock_name:
          stocks = stock["position"]
          current_price = stock["market_price"]
          break
        
      if stocks < stock_attr["reserve_stocks"]:
        # that is not allowed. one stock has to have reserve stocks
        _log.warning("stocks is less than reserve stocks for %s",stock_name)
        return
      
      #check if it is in trade time
      if stock_attr["stock_currency"] == "HKD" and not trade_time.is_hk_trade_time():
        _log.debug("not in hk trade time")
        return
      
      if stock_attr["stock_currency"] == "USD" and not trade_time.is_us_trade_time():
        _log.debug("not in us trade time")
        return
      
      stocks -= stock_attr["reserve_stocks"]
      
      #calcuate the degree and run the policy
      buy, stock_num = self._cal_buy_sell_stocks(stocks,
                                                 stock_attr["total_amount_money"],
                                                 stock_attr["max_price"],
                                                 stock_attr["min_price"],
                                                 current_price,
                                                 stock_attr["degree"],
                                                 stock_attr["min_trade_stocks"],
                                                 stock_attr["round_stocks"],
                                                 stock_attr["fraction"])
      
      #TODO: just for testing
      #if buy and stock_num > 0 and account_balance >= stock_num*current_price:
      if buy and stock_num > 0:
        #place buy order
        proxy.place_order(buy,stock_name,stock_attr["stock_currency"],current_price,stock_num)
        _log.debug("place one order: %s, %s, %s, %s ",buy,stock_name,current_price,stock_num)
      
      if not buy and stock_num > 0:
        proxy.place_order(buy,stock_name,stock_attr["stock_currency"],current_price,stock_num)
        _log.debug("place one order: %s, %s, %s, %s ",buy,stock_name,current_price,stock_num)
        
    except:
      #something wrong happen to this policy, just skip it
      traceback_str = traceback.format_exc()
      _log.warning("internal error: %s", traceback_str)
      return
