#!/usr/bin/env python3
"""
Weekly Backdrop Generator Automation Script
v1.0
By Chris Holmes

Runs a script that uses Playwright to automate the Nuvio Backdrop Generator web app, generating backdrops for various categories
and uploading them to my GitHub repository.
"""

import os
import sys
import base64
import datetime
import json
import time


# Dependency check
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    sys.exit(
        "playwright is not installed.\n"
        "Run:  pip install playwright && playwright install chromium"
    )

try:
    import requests
except ImportError:
    sys.exit("requests is not installed.\nRun:  pip install requests")

GENERATOR_URL   = "https://paytonjewell.github.io/Nuvio-Backdrop-Generator/"
GITHUB_TOKEN    = os.environ["GITHUB_TOKEN"]
GITHUB_BRANCH   = os.environ.get("GITHUB_BRANCH", "main")
GITHUB_FILE     = "Backdrops/"
TMDB_KEY        = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlY2RkZjFjNzk4ZGUzYTRjNzk1NGViOTRkM2FkODY3ZCIsIm5iZiI6MTc3MDc3MTQwNi4wMDE5OTk5LCJzdWIiOiI2OThiZDNjZDJhMWM2MTI2ZTc4ODVjODgiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.EnCCVp3ieKgmi5hFEavsPkDBfA2_e7gI2iAuLSJYYG0"
MDBLIST_KEY     = "yiuz1vhq6o16wxv4o2y7km8xw"
TRAKT_KEY       = "9ff48c3135acd6cc174fc136eb6389d1d51a86bf861862c75ea8a753cf23309d"

# Main function to generate backdrops using the Nuvio Backdrop Generator
def generate_backdrops():

    # Open a Playwright browser and navigate to the generator URL    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"2. Navigating to {GENERATOR_URL}")
        page.goto(GENERATOR_URL, wait_until="networkidle", timeout=60_000)

        # Give any JS/canvas init a moment to settle
        #page.wait_for_timeout(2_000)

        # Fill in API keys
        page.locator("#tmdbKey").fill(TMDB_KEY)
        page.locator("#traktKey").fill(TRAKT_KEY)
        page.locator("#mdblistKey").fill(MDBLIST_KEY)
        
        # Select 'Posters'. This setting never changes.
        page.get_by_text("Posters").click()
        
    ## Generate 'New Movies' backdrop.
        print("   A. Generating backdrop for 'New Movies'")
        
        page.get_by_role("button", name="Trakt").click()
        page.get_by_placeholder("https://trakt.tv/users/username/lists/listname").fill("https://app.trakt.tv/users/giladg/lists/latest-releases?mode=movie")
        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download").click(trial=True)

        capture_canvas_and_upload(page, "Backdrop_New_Movies.png")

# Capture the canvas image data, save it locally, and upload it to GitHub
def capture_canvas_and_upload(page, path):
    # Locate image data from the canvas element
    canvas_data: str = page.evaluate("""() => {
        const canvas = document.querySelector('canvas');
        if (!canvas) return null;
        return canvas.toDataURL('image/png');
    }""")

    # Extract the base64-encoded PNG data from the data URL and decode it to bytes
    if canvas_data and canvas_data.startswith("data:image"):
        header, encoded = canvas_data.split(",", 1)
        png_bytes = base64.b64decode(encoded)
        print(f"      a. Extracted canvas image ({len(png_bytes):,} bytes)")
    else:
        print("✗ Failed to extract canvas image data")
        sys.exit(1) 

    # Save the image locally
    with open(path, "wb") as f:
        f.write(png_bytes)
    print(f"      b. Saved image locally: {path} ({len(png_bytes):,} bytes)")

    # Uploads the image to GitHub using the GitHub API
    GITHUB_FILE = "Backdrops/" + path
    print(f"      c. Uploading to GitHub using API Token credentials")

    api_base = f"https://api.github.com/repos/chrisholmes02/TVImages/contents/{GITHUB_FILE}"
    headers  = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept":        "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    date_str = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
    commit_message = f"chore: weekly backdrop update ({date_str})"
    encoded_content = base64.b64encode(png_bytes).decode()

    # Check if the file already exists (we need its SHA to update it)
    sha = None
    print(f"         1. Checking existing file at chrisholmes02/TVImages/{GITHUB_FILE}")
    resp = requests.get(api_base, headers=headers, params={"ref": GITHUB_BRANCH})
    if resp.status_code == 200:
        sha = resp.json().get("sha")
        print(f"         2. File exists (sha: {sha[:8]}…) – will update")
    elif resp.status_code == 404:
        print("         2. File does not exist yet – will create")
    else:
        print(f"✗  GitHub API error {resp.status_code}: {resp.text}")
        sys.exit(1)

    payload: dict = {
        "message": commit_message,
        "content": encoded_content,
        "branch":  GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    print(f"         3. Pushing to GitHub (chrisholmes02/TVImages/{GITHUB_FILE}) … ", end="")
    put_resp = requests.put(api_base, headers=headers, data=json.dumps(payload))

    if put_resp.status_code in (200, 201):
        action = "Updated" if sha else "Created"
        commit_url = put_resp.json().get("commit", {}).get("html_url", "")
        print(f"{action} successfully")
        if commit_url:
            print(f"         4. Commit: {commit_url}")
    else:
        print(f"✗ GitHub API error {put_resp.status_code}: {put_resp.text}")
        sys.exit(1)

def main():
    print("=" * 60)
    print("  Nuvio Backdrop Image Generator - Weekly Automation")
    print("=" * 60, "\n")

    print("1. Opening Chromium browser in headless session")
    
    generate_backdrops()

    print("3. Done Successfully!")


if __name__ == "__main__":
    main()
