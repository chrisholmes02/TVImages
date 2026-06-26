#!/usr/bin/env python3
"""
Nuvio Backdrop Generator – Weekly automation
Visits https://paytonjewell.github.io/Nuvio-Backdrop-Generator/,
generates a backdrop image, then pushes it to a GitHub repository.

Required env vars:
  GITHUB_TOKEN      – Personal Access Token with repo write access
  GITHUB_REPO       – owner/repo  (e.g. "yourname/my-backdrops")
  GITHUB_BRANCH     – branch to commit to (default: main)
  GITHUB_FILE_PATH  – path inside the repo (default: backdrop/backdrop.png)

Optional env vars:
  BACKDROP_WIDTH    – canvas width  (default: 1920)
  BACKDROP_HEIGHT   – canvas height (default: 1080)
  HEADLESS          – set to "false" to watch the browser (default: true)
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
GITHUB_TOKEN    = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO     = os.environ.get("GITHUB_REPO", "")            # owner/repo
GITHUB_BRANCH   = os.environ.get("GITHUB_BRANCH", "main")
GITHUB_FILE     = os.environ.get("GITHUB_FILE_PATH", "Backdrops/backdrop.png")
WIDTH           = int(os.environ.get("BACKDROP_WIDTH",  "1920"))
HEIGHT          = int(os.environ.get("BACKDROP_HEIGHT", "1080"))
HEADLESS        = os.environ.get("HEADLESS", "true").lower() != "false"

LOCAL_OUTPUT    = "backdrop.png"


# ---------------------------------------------------------------------------
# Step 1 – Generate the backdrop image
# ---------------------------------------------------------------------------
def generate_backdrop() -> bytes:
    """Launch a headless browser, use the generator, and return PNG bytes."""
    print("→ Launching browser …")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
        )
        page = context.new_page()

        print(f"→ Navigating to {GENERATOR_URL} …")
        page.goto(GENERATOR_URL, wait_until="networkidle", timeout=60_000)

        # Give any JS/canvas init a moment to settle
        page.wait_for_timeout(2_000)

        # ----------------------------------------------------------------
        # Try common patterns for "generate" / "randomise" buttons.
        # The exact selector depends on the page's HTML; we try several.
        # ----------------------------------------------------------------
        generate_selectors = [
            "button:has-text('Generate')",
            "button:has-text('Randomize')",
            "button:has-text('Random')",
            "button:has-text('Create')",
            "[id*='generate']",
            "[id*='random']",
            "[class*='generate']",
            "[class*='random']",
        ]

        clicked = False
        for sel in generate_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=1_000):
                    btn.click()
                    print(f"  ✓ Clicked '{sel}'")
                    clicked = True
                    break
            except Exception:
                continue

        if not clicked:
            print("  ⚠  No generate button found – using whatever is rendered.")

        # Wait for canvas rendering
        page.wait_for_timeout(3_000)

        # ----------------------------------------------------------------
        # Try to click a "Download" button first; if it saves to disk we
        # read that file.  Otherwise we extract the canvas directly.
        # ----------------------------------------------------------------
        download_selectors = [
            "button:has-text('Download')",
            "a:has-text('Download')",
            "[id*='download']",
            "[class*='download']",
        ]

        png_bytes: bytes = b""

        # Attempt canvas extraction via JavaScript (most reliable)
        canvas_data: str = page.evaluate("""() => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            return canvas.toDataURL('image/png');
        }""")

        if canvas_data and canvas_data.startswith("data:image"):
            header, encoded = canvas_data.split(",", 1)
            png_bytes = base64.b64decode(encoded)
            print(f"  ✓ Extracted canvas image ({len(png_bytes):,} bytes)")
        else:
            # Fallback: full-page screenshot
            print("  ⚠  Canvas extraction failed – taking full-page screenshot.")
            png_bytes = page.screenshot(full_page=False)

        browser.close()

    if not png_bytes:
        raise RuntimeError("Failed to capture any image from the generator page.")

    return png_bytes


# ---------------------------------------------------------------------------
# Step 2 – Save locally
# ---------------------------------------------------------------------------
def save_locally(png_bytes: bytes, path: str = LOCAL_OUTPUT) -> None:
    with open(path, "wb") as f:
        f.write(png_bytes)
    print(f"→ Saved locally: {path} ({len(png_bytes):,} bytes)")


# ---------------------------------------------------------------------------
# Step 3 – Upload to GitHub
# ---------------------------------------------------------------------------
def upload_to_github(png_bytes: bytes) -> None:
    if not GITHUB_TOKEN:
        print("  ⚠  GITHUB_TOKEN not set – skipping upload.")
        return
    if not GITHUB_REPO:
        print("  ⚠  GITHUB_REPO not set – skipping upload.")
        return

    api_base = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    headers  = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept":        "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    commit_message = f"chore: weekly backdrop update ({date_str})"
    encoded_content = base64.b64encode(png_bytes).decode()

    # Check if the file already exists (we need its SHA to update it)
    sha = None
    print(f"→ Checking existing file at {GITHUB_REPO}/{GITHUB_FILE} …")
    resp = requests.get(api_base, headers=headers, params={"ref": GITHUB_BRANCH})
    if resp.status_code == 200:
        sha = resp.json().get("sha")
        print(f"  ✓ File exists (sha: {sha[:8]}…) – will update.")
    elif resp.status_code == 404:
        print("  ✓ File does not exist yet – will create.")
    else:
        print(f"  ⚠  Unexpected status {resp.status_code} checking file existence.")

    payload: dict = {
        "message": commit_message,
        "content": encoded_content,
        "branch":  GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    print(f"→ Pushing to GitHub ({GITHUB_REPO} / {GITHUB_FILE}) …")
    put_resp = requests.put(api_base, headers=headers, data=json.dumps(payload))

    if put_resp.status_code in (200, 201):
        action = "Updated" if sha else "Created"
        commit_url = put_resp.json().get("commit", {}).get("html_url", "")
        print(f"  ✓ {action} successfully!")
        if commit_url:
            print(f"    Commit: {commit_url}")
    else:
        print(f"  ✗ GitHub API error {put_resp.status_code}: {put_resp.text}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  Nuvio Backdrop Generator – Weekly Automation")
    print("=" * 60)

    png_bytes = generate_backdrop()
    save_locally(png_bytes)
    upload_to_github(png_bytes)

    print("\n✅  Done!")


if __name__ == "__main__":
    main()
