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

st.set_page_config(page_title="CodeTriage AI", layout="wide")
PER_PAGE = 20
def parse_owner_repo(url: str):
    try:
        path = urlparse(url).path.strip("/")
        owner, repo = path.split("/")[:2]
        return owner, repo
    except:
        return None, None
    
def get_total_open_issues(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("open_issues_count", 0)
    return 0

def fetch_issues(owner, repo, page):
    headers = {}
    # (optionally add your token here)
    params = {"state": "open", "per_page": PER_PAGE, "page": page}
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/issues",
        params=params,
        headers=headers,
    )
    return resp.json() if resp.status_code == 200 else []

# collect and parse repo url
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

# display issues table
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

    # pagination controls
    total_issues = get_total_open_issues(owner, repo)
    total_pages = (total_issues + PER_PAGE - 1) // PER_PAGE

    start_page = max(1, page - 4)
    end_page = min(total_pages, start_page + 9)
    start_page = max(1, end_page - 9)

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
    