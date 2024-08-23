import math

_hk_stock_tick_list = [(0.01,0.001,3),(0.25,0.005,3),(0.5,0.01,2),(10.0,0.02,2),(20.0,0.05,2),(100.0,0.1,1),(200.0,0.2,1),(500.0,0.5,1),(1000.0,1.0,0),(2000.0,2.0,0),(5000.0,5.0,0)]
_us_stock_tick_list = [(0.0,0.0001,4),(1.0,0.01,2)]


def _align_tick_price(price,up,stock_tick_list):
  #find the tick
  tick = 0.0
  decimal_number = 0
  for low_price,t,d in stock_tick_list:
    if price >= low_price:
      tick = t
      decimal_number = d
    if price < low_price:
      break
  
  if up:
    return round(math.ceil(price/tick)*tick,decimal_number)
  else:
    return round(math.floor(price/tick)*tick,decimal_number)
    

def align_hk_tick_price(price,up):
  return _align_tick_price(price,up,_hk_stock_tick_list)

def align_us_tick_price(price,up):
  return _align_tick_price(price,up,_us_stock_tick_list)
