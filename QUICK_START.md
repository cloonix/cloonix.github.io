# Quick Start: Typora → Hugo Workflow

## One-Time Setup

### 1. Install Dependencies (MacBook)

```bash
cd ~/git/cloonix.github.io
pip3 install -r requirements.txt

# Verify installation
python3 check-dependencies.py
```

### 2. Create Drafts Folder

```bash
mkdir -p ~/Documents/blog-drafts/published
```

### 3. Configure Typora

Open **Typora → Preferences → Image**:
- When Insert Local Images: `Copy image to custom folder`
- Image Root Path: `./`
- Use relative path: ✓
- Custom Folder: `./assets`

---

## Daily Workflow

### Write a Post

1. Open Typora
2. Create new file: `~/Documents/blog-drafts/my-post.md`
3. Add front matter:

```yaml
---
title: "My Post Title"
categories:
  - tutorial
tags:
  - hugo
---
```

4. Write content, paste images (⌘+V)
5. Save (⌘+S)

### Publish

```bash
cd ~/git/cloonix.github.io
python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md
```

### Preview

```bash
hugo server -D
```

Visit: http://localhost:1313

### Commit

```bash
git add content/blog/YYYYMMDD_my_post.md
git add static/images/blog/YYYYMMDD_my_post/
git commit -m "Add blog post: My Post Title"
git push
```

---

## Common Commands

```bash
# Basic publish
python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md

# Custom image width
python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md --max-width 1200

# Dry run (test without changes)
python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md --dry-run

# Verbose output
python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md --verbose

# Shell alias (add to ~/.zshrc)
alias publish='python3 ~/git/cloonix.github.io/publish-blog-post.py'
# Then use: publish ~/Documents/blog-drafts/my-post.md
```

---

## Required Front Matter

Every post **must** have:

```yaml
---
title: "Your Title Here"
categories:
  - at-least-one
tags:
  - at-least-one
---
```

---

## Troubleshooting

**Error: "No front matter found"**
→ Add YAML front matter (see above)

**Error: "Missing required fields"**
→ Ensure you have title, categories, and tags

**Error: "Image not found"**
→ Check images are in `assets/` folder

**Error: "Can't find Hugo root"**
→ Run from `~/git/cloonix.github.io` directory

---

For full documentation, see: [TYPORA_WORKFLOW.md](TYPORA_WORKFLOW.md)
