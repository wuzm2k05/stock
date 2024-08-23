import datetime

from . import email
from . import snowball_proxy
from . import config

_last_report_date = None

def _report():
  # get the order list from snowball
  proxy = snowball_proxy.SnowBallProxy()
  balance_response = proxy.get_balance()
  order_list_response = proxy.get_order_list()
  position_list_response = proxy.get_position_list()
  
  msg_body = ""
  if balance_response.result_code == "60000":
    msg_body += "Balance: \n"
    for cash in balance_response.data["balance_detail_items"]:
      msg_body += "  "+cash["currency"]+": "+ str(cash["cash"])+"\n"
  
  msg_body += "\n"
  if position_list_response.result_code == "60000":
    msg_body += "Position: \n"
    for stock in position_list_response.data:
      msg_body += "  "+ stock["symbol"] + ": " + str(stock["position"]) + "\n"
  
  msg_body += "\n"
  if order_list_response.result_code == "60000":
    msg_body += "Completed Orders: \n"
    for order in order_list_response.data["items"]:
      if order["status"] == "CONCLUDED":
        msg_body += "  " + order["symbol"] +": " + order["side"]+" "+ str(order["quantity"]) +" "+ str(order["price"])
  
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
    
    
  
  