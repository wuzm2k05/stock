import asyncio,traceback,json

import core.config as config
import core.degree_policy as degree_policy
import core.snowball_proxy as snowball_proxy
import core.logger as logger
import core.trade_time as trade_time
import core.report as report
import core.email as email
import core.add_balance as add_balance

_log = logger.get_logger()

def check_stock_config_attr(stock_name,stock_attr):
  """
  Raise: Exception if stock_attr check fail
  """
  if (stock_attr["max_price"] <= stock_attr["min_price"] 
      or stock_attr["stock_currency"] not in ("USD","HKD")):
    raise Exception(" %s stock_attr check fail",stock_name)

async def main():
  config.output_configs(_log)
  min_trade_stocks = config.get_policy_min_trade_stocks()
  stocks = json.loads(config.get_policy_stocks_config())
  for stock_name, stock_attr in stocks.items():
    check_stock_config_attr(stock_name,stock_attr)
    # fill the min trade stocks for those stocks which not configured in trade stocks
    if "min_trade_stocks" not in stock_attr:
      stock_attr["min_trade_stocks"] = min_trade_stocks
    
  proxy = snowball_proxy.SnowBallProxy()
  policy = degree_policy.DegreePolicy()
  error_info = None
  
  while True:
    try:  
      await asyncio.sleep(config.get_policy_check_interval_in_seconds())
      
      if error_info:
        # try send error information last time
        email.send_error_email(error_info)
        error_info = None
        
      _log.debug("one cycle")
      report.trigger_report()
      # first check if it is in non-trade time
      if not trade_time.possible_trade_time():
        _log.debug("not in trade time, so skip this cycle")
        continue
      
      # first get position list, balance, order list from snowball.
      balance = proxy.get_balance()
      order_list = proxy.get_order_list()
      position_list = proxy.get_position_list()
      
      add_balance.AddBalance().trigger_add_balance(balance,order_list,position_list)
      
      #then for each stock, run policy
      for stock_name, stock_attr in stocks.items():
        policy.run_policy_for_stock(stock_name,stock_attr,balance,order_list,position_list)
    
    except Exception as e:
      # any uncaughted exception will make program exit
      traceback_str = traceback.format_exc()
      _log.warning("internal error: %s", traceback_str)
      error_info = traceback_str
    
# Start servers
if __name__ == "__main__":
  # Get the default event loop and run the main routine
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
