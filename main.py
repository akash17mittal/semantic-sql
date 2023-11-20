import pandas as pd
from db_setup import DBTableSetup

DB_URL = 'sqlite+aiosqlite://'
DB_NAME = 'ssql_test.sqlite'

base_table_setup = DBTableSetup(f"{DB_URL}/{DB_NAME}")
d = pd.read_csv("data/amazon_reviews.csv")
base_table_setup.insert_blob_data("reviews", d, ["review_id"])