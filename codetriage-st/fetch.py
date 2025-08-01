import streamlit as st
import pandas as pd
import os
import requests
from urllib.parse import urlparse
import math

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

def pagination(owner, repo, page):
    total_issues = get_total_open_issues(owner, repo)
    total_pages = (total_issues + PER_PAGE - 1) // PER_PAGE

    start_page = max(1, page - 4)
    end_page = min(total_pages, start_page + 9)
    start_page = max(1, end_page - 9)

    return start_page, end_page, total_pages