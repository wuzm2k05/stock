import traceback,math

from . import trade_time
from . import snowball_proxy
from . import logger
from . import price_tick
from . import add_balance
from . import policy_helper
from . import adjust_decision
from . import config

_log = logger.get_logger()

class DegreePolicy:
  def __init__(self):
    pass
  
  def _calculate_stock_num_array(self,price_degree_array,total_money,num_degree,round_stocks):
    balance_each_degree = math.floor(total_money/(num_degree-1))
    stock_num_array = [0]
    left_balance = 0
    for price in price_degree_array[1:]:
      stock_num_price = math.floor((balance_each_degree+left_balance)/price)
      stock_num_for_this_price = math.floor(stock_num_price/round_stocks)*round_stocks
      stock_for_next = stock_num_price - stock_num_for_this_price
      left_balance = math.floor(stock_for_next * price)
      stock_num_array.append(stock_num_for_this_price)
     
    return stock_num_array
    
  def _cal_buy_sell_stocks(self,
                           stocks,
                           current_price,
                           min_trade_stocks,
                           round_stocks,
                           fraction,
                           price_degree_array,
                           stock_num_array):
    """
    Des:
      calculate the stocks we need to buy or sell based on the input information.
    Argument:
      stocks: how many stocks the account have right now.
      min_trade_stocks: minmum trade stocks. that means if sell or buy stock num is less than this num, shoud not trade.
      round_stocks: 
      fraction: the price fraction. for example, if the degree price is 10$, then we will buy when the price is (10-0.05)$, 
        and sell when the price is (10+0.05)$
      price_degree_array: 
      stock_num_array:
    Return: buy_or_sell,stock_num,price
    """
    #price_degree_array = policy_helper.calculate_price_groups(max_price,min_price,num_degree)
    #stock_num_array = self._calculate_stock_num_array(price_degree_array,total_money,num_degree,round_stocks)
    _log.debug("price_degree_array: %s",price_degree_array)
    _log.debug("stock_num_array: %s",stock_num_array)
    
    # calculate how many stock we should have
    stock_willing_for_buy = 0
    stock_willing_for_sell = 0
    buy_price = current_price + fraction
    sell_price = current_price - fraction
    
    for i in range(len(price_degree_array)):
      price = price_degree_array[i]
      if current_price < price-fraction:
        stock_willing_for_buy += stock_num_array[i]
        buy_price = buy_price if buy_price < price else price
      
      if i > 0:
        if current_price <= price_degree_array[i-1]+fraction:
          # stock_willing_for_sell: how many stocks we want reserve when calcuate selling
          stock_willing_for_sell += stock_num_array[i]
        else:
          sell_price = price_degree_array[i-1] if price_degree_array[i-1] > sell_price else sell_price
      
    if stock_willing_for_buy > stocks:
      buy_stock_num = ((stock_willing_for_buy - stocks)/round_stocks)*round_stocks
      buy_stock_num = buy_stock_num if buy_stock_num >= min_trade_stocks else 0
      return True, buy_stock_num, buy_price
    
    if stocks > stock_willing_for_sell:
      sell_stock_num = ((stocks - stock_willing_for_sell)/round_stocks)*round_stocks
      sell_stock_num = sell_stock_num if sell_stock_num >= min_trade_stocks else 0
      return False, sell_stock_num, sell_price
    
    return True, 0, 0
  
  def make_orders(self,stock_name, order_list_res, stock_attr,fraction,stocks,stock_num_array, price_degree_array,current_price, buy, stock_num, execute_price):
    """
    """
    proxy = snowball_proxy.SnowBallProxy()
    
    if stock_num > 0:
      need_exit = False
      
      #cancel any unfinished order for this stock
      for order in order_list_res.data["items"]:
        if order["symbol"] == stock_name:
          if order["status"] == "REPORTED" or order["status"] == "PART_CONCLUDED":
            proxy.cancel_order(order["id"])
            need_exit = True
          
          if order["status"] in ("NO_REPORT","WAIT_REPORT","WAIT_WITHDRAW","PART_WAIT_WITHDRAW"):
            need_exit = True
        
      if need_exit:
        _log.debug("stock %s cannot be run since there are some pending order need be canncelled",stock_name)
        # if we need to cancel order, need to wait next time run policy. since the balance and stocks may not accurate.
        return
      else:
        # place an order to execute
        # adjust the tick
        execute_price = price_tick.align_tick(buy,stock_attr["stock_currency"],execute_price)
      
        # adjust decision based on trend
        if adjust_decision.AdjustDecision().query(buy,stock_name):
          _log.debug("place one order: %s, %s, %s, %s ",buy,stock_name,execute_price,stock_num)
          proxy.place_order(buy,stock_name,stock_attr["stock_currency"],execute_price,stock_num)
          #TODO: report this action
          add_balance.AddBalance().report_action(buy,stock_name,stock_attr["stock_currency"],execute_price,stock_num)
    else:
      # there is no immediate trade. so we need use order strategy
      # use order stragy here
      if not config.get_use_order():
        return
      
      # 1. calculate ( high sell price and volume, low buy price and volume)
      high_sell_price = 0
      high_sell_volume = 0
      low_buy_price = 0 
      low_buy_volume = 0
      need_exit = False
      
      for i in range(len(price_degree_array)):
        stocks -= stock_num_array[i]
        if stocks == 0:
          # get the high sell price and volume
          if i > 0:
            if price_degree_array[-1] == price_degree_array[i]:
              # here is the last one
              if current_price <= price_degree_array[i-1] + fraction:
                high_sell_price = price_degree_array[i-1] + fraction
                high_sell_volume = stock_num_array[i]
              else:
                need_exit = True
            else:
              #normal slot
              if current_price >= price_degree_array[i+1] - fraction and current_price <= price_degree_array[i-1] + fraction:
                high_sell_price = price_degree_array[i-1] + fraction
                high_sell_volume = stock_num_array[i]
                low_buy_price = price_degree_array[i+1] - fraction
                low_buy_volume = stock_num_array[i+1]
              else:
                need_exit = True
          else:
            # this is the first one
            if current_price >= price_degree_array[0] - fraction:
              low_buy_price = price_degree_array[i+1]-fraction
              low_buy_volume = stock_num_array[i+1]
            else:
              need_exit = True
          
          # we found the slot, so break the loop    
          break
        elif stocks < 0:
          # that means some order partially executed, so we don't handle in order way. 
          # we just wait untill partially order finished, or immediate (when stock_num > 0) part handle the situation.
          _log.warning("some order is partillay executed, so skip this order step and wait. stocks: %s",stocks)
          return
      
      if need_exit:
        _log.warning("why current price %s and stocks number %s not match when using ording?",current_price,stocks)  
        return
      
      # now lets place orders,
      if high_sell_volume > 0:
        high_sell_price = price_tick.align_tick(False,stock_attr["stock_currency"],high_sell_price)
        
      if low_buy_volume > 0:
        low_buy_price = price_tick.align_tick(True,stock_attr["stock_currency"],low_buy_price)
       
      #check if there already have this kind of orders
      need_cancel_all_orders = False
      high_order_exist = False
      low_order_exist = False
      for order in order_list_res.data["items"]:
        # we only expect high sell order and low buy order in order list.
        # so if there is any unexpected order, we should canncel all orders and wait next round.
        if order["symbol"] == stock_name:
          if order["status"] == "REPORTED" and not need_cancel_all_orders:
            if (order["price"] == high_sell_price
                and order["quantity"] == high_sell_volume
                and order["side"] == "SELL"):
              high_order_exist = True
            elif (order["price"] == low_buy_price
                and order["quantity"] == low_buy_volume
                and order["side"] == "BUY"):
              low_order_exist = True
            else:
              need_cancel_all_orders = True
          
          if order["status"] in ("NO_REPORT","WAIT_REPORT","WAIT_WITHDRAW","PART_WAIT_WITHDRAW","PART_CONCLUDED"):
            need_cancel_all_orders = True
          
          if need_cancel_all_orders and (order["status"] == "REPORTED" or order["status"] == "PART_CONCLUDED"):
            _log.debug("cancel order: %s %s %s %s",order["id"],order["side"], order["price"], order["quantity"])
            proxy.cancel_order(order["id"])
      
      if not need_cancel_all_orders:
        # then we need to make sure there are high sell order and low buy order
        if high_sell_volume > 0 and not high_order_exist:
          proxy.place_order(False,stock_name,stock_attr["stock_currency"],high_sell_price,high_sell_volume)
          _log.debug("place one order: False, %s, %s, %s ",stock_name,high_sell_price,high_sell_volume)
        
        if low_buy_volume > 0 and not low_order_exist:
          proxy.place_order(True,stock_name,stock_attr["stock_currency"],low_buy_price,low_buy_volume)
          _log.debug("place one order: True, %s, %s, %s ",stock_name,low_buy_price,low_buy_volume)
         
  def run_policy_for_stock(self,stock_name:str, stock_attr:dict,balance_res,order_list_res,position_list_res):
    try:
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
      
      # update the price for adjust decsion
      adjust_decision.AdjustDecision().update_price(stock_name,current_price)
      
      stocks -= stock_attr["reserve_stocks"]
      _log.debug("stocks_without_reserve: %s, current_price: %s, balance: %s",stocks,current_price, account_balance)
      
      #every time use new amount
      amount_money_for_stock = add_balance.AddBalance().get_new_amount(stock_name)
      
      #calculate price array and stock number array
      price_degree_array = policy_helper.calculate_price_groups(stock_attr["max_price"],stock_attr["min_price"],stock_attr["degree"])
      stock_num_array = self._calculate_stock_num_array(price_degree_array,amount_money_for_stock,stock_attr["degree"],stock_attr["round_stocks"])
      
      #calcuate the degree and run the policy
      buy, stock_num, execute_price = self._cal_buy_sell_stocks(stocks,
                                                 current_price,
                                                 stock_attr["min_trade_stocks"],
                                                 stock_attr["round_stocks"],
                                                 stock_attr["fraction"],
                                                 price_degree_array,
                                                 stock_num_array)
      self.make_orders(stock_name,order_list_res,stock_attr,stock_attr["fraction"],stocks,stock_num_array,price_degree_array,current_price,buy,stock_num,execute_price)
    except:
      #something wrong happen to this policy, just skip it
      traceback_str = traceback.format_exc()
      _log.warning("internal error: %s", traceback_str)
      return
