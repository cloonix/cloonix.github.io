import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.environ.get('RAINDROP_API_KEY')
collection_id = os.environ.get('RAINDROP_COLLECTION_ID')
endpoint = os.environ.get('RAINDROP_ENDPOINT')

# Check if the required environment variables are set
if not api_key or not collection_id or not endpoint:
    print("Please set the environment variables")
    exit(1)

# Get the last 5 bookmarks from the API endpoint
url = f"{endpoint}/{collection_id}?perpage=5"
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code != 200:
    print("Failed to retrieve bookmarks from the API")
    exit(1)

# Process the bookmarks
bookmarks = response.json().get("items", [])
for bookmark in bookmarks:
    link = bookmark.get("link")
    excerpt = bookmark.get("excerpt")
    note = bookmark.get("note")
    tags = bookmark.get("tags")
    created_timestamp = int(datetime.fromisoformat(bookmark.get("created")).timestamp())
    creation_date = datetime.fromtimestamp(created_timestamp)

    # Generate the markdown file path
    file_name = f"content/bookmarks/bookmark-{creation_date.strftime('%Y%m%d')}.md"

    # Check if the markdown file already exists
    if os.path.exists(file_name):
        continue

    # Generate the markdown content
    markdown_content = f"""+++
title = "{bookmark.get('title')}"
date = "{creation_date}"
categories = [ 'bookmarks' ]
tags = {tags}
+++

{note}

{link}

{excerpt}
"""

    # Write the markdown content to the file
    with open(file_name, "w") as file:
        file.write(markdown_content)

print("Bookmark generation completed.")