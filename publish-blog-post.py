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
        
        if not dry_run:
            self.content_dir.mkdir(parents=True, exist_ok=True)
    
    def log(self, message, force=False):
        """Print message if verbose or forced"""
        if self.verbose or force:
            print(message)
    
    def parse_and_validate_front_matter(self, content):
        """Extract and validate YAML front matter"""
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
        
        if not match:
            raise ValueError(
                "No front matter found. Please add:\n"
                "---\ntitle: \"Your Title\"\ncategories:\n  - cat1\ntags:\n  - tag1\n---"
            )
        
        try:
            front_matter = yaml.safe_load(match.group(1))
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML front matter: {e}")
        
        # Validate required fields
        required = {'title': str, 'categories': list, 'tags': list}
        for field, field_type in required.items():
            if field not in front_matter:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(front_matter[field], field_type):
                raise ValueError(f"'{field}' must be a {field_type.__name__}")
        
        return front_matter, match.group(2)
    
    def generate_filename(self, title):
        """Generate Hugo filename: YYYYMMDD_slug.md"""
        date_str = datetime.now().strftime("%Y%m%d")
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '_', slug).strip('_')
        return f"{date_str}_{slug}.md"
    
    def optimize_image(self, source, dest):
        """Resize and optimize image"""
        try:
            with Image.open(source) as img:
                if img.width > self.max_image_width:
                    ratio = self.max_image_width / img.width
                    new_height = int(img.height * ratio)
                    self.log(f"  Resizing: {img.width}x{img.height} → {self.max_image_width}x{new_height}")
                    img = img.resize((self.max_image_width, new_height), Image.Resampling.LANCZOS)
                    
                    if img.format in ['JPEG', 'JPG']:
                        img.save(dest, 'JPEG', quality=85, optimize=True)
                    elif img.format == 'PNG':
                        img.save(dest, 'PNG', optimize=True)
                    else:
                        img.save(dest, optimize=True)
                else:
                    self.log(f"  Copying: {img.width}x{img.height} (no resize needed)")
                    shutil.copy2(source, dest)
        except Exception as e:
            print(f"⚠️  Warning: Could not optimize {source.name}: {e}")
            shutil.copy2(source, dest)
    
    def find_image_path(self, draft_dir, img_path, is_in_published):
        """Find image file, checking multiple locations if needed"""
        source = (draft_dir / img_path.strip()).resolve()
        
        if not source.exists() and is_in_published:
            # Check parent directory for images
            source_parent = (draft_dir.parent / img_path.strip()).resolve()
            if source_parent.exists():
                return source_parent
        
        return source if source.exists() else None
    
    def process_images(self, draft_dir, body, post_slug, post_bundle_dir, is_in_published):
        """Process all images: find, optimize, rename, update references"""
        # Images go in the same folder as index.md (page bundle)
        post_image_dir = post_bundle_dir
        
        # Find all image references
        images_found = re.findall(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)', body)
        if not images_found:
            return body, 0, []
        
        self.log(f"\nProcessing {len(images_found)} images:", force=True)
        updated_body = body
        image_renames = []
        counter = 1
        
        for alt_text, img_path in images_found:
            # Skip external URLs and already processed images
            if img_path.startswith(('http://', 'https://', '//', '/images/blog/')):
                self.log(f"  Skipping: {img_path}")
                continue
            
            # Find source image
            source = self.find_image_path(draft_dir, img_path, is_in_published)
            if not source:
                print(f"⚠️  Warning: Image not found: {img_path}")
                continue
            
            # Generate clean filename
            ext = source.suffix
            clean_name = f"{post_slug}-{counter:02d}{ext}"
            dest = post_image_dir / clean_name
            dest_url = clean_name  # Relative path for page bundles
            counter += 1
            
            # Show/process image
            if self.dry_run:
                print(f"  📷 {source.name} → {clean_name}")
                print(f"     {source} → {dest}")
                try:
                    with Image.open(source) as img:
                        if img.width > self.max_image_width:
                            ratio = self.max_image_width / img.width
                            print(f"     Resize: {img.width}x{img.height} → {self.max_image_width}x{int(img.height*ratio)}")
                        else:
                            print(f"     Copy: {img.width}x{img.height}")
                except:
                    print(f"     Copy (dimensions unknown)")
            else:
                self.log(f"  {source.name} → {clean_name}")
                self.optimize_image(source, dest)
            
            # Update markdown references
            old_ref = f"![{alt_text}]({img_path})"
            new_ref = f"![{alt_text}]({dest_url})"
            updated_body = updated_body.replace(old_ref, new_ref)
            
            image_renames.append({'old_path': img_path, 'new_name': clean_name, 'alt_text': alt_text})
        
        if image_renames and not self.dry_run:
            self.log(f"✓ Processed {len(image_renames)} images → {post_slug}/", force=True)
        elif image_renames and self.dry_run:
            print(f"[DRY RUN] Would process {len(image_renames)} images → {post_slug}/")
        
        return updated_body, len(image_renames), image_renames
    
    def update_source_markdown(self, content, image_renames):
        """Update markdown with cleaned image names for source file (relative paths)"""
        updated = content
        for img in image_renames:
            old_ref = f"![{img['alt_text']}]({img['old_path']})"
            new_ref = f"![{img['alt_text']}]({img['new_name']})"  # Relative to bundle root
            updated = updated.replace(old_ref, new_ref)
        return updated
    
    def publish(self, draft_path):
        """Main publishing workflow"""
        draft_path = Path(draft_path).resolve()
        
        if not draft_path.exists():
            raise FileNotFoundError(f"Draft file not found: {draft_path}")
        if draft_path.suffix != '.md':
            raise ValueError(f"File must be markdown (.md): {draft_path}")
        
        self.log(f"\n{'='*60}", force=True)
        self.log(f"Publishing: {draft_path.name}", force=True)
        self.log(f"{'='*60}\n", force=True)
        
        # Read and parse
        content = draft_path.read_text(encoding='utf-8')
        front_matter, body = self.parse_and_validate_front_matter(content)
        self.log("✓ Front matter validated", force=True)
        
        # Update front matter
        if 'date' not in front_matter:
            front_matter['date'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        front_matter.setdefault('type', 'blog')
        front_matter.setdefault('draft', False)
        
        # Generate filename
        filename = self.generate_filename(front_matter['title'])
        post_slug = filename[:-3]
        self.log(f"✓ Generated bundle: {post_slug}/", force=True)
        
        # Create page bundle directory
        post_bundle_dir = self.content_dir / post_slug
        if not self.dry_run:
            post_bundle_dir.mkdir(parents=True, exist_ok=True)
        
        # Process images
        is_already_published = "published" in draft_path.parts
        draft_dir = draft_path.parent
        updated_body, image_count, image_renames = self.process_images(
            draft_dir, body, post_slug, post_bundle_dir, is_already_published
        )
        
        # Write Hugo content as index.md in bundle
        front_matter_yaml = yaml.dump(front_matter, default_flow_style=False, allow_unicode=True)
        hugo_content = f"---\n{front_matter_yaml}---\n{updated_body}"
        
        if not self.dry_run:
            (post_bundle_dir / "index.md").write_text(hugo_content, encoding='utf-8')
            self.log(f"✓ Created: content/blog/{post_slug}/index.md", force=True)
        else:
            self.log(f"[DRY RUN] Would create: content/blog/{post_slug}/index.md", force=True)
        
        # Handle source file in published folder (mirror bundle structure)
        published_base = draft_path.parent / "published"
        published_bundle = published_base / post_slug
        published_index = published_bundle / "index.md"
        
        if not is_already_published:
            # First time publishing
            if not self.dry_run:
                published_bundle.mkdir(parents=True, exist_ok=True)
                source_markdown = self.update_source_markdown(content, image_renames)
                published_index.write_text(source_markdown, encoding='utf-8')
                draft_path.unlink()
                self.log(f"✓ Moved to bundle: {draft_path.name} → {post_slug}/index.md", force=True)
                
                # Move images from assets/ to bundle folder
                if image_renames:
                    assets_dir = draft_dir / "assets"
                    for img in image_renames:
                        old_img = assets_dir / Path(img['old_path']).name
                        if old_img.exists():
                            new_img = published_bundle / img['new_name']
                            old_img.replace(new_img)
                    # Cleanup empty assets dir
                    if assets_dir.exists() and not list(assets_dir.iterdir()):
                        assets_dir.rmdir()
                    self.log(f"✓ Moved {len(image_renames)} images to {post_slug}/", force=True)
            else:
                self.log(f"[DRY RUN] Would create bundle: {published_bundle}/", force=True)
        else:
            # Re-publishing
            if not self.dry_run:
                source_markdown = self.update_source_markdown(content, image_renames)
                published_index.write_text(source_markdown, encoding='utf-8')
                
                # Handle images in bundle
                if image_renames:
                    for img in image_renames:
                        old_img = draft_path.parent / Path(img['old_path']).name
                        new_img = published_bundle / img['new_name']
                        if old_img.exists() and old_img != new_img:
                            old_img.replace(new_img)
                    self.log(f"✓ Renamed {len(image_renames)} images in bundle", force=True)
            
            self.log(f"✓ File already in published/ - regenerated output files", force=True)
        
        # Summary
        self.log(f"\n{'='*60}", force=True)
        if self.dry_run:
            print("🔍 DRY RUN SUMMARY - No files were changed")
            print(f"\nWould create/modify:")
            print(f"  📁 content/blog/{post_slug}/")
            print(f"     - index.md")
            if image_count > 0:
                print(f"     - {image_count} images")
            print(f"  📁 ~/Documents/Blog/published/{post_slug}/")
            print(f"\nRun without --dry-run to actually publish")
        else:
            self.log("✅ Publishing complete!", force=True)
            self.log(f"{'='*60}\n", force=True)
            self.log("Next steps:", force=True)
            self.log(f"  1. Preview: hugo server -D", force=True)
            self.log(f"  2. Visit: http://localhost:1313/", force=True)
            self.log(f"  3. Commit when ready:", force=True)
            self.log(f"     git add content/blog/{post_slug}/", force=True)
            self.log(f"     git commit -m \"Add blog post: {front_matter['title']}\"", force=True)


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
    
    # Detect Hugo root
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
        publisher.publish(args.draft_file)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
