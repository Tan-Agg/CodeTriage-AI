import streamlit as st
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
import os
import requests
from urllib.parse import urlparse
import math
from fetch import parse_owner_repo, get_total_open_issues, fetch_issues, pagination

st.set_page_config(page_title="CodeTriage AI", layout="wide")

if "owner" not in st.session_state:
    st.markdown("<h1 style='text-align: center;'>CodeTriage AI</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        repo_input = st.text_input("Enter GitHub Repository URL", placeholder="https://github.com/owner/repo")
        if st.button("Load Issues"):
            owner, repo = parse_owner_repo(repo_input)
            if owner:
                st.session_state.owner = owner
                st.session_state.repo = repo
                st.session_state.page = 1
                st.rerun()
            else:
                st.error("Invalid GitHub URL")

else:
    owner = st.session_state.owner
    repo = st.session_state.repo
    page = st.session_state.page

    st.markdown(f"### Issues for `{owner}/{repo}` - Page {page}")

    issues = fetch_issues(owner, repo, page)
    if not issues:
        st.info("No issues found!")
    else:
        df = pd.DataFrame([{
            "Number": i["number"],
            "Title": i["title"],
            "URL": i["html_url"],
        } for i in issues])
        st.table(df)

    start_page, end_page, total_pages = pagination(owner, repo, page)
    prev, _ ,  pages_col , _ , nxt = st.columns([1, 4, 8, 4, 1])

    with prev:
        if st.button("<- Prev") and page > 1:
                st.session_state.page -= 1
                st.rerun()

    with pages_col:
        num_page_buttons = end_page - start_page + 1
        if num_page_buttons > 0:
            pagination_cols = st.columns(num_page_buttons)
            for idx, i in enumerate(range(start_page, end_page + 1)):
                button_label = f"**{i}**" if i == page else str(i)
                with pagination_cols[idx]:
                    if st.button(button_label, key=f"page_{i}"):
                        st.session_state.page = i
                        st.rerun()
        else:
            st.write("No pages to display.")

        
    with nxt:
        if st.button("Next ->") and page < total_pages:
            st.session_state.page += 1
            st.rerun()