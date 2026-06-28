import os
import base64
import json
import urllib.request
import urllib.error

# --- Configuration (set these as GitHub Actions secrets/env vars) ---
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO_OWNER = os.environ["REPO_OWNER"]       # e.g. "octocat"
REPO_NAME = os.environ["REPO_NAME"]         # e.g. "my-repo"
FILE_PATH = os.environ.get("FILE_PATH", "hello.txt")          # path inside repo
COMMIT_MESSAGE = os.environ.get("COMMIT_MESSAGE", "Update file via GitHub Actions")
FILE_CONTENT = os.environ.get("FILE_CONTENT", "Hello from GitHub Actions!")
BRANCH = os.environ.get("BRANCH", "main")

API_BASE = "https://api.github.com"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Content-Type": "application/json",
}


def api_request(method: str, url: str, body: dict | None = None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise RuntimeError(f"GitHub API error {e.code}: {error_body}") from e


def get_file_sha(path: str) -> str | None:
    """Return the blob SHA of an existing file, or None if it doesn't exist."""
    url = f"{API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}?ref={BRANCH}"
    try:
        data, _ = api_request("GET", url)
        return data["sha"]
    except RuntimeError as e:
        if "404" in str(e):
            return None
        raise


def create_or_update_file(path: str, content: str, message: str, sha: str | None):
    url = f"{API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    encoded = base64.b64encode(content.encode()).decode()
    body = {
        "message": message,
        "content": encoded,
        "branch": BRANCH,
    }
    if sha:
        body["sha"] = sha  # required when updating an existing file

    data, status = api_request("PUT", url, body)
    action = "Updated" if sha else "Created"
    print(f"✅ {action} '{path}' — commit: {data['commit']['sha']}")


if __name__ == "__main__":
    print(f"📂 Targeting {REPO_OWNER}/{REPO_NAME} on branch '{BRANCH}'")
    sha = get_file_sha(FILE_PATH)
    if sha:
        print(f"📝 File exists (SHA: {sha}), updating...")
    else:
        print("🆕 File does not exist, creating...")
    create_or_update_file(FILE_PATH, FILE_CONTENT, COMMIT_MESSAGE, sha)
