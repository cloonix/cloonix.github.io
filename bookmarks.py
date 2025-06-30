import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Change directory to the script's folder
script_folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_folder)

# Load environment variables from .env file
load_dotenv()
api_key = os.environ.get('LINKDING_API_KEY')
endpoint = os.environ.get('LINKDING_API_ENDPOINT')

# Check if the required environment variables are set
if not api_key or not endpoint:
    print("Please set the LINKDING_API_KEY and LINKDING_API_ENDPOINT environment variables")
    exit(1)

# Get bookmarks from the Linkding API
url = f"{endpoint}/bookmarks/?limit=50&ordering=-date_added"
headers = {"Authorization": f"Token {api_key}"}
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Failed to retrieve bookmarks from the Linkding API")
    exit(1)

bookmarks = response.json().get("results", [])
for bookmark in bookmarks:
    tags = [tag['name'] for tag in bookmark.get("tag_names", [])] if isinstance(bookmark.get("tag_names"), list) else bookmark.get("tag_names", [])
    # Only process bookmarks with BOTH "public" and "blog" tags
    if not (("public" in tags) and ("blog" in tags)):
        continue

    link = bookmark.get("url")
    excerpt = bookmark.get("description", "")
    note = bookmark.get("notes", "")
    title = bookmark.get("title", "")
    date_added = bookmark.get("date_added")
    creation_date = datetime.fromisoformat(date_added.rstrip('Z'))

    # Generate the markdown file path
    file_name = f"content/bookmarks/bookmark-{creation_date.strftime('%Y%m%d')}.md"

    # Generate the markdown content
    markdown_content = f"""+++
title = "{title}"
date = "{creation_date}"
categories = [ 'bookmarks' ]
tags = {tags}
type = "bookmark"
+++

{note}  

<{link}>  

{excerpt}  
"""

    # Write the markdown content to the file
    with open(file_name, "w") as file:
        file.write(markdown_content)

print("Bookmark generation completed.")
