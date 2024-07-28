+++
title = 'Writing a Hugo Raindrop.io bookmark integration with AI'
date = 2024-07-27T17:11:47Z
draft = true
tags = [ 'python', 'bookmarks', 'howto', 'blog', 'personal' ]
categories = [ 'howto' ]
toc = 1
[params]
  author = 'Claus Malter'
+++

[bacardi55](https://bacardi55.io/2024/02/13/bookmarks-section-the-pesos-way-kind-of/) has an interesting bookmarks section on his blog, where a script generates Hugo markdown pages for bookmarks he has added to a central (self-hosted) bookmark manager. I found this very interesting and wanted to build something similar. I've been using raindrop.io for some time now, and this service also provides an API. So this could be an easy project to do with the help of Github Copilot, which I have recently been using to give my software development projects a boost.  

So here are my goals:

1. Generate Hugo Markdown content using the Raindrop.io API (link and note)
2. Use only bookmarks from a specific publicly shared collection
3. A new section on my blog, only for bookmarks
4. Execution of the script on demand
5. Use python
6. Use Github Copilot for creating the python script
7. (future goal) Integrate the script into github's deployment action

There was one step in the workflow that I was not sure how to do: I don't want to manually deploy my pages every time I bookmark a page. Ideally, saving a bookmark would execute a web-hook, but Raindrop.io does not support this. So the alternative is to run a script on my server that fetches new bookmarks, generates the markdown files and pushes them to Github pages. But for now I will do it the manual way and decide later how4 improve it.  

## The AI guided script generation

I used the following prompt to generate the Python script with GitHub Copilot. I just selected the following snippet of text and used the Visual Code Copilot plugin: "Write the Python script based on my comments in file":  

```txt
# import API token, API endpoint and collection ID from .env file
# RAINDROP_API_KEY=
# RAINDROP_COLLECTION_ID=46414428
# RAINDROP_ENDPOINT=https://api.raindrop.io/rest/v1/raindrops/

# get the last 5 bookmarks from the API endpoint
# use only links with a note

# generate markdown files with the following content
# +++
# title = <title>
# date = <bookmark creation date>
# categories: [ 'bookmarks' ]
# +++
# 
# <note>
# 
# <link>
# <excerpt>

# generated files stay in subfolder content/bookmarks
# don't process links you already have a markdown file for
```

The result was almost usable on the first try. Only the variable for the endpoint and the handling of the API date field (which is a string, but Copilot assumed an integer) needed manual fixing. Here is the output:

```python
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
    created_timestamp = int(datetime.fromisoformat(bookmark.get("created")).timestamp())
    creation_date = datetime.fromtimestamp(created_timestamp)

    # Generate the markdown file path
    file_name = f"content/bookmarks/{creation_date.strftime('%Y%m%d')}.md"

    # Check if the markdown file already exists
    if os.path.exists(file_name):
        continue

    # Generate the markdown content
    markdown_content = f"""+++
title = "{bookmark.get('title')}"
date = "{creation_date}"
categories: [ 'bookmarks' ]
+++

{note}

{link}

{excerpt}
"""

    # Write the markdown content to the file
    with open(file_name, "w") as file:
        file.write(markdown_content)

print("Bookmark generation completed.")
```

## Links

https://bacardi55.io/2024/02/13/bookmarks-section-the-pesos-way-kind-of/