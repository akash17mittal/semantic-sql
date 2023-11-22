import logging
import os

import streamlit as st
import pandas as pd
from db_setup import DBTableSetup
from query_execution import QueryExecution
from text_to_image_semantic_search import create_and_save_faiss_index_with_ids
from constants import *

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':

  data_files = ["data/objects.csv"]

  # UI Elements
  st.set_page_config(layout="wide", page_title="Semantic SQL")
  st.title("Semantic SQL")

  col1, col2, col3 = st.columns([5, 5, 5])

  selectedData = st.sidebar.selectbox('Choose Data', data_files)
  if st.sidebar.button("Setup DB"):
    base_table_setup = DBTableSetup(f"{DB_URL}/{DB_NAME}")
    d = pd.read_csv(selectedData)
    base_table_setup.insert_blob_data("objects", d, ["id", "object_id"])
    create_and_save_faiss_index_with_ids("data/embeddings-instances.pt", "data/imageIds-instances.pt",
                                         index_path="data/index", ids_save_path="data/index_ids.npy")

  if st.sidebar.button("Reset Database", key="db_reset"):
    # delete everything in database
    os.remove(DB_NAME)
    os.remove("data/index")
    os.remove("data/index_ids.npy")
    st.session_state["curr_executing"] = False

  if st.sidebar.button("New Query", key="new_query"):
    # delete everything in database
    st.session_state["curr_executing"] = False
    st.session_state["results_ready"] = False

  if "curr_executing" not in st.session_state:
    st.session_state["curr_executing"] = False

  if "results_ready" not in st.session_state:
    st.session_state["results_ready"] = False

  if "curr_query" not in st.session_state:
    st.session_state["curr_query"] = "SELECT DISTINCT id from objects WHERE class_name='car' SEMANTIC 'red car'"

  with col1:
    col1.header("Query the Data")
    input_query = st.text_area('Type SQL query here', st.session_state["curr_query"], 300)
    if st.button("Execute query"):
      st.session_state.curr_executing = True
      st.session_state.results_ready = False
      st.session_state["curr_query"] = input_query
      st.session_state["query_execution"] = QueryExecution(input_query)
      if st.session_state["query_execution"].execution_complete:
        st.session_state["results_ready"] = True

  with col2:
    col2.header("User in the loop feedback")

  if st.session_state.curr_executing:
    with col2:
      if not st.session_state["query_execution"].execution_complete:
        print("Rerendeded", "+" * 20)
        image_for_user_feedback = st.session_state["query_execution"].img_selection.get_next_image()
        if image_for_user_feedback:
          st.image(image_for_user_feedback, use_column_width=True)
          col_n_1, col_n_2 = st.columns([1, 1])
          with col_n_1:
            if st.button("Satisfies?", key="yes", use_container_width=True):
              v = st.session_state["query_execution"].img_selection.update_user_feedback(True)
              st.session_state.curr_executing = v
              st.session_state.results_ready = not v
              st.rerun()
          with col_n_2:
            if st.button("Does NOT Satisfy?", key="no", use_container_width=True):
              v = st.session_state["query_execution"].img_selection.update_user_feedback(False)
              st.session_state.curr_executing = v
              st.session_state.results_ready = not v
              st.rerun()

  with col3:
    col3.header("Query Results")
  if st.session_state.results_ready:
    with col3:
      st.write(st.session_state["query_execution"].get_results())
