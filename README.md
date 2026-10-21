# Nuvio Library

**Your picks. Your home screen.**

A self-hosted add-on for Nuvio that republishes your own Nuvio Library as a catalog on your home screen or in a collection folder. You choose the row layout, sort order, card shape and artwork from a web editor, with optional TMDB artwork and a local image cache.

---

## 🚀 Features

- **Your Library as a Catalog**: reads a Nuvio profile's Library and serves it as a Movies row and a Series row, or as one combined row.
- **Any Number of Profiles**: each add-on profile has its own settings, add-on link and cache, and points at one Nuvio profile (1 to 6). Several can point at the same one.
- **Web Editor**: a password-protected page where you set everything up and install the add-on into Nuvio with one button.
- **Layout and Sorting**: row names, sort order (added, released, name or random), card shape, titles per page, and whether the row shows on the home screen.
- **TMDB Artwork (Optional)**: posters and landscape images in your language, resized to save bandwidth.
- **Image Cache (Optional)**: serve artwork from your own server, and cut landscape images from posters for titles that have none.
- **Background Refresh**: the catalog is rebuilt on a schedule, and the last good catalog keeps being served if Nuvio can't be reached.

---

## 🧩 What You Need

- **Docker**: [Docker Desktop](https://docs.docker.com/get-docker/) on Windows or macOS, Docker Engine on Linux.
- **A Nuvio Account**: the email and password you use in Nuvio, so the add-on can read your Library.
- **Nuvio's Public API Key**: the same value your Nuvio app uses. It is not included in this project.
- **A TMDB API Key (Optional)**: only needed for TMDB artwork and landscape crops.

---

## 🛠️ Installation

### Option 1: Docker Compose (Recommended)

1. Create a folder for it, for example `nuvio_library`.
2. In that folder, create a file named `docker-compose.yml` with this content, and change the three marked values:

   ```yaml
   services:
     nuvio_library:
       image: ghcr.io/chrisholmes02/nuvio_library:latest
       container_name: nuvio_library
       restart: unless-stopped
       ports:
         - "7000:7000"
       environment:
         ADMIN_PASSWORD: "change-me"                # 1. the password for the editor
         NUVIO_API_KEY: "paste-nuvio-public-key"    # 2. Nuvio's public API key
         HOST_NAME: "http://192.168.1.50:7000"      # 3. the address your Nuvio apps use to reach this machine
       volumes:
         - nuvio_library_data:/data

   volumes:
     nuvio_library_data:
   ```

   `HOST_NAME` must be an address your phone or TV can reach, so not `localhost`. On a home network that is the machine's LAN address plus the port (on Windows, run `ipconfig` and use the IPv4 address). Behind a reverse proxy, use your public `https://` address.
3. In that folder, run:

   ```bash
   docker compose up -d
   ```

4. Open `http://localhost:7000/configure` and sign in with your `ADMIN_PASSWORD`.

To update later: `docker compose pull`, then `docker compose up -d`. To stay on one version, use `:1.0.0` instead of `:latest` in the image line.

### Option 2: Docker Run

```bash
docker run -d --name nuvio_library --restart unless-stopped -p 7000:7000 \
  -e ADMIN_PASSWORD="change-me" \
  -e NUVIO_API_KEY="paste-nuvio-public-key" \
  -e HOST_NAME="http://192.168.1.50:7000" \
  -v nuvio_library_data:/data \
  ghcr.io/chrisholmes02/nuvio_library:latest
```

On Windows PowerShell, end each line with a backtick (`` ` ``) instead of `\`.

### Option 3: Build from Source

Download this repository (**Code**, then **Download ZIP**), unzip it, and copy `docker-compose.example.yml` to `docker-compose.yml`. Replace its `image:` line with `build: .`, set the three values, then run `docker compose up -d --build` in that folder.

### First-Time Setup

1. **Account tab:** enter your Nuvio email and password and select **Validate Login**. The first successful check also saves the login, which unlocks the **+** tab. A TMDB API key is optional: enter it, select **Validate Key**, then **Save Changes**.
2. **+ tab:** adds an add-on profile. Choose which **Nuvio Profile** it shows, adjust the settings, and select **Save Changes**.
3. Select **Refresh Catalog** to build it right away.
4. Select **Install to Nuvio** to add it for you, or copy the **Install URL** into Nuvio under Settings, Add-ons. Your existing add-ons are kept.

Nothing saves automatically. Save the Account tab first, then the profile, then use Refresh Catalog or Install to Nuvio. The editor tells you if something is still unsaved.

---

## ⚙️ Configuration

### Environment Variables

| Variable         | Default                | Required | Meaning |
|------------------|------------------------|----------|---------|
| `ADMIN_PASSWORD` | none                   | Yes      | Password for the web editor. |
| `NUVIO_API_KEY`  | none                   | Yes      | Nuvio's public API key. It is the same for every Nuvio user and is not included in this project. |
| `HOST_NAME`      | from the request       | Advised  | The public base URL, no trailing slash. It builds the add-on link and cached image links. |
| `PORT`           | `7000`                 | No       | Port the app listens on inside the container. If you change it, change the container side of the port mapping to match. |
| `DATA_DIR`       | `/data`                | No       | Where the database, session key and image caches are stored. Mount it as a volume. |
| `LOG_LEVEL`      | `INFO`                 | No       | `DEBUG`, `INFO`, `WARNING` or `ERROR`. |
| `NUVIO_BASE_URL` | `https://api.nuvio.tv` | No       | Nuvio's backend. Change it only to use a different server. |

### Account Tab

The Nuvio email and password the add-on signs in with, and an optional TMDB API key (a v3 key or a v4 read access token). Without a TMDB key, no TMDB request is ever made.

### Profile Settings

| Setting                            | Default                  | What it does |
|------------------------------------|--------------------------|--------------|
| Profile Name                       | `Profile N`              | Labels the tab and the log lines. |
| Nuvio Profile                      | 1                        | Which Nuvio profile's Library is shown, and where Install to Nuvio adds the add-on. |
| Combine Movies and Series          | Off                      | Off gives a Movies row and a Series row. On gives one row. |
| Catalog Name / Movies / Series     | `Nuvio Library`, `Nuvio Library - Movies`, `Nuvio Library - Series` | The row names on Nuvio's home screen. |
| Show on the Home Screen            | On                       | Off keeps the rows only in Nuvio's catalog list. |
| Sort Order                         | Newest Added First       | Added, released, name or random. Random reshuffles on every refresh. |
| Card Shape                         | Automatic                | Automatic keeps each title's saved shape. Portrait or Landscape forces one. |
| Titles per Page                    | 20                       | How many titles Nuvio loads at a time (1 to 100). |
| Catalog Cache TTL                  | 3600 s                   | How long a built catalog is served before it expires (300 to 604,800). |
| Refresh in Background              | On                       | Rebuilds the catalog on a schedule so Nuvio is always answered from memory. |
| Cache Posters / Landscape Images   | Off                      | Download artwork to this server and serve it from there. **Delete Cache** removes it. |
| Artwork Language                   | `en`                     | Two-letter language code for TMDB artwork with the title printed on it. |
| Artwork Lookup TTL                 | 14 days                  | How often each title is looked up again on TMDB (7 to 365). |
| Smaller Posters / Landscape Images | On                       | Request TMDB images at 500 px and 780 px wide instead of the original size. |
| Crop Landscape Images from Posters | Off                      | For titles with no landscape art, cut one from the poster. Needs Cache Landscape Images and a TMDB key. |

The TMDB settings (language, lookup TTL, smaller images and the crop) are locked until a TMDB key is entered on the Account tab. Every value is checked against these limits when you save.

---

## 🔍 How It Works

- **Building:** a build downloads the Library, drops titles without an ID, sorts them and turns each into a catalog entry. The catalog lives in memory, per profile.
- **Refreshing:** with Refresh in Background on, the catalog is rebuilt when its cache expires. If Nuvio can't be reached, the last catalog keeps being served and the next try comes five minutes later. A Library that suddenly comes back empty does not replace a catalog that has titles.
- **Saving:** saving a profile only saves. The catalog picks up the new settings at its next refresh, or when you select **Refresh Catalog**.
- **Artwork:** with a TMDB key, a background job looks up each title and picks the best poster and landscape image in your language, falling back to the Library's own artwork. Nothing is looked up without a key.
- **Image cache:** downloaded images are stored once per distinct link, kept for 30 days, then checked against their source before being kept again.
- **New profiles** stay idle, fetching nothing from Nuvio, until they are first saved, refreshed or installed.
- **Limits:** Nuvio numbers its profiles 1 to 6. The add-on serves a catalog only, with no streams, metadata or subtitles.

---

## 📜 Logs

Logs go to stdout, so `docker compose logs -f` shows them. Add `-t` for timestamps. A line is `[LEVEL] [tag] message`, and the tag is the profile's name (`[Account]` for account actions):

```
Nuvio Library 1.0.0
• Port 7000 · Account saved · TMDB enabled
• Profile 1 → Nuvio profile 1
[INFO] [Profile 1] [startup] catalog built: 34 item(s) (28 movie, 6 series) from Nuvio profile 1 in 5.64s
[INFO] [Profile 1] [cache-warming] 68/68 image(s) ready in 11.2s: 68 downloaded (5.4 MB), 0 already cached, 0 failed, 0 stale file(s) removed, 0 re-checked
[INFO] [Profile 1] [tmdb-art-refresh] 34/34 title(s) looked up in 3.8s: 6 with new artwork, 0 failed
```

Builds, profile and account changes, installs and every failure are logged. Sign-ins and ordinary catalog requests are not. `WARNING` marks a failure, and `LOG_LEVEL=DEBUG` adds individual image and TMDB lookup failures.

---

## 🔌 Endpoints

Add-on routes (open, so Nuvio can use them):

- `/<id>/manifest.json`: the add-on manifest for one profile.
- `/<id>/catalog/<type>/<catalog id>.json`: a catalog page, with `/skip=N` for paging.
- `/<id>/poster-cache/<kind>/<file>`: a cached poster or landscape image.
- `/<id>/configure`: opens the editor on that profile.

Editor routes (need the editor sign-in):

- `/configure`: the web editor.
- `/api/*`: the editor's API.

---

## 🔒 Security

- The editor signs you out after an hour without activity, and five wrong passwords from one address lock it for a minute. Put it behind HTTPS and a reverse proxy.
- Your Nuvio password and TMDB key are stored in plain text in the database, because the add-on has to sign in for you. Keep the data folder private.
- An add-on link contains the profile's ID, and anyone with it can read that profile's catalog. The add-on routes need no sign-in so that Nuvio can use them.
- **Delete Account** (Danger Zone) deletes everything the add-on stores. Your Nuvio account is not touched, and deleting a profile does not remove the add-on from Nuvio.

---

## 🧑‍💻 Development

```bash
pip install -r requirements.txt      # Flask, requests, gunicorn, Pillow
ADMIN_PASSWORD=... NUVIO_API_KEY=... DATA_DIR=./data \
  gunicorn -w 1 --threads 16 -b 0.0.0.0:7000 'nuvio_library.web:create_app()'
```

- The folder holding the code must be named `nuvio_library`. Keep one worker, since each profile keeps its catalog in memory and refreshes it from a background thread.
- `python -m nuvio_library` runs Flask's built-in server for local development only.
- Pillow is only needed for landscape crops.

---

## 🤝 Contributing

Issues and pull requests are welcome. Please open an issue before large changes.

---

## 📄 License

MIT, see [LICENSE](LICENSE).

---

## 🙏 Credits

- Nuvio
- [TMDB](https://www.themoviedb.org/)
- [Docker](https://www.docker.com/)
- [Flask](https://flask.palletsprojects.com/)

This product uses the TMDB API but is not endorsed or certified by TMDB.

---

## ⚠️ Disclaimer

Nuvio Library is an independent, self-hosted add-on. It is not made by or affiliated with Nuvio, and it signs in to your Nuvio account only to read your own Library. Artwork availability depends on your Library and on TMDB.
