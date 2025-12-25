# Blog Publishing Workflow

Write blog posts in Typora, publish to Hugo with automatic image handling.

## Setup

```bash
pip3 install -r requirements.txt
python3 check-dependencies.py
mkdir -p ~/Documents/blog-drafts/published
```

## Typora Configuration

**Preferences → Image:**
- When Insert Local Images: `Copy image to custom folder`
- Image Root Path: `./`
- Use relative path: ✓
- Custom Folder: `./assets`

## Required Front Matter

```yaml
---
title: "Your Post Title"
categories:
  - category1
tags:
  - tag1
---
```

## Usage

```bash
python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md
python3 publish-blog-post.py --help  # For all options
```

## Workflow

1. Write in Typora → `~/Documents/blog-drafts/my-post.md`
2. Paste images (auto-saved to `./assets/`)
3. Run: `python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md`
4. Preview: `hugo server -D`
5. Commit and push
