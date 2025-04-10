class OrderListRes:
  def __init__(self):
    self.data = {}
    self.data["items"] = []
  
  def add_order(self,item):
    """
    add one item to list
    """
    self.data["items"].append(item)