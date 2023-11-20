import logging
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

    col1, col2 = st.columns([5, 5])

    selectedData = st.sidebar.selectbox('Choose Data', data_files)
    if st.sidebar.button("Setup DB"):
        base_table_setup = DBTableSetup(f"{DB_URL}/{DB_NAME}")
        d = pd.read_csv("data/amazon_reviews.csv")
        base_table_setup.insert_blob_data("reviews", d, ["review_id"])

    if st.sidebar.button("Reset Database", key="videodatareset"):
        # delete everything in database
        pass

    if "curr_executing" not in st.session_state:
        st.session_state["curr_executing"] = False

    if "img_selection" not in st.session_state:
        st.session_state["img_selection"] = ImageSelection()

    with col1:
        col1.header("Query the Data")
        input_query = st.text_area('Type SQL query here', 'SELECT * FROM objectdetectionresults', 150)
        if st.button("Execute query"):
            st.session_state.curr_executing = True
    if st.session_state.curr_executing:
        with col2:
            image_for_user_feedback = st.session_state.img_selection.get_next_image()
            if image_for_user_feedback:
                st.image(image_for_user_feedback)
                if st.button("Satisfies?", key="yes"):
                    st.session_state.img_selection.update_user_feedback()
                if st.button("Not Satisfied", key="no"):
                    st.session_state.img_selection.update_user_feedback()
