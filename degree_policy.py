import asyncio,traceback,json

import core.config as config
import core.degree_policy as degree_policy
import core.snowball_proxy as snowball_proxy
import core.logger as logger
import core.trade_time as trade_time
import core.report as report

_log = logger.get_logger()

async def main():
  try:
    config.output_configs(_log)
    min_trade_stocks = config.get_policy_min_trade_stocks()
    stocks = json.loads(config.get_policy_stocks_config())
    for _, stock_attr in stocks.items():
      # fill the min trade stocks for those stocks which not configured in trade stocks
      if "min_trade_stocks" not in stock_attr:
        stock_attr["min_trade_stocks"] = min_trade_stocks
    
    proxy = snowball_proxy.SnowBallProxy()
    policy = degree_policy.DegreePolicy()
    
    while True:
      await asyncio.sleep(config.get_policy_check_interval_in_seconds())
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
      
      #check if responses are okay, otherwise skip this time
      if balance.result_code != "60000" or order_list.result_code != "60000" or position_list.result_code != "60000":
        _log.warn("proxy get balance,order_list,position_list fail")
        continue
      
      #then for each stock, run policy
      for stock_name, stock_attr in stocks.items():
        policy.run_policy_for_stock(stock_name,stock_attr,balance,order_list,position_list)
      
  except Exception as e:
    # any uncaughted exception will make program exit
    traceback_str = traceback.format_exc()
    _log.warning("internal error: %s", traceback_str)
    
# Start servers
if __name__ == "__main__":
  # Get the default event loop and run the main routine
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
