from datetime import datetime
import pytz

def is_us_trade_time():
  # 定义美东时间时区
  eastern = pytz.timezone('US/Eastern')
  
  # 获取当前美东时间
  now = datetime.now(eastern)
  
  # 定义常规交易时间
  market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
  market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
  
  # 判断是否在交易时间内
  if market_open <= now <= market_close:
    return True
  else:
    return False

def is_hk_trade_time():
  # 定义香港时间时区
  hong_kong = pytz.timezone('Asia/Hong_Kong')
  
  # 获取当前香港时间
  now = datetime.now(hong_kong)
  
  # 定义上午和下午的交易时间
  morning_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
  morning_close = now.replace(hour=12, minute=0, second=0, microsecond=0)
  afternoon_open = now.replace(hour=13, minute=0, second=0, microsecond=0)
  afternoon_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
  
  # 判断是否在交易时间内
  if (morning_open <= now <= morning_close) or (afternoon_open <= now <= afternoon_close):
      return True
  else:
      return False

def possible_trade_time():
  if is_us_trade_time():
    return True
  
  if is_hk_trade_time():
    return True
  
  return False

if __name__ == "__main__":
  is_open = is_us_trade_time()
  print("us market is ",is_open)
  is_open = is_hk_trade_time()
  print("hk market is ",is_open)