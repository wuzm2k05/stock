from . import logger
from . import config

_log = logger.get_logger()

class SingletonMeta(type):
  _instances = {}

  def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super().__call__(*args, **kwargs)
    return cls._instances[cls]

class AdjustDecision(metaclass=SingletonMeta):
  def __init__(self):
    self.stocks = {}
    self.enable = config.get_adjust_decision() and not config.get_use_order() # if use order, then cannot adjust decision
  
  def update_price(self,stock,current_price):
    if not self.enable:
      # not enable adjust decision, then do nothing
      return
    
    if stock not in self.stocks:
      # If it's the first time we encounter this stock, initialize the last price
      self.stocks[stock] = {"price":current_price,"trend":"flat"}
      _log.debug(f"Initialized stock {stock} with price {current_price}")
      return
    else:
      last_price = self.stocks[stock]["price"]
      self.stocks[stock]["price"] = current_price
      if (last_price > current_price):
        self.stocks[stock]["trend"] = "down"
      elif (last_price < current_price):
        self.stocks[stock]["trend"] = "up"
      else:
        self.stocks[stock]["trend"] = "flat"
        
    
  # decide if we should process the action to buy or sell stock.
  # Arguments:
  # 
  def query(self,is_buy,stock) -> bool:
    """
    Des:
      decide if we should process the action to buy or sell stock. remember the current price to self.stocks for each stock.
      if we find the current_price is higher than last price, then means the price is rising, don't sell untill the price not rising.
      if we find the current_price is lower than last price, then means the price is going down, don't buy untill the price not going down.
    Arguments:
      is_buy: true for buy, false for sell.
      stock: stock name
      current_price: current price of the stock
    Return:
      true: to process the action
      false: not process the action
    """
    if not self.enable:
      # not enable adjust decision, then return True always
      return True
    
    # Check if we have recorded this stock before
    if stock not in self.stocks:
      # something wrong happen, so return true
      return True
    
    if is_buy:
      # For buying, if the price is not going down, then do it.
      if self.stocks[stock]["trend"] != "down":
        _log.debug("buy stocks since the trend is not down anymore")
        return True
      else:
        _log.debug("postpone buying since the trend is down")
        return False
    else:
      # For selling, if the price is not rising, then do it.
      if self.stocks[stock]["trend"] != "up":
        _log.debug("sell stocks since the trend is not up anymore")
        return True
      else:
        _log.debug("postpone selling since the trend is up")
        return False