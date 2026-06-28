#!/usr/bin/env python3
"""
Weekly Backdrop Generator Automation Script
v1.0
By Chris Holmes

Runs a script that uses Playwright to automate the Nuvio Backdrop Generator web app, generating backdrops for various categories
and uploading them to a my GitHub repository.
"""

import os
import sys
import base64
import datetime
import json
import time

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Configuration (read from environment with sane defaults)
# ---------------------------------------------------------------------------
GENERATOR_URL   = "https://paytonjewell.github.io/Nuvio-Backdrop-Generator/"
GITHUB_TOKEN    = os.environ.get("BACKDROP_TOKEN", "") 
GITHUB_REPO     = "chrisholmes02/TVImages"
GITHUB_BRANCH   = os.environ.get("GITHUB_BRANCH", "main")
GITHUB_FILE     = "Backdrops/"
TMDB_KEY        = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlY2RkZjFjNzk4ZGUzYTRjNzk1NGViOTRkM2FkODY3ZCIsIm5iZiI6MTc3MDc3MTQwNi4wMDE5OTk5LCJzdWIiOiI2OThiZDNjZDJhMWM2MTI2ZTc4ODVjODgiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.EnCCVp3ieKgmi5hFEavsPkDBfA2_e7gI2iAuLSJYYG0"
TRAKT_KEY       = "9ff48c3135acd6cc174fc136eb6389d1d51a86bf861862c75ea8a753cf23309d"
LOCAL_OUTPUT    = ""
bytes           = b""

# Main function to generate backdrops using the Nuvio Backdrop Generator
def generate_backdrops():
    global png_bytes, bytes, LOCAL_OUTPUT

    print(f"Backdrop token: {GITHUB_TOKEN}")

    print("1. Opening Chromium browser in headless session")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"2. Navigating to {GENERATOR_URL}")
        page.goto(GENERATOR_URL, wait_until="networkidle", timeout=60_000)

        # Give any JS/canvas init a moment to settle
        page.wait_for_timeout(2_000)

        # Fill in API keys
        page.locator("#tmdbKey").fill(TMDB_KEY)
        page.locator("#traktKey").fill(TRAKT_KEY)
        
        # Select 'Posters'. This setting never changes.
        page.get_by_text("Posters").click()
        
    ## Generate 'New Movies' backdrop.
        # Select 'Trakt' as source.
        print("   A. Generating backdrop for 'New Movies'")
        page.get_by_role("button", name="Trakt").click()
        page.get_by_placeholder("https://trakt.tv/users/username/lists/listname").fill("https://app.trakt.tv/users/giladg/lists/latest-releases?mode=movie")

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = "Backdrop_New_Movies.png"
        save_locally(png_bytes, LOCAL_OUTPUT) 
        upload_to_github(png_bytes, LOCAL_OUTPUT)

    ## Generate 'Trending' backdrop.
        print("   A. Generating backdrop for 'Trending'")
        page.get_by_role("button", name="TMDB Filter").click()

        # Find any <option> element with text "Trending This Week"
        option = page.locator("option", has_text="Trending This Week")
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label="Trending This Week")

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = "Backdrop_Trending.png"
        save_locally(png_bytes, LOCAL_OUTPUT) 
        upload_to_github(png_bytes, LOCAL_OUTPUT)

    ## Generate 'Recommended' backdrop.
        print("   A. Generating backdrop for 'Recommended'")

        # Find any <option> element with text "Popular"
        option = page.locator("option", has_text="Popular")
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label="Popular")

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = "Backdrop_Recommended.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'Top Rated' backdrop.
        print("   A. Generating backdrop for 'Top Rated'")

        # Find any <option> element with text "Top Rated"
        option = page.locator("option", has_text="Top Rated")
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label="Top Rated")

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = "Backdrop_Top_Rated.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'Action' backdrop.
        GENRE = "Action"
        print(f"   A. Generating backdrop for '{GENRE}'")

        #Set 'Source' to "Popular" as it will be used for all Genres going forward.
        option = page.locator("option", has_text="Popular")
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label="Popular")

        # Find any <option> element with text "Action"
        option = page.locator("option", has_text=GENRE)
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label=GENRE)

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = f"Backdrop_{GENRE}.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'Comedy' backdrop.
        GENRE = "Comedy"
        print(f"   A. Generating backdrop for '{GENRE}'")

        # Find any <option> element with text "Comedy"
        option = page.locator("option", has_text=GENRE)
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label=GENRE)

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = f"Backdrop_{GENRE}.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'Crime' backdrop.
        GENRE = "Crime"
        print(f"   A. Generating backdrop for '{GENRE}'")

        # Find any <option> element with text "Crime"
        option = page.locator("option", has_text=GENRE)
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label=GENRE)

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = f"Backdrop_{GENRE}.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'Drama' backdrop.
        GENRE = "Drama"
        print(f"   A. Generating backdrop for '{GENRE}'")

        # Find any <option> element with text "Drama"
        option = page.locator("option", has_text=GENRE)
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label=GENRE)

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = f"Backdrop_{GENRE}.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'Drama' backdrop.
        GENRE = "Drama"
        print(f"   A. Generating backdrop for '{GENRE}'")

        # Find any <option> element with text "Drama"
        option = page.locator("option", has_text=GENRE)
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label=GENRE)

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = f"Backdrop_{GENRE}.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'Kids & Family' backdrop.
        GENRE = "Animation"
        print(f"   A. Generating backdrop for '{GENRE}'")

        # Find any <option> element with text "Drama"
        option = page.locator("option", has_text=GENRE)
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label=GENRE)

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = "Backdrop_Kids_&_Family.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'Drama' backdrop.
        GENRE = "Drama"
        print(f"   A. Generating backdrop for '{GENRE}'")

        # Find any <option> element with text "Drama"
        option = page.locator("option", has_text=GENRE)
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label=GENRE)

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = f"Backdrop - {GENRE}.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'History' backdrop.
        GENRE = "Documentary"
        print(f"   A. Generating backdrop for '{GENRE}'")

        # Find any <option> element with text "Documentary"
        option = page.locator("option", has_text=GENRE)
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label=GENRE)

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = f"Backdrop - History.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'Mystery' backdrop.
        GENRE = "Mystery"
        print(f"   A. Generating backdrop for '{GENRE}'")

        # Find any <option> element with text "Mystery"
        option = page.locator("option", has_text=GENRE)
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label=GENRE)

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = f"Backdrop - {GENRE}.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'Romance' backdrop.
        GENRE = "Romance"
        print(f"   A. Generating backdrop for '{GENRE}'")

        # Find any <option> element with text "Romance"
        option = page.locator("option", has_text=GENRE)
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label=GENRE)

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = f"Backdrop - {GENRE}.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'Romance' backdrop.
        GENRE = "Romance"
        print(f"   A. Generating backdrop for '{GENRE}'")

        # Find any <option> element with text "Romance"
        option = page.locator("option", has_text=GENRE)
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label=GENRE)

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = f"Backdrop - {GENRE}.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'Thriller' backdrop.
        GENRE = "Thriller"
        print(f"   A. Generating backdrop for '{GENRE}'")

        # Find any <option> element with text "Thriller"
        option = page.locator("option", has_text=GENRE)
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label=GENRE)

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = f"Backdrop - {GENRE}.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'Science Fiction' backdrop.
        GENRE = "Science Fiction"
        print(f"   A. Generating backdrop for '{GENRE}'")

        # Find any <option> element with text "Science Fiction"
        option = page.locator("option", has_text=GENRE)
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label=GENRE)

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = f"Backdrop - {GENRE}.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

    ## Generate 'War Stories' backdrop.
        GENRE = "War"
        print(f"   A. Generating backdrop for '{GENRE}'")

        # Find any <option> element with text "War"
        option = page.locator("option", has_text=GENRE)
    
        # Get the parent <select> and select it
        parent_select = page.locator("select").filter(has=option)
        parent_select.select_option(label=GENRE)

        page.get_by_role("button", name="Generate Backdrop").click()
        page.get_by_role("button", name="Download PNG").click(trial=True)

        # Locate image data from the canvas element
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        extract_canvas_image(canvas_data)
        LOCAL_OUTPUT = f"Backdrop - War Stories.png"
        save_locally(png_bytes, LOCAL_OUTPUT)
        upload_to_github(png_bytes, LOCAL_OUTPUT) 

# Extracts the canvas image data from the page and decodes it into bytes
def extract_canvas_image(canvas_data: str):
    global png_bytes

    if canvas_data and canvas_data.startswith("data:image"):
        header, encoded = canvas_data.split(",", 1)
        png_bytes = base64.b64decode(encoded)
        print(f"      a. Extracted canvas image ({len(png_bytes):,} bytes)")
        return png_bytes

# Saves image locally to the specified path
def save_locally(png_bytes: bytes, path: str = LOCAL_OUTPUT) -> None:
    global LOCAL_OUTPUT
    
    with open(path, "wb") as f:
        f.write(png_bytes)
    print(f"      b. Saved image locally: {path} ({len(png_bytes):,} bytes)")

#Uploads the image to GitHub using the GitHub API
def upload_to_github(png_bytes: bytes, path: str = LOCAL_OUTPUT) -> None:
    GITHUB_FILE = "Backdrops/" + LOCAL_OUTPUT
    
    print(f"      c. Uploading to GitHub: {GITHUB_REPO}/{GITHUB_FILE}")

    api_base = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"
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
    print(f"         1. Checking existing file at {GITHUB_REPO}/{GITHUB_FILE}")
    resp = requests.get(api_base, headers=headers, params={"ref": GITHUB_BRANCH})
    if resp.status_code == 200:
        sha = resp.json().get("sha")
        print(f"         2. File exists (sha: {sha[:8]}…) – will update")
    elif resp.status_code == 404:
        print("         2. File does not exist yet – will create")
    else:
        print(f"  ⚠  Unexpected status {resp.status_code} checking file existence.")

    payload: dict = {
        "message": commit_message,
        "content": encoded_content,
        "branch":  GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    print(f"         3. Pushing to GitHub ({GITHUB_REPO}/{GITHUB_FILE}) … ", end="")
    put_resp = requests.put(api_base, headers=headers, data=json.dumps(payload))

    if put_resp.status_code in (200, 201):
        action = "Updated" if sha else "Created"
        commit_url = put_resp.json().get("commit", {}).get("html_url", "")
        print(f"{action} successfully")
        if commit_url:
            print(f"         4. Commit: {commit_url}")
    else:
        print(f"  ✗ GitHub API error {put_resp.status_code}: {put_resp.text}")
        sys.exit(1)

def main():
    print("=" * 60)
    print("  Nuvio Backdrop Generator - Weekly Automation")
    print("=" * 60, "\n")

    generate_backdrops()

    print("3. Done Successfully!")


if __name__ == "__main__":
    main()
