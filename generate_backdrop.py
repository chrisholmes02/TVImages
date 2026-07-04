#!/usr/bin/env python3
"""
Weekly Backdrop Generator Automation Script
v1.0
By Chris Holmes
7/4/2026
"""

import os
import sys
import base64
import datetime
import json
import requests

from copy import deepcopy
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# Environment variables
# GitHub
GITHUB_TOKEN    = os.environ["GITHUB_TOKEN"]
GITHUB_BRANCH   = os.environ.get("GITHUB_BRANCH", "main")
GITHUB_FILE     = "Backdrops/"

#Website
GENERATOR_URL   = "https://paytonjewell.github.io/Nuvio-Backdrop-Generator/"
TMDB_KEY        = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlY2RkZjFjNzk4ZGUzYTRjNzk1NGViOTRkM2FkODY3ZCIsIm5iZiI6MTc3MDc3MTQwNi4wMDE5OTk5LCJzdWIiOiI2OThiZDNjZDJhMWM2MTI2ZTc4ODVjODgiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.EnCCVp3ieKgmi5hFEavsPkDBfA2_e7gI2iAuLSJYYG0"
MDBLIST_KEY     = "yiuz1vhq6o16wxv4o2y7km8xw"
TRAKT_KEY       = "9ff48c3135acd6cc174fc136eb6389d1d51a86bf861862c75ea8a753cf23309d"

#Nuvio
BASE_URL        = "https://api.nuvio.tv"
AUTH_URL        = f"{BASE_URL}/auth/v1"
REST_URL        = f"{BASE_URL}/rest/v1"
PUBLISHABLE_KEY = "sb_publishable_1Clq8rlTVACkdcZuqr6_AD__xUUC_EN"
NUVIO_EMAIL     = "chris.holmes02@gmail.com"
NUVIO_PASSWORD  = "08161983zZ!"
PROFILE_ID      = ""
FOLDER_NAME     = ""
BACKDROP_URL    = ""


# Main function to generate backdrops using the Nuvio Backdrop Generator
def generate_backdrops():

    # Sign into Nuvio API and get access token
    print(f"1. Logging into Nuvio with {NUVIO_EMAIL} ... ", end="")
    client = NuvioClient(NUVIO_EMAIL, NUVIO_PASSWORD)
    print("login successfully")

    # Open a Playwright browser and navigate to the generator URL    
    with sync_playwright() as p:
        print("2. Opening Chromium browser in headless session")
        
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print(f"3. Navigating to {GENERATOR_URL}")
        page.goto(GENERATOR_URL, wait_until="networkidle", timeout=60_000)

        print("4. Setting API keys and selecting posters")
        # Fill in API keys
        page.locator("#tmdbKey").fill(TMDB_KEY)
        page.locator("#traktKey").fill(TRAKT_KEY)
        page.locator("#mdblistKey").fill(MDBLIST_KEY)

        """ Login to Nuvio NOTE functionality broken on website. 
        Using Nuvio API to push backdrop directly into Nuvio.
        page.get_by_role("button", name="Settings").click()
        page.get_by_role("button", name="Sign in with Nuvio").click()
        page.get_by_placeholder("you@example.com").fill("chrisholmes02@gmail.com")
        page.get_by_placeholder("••••••••").fill("08161983zZ!")
        page.get_by_role("button", name="Sign In").click()
        time.sleep(0.5)  # Wait for the login to complete
        """
        # Select 'Posters'. This setting never changes
        page.get_by_text("Posters").click()
        
    ## Generate 'New Movies' backdrop
        collection = "New Movies"
        print(f"↳  A. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Trakt").click()

        page.get_by_role("button", name="Popular on Trakt", exact=True).click()
        page.get_by_text("URL", exact=True).click()
        page.get_by_placeholder("https://trakt.tv/users/username/lists/listname").fill("https://app.trakt.tv/users/giladg/lists/latest-releases?mode=movie")
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)
        
    ## Generate 'Trending' backdrop
        collection = "Trending"
        print(f"   B. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="TMDB").click()
        
        # Set language to English. This setting never changes
        page.get_by_role("button", name="Any Language", exact=True).click()
        page.get_by_text("English", exact=True).click()

        # Set content type to Movies & Shows. This setting stays until Genres
        page.get_by_role("button", name="Movies", exact=True).click()
        page.get_by_text("Movies & Shows", exact=True).click()
        
        page.get_by_role("button", name="Popular", exact=True).click()
        page.get_by_text("Trending This Week", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generate 'Recommended' backdrop
        collection = "Recommended"
        print(f"   C. Generating backdrop for '{collection}'")
        
        page.get_by_role("button", name="Trending This Week", exact=True).click()
        page.get_by_text("Popular", exact=True).click() 
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)


    ## Generating 'Top Rated' backdrop
        collection = "Top Rated"
        print(f"   D. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Popular", exact=True).click()
        page.get_by_text("Top Rated", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Netflix' backdrop
        collection = "Netflix"
        print(f"   E. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Top Rated", exact=True).click()
        page.get_by_text("Popular", exact=True).click()
        page.get_by_role("button", name="Any", exact=True).click()
        page.get_by_text("Netflix", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Prime Video' backdrop
        collection = "Prime Video"
        print(f"   F. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Netflix", exact=True).click()
        page.get_by_text("Amazon Prime", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'HBO Max' backdrop
        collection = "HBO Max"
        print(f"   G. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Amazon Prime", exact=True).click()
        page.get_by_text("HBO Max", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Disney+' backdrop
        collection = "Disney+"
        print(f"   H. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="HBO Max", exact=True).click()
        page.get_by_text("Disney+", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating Apple TV' backdrop
        collection = "Apple TV"
        print(f"   I. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Disney+", exact=True).click()
        page.get_by_text("Apple TV", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Hulu' backdrop
        collection = "Hulu"
        print(f"   J. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Apple TV", exact=True).click()
        page.get_by_text("Hulu", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Paramount+' backdrop
        collection = "Paramount+"
        print(f"   K. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Hulu", exact=True).click()
        page.get_by_text("Paramount+", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Starz' backdrop
        collection = "Starz"
        print(f"   L. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Paramount+", exact=True).click()
        page.get_by_text("Starz", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Action' backdrop
        collection = "Action"
        print(f"   M. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="MDBList").click()
        page.get_by_role("button", name="URL", exact=True).click()
        page.get_by_text("Top lists", exact=True).click()
        page.get_by_role("button", name="— choose a list —", exact=True).click()
        page.get_by_text("Action (400) · garycrawfordgc", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Comedy' backdrop
        collection = "Comedy"
        print(f"   N. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Action (400) · garycrawfordgc", exact=True).click()
        page.get_by_text("Comedy (400) · garycrawfordgc", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Crime' backdrop
        collection = "Crime"
        print(f"   O. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Comedy (400) · garycrawfordgc", exact=True).click()
        page.get_by_text("Crime (400) · garycrawfordgc", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Drama' backdrop
        collection = "Drama"
        print(f"   P. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Crime (400) · garycrawfordgc", exact=True).click()
        page.get_by_text("Drama (400) · garycrawfordgc", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path =capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Thriller' backdrop
        collection = "Thriller"
        print(f"   Q. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Drama (400) · garycrawfordgc", exact=True).click()
        page.get_by_text("Thriller (400) · garycrawfordgc", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Sci-Fi' backdrop
        collection = "Sci-Fi"
        print(f"   R. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Thriller (400) · garycrawfordgc", exact=True).click()
        page.get_by_text("Sci-Fi (280) · garycrawfordgc", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'War Stories' backdrop
        collection = "War Stories"
        print(f"   S. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Sci-Fi (280) · garycrawfordgc", exact=True).click()
        page.get_by_text("War (195) · garycrawfordgc", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Romance' backdrop
        collection = "Romance"
        print(f"   T. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="TMDB").click()
        page.get_by_role("button", name="Movies & Shows", exact=True).click()
        page.get_by_text("Movies", exact=True).click()
        page.get_by_role("button", name="Starz", exact=True).click()
        page.get_by_text("Any", exact=True).click()
        page.get_by_role("button", name="Any Genre", exact=True).click()
        page.get_by_text("Romance", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Kids & Family' backdrop
        collection = "Kids & Family"
        print(f"   U. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Romance", exact=True).click()
        page.get_by_text("Family", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

    ## Generating 'Mystery' backdrop
        collection = "Mystery"
        print(f"   V. Generating backdrop for '{collection}'")
        page.get_by_role("button", name="Family", exact=True).click()
        page.get_by_text("Mystery", exact=True).click()
        #generate_backdrop_add_to_Nuvio(page, collection)
        path = capture_canvas_and_upload(page, collection)
        publish_collection(client, 1, collection, path); publish_collection(client, 2, collection, path)

### Generates backdrop and saves to collections with inernal Nuvio API. NOTE Possibly broken due to website changes.
def generate_backdrop_add_to_Nuvio(page, collection):
    page.get_by_role("button", name="Generate Backdrop").click()
    page.get_by_role("button", name="Save to Collection").click()
    page.get_by_role("button", name="Chris").click()
    page.get_by_alt_text(collection).click()
    page.get_by_role("button", name="Save to Nuvio").click()
    page.get_by_role("button", name="Save to Nuvio").click(trial=True) #Wait for button to be enabled again, this means process finished
    page.get_by_role("button", name="Close").click() #Close the success message
    print("saved to Nuvio")

# Capture the canvas image data, save it locally, remove last weeks versions and upload it to GitHub
def capture_canvas_and_upload(page, path):
    # Set the filename with today's date
    path_collection = "Backdrop - " + path
    path = f"Backdrop - {path} " + datetime.date.today().strftime("%Y-%m-%d") + ".png"
    
    page.get_by_role("button", name="Generate Backdrop").click()
    page.get_by_role("button", name="Download").click(trial=True) #Wait for button to be enabled again, this means process finished
    
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

    #api_base = f"https://api.github.com/repos/chrisholmes02/TVImages/contents/{GITHUB_FILE}"
    api_base = "https://api.github.com/repos/chrisholmes02/TVImages" #contents/{GITHUB_FILE}"
    headers  = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept":        "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Checking for existing files in the repository that match the collection name (case-insensitive) and deleting them
    print(f"         1. Checking existing backdrop file with name containing '{path_collection}'", end="")
    resp = requests.get(f"{api_base}/git/trees/{GITHUB_BRANCH}?recursive=1", headers=headers, params={"ref": GITHUB_BRANCH})
    resp.raise_for_status()
    tree = resp.json().get("tree", [])
    files_list = [item["path"] for item in tree if item["type"] == "blob"]
    matches = [f for f in files_list if path_collection.lower() in f.lower()]

    sha = None
    if not matches:
        print(" ... no matching files found")
    elif len(matches) > 0: # Found file, now deleting it
        print(f"\n            - found {len(matches)} matching file(s): {matches} and deleting")

        resp = requests.get(api_base + f"/contents/{matches[0]}", headers=headers, params={"ref": GITHUB_BRANCH})
        sha = resp.json()["sha"]
        payload = {"message": f"Delete {matches[0]}", "sha": sha, "branch": GITHUB_BRANCH}
        resp = requests.delete(f"{api_base}/contents/{matches[0]}", headers=headers, json=payload, params={"ref": GITHUB_BRANCH})

    # Create a commit message with the current date and prepare the payload for the GitHub API request
    date_str = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
    commit_message = f"chore: weekly backdrop update ({date_str})"
    encoded_content = base64.b64encode(png_bytes).decode()

    """ # Check if the file already exists (we need its SHA to update it)
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
        sys.exit(1)"""

    payload: dict = {
        "message": commit_message,
        "content": encoded_content,
        "branch":  GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    print(f"         2. Pushing to GitHub (chrisholmes02/TVImages/{GITHUB_FILE}) … ", end="")
    put_resp = requests.put(api_base + f"/contents/{GITHUB_FILE}", headers=headers, data=json.dumps(payload))

    if put_resp.status_code in (200, 201):
        commit_url = put_resp.json().get("commit", {}).get("html_url", "")
        print(f"created successfully")
        if commit_url:
            print(f"         3. Commit: {commit_url}")
    else:
        print(f"✗ GitHub API error {put_resp.status_code}: {put_resp.text}")
        sys.exit(1)

    return path

#Publish the GitHub backdrop URL path to Nuvio
def publish_collection(client, PROFILE_ID, FOLDER_NAME, BACKDROP_URL):
    print(f"      d. Publishing backdrop to Nuvio, on Profile {PROFILE_ID} ... ", end="")
    BACKDROP_URL = f"https://raw.githubusercontent.com/chrisholmes02/TVImages/main/Backdrops/{BACKDROP_URL}"
    
    current = client.pull_collections(PROFILE_ID)
    proposed = deepcopy(current)

    try:
        set_folder_backdrop(proposed, FOLDER_NAME, BACKDROP_URL)
    except ValueError as exc:
        sys.exit(str(exc))

    client.push_collections(PROFILE_ID, proposed)
    print("completed successfully")

# Nuvio client functions
class NuvioClient:
    def __init__(self, email: str, password: str):
        self.session = requests.Session()
        self.session.headers.update({"apikey": PUBLISHABLE_KEY})
        self.access_token = None
        self._sign_in(email, password)

    def _sign_in(self, email: str, password: str):
        resp = self.session.post(
            f"{AUTH_URL}/token",
            params={"grant_type": "password"},
            json={"email": email, "password": password},
        )
        resp.raise_for_status()
        data = resp.json()
        self.access_token = data["access_token"]
        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})

    def _rpc(self, function_name: str, payload=None):
        resp = self.session.post(f"{REST_URL}/rpc/{function_name}", json=payload or {})
        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except ValueError:
                detail = resp.text
            raise RuntimeError(f"{function_name} failed ({resp.status_code}): {detail}")
        if resp.status_code == 204 or not resp.content:
            return None
        return resp.json()

    def pull_collections(self, profile_id: int) -> list:
        """Returns the raw collections_json array for a profile (empty list if none)."""
        result = self._rpc("sync_pull_collections", {"p_profile_id": profile_id})
        if not result:
            return []
        # sync_pull_collections returns a list with one row (or empty)
        return result[0]["collections_json"] if result else []

    def push_collections(self, profile_id: int, collections: list):
        """Full replace of the collections array for a profile."""
        self._rpc(
            "sync_push_collections",
            {"p_profile_id": profile_id, "p_collections_json": collections},
        )

def find_folders_by_name(collections: list, folder_name: str) -> list:
    """Returns a list of (collection, folder) tuples for every folder
    whose title exactly matches folder_name, across all collections."""
    matches = []
    for c in collections:
        for f in c.get("folders", []):
            if f.get("title") == folder_name:
                matches.append((c, f))
    return matches

def set_folder_backdrop(collections: list, folder_name: str, url: str) -> None:
    """Sets (or clears, if url == 'clear') the heroBackdropUrl for the
    folder whose title matches folder_name, in-place. Raises ValueError
    if there isn't exactly one match."""
    matches = find_folders_by_name(collections, folder_name)
    if not matches:
        raise ValueError(f"No folder titled {folder_name!r} was found.")
    if len(matches) > 1:
        locations = ", ".join(
            f"collection {c.get('id')!r}" for c, _ in matches
        )
        raise ValueError(
            f"Folder title {folder_name!r} is ambiguous -- found in: {locations}. "
            "Rename one of them or match by collection instead."
        )
    _, folder = matches[0]
    if url.strip().lower() == "clear":
        folder["heroBackdropUrl"] = None
    else:
        folder["heroBackdropUrl"] = url

def main():
    print("=" * 60)
    print("  Nuvio Backdrop Image Generator - Weekly Automation")
    print("=" * 60, "\n")
    
    generate_backdrops()

    print("3. Done Successfully!")


if __name__ == "__main__":
    main()
