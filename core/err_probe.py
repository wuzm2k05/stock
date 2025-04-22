_last_concluded_order_nbr_map = {}

def has_recent_concluded_order(order_list_res,stock_name)->bool:
  global _last_concluded_order_nbr_map
  
  #calculate how many concluded order this time
  current_concluded_order_nbr = 0
  for order in order_list_res.data["items"]:
    if order["symbol"] == stock_name:
      if order["status"] == "CONCLUDED":
        current_concluded_order_nbr += 1
       
  if stock_name in _last_concluded_order_nbr_map:
    if _last_concluded_order_nbr_map[stock_name] == current_concluded_order_nbr:
      return False
  
  _last_concluded_order_nbr_map[stock_name] = current_concluded_order_nbr
  return True