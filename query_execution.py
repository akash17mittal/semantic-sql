from query import Query
from constants import *
from image_selection import ImageSelection
from text_to_image_semantic_search import TextToImageSemanticSearcher


class QueryExecution:

  def __init__(self, sql_str: str):
    self.query = Query(sql_str)
    if self.query.semantic_predicate is not None:
      self.img_selection = ImageSelection()
      self.searcher = TextToImageSemanticSearcher(index_path='data/index', ids_path="data/index_ids.npy")



