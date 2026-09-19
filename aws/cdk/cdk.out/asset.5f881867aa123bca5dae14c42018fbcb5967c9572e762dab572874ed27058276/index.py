#!/usr/bin/env python3
"""
Squeeze AI - Codebase Indexer API
Priority 4:
Clones or downloads a repository, generates topological centrality graph and AST skeletons,
and returns a compact symbol map for Amazon Q Developer or custom Bedrock coding agents.
"""

import os
import sys
import json
import shutil
import zipfile
import urllib.request
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import squeeze_core as engine

def download_and_extract_repo(repo_url: str, target_dir: str) -> str:
    """Downloads repository archive using zipball (zero git binary dependency)."""
    clean_url = repo_url.rstrip("/")
    if clean_url.endswith(".git"):
        clean_url = clean_url[:-4]
    
    # Standard GitHub zip URL format
    # e.g. https://github.com/owner/repo/archive/refs/heads/main.zip
    zip_url = f"{clean_url}/archive/refs/heads/main.zip"
    zip_path = os.path.join(target_dir, "repo.zip")

    print(f"📥 Fetching repository archive: {zip_url}...")
    headers = {"User-Agent": "Squeeze-AI-AWS-Indexer/1.0"}
    req = urllib.request.Request(zip_url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp, open(zip_path, "wb") as out:
            out.write(resp.read())
    except Exception as e:
        # Try 'master' branch fallback
        zip_url = f"{clean_url}/archive/refs/heads/master.zip"
        req = urllib.request.Request(zip_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp, open(zip_path, "wb") as out:
            out.write(resp.read())

    extract_path = os.path.join(target_dir, "extracted")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_path)

    # Find the top-level extracted directory
    entries = os.listdir(extract_path)
    if entries:
        return os.path.join(extract_path, entries[0])
    return extract_path


def lambda_handler(event, context):
    print("Received event for Codebase Indexer.")
    
    # Parse request
    body = {}
    if "body" in event and event["body"]:
        try:
            body = json.loads(event["body"])
        except Exception:
            body = {}
    elif isinstance(event, dict):
        body = event

    repo_url = body.get("repo_url", "")
    max_files = int(body.get("max_files", 50))
    inline_code = body.get("inline_code", "")

    work_dir = f"/tmp/sqz_index_{int(time.time() * 1000)}"
    os.makedirs(work_dir, exist_ok=True)

    try:
        if repo_url:
            target_scan_dir = download_and_extract_repo(repo_url, work_dir)
        elif inline_code:
            # Inline code snippet indexing
            sample_file = os.path.join(work_dir, "sample.py")
            with open(sample_file, "w", encoding="utf-8") as fp:
                fp.write(inline_code)
            target_scan_dir = work_dir
        else:
            # Default to indexing current package
            target_scan_dir = os.path.dirname(os.path.abspath(__file__))

        start_time = time.time()
        graph_md = engine.generate_codebase_graph(target_scan_dir, max_files=max_files)
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "status": "success",
                "repo_url": repo_url,
                "elapsed_ms": elapsed_ms,
                "graph_markdown": graph_md
            })
        }
    except Exception as e:
        print(f"Error indexing repository: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"status": "error", "message": str(e)})
        }
    finally:
        # Clean up ephemeral storage
        try:
            shutil.rmtree(work_dir, ignore_errors=True)
        except Exception:
            pass
