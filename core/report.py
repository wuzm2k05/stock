import datetime,time,traceback

from . import email
from . import snowball_proxy
from . import config

_last_report_date = None

def _report():
  msg_body = ""
  
  try:
    # get the order list from snowball
    proxy = snowball_proxy.SnowBallProxy()
    balance_response = proxy.get_balance()
    order_list_response = proxy.get_order_list()
    position_list_response = proxy.get_position_list()
    current_ms_ts = int(time.time()*1000)
    time_one_day_ago = datetime.datetime.now() -datetime.timedelta(hours=24)
    one_day_before_ms_ts = int(time_one_day_ago.timestamp() * 1000)
    transaction_list = proxy.get_transactions(min_time=one_day_before_ms_ts,max_time=current_ms_ts)
    
    msg_body += "Balance: \n"
    for cash in balance_response.data["balance_detail_items"]:
      msg_body += "  "+cash["currency"]+": "+ str(cash["cash"])+"\n"
  
    msg_body += "\n"
    msg_body += "Position: \n"
    for stock in position_list_response.data:
      msg_body += "  "+ stock["symbol"] + ": " + str(stock["position"]) + "\n"
  
    msg_body += "\n"
    msg_body += "Completed[INVALID] Orders: \n"
    for order in order_list_response.data["items"]:
      if order["status"] == "CONCLUDED":
        msg_body += "  " + order["symbol"] +": " + order["side"]+" "+ str(order["quantity"]) +" "+ str(order["price"]) + "\n"
      elif order["status"] == "INVALID":
        msg_body += "  " + "INVALID_ORDRE!" + "   " + order["symbol"] +": " + order["side"]+" "+ str(order["quantity"]) +" "+ str(order["price"]) + "\n"   
  
    msg_body += "\n"
    msg_body += "Completed Transactions: \n"
    for t in transaction_list.data["items"]:
      if t["status"] == "CONCLUDED":
        msg_body += "  " + t["symbol"] +": " + t["side"]+" "+ str(t["quantity"]) +" "+ str(t["price"]) + "\n"
  
  except Exception as e:
    # any uncaughted exception will make program exit
    traceback_str = traceback.format_exc()
    msg_body += traceback_str
  
  finally: 
    email.send_email("stock daily report",msg_body)
  
def trigger_report():
  global _last_report_date
  
  current_date = datetime.date.today()
  if current_date == _last_report_date:
    # already report, so do nothing
    return
  
  current_time = datetime.datetime.now().time()
  report_hour_start = config.get_report_start_hour()
  report_hour_end = config.get_report_end_hour()
  
  if current_time >= datetime.time(report_hour_start,0) and current_time <= datetime.time(report_hour_end,0):
    # report
    _report()
    _last_report_date = current_date
    
    
  
  