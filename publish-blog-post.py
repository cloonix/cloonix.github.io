#!/usr/bin/env python3
"""
Publish Blog Post Script for Hugo
Converts Typora drafts with local images to Hugo blog posts.

Usage:
    python3 publish-blog-post.py <draft_file.md> [options]

Options:
    --max-width <pixels>    Maximum image width (default: 1920)
    --dry-run               Show what would happen without making changes
    --verbose               Show detailed output
"""

import os
import sys
import re
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from PIL import Image
import yaml


class BlogPublisher:
    def __init__(self, hugo_root, max_image_width=1920, dry_run=False, verbose=False):
        self.hugo_root = Path(hugo_root)
        self.max_image_width = max_image_width
        self.dry_run = dry_run
        self.verbose = verbose
        
        self.content_dir = self.hugo_root / "content" / "blog"
        self.images_dir = self.hugo_root / "static" / "images" / "blog"
        
        # Ensure directories exist
        if not dry_run:
            self.content_dir.mkdir(parents=True, exist_ok=True)
            self.images_dir.mkdir(parents=True, exist_ok=True)
    
    def log(self, message, force=False):
        """Print message if verbose or forced"""
        if self.verbose or force:
            print(message)
    
    def parse_front_matter(self, content):
        """Extract YAML front matter from markdown content"""
        # Match YAML front matter (--- ... ---)
        yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(yaml_pattern, content, re.DOTALL)
        
        if match:
            try:
                front_matter = yaml.safe_load(match.group(1))
                body = match.group(2)
                return front_matter, body
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML front matter: {e}")
        
        # No front matter found
        return None, content
    
    def validate_front_matter(self, front_matter):
        """Validate that required front matter fields exist"""
        if not front_matter:
            raise ValueError(
                "No front matter found. Please add front matter with at least:\n"
                "---\n"
                "title: \"Your Post Title\"\n"
                "categories:\n"
                "  - category1\n"
                "tags:\n"
                "  - tag1\n"
                "---"
            )
        
        required_fields = ['title', 'categories', 'tags']
        missing = [field for field in required_fields if field not in front_matter]
        
        if missing:
            raise ValueError(
                f"Missing required front matter fields: {', '.join(missing)}\n"
                f"Please add these fields to your markdown file."
            )
        
        # Validate categories and tags are lists
        if not isinstance(front_matter['categories'], list):
            raise ValueError("Front matter 'categories' must be a list (YAML array)")
        if not isinstance(front_matter['tags'], list):
            raise ValueError("Front matter 'tags' must be a list (YAML array)")
        
        return True
    
    def generate_filename(self, title):
        """Generate Hugo filename from title: YYYYMMDD_slug.md"""
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Create slug from title
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
        slug = re.sub(r'[-\s]+', '_', slug)   # Replace spaces/hyphens with underscore
        slug = slug.strip('_')
        
        return f"{date_str}_{slug}.md"
    
    def update_front_matter(self, front_matter):
        """Add/update Hugo-specific front matter fields"""
        # Ensure required Hugo fields exist
        if 'date' not in front_matter:
            front_matter['date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        if 'type' not in front_matter:
            front_matter['type'] = 'blog'
        
        if 'draft' not in front_matter:
            front_matter['draft'] = False
        
        return front_matter
    
    def optimize_image(self, image_path, output_path):
        """Resize and optimize image if needed"""
        try:
            with Image.open(image_path) as img:
                original_size = img.size
                
                # Check if resize needed (only resize width, maintain aspect ratio)
                if img.width > self.max_image_width:
                    # Calculate new height maintaining aspect ratio
                    # ratio = new_width / old_width
                    # new_height = old_height * ratio
                    ratio = self.max_image_width / img.width
                    new_height = int(img.height * ratio)
                    
                    self.log(f"  Resizing: {original_size[0]}x{original_size[1]} → {self.max_image_width}x{new_height}")
                    
                    if not self.dry_run:
                        img = img.resize((self.max_image_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Save with optimization
                        if img.format in ['JPEG', 'JPG']:
                            img.save(output_path, 'JPEG', quality=85, optimize=True)
                        elif img.format == 'PNG':
                            img.save(output_path, 'PNG', optimize=True)
                        else:
                            img.save(output_path, optimize=True)
                else:
                    # Just copy if no resize needed
                    self.log(f"  Copying: {original_size[0]}x{original_size[1]} (no resize needed)")
                    if not self.dry_run:
                        shutil.copy2(image_path, output_path)
                
                return True
        except Exception as e:
            print(f"⚠️  Warning: Could not optimize {image_path.name}: {e}")
            # Fallback: just copy the file
            if not self.dry_run:
                shutil.copy2(image_path, output_path)
            return False
    
    def process_images(self, draft_dir, body_content, post_slug, is_in_published=False):
        """Find, copy, optimize images and update markdown references"""
        # Create image directory for this post
        post_image_dir = self.images_dir / post_slug
        
        if not self.dry_run:
            post_image_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all image references in markdown
        # Matches: ![alt](path) and ![alt](path "title")
        image_pattern = r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)'
        images_found = re.findall(image_pattern, body_content)
        
        if not images_found:
            self.log("No images found in markdown")
            return body_content, 0
        
        self.log(f"\nProcessing {len(images_found)} images:", force=True)
        processed_count = 0
        updated_content = body_content
        
        for alt_text, img_path in images_found:
            # Skip external URLs
            if img_path.startswith(('http://', 'https://', '//')):
                self.log(f"  Skipping external URL: {img_path}")
                continue
            
            # Skip already processed images (already in /images/blog/)
            if img_path.startswith('/images/blog/'):
                self.log(f"  Skipping already published: {img_path}")
                continue
            
            # Resolve image path relative to draft file
            img_path_clean = img_path.strip()
            source_image = (draft_dir / img_path_clean).resolve()
            
            # If not found and draft is in published/, check parent directory
            if not source_image.exists() and is_in_published:
                source_image_parent = (draft_dir.parent / img_path_clean).resolve()
                if source_image_parent.exists():
                    source_image = source_image_parent
            
            if not source_image.exists():
                print(f"⚠️  Warning: Image not found: {source_image}")
                print(f"    (looked in {draft_dir / img_path_clean})")
                if is_in_published:
                    print(f"    (also tried {draft_dir.parent / img_path_clean})")
                continue
            
            # Destination path
            dest_image = post_image_dir / source_image.name
            dest_url = f"/images/blog/{post_slug}/{source_image.name}"
            
            if self.dry_run:
                # Show what would happen in dry-run mode
                print(f"  📷 {source_image.name}")
                print(f"     Source: {source_image}")
                print(f"     Dest:   {dest_image}")
                
                # Show if resize would happen
                try:
                    from PIL import Image
                    with Image.open(source_image) as img:
                        if img.width > self.max_image_width:
                            ratio = self.max_image_width / img.width
                            new_height = int(img.height * ratio)
                            print(f"     Action: Resize {img.width}x{img.height} → {self.max_image_width}x{new_height}")
                        else:
                            print(f"     Action: Copy {img.width}x{img.height} (no resize needed)")
                except Exception as e:
                    print(f"     Action: Copy (could not read dimensions: {e})")
                
                print(f"     Markdown: {img_path} → {dest_url}")
                print()
            else:
                self.log(f"  {source_image.name}")
                # Optimize and copy image
                self.optimize_image(source_image, dest_image)
            
            # Update markdown reference
            old_reference = f"![{alt_text}]({img_path})"
            new_reference = f"![{alt_text}]({dest_url})"
            updated_content = updated_content.replace(old_reference, new_reference)
            
            processed_count += 1
        
        return updated_content, processed_count
    
    def publish(self, draft_path):
        """Main publishing workflow"""
        draft_path = Path(draft_path).resolve()
        
        if not draft_path.exists():
            raise FileNotFoundError(f"Draft file not found: {draft_path}")
        
        if not draft_path.suffix == '.md':
            raise ValueError(f"File must be a markdown file (.md): {draft_path}")
        
        self.log(f"\n{'='*60}", force=True)
        self.log(f"Publishing: {draft_path.name}", force=True)
        self.log(f"{'='*60}\n", force=True)
        
        # Read draft content
        with open(draft_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse front matter
        self.log("Parsing front matter...")
        front_matter, body = self.parse_front_matter(content)
        
        # Validate front matter
        self.validate_front_matter(front_matter)
        self.log("✓ Front matter validated", force=True)
        
        # Update front matter with Hugo fields
        front_matter = self.update_front_matter(front_matter)
        
        # Generate filename
        filename = self.generate_filename(front_matter['title'])
        post_slug = filename[:-3]  # Remove .md extension
        dest_file = self.content_dir / filename
        
        self.log(f"✓ Generated filename: {filename}", force=True)
        
        # Check if draft is already in published folder
        is_already_published = "published" in draft_path.parts
        
        # Process images
        draft_dir = draft_path.parent
        updated_body, image_count = self.process_images(draft_dir, body, post_slug, is_already_published)
        
        if image_count > 0:
            if self.dry_run:
                print(f"[DRY RUN] Would process {image_count} images → static/images/blog/{post_slug}/")
            else:
                self.log(f"✓ Processed {image_count} images → static/images/blog/{post_slug}/", force=True)
        
        # Reconstruct markdown with updated front matter and body
        front_matter_yaml = yaml.dump(front_matter, default_flow_style=False, allow_unicode=True)
        final_content = f"---\n{front_matter_yaml}---\n{updated_body}"
        
        # Write to destination
        if not self.dry_run:
            with open(dest_file, 'w', encoding='utf-8') as f:
                f.write(final_content)
            self.log(f"✓ Created: content/blog/{filename}", force=True)
        else:
            self.log(f"[DRY RUN] Would create: content/blog/{filename}", force=True)
        
        # Move draft to published folder
        published_dir = draft_path.parent / "published"
        
        if not is_already_published:
            if not self.dry_run:
                published_dir.mkdir(exist_ok=True)
                # Rename to match Hugo convention
                published_path = published_dir / filename
                shutil.move(str(draft_path), str(published_path))
                self.log(f"✓ Moved and renamed draft to: {published_path}", force=True)
                
                # Move assets folder if it exists
                assets_dir = draft_dir / "assets"
                if assets_dir.exists() and assets_dir.is_dir():
                    published_assets = published_dir / "assets"
                    if published_assets.exists():
                        shutil.rmtree(published_assets)
                    shutil.move(str(assets_dir), str(published_assets))
                    self.log(f"✓ Moved assets folder to published/", force=True)
            else:
                self.log(f"[DRY RUN] Would move draft to: {published_dir / filename}", force=True)
        else:
            # Update the published markdown file with new content
            if not self.dry_run:
                published_path = draft_path.parent / filename
                # If filename changed, rename the file
                if draft_path.name != filename:
                    shutil.move(str(draft_path), str(published_path))
                    self.log(f"✓ Renamed {draft_path.name} → {filename}", force=True)
            self.log(f"✓ File already in published/ - regenerated output files", force=True)
        
        # Summary
        self.log(f"\n{'='*60}", force=True)
        if self.dry_run:
            print("🔍 DRY RUN SUMMARY - No files were changed")
        else:
            self.log("✅ Publishing complete!", force=True)
        self.log(f"{'='*60}\n", force=True)
        
        if self.dry_run:
            print("Would create/modify:")
            print(f"  📄 content/blog/{filename}")
            if image_count > 0:
                print(f"  📁 static/images/blog/{post_slug}/")
                print(f"     ({image_count} images)")
            if not is_already_published:
                print(f"  📦 {published_dir / draft_path.name} (moved from drafts)")
                assets_dir = draft_dir / "assets"
                if assets_dir.exists() and assets_dir.is_dir():
                    print(f"  📦 {published_dir / 'assets'} (moved from drafts)")
            print(f"\nRun without --dry-run to actually publish")
        else:
            self.log("Next steps:", force=True)
            self.log(f"  1. Preview: hugo server -D", force=True)
            self.log(f"  2. Visit: http://localhost:1313/", force=True)
            self.log(f"  3. Commit when ready:", force=True)
            self.log(f"     git add content/blog/{filename}", force=True)
            if image_count > 0:
                self.log(f"     git add static/images/blog/{post_slug}/", force=True)
            self.log(f"     git commit -m \"Add blog post: {front_matter['title']}\"", force=True)
        
        return {
            'filename': filename,
            'slug': post_slug,
            'image_count': image_count,
            'dest_file': dest_file
        }


def main():
    parser = argparse.ArgumentParser(
        description='Publish Typora draft to Hugo blog',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md
  python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md --max-width 1200
  python3 publish-blog-post.py ~/Documents/blog-drafts/my-post.md --dry-run --verbose
        """
    )
    
    parser.add_argument('draft_file', help='Path to the draft markdown file')
    parser.add_argument('--max-width', type=int, default=1920,
                        help='Maximum image width in pixels (default: 1920)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would happen without making changes')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed output')
    
    args = parser.parse_args()
    
    # Detect Hugo root (current directory or parent)
    current_dir = Path.cwd()
    if (current_dir / 'hugo.toml').exists() or (current_dir / 'config.toml').exists():
        hugo_root = current_dir
    elif (current_dir.parent / 'hugo.toml').exists():
        hugo_root = current_dir.parent
    else:
        print("❌ Error: Could not find Hugo root directory (hugo.toml not found)")
        print("   Please run this script from your Hugo project directory")
        sys.exit(1)
    
    try:
        publisher = BlogPublisher(
            hugo_root=hugo_root,
            max_image_width=args.max_width,
            dry_run=args.dry_run,
            verbose=args.verbose
        )
        
        result = publisher.publish(args.draft_file)
        
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
