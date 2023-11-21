from query import Query
from constants import *
from image_selection import ImageSelection


class QueryExecution:

  def __init__(self, sql_str: str):
    self.query = Query(sql_str)
    if self.query.semantic_predicate is not None:
      self.img_selection = ImageSelection()



