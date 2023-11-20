from typing import List

import asyncio
import pandas as pd
import sqlalchemy
import sqlalchemy.ext.asyncio
from sqlalchemy import MetaData


def python_type_to_sqlalchemy_type(python_type):
  if python_type == int:
    return sqlalchemy.Integer
  elif python_type == float:
    return sqlalchemy.Float
  elif python_type == str or python_type == object:
    return sqlalchemy.String
  elif python_type == bool:
    return sqlalchemy.Boolean
  else:
    raise ValueError(f'Unknown python type {python_type}')


class DBTableSetup(object):

  def __init__(self, connection_uri):
    self._sql_engine = sqlalchemy.ext.asyncio.create_async_engine(
      connection_uri,
    )

  async def _create_table(self, table_name, table_columns):
    '''
    creates the table in the database
    '''
    async with self._sql_engine.begin() as conn:
      metadata = MetaData(bind=conn)
      _ = sqlalchemy.Table(table_name, metadata, *[
        sqlalchemy.Column(c_name, c_type, primary_key=is_pk) for c_name, c_type, is_pk in table_columns
      ])
      await conn.run_sync(lambda conn: metadata.create_all(conn))

  async def _insert_data_in_table(self, table_name: str, data: pd.DataFrame):
    '''
    inserts rows in the table
    '''
    async with self._sql_engine.begin() as conn:
      try:
        await conn.run_sync(lambda conn: data.to_sql(table_name, conn, if_exists='append', index=False))
      except sqlalchemy.exc.IntegrityError:
        print(f"Skipping: Blob table is already populated with the blobs")

  def insert_blob_data(self, table_name, blob_data: pd.DataFrame, primary_key_cols: List[str]):
    '''
    inserts the blob data in the blob table
    '''
    assert len(primary_key_cols) > 0, 'Primary key should be specified'
    assert blob_data.shape[0] > 0, 'No blobs to insert in the blob table'
    table_columns = []
    for column in blob_data.columns:
      dtype = python_type_to_sqlalchemy_type(blob_data[column].dtype)
      if dtype == sqlalchemy.String:
        c_type = sqlalchemy.Text()
      else:
        c_type = dtype
      table_columns.append((column, c_type, column in primary_key_cols))

    try:
      loop = asyncio.get_event_loop()
    except Exception as e:
      loop = asyncio.new_event_loop()
      asyncio.set_event_loop(loop)
    loop.run_until_complete(self._create_table(table_name, table_columns))
    loop.run_until_complete(self._insert_data_in_table(table_name, blob_data))
    loop.close()
