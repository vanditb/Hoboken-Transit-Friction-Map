# Streamlit Community Cloud Notes

The app does not use API keys. To deploy it on Streamlit Community Cloud:

1. Push the reviewed repository to GitHub.
2. Create a new app from the repository.
3. Set the main file to `src/app.py`.
4. Let Streamlit install `requirements.txt`.

The first time someone asks for road-snapped construction lines, OSMnx may need to download the small Hoboken street graph from OpenStreetMap. The app has a straight-line fallback if that request fails, so the rest of the map should still work.

The local GraphML cache is intentionally ignored by Git. A later deployment improvement could pre-generate a reviewed small Hoboken graph, but that should be tested before committing one to the repository.
