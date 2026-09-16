# Lost & Found app

This imported project is a Flask web app that stores data in a local SQLite database and uploaded images under `static/uploads`.

## Run

The **Start application** workflow runs:

```sh
uv run python app.py
```

The server listens on `0.0.0.0:5000` for Replit's web preview. Flask sessions use the Replit `SESSION_SECRET` secret when available.