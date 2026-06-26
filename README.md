# Nuvio Backdrop Generator – Weekly Automation

Automatically visits [paytonjewell's Nuvio Backdrop Generator](https://paytonjewell.github.io/Nuvio-Backdrop-Generator/), captures a fresh backdrop image, and pushes it to a GitHub repository on a weekly schedule.

---

## Files

| File | Purpose |
|------|---------|
| `generate_backdrop.py` | Main script – drives the browser, captures the image, uploads via GitHub API |
| `.github/workflows/weekly_backdrop.yml` | GitHub Actions workflow (runs every Monday at 08:00 UTC) |

---

## Quick setup

### 1. Add the files to a GitHub repository

Place both files at the root of a repository (the workflow file goes in `.github/workflows/`).

### 2. Create a GitHub Personal Access Token (PAT)

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Create a token with **Contents: Read & Write** permission on the target repository
3. Copy the token value

### 3. Set repository secrets & variables

In the repository that holds the workflow, go to **Settings → Secrets and variables → Actions**:

**Secrets** (sensitive – use "New repository secret"):

| Name | Value |
|------|-------|
| `BACKDROP_GITHUB_TOKEN` | The PAT you created above |
| `BACKDROP_GITHUB_REPO` | `owner/repo` of the repository where the image will be saved (e.g. `yourname/my-backdrops`) |

**Variables** (optional overrides – use "New repository variable"):

| Name | Default | Description |
|------|---------|-------------|
| `BACKDROP_BRANCH` | `main` | Branch to commit to |
| `BACKDROP_FILE_PATH` | `backdrop/backdrop.png` | Path inside the repo |
| `BACKDROP_WIDTH` | `1920` | Canvas / viewport width |
| `BACKDROP_HEIGHT` | `1080` | Canvas / viewport height |

### 4. Trigger manually (optional)

Go to **Actions → Weekly Backdrop Generator → Run workflow** to test immediately without waiting for Monday.

---

## Run locally

```bash
# Install dependencies
pip install playwright requests
playwright install chromium

# Set environment variables
export GITHUB_TOKEN="ghp_..."
export GITHUB_REPO="yourname/my-backdrops"
export GITHUB_BRANCH="main"
export GITHUB_FILE_PATH="backdrop/backdrop.png"

# Run
python generate_backdrop.py
```

Set `HEADLESS=false` to watch the browser open (useful for debugging).

---

## How it works

1. **Playwright** launches a headless Chromium browser and navigates to the generator page.
2. It looks for a **Generate / Randomize** button and clicks it to produce a fresh backdrop.
3. The resulting `<canvas>` element is read via JavaScript's `toDataURL()` to extract a PNG.
4. The PNG is saved locally (`backdrop.png`) and then **pushed to your GitHub repo** via the GitHub Contents API.
5. If the file already exists in the repo it is **updated** (no duplicate commits); if it doesn't exist it is **created**.
6. The workflow also saves the image as a **GitHub Actions artifact** for quick inspection.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "No generate button found" | The page may have updated its HTML. Open the generator in a browser, inspect the button, and add its selector to `generate_selectors` in `generate_backdrop.py`. |
| Canvas extraction returns `null` | Some generators disable `toDataURL` for CORS reasons. The script falls back to a full-page screenshot automatically. |
| `403` from GitHub API | Check your PAT scope and that `BACKDROP_GITHUB_REPO` matches the repo the token has access to. |
| Blank or very small image | Increase `BACKDROP_WIDTH`/`BACKDROP_HEIGHT` or add a longer `page.wait_for_timeout()` after clicking Generate. |
