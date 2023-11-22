from query import Query
from constants import *
from image_selection import ImageSelection
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
    except Exception:
      loop = asyncio.new_event_loop()
      asyncio.set_event_loop(loop)
    loop.run_until_complete(self._execute_base_query())
    loop.close()

    if self.query.semantic_predicate is not None:
      self.img_selection = ImageSelection(self.results_df, self.query.semantic_predicate)
      self.execution_complete = False
    else:
      self.execution_complete = True

  async def _execute_base_query(self):
    async with self._sql_engine.begin() as conn:
      self.results_df = await conn.run_sync(
        lambda conn: pd.read_sql(text(self.query.base_query_without_semantic), conn))

  def get_results(self):
    if self.execution_complete:
      return self.results_df
    else:
      satisfied_image_ids = self.img_selection.satisfied_ids
      return self.results_df.set_index("id", drop=True).loc[satisfied_image_ids["id"].values].reset_index()
