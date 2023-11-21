from query import Query
from constants import *
from image_selection import ImageSelection
from text_to_image_semantic_search import TextToImageSemanticSearcher
from sqlalchemy.sql import text

import asyncio
import pandas as pd
import sqlalchemy
import sqlalchemy.ext.asyncio


class QueryExecution:

  def __init__(self, sql_str: str):
    self._sql_engine = sqlalchemy.ext.asyncio.create_async_engine(
      f"{DB_URL}/{DB_NAME}",
    )
    self.query = Query(sql_str)

    try:
      loop = asyncio.get_event_loop()
    except Exception as e:
      loop = asyncio.new_event_loop()
      asyncio.set_event_loop(loop)
    loop.run_until_complete(self._execute_base_query())
    loop.close()

    if self.query.semantic_predicate is not None:
      self.img_selection = ImageSelection()
      self.searcher = TextToImageSemanticSearcher(index_path='data/index', ids_path="data/index_ids.npy")
      self.execution_complete = False
    else:
      self.execution_complete = True

  async def _execute_base_query(self):
    async with self._sql_engine.begin() as conn:
      self.results_df = await conn.run_sync(
        lambda conn: pd.read_sql(text(self.query.base_query_without_semantic), conn))

  def get_results(self):
    return self.results_df
