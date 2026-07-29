"""Top-level entry point for the garden analytics dashboard."""

from dashboard.app import app, server


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
