# Typora → Hugo Blog Workflow

A complete workflow for writing blog posts in Typora and publishing them to your Hugo blog with automatic image handling.

## Table of Contents

1. [Overview](#overview)
2. [Setup Instructions](#setup-instructions)
3. [Typora Configuration](#typora-configuration)
4. [Writing Workflow](#writing-workflow)
5. [Publishing Workflow](#publishing-workflow)
6. [Troubleshooting](#troubleshooting)

---

## Overview

This workflow allows you to:
- Write blog posts in Typora on your MacBook with live preview
- Paste/drag images directly into your posts
- Automatically organize and optimize images
- Generate proper Hugo front matter and filenames
- Publish with a single command

### Folder Structure

**On MacBook (drafts):**
```
~/Documents/blog-drafts/
├── my-first-post.md
├── assets/
│   ├── screenshot1.png
│   └── diagram.jpg
├── another-post.md
└── assets/
    └── photo.png
```

**In Hugo repo (published):**
```
~/git/cloonix.github.io/
├── content/blog/
│   └── 20251225_my_first_post.md
└── static/images/blog/
    └── 20251225_my_first_post/
        ├── screenshot1.png
        └── diagram.jpg
```

---

## Setup Instructions

### 1. Install Python Dependencies

On your MacBook, navigate to your Hugo repository:

```bash
cd ~/git/cloonix.github.io
pip3 install -r requirements.txt
```

This installs:
- `Pillow>=10.0.0` - for image optimization and resizing (maintains aspect ratio)
- `PyYAML>=6.0` - for front matter parsing

**Verify installation:**
```bash
python3 check-dependencies.py
```

This will check if all dependencies are correctly installed.

### 2. Create Drafts Folder

Create a dedicated folder for your Typora drafts:

```bash
mkdir -p ~/Documents/blog-drafts
mkdir -p ~/Documents/blog-drafts/published
mkdir -p ~/Documents/blog-drafts/assets
```

### 3. Verify Script Installation

Test that the script is working:

```bash
cd ~/git/cloonix.github.io
python3 publish-blog-post.py --help
```

You should see the help message with usage instructions.

---

## Typora Configuration

Configure Typora on your MacBook to automatically handle images:

### Step 1: Open Typora Preferences

Press `⌘ + ,` (Command + Comma) or go to `Typora → Preferences`

### Step 2: Configure Image Settings

Navigate to the **Image** section and configure:

| Setting | Value |
|---------|-------|
| **When Insert Local Images** | `Copy image to custom folder` |
| **Image Root Path** | `./` (dot slash) |
| **Use relative path** | ✓ **Checked** |
| **Custom Folder** | `./assets` |
| **Allow upload images** | Optional (for online images) |

### What This Does

When you paste or drag an image into Typora:
1. Image is automatically copied to `./assets/` folder
2. Typora inserts markdown: `![Description](assets/image.png)`
3. The publish script will move it to the Hugo static folder later

### Visual Reference

Your Typora Image Preferences should look like this:

```
┌─────────────────────────────────────────────┐
│ Image                                        │
├─────────────────────────────────────────────┤
│                                              │
│ When Insert Local Images:                   │
│ ⦿ Copy image to custom folder              │
│                                              │
│ Image Root Path: ./                         │
│                                              │
│ ☑ Use relative path                         │
│                                              │
│ Custom Folder: ./assets                     │
│                                              │
└─────────────────────────────────────────────┘
```

---

## Writing Workflow

### Step 1: Create a New Draft

1. Open Typora
2. Create new file in `~/Documents/blog-drafts/`
3. Name it descriptively (e.g., `typora-hugo-workflow.md`)

### Step 2: Add Front Matter

Every blog post **must** have YAML front matter with these required fields:

```yaml
---
title: "Your Awesome Blog Post Title"
categories:
  - howto
  - development
tags:
  - hugo
  - typora
  - workflow
  - markdown
---
```

**Required fields:**
- `title` - Your post title (will be used to generate filename)
- `categories` - List of categories (at least one)
- `tags` - List of tags (at least one)

**Optional fields** (script will add these if missing):
- `date` - Publication date (auto-generated if missing)
- `type` - Always set to `blog`
- `draft` - Set to `false` for published posts

### Step 3: Write Your Content

Write your blog post in Typora with markdown. The editor provides live preview!

**Tips:**
- Use `#` for headings (`##` for h2, `###` for h3, etc.)
- Use ` ```language ` for code blocks
- Paste images directly from clipboard (Cmd+V)
- Drag and drop images from Finder

### Step 4: Add Images

**Method 1: Copy & Paste**
1. Copy image to clipboard (screenshot, browser, etc.)
2. Paste in Typora (`⌘ + V`)
3. Typora automatically saves to `assets/` folder
4. Image reference is inserted: `![](assets/image.png)`

**Method 2: Drag & Drop**
1. Drag image from Finder
2. Drop into Typora document
3. Same result as copy/paste

**Method 3: Insert Dialog**
1. Click `Format → Image → Insert Image` or `⌘ + ⌃ + I`
2. Choose image file
3. Typora copies to `assets/` automatically

### Step 5: Add Alt Text to Images

Good practice: Add descriptive alt text to your images:

```markdown
![Screenshot showing Typora preferences](assets/typora-settings.png)
```

---

## Publishing Workflow

When your draft is ready to publish:

### Basic Usage

```bash
cd ~/git/cloonix.github.io
python3 publish-blog-post.py ~/Documents/blog-drafts/your-post.md
```

### What the Script Does

1. ✓ **Validates front matter** (checks required fields exist)
2. ✓ **Generates filename** from date + title slug (e.g., `20251225_your_post.md`)
3. ✓ **Updates front matter** (adds date, type, draft fields if missing)
4. ✓ **Processes images:**
   - Resizes images wider than max-width (default 1920px) by scaling width only
   - Automatically maintains aspect ratio (height scales proportionally)
   - Optimizes JPEG/PNG files (JPEG: 85% quality, PNG: lossless)
   - Copies to `static/images/blog/YYYYMMDD_slug/`
5. ✓ **Updates image paths** in markdown (`assets/img.png` → `/images/blog/YYYYMMDD_slug/img.png`)
6. ✓ **Moves draft to published/** folder (keeps backup)
7. ✓ **Shows git commands** for committing

### Script Options

```bash
# Custom maximum image width
python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md --max-width 1200

# Dry run (see what would happen without making changes - shows image details)
python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md --dry-run

# Verbose output (see detailed processing steps)
python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md --verbose

# Combine options
python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md --max-width 1200 --verbose
```

### Example Output (Normal Mode)

```
============================================================
Publishing: typora-hugo-workflow.md
============================================================

✓ Front matter validated
✓ Generated filename: 20251225_typora_hugo_workflow.md

Processing 3 images:
  screenshot1.png
  Resizing: 2560x1440 → 1920x1080
  diagram.jpg
  Copying: 1200x800 (no resize needed)
  photo.png
  Resizing: 3000x2000 → 1920x1280

✓ Processed 3 images → static/images/blog/20251225_typora_hugo_workflow/
✓ Created: content/blog/20251225_typora_hugo_workflow.md
✓ Moved draft to: ~/Documents/blog-drafts/published/typora-hugo-workflow.md
✓ Moved assets folder to published/

============================================================
✅ Publishing complete!
============================================================

Next steps:
  1. Preview: hugo server -D
  2. Visit: http://localhost:1313/
  3. Commit when ready:
     git add content/blog/20251225_typora_hugo_workflow.md
     git add static/images/blog/20251225_typora_hugo_workflow/
     git commit -m "Add blog post: Typora Hugo Workflow"
```

### Example Output (Dry-Run Mode)

```bash
python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md --dry-run
```

```
============================================================
Publishing: my-post.md
============================================================

✓ Front matter validated
✓ Generated filename: 20251225_my_post.md

Processing 2 images:
  📷 screenshot.png
     Source: /Users/claus/Documents/blog-drafts/assets/screenshot.png
     Dest:   /Users/claus/git/cloonix.github.io/static/images/blog/20251225_my_post/screenshot.png
     Action: Resize 2560x1440 → 1920x1080
     Markdown: assets/screenshot.png → /images/blog/20251225_my_post/screenshot.png

  📷 diagram.jpg
     Source: /Users/claus/Documents/blog-drafts/assets/diagram.jpg
     Dest:   /Users/claus/git/cloonix.github.io/static/images/blog/20251225_my_post/diagram.jpg
     Action: Copy 1024x768 (no resize needed)
     Markdown: assets/diagram.jpg → /images/blog/20251225_my_post/diagram.jpg

[DRY RUN] Would process 2 images → static/images/blog/20251225_my_post/
[DRY RUN] Would create: content/blog/20251225_my_post.md
[DRY RUN] Would move draft to: ~/Documents/blog-drafts/published/my-post.md

============================================================
🔍 DRY RUN SUMMARY - No files were changed
============================================================

Would create/modify:
  📄 content/blog/20251225_my_post.md
  📁 static/images/blog/20251225_my_post/
     (2 images)
  📦 ~/Documents/blog-drafts/published/my-post.md (moved from drafts)
  📦 ~/Documents/blog-drafts/published/assets (moved from drafts)

Run without --dry-run to actually publish
```

### Preview Your Post

Start Hugo's development server:

```bash
hugo server -D
```

Visit `http://localhost:1313/` in your browser to see your post.

**Tip:** Hugo automatically reloads when you make changes!

### Commit and Publish

When you're happy with the preview:

```bash
git add content/blog/20251225_your_post.md
git add static/images/blog/20251225_your_post/
git commit -m "Add blog post: Your Post Title"
git push
```

Your GitHub Actions workflow will automatically build and deploy the site.

---

## Re-Publishing (Fixing Errors)

If you need to fix a published post:

1. Edit the file in `~/Documents/blog-drafts/published/your-post.md`
2. Run the publish script again:
   ```bash
   python3 publish-blog-post.py ~/Documents/blog-drafts/published/your-post.md
   ```
3. The script will regenerate the Hugo files
4. The draft stays in `published/` folder (not moved again)

---

## Complete Example Workflow

### Start to Finish

```bash
# 1. Create new draft in Typora
cd ~/Documents/blog-drafts
open -a Typora "my-awesome-post.md"

# 2. Add front matter in Typora:
---
title: "My Awesome Post"
categories:
  - tutorial
tags:
  - hugo
  - automation
---

# 3. Write content, paste images...
# 4. Save in Typora (⌘ + S)

# 5. Publish when ready
cd ~/git/cloonix.github.io
python3 publish-blog-post.py ~/Documents/blog-drafts/my-awesome-post.md

# 6. Preview
hugo server -D
# Visit http://localhost:1313

# 7. Commit
git add content/blog/20251225_my_awesome_post.md
git add static/images/blog/20251225_my_awesome_post/
git commit -m "Add blog post: My Awesome Post"
git push
```

---

## Troubleshooting

### Error: "No front matter found"

**Problem:** Your markdown file doesn't have YAML front matter.

**Solution:** Add front matter at the top of your file:

```yaml
---
title: "Your Title"
categories:
  - category1
tags:
  - tag1
---
```

### Error: "Missing required front matter fields"

**Problem:** You're missing `title`, `categories`, or `tags`.

**Solution:** Ensure all three fields exist in your front matter.

### Error: "Image not found"

**Problem:** An image referenced in your markdown doesn't exist.

**Solution:** 
- Check that images are in the `assets/` folder
- Verify the image path in your markdown matches the actual filename
- Make sure you saved after pasting images in Typora

### Error: "Front matter 'categories' must be a list"

**Problem:** Categories or tags are not formatted as YAML lists.

**Incorrect:**
```yaml
categories: tutorial
tags: hugo
```

**Correct:**
```yaml
categories:
  - tutorial
tags:
  - hugo
```

### Images Not Resizing

**Problem:** PIL/Pillow might not support your image format.

**Solution:**
- Convert images to JPEG or PNG
- Or use `--dry-run --verbose` to see error messages

### Script Can't Find Hugo Root

**Problem:** You're running the script from the wrong directory.

**Solution:** Always run from your Hugo project directory:
```bash
cd ~/git/cloonix.github.io
python3 publish-blog-post.py <draft_path>
```

---

## Tips & Best Practices

### 1. Use Descriptive Filenames

Draft filenames should be descriptive:
- ✅ `typora-hugo-workflow.md`
- ✅ `self-hosting-pangolin.md`
- ❌ `post1.md`
- ❌ `draft.md`

The script generates the date prefix automatically.

### 2. Optimize Images Before Pasting

While the script resizes large images, it's good practice to:
- Screenshot at reasonable resolution (not 4K)
- Crop unnecessary parts before pasting
- Use PNG for screenshots, JPEG for photos

**How image resizing works:**
- Only resizes if image width exceeds max-width (default: 1920px)
- Scales width to max-width
- Height is automatically calculated to maintain original aspect ratio
- Example: 3000x2000 image → 1920x1280 (maintains 3:2 ratio)
- Uses high-quality LANCZOS resampling for best results

### 3. Use Meaningful Alt Text

Good alt text helps with accessibility and SEO:
```markdown
![Typora image preferences dialog showing custom folder settings](assets/settings.png)
```

### 4. Keep Drafts Organized

Create subfolders for different topics:
```
~/Documents/blog-drafts/
├── tutorials/
├── personal/
├── reviews/
└── published/
```

### 5. Preview Before Committing

Always run `hugo server -D` to preview your post before committing.

### 6. Version Control Your Drafts

Consider making `blog-drafts/` a git repository too:
```bash
cd ~/Documents/blog-drafts
git init
git add .
git commit -m "Initial drafts"
```

---

## Advanced Configuration

### Custom Image Width Per Post

```bash
# For posts with large diagrams
python3 publish-blog-post.py my-post.md --max-width 2560

# For mobile-optimized posts
python3 publish-blog-post.py my-post.md --max-width 1200
```

### Shell Alias

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias publish-post='python3 ~/git/cloonix.github.io/publish-blog-post.py'
```

Then use:
```bash
publish-post ~/Documents/blog-drafts/my-post.md
```

---

## Questions or Issues?

- Check the [Hugo documentation](https://gohugo.io/documentation/)
- Review your existing published posts in `content/blog/` for examples
- Test with `--dry-run --verbose` to see what the script would do

Happy blogging! ✍️
