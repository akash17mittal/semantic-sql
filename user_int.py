import logging
import os

import streamlit as st
import pandas as pd
from image_selection import ImageSelection
from db_setup import DBTableSetup

DB_URL = 'sqlite+aiosqlite://'
DB_NAME = 'ssql_test.sqlite'

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':

    data_files = ["data/amazon_reviews.csv"]

    # UI Elements
    st.set_page_config(layout="wide", page_title="Semantic SQL")
    st.title("Semantic SQL")

    col1, col2, col3 = st.columns([5, 5, 5])

    selectedData = st.sidebar.selectbox('Choose Data', data_files)
    if st.sidebar.button("Setup DB"):
        base_table_setup = DBTableSetup(f"{DB_URL}/{DB_NAME}")
        d = pd.read_csv(selectedData)
        base_table_setup.insert_blob_data("reviews", d, ["review_id"])

    if st.sidebar.button("Reset Database", key="db_reset"):
        # delete everything in database
        os.remove(DB_NAME)
        st.session_state["curr_executing"] = False
        st.session_state["img_selection"] = ImageSelection()

    if "curr_executing" not in st.session_state:
        st.session_state["curr_executing"] = False

    if "results_ready" not in st.session_state:
        st.session_state["results_ready"] = False

    if "img_selection" not in st.session_state:
        st.session_state["img_selection"] = ImageSelection()

    with col1:
        col1.header("Query the Data")
        input_query = st.text_area('Type SQL query here', 'SELECT * FROM objectdetectionresults', 150)
        if st.button("Execute query"):
            st.session_state.curr_executing = True

    with col2:
        col2.header("User in the loop feedback")

    if st.session_state.curr_executing:
        with col2:
            image_for_user_feedback = st.session_state.img_selection.get_next_image()
            if image_for_user_feedback:
                st.image(image_for_user_feedback, use_column_width=True)
                col_n_1, col_n_2 = st.columns([1,1])
                with col_n_1:
                    if st.button("Satisfies?", key="yes", use_container_width=True):
                        st.session_state.img_selection.update_user_feedback()
                with col_n_2:
                    if st.button("Does NOT Satisfy?", key="no", use_container_width=True):
                        st.session_state.img_selection.update_user_feedback()

    with col3:
        col3.header("Query Results")
    if st.session_state.results_ready:
        with col3:
            pass
