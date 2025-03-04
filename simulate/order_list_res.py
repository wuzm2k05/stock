class OrderListRes:
  def __init__(self):
    self.data = {}
    self.data["items"] = []
  
  def add_order(self,symbol:str,status:str,side:str,quantity):
    """
    Arguments:
    symbol: name of the stock
    status: one of "REPORTED" "NO_REPORT","WAIT_REPORT","WAIT_WITHDRAW","PART_WAIT_WITHDRAW","PART_WITHDRAW","PART_CONCLUDED"
    side: "BUY" or "SELL"
    quantity: the quantity of the order
    """
    self.data["items"].append({"symbol":symbol,"status":status,"side":side,"quantity":quantity})