import streamlit as st
from transformers import pipeline
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
import os
import requests
from urllib.parse import urlparse

st.set_page_config(page_title="CodeTriage AI", layout="wide")

def parse_owner_repo(url: str):
    try:
        path = urlparse(url).path.strip("/")
        owner, repo = path.split("/")[:2]
        return owner, repo
    except:
        return None, None
    
def fetch_issues(owner, repo, page):
    headers = {}
    # (optionally add your token here)
    params = {"state": "all", "per_page": 30, "page": page}
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
    prev, _ , nxt = st.columns([1,8,1])
    with prev:
        if st.button("<- Previous") and page > 1:
            st.session_state.page -= 1
            st.rerun()
    with nxt:
        if st.button("Next ->") and issues:
            st.session_state.page += 1
            st.rerun()
    