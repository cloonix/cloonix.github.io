+++
title = 'Writing a Hugo Raindrop.io bookmark integration with AI'
date = 2024-07-30T13:11:47Z
tags = [ 'python', 'bookmarks', 'howto', 'blog', 'personal' ]
categories = [ 'howto' ]
type = "blog"
series = ['hugo']
toc = 1
[params]
  author = 'Claus Malter'
+++

[bacardi55](https://bacardi55.io/2024/02/13/bookmarks-section-the-pesos-way-kind-of/) [1] has an interesting bookmarks section on his blog, where a script generates Hugo markdown pages for bookmarks he has added to a central (self-hosted) bookmark manager. I found this very interesting and wanted to build something similar. I've been using [raindrop.io](https://raindrop.io) for some time now, and this service also provides an API. So this could be an easy project to do with the help of Github Copilot, which I have recently been using to give my software development projects a boost.  

So here are my goals:

1. Generate Hugo Markdown content using the Raindrop.io API (link and note)
2. Use only bookmarks from a specific publicly shared collection
3. A new section on my blog, only for bookmarks
4. Use python
5. Use Github Copilot for creating the python script
6. Find a way to automate the update of the GitHub pages  

There was one step in the workflow that I was not sure how to do: I don't want to manually deploy my pages every time I bookmark a page. Ideally, saving a bookmark would execute a web-hook, but Raindrop.io does not support this. So the alternative is to run a script on my server that fetches new bookmarks, generates the markdown files and pushes them to Github pages. But for now I will do it the manual way and decide later how improve it.  

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
# categories = [ 'bookmarks' ]
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
    tags = bookmark.get("tags")
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
```

## The Theme - The hardest part

I wasn't expecting that: Customising the theme was the part that took the most time. Not that it was complicated or anything. A change here, a change there... Made me understand the core of Hugo a bit more. So I'm ok. But for this blog post it's too much to point out all the changes. In a nutshell, that's what I did:

1. I added a section named `content/bookmarks`.  
2. I added a menu item in my `config.toml`
3. I added a small section on the mainpage for the last 5 bookmarks. For that I added this code:

```html
<h3>🔗 Recent bookmarks</h3>
<ul>
    {{ range first 5 (where site.RegularPages "Section" "bookmarks") }}
    <li>
        <div class="post-title">
            <time>{{ .Date.Format "2006-01-02" }}</time> 
            <a href="{{ .RelPermalink }}">{{ .Title }}</a>
    </li>
    </div>
    {{ end }}
</ul>
```

## Automation

I thought: "How can I make this automatic, but as simple as possible?" Since my deployment is through GitHub pages, this means that I always have to push my Markdown files to my GitHub repository. This also means I have to use the git client and do a pull/push for each bookmark update.  

So I need a computer to fetch my repository, run the python script on the local repository, git commit/push the changes to GitHub. To do this, I also need access to GitHub via a password-less SSH deployment key [2]. A deployment key can be explicitly added to a single repository and only allow access to that repository.  

1. Adding my python script to the repository
2. Generate a ssh-key (w/o password): `ssh-keygen -t ed25519 -C "your_email@example.com" ./deploy_key` and added the public key to the Deployment section of my repository
3. Added an entry to my `~/.ssh/config` to use the new ssh key for that GitHub repository:

    ```sh
    Host blog
        Hostname github.com
        IdentityFile ~/.ssh/git_deploy_key
        IdentitiesOnly yes 
        AddKeysToAgent yes
    ```

4. Clone the repository only for the bookmark creation workflow: `git clone git@blog:cloonix/cloonix.github.io ./bookmark-update`
5. Running a script through crontab:  

    ```sh
    git pull
    python3 raindrop_bookmarks.py
    git add ./content/bookmarks
    git commit -m "updated raindrop bookmarks"
    git push
    ```

6. Created a crontab to run the script.  

## Conclusion

This is not a step-by-step howto. More a diary of that kinda simple integration of the Raindrop API into my Hugo Github Pages deployment. But i achieved my goal: The crontab is running every how, which is more than enough, and fetches new bookmarks from my public bookmark collection. It generates the Markdown files and pushes them to Github where Actions deploy the static site.

## Links

[1] <https://bacardi55.io/2024/02/13/bookmarks-section-the-pesos-way-kind-of/>  
[2] <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys>
