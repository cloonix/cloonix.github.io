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
import os
import shutil
import argparse
import subprocess
import tempfile
import tty
import termios
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
from PIL import Image
import yaml


# Constants
STEP_COUNT = 4
H1_PATTERN = r'^\s*#\s+[^\n]+\n*'
IMAGE_PATTERN = r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)'
FRONTMATTER_PATTERN = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
DATE_FORMAT_ISO = "%Y-%m-%dT%H:%M:%SZ"
DATE_FORMAT_DISPLAY = '%Y-%m-%d %H:%M UTC'


class FrontmatterValidator:
    """Validates and ensures frontmatter completeness"""
    
    REQUIRED_FIELDS = {
        'title': str,
        'categories': list,
        'tags': list,
    }
    
    DEFAULTS = {
        'type': 'blog',
        'draft': False,
    }
    
    @classmethod
    def validate(cls, frontmatter):
        """Returns (is_valid, missing_fields)"""
        if not frontmatter:
            return False, ['all fields (no frontmatter)']
        
        missing = []
        for field, expected_type in cls.REQUIRED_FIELDS.items():
            if field not in frontmatter:
                missing.append(field)
            elif not isinstance(frontmatter[field], expected_type):
                missing.append(f"{field} (wrong type)")
        
        return len(missing) == 0, missing
    
    @classmethod
    def ensure_complete(cls, frontmatter):
        """Add missing non-required fields with defaults"""
        if 'date' not in frontmatter:
            frontmatter['date'] = datetime.now(timezone.utc).strftime(DATE_FORMAT_ISO)
        
        for field, default in cls.DEFAULTS.items():
            frontmatter.setdefault(field, default)
        
        return frontmatter


class FrontmatterParser:
    """Handles parsing and extraction of frontmatter from markdown"""
    
    @staticmethod
    def parse_frontmatter_section(content):
        """Extract YAML frontmatter from content"""
        if not content.startswith('---'):
            return None
        
        end = content.find('---', 3)
        if end <= 0:
            return None
        
        try:
            return yaml.safe_load(content[3:end])
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML front matter: {e}")
    
    @staticmethod
    def extract_h1_title(text):
        """Extract first H1 heading from text"""
        match = re.match(r'^\s*#\s+(.+?)(?:\n|$)', text, re.MULTILINE)
        return match.group(1).strip() if match else None
    
    @staticmethod
    def remove_h1(text):
        """Remove first H1 heading from text"""
        return re.sub(H1_PATTERN, '', text, count=1)
    
    @classmethod
    def parse(cls, content):
        """Parse content and return (frontmatter, body, extracted_title)"""
        match = re.match(FRONTMATTER_PATTERN, content, re.DOTALL)
        
        if not match:
            # No frontmatter
            extracted_title = cls.extract_h1_title(content)
            body = cls.remove_h1(content)
            return None, body, extracted_title
        
        # Has frontmatter
        try:
            front_matter = yaml.safe_load(match.group(1))
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML front matter: {e}")
        
        body = match.group(2)
        extracted_title = cls.extract_h1_title(body)
        body = cls.remove_h1(body)
        
        return front_matter, body, extracted_title
    
    @staticmethod
    def serialize(frontmatter):
        """Convert frontmatter dict to YAML string"""
        return yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, indent=2)
    
    @staticmethod
    def create_markdown(frontmatter, body):
        """Create full markdown with frontmatter"""
        yaml_str = FrontmatterParser.serialize(frontmatter)
        return f"---\n{yaml_str}---\n{body}"


class UserInput:
    """Handles all user input operations"""
    
    @staticmethod
    def get_single_key():
        """Get a single keypress without Enter"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setraw(fd)
            char = sys.stdin.read(1).lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        return char
    
    @staticmethod
    def text_field(field_name, default='', required=True, step_info=None, hint=None):
        """Collect a single text field with validation"""
        if step_info:
            print(f"\n[{step_info}/{STEP_COUNT}] {field_name}")
        
        if hint:
            print(f"  {hint}")
        
        while True:
            prompt = f"  Enter {field_name.lower()}"
            if default:
                prompt += f" [{default}]"
            prompt += ": "
            
            value = input(prompt).strip()
            if not value and default:
                value = default
            
            if value or not required:
                return value
            
            print(f"  ⚠️  {field_name} is required!")
    
    @staticmethod
    def list_field(field_name, default_list=None, required=True, step_info=None, suggestions=None):
        """Collect a comma-separated list field with lowercase normalization"""
        if step_info:
            print(f"\n[{step_info}/{STEP_COUNT}] {field_name} (lowercase, comma-separated)")
        
        if suggestions:
            print(f"  Suggestions: {', '.join(suggestions)}")
        
        default_str = ', '.join(default_list) if default_list else ''
        
        while True:
            prompt = f"  Enter {field_name.lower()}"
            if default_str:
                prompt += f" [{default_str}]"
            prompt += ": "
            
            value = input(prompt).strip()
            if not value and default_str:
                value = default_str
            
            if value:
                return [item.strip().lower() for item in value.split(',') if item.strip()]
            
            if not required:
                return []
            
            print(f"  ⚠️  At least one {field_name.lower()} is required!")


class GitOperations:
    """Handles git operations"""
    
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)
    
    def _run(self, cmd):
        """Run git command"""
        return subprocess.run(
            cmd,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=True
        )
    
    def add(self, path):
        """Stage files"""
        self._run(['git', 'add', path])
    
    def has_changes(self):
        """Check if there are staged changes"""
        result = self._run(['git', 'status', '--porcelain'])
        return bool(result.stdout.strip())
    
    def commit(self, message):
        """Commit staged changes"""
        self._run(['git', 'commit', '-m', message])
    
    def push(self):
        """Push to remote"""
        self._run(['git', 'push'])
    
    def commit_and_push(self, post_slug, title):
        """Commit and push blog post"""
        print(f"\n{'='*60}")
        print("📦 Committing and pushing to git...")
        print(f"{'='*60}\n")
        
        try:
            self.add(f'content/blog/{post_slug}/')
            print(f"✓ Staged content/blog/{post_slug}/")
            
            if not self.has_changes():
                print(f"ℹ️  No changes to commit - post already up to date")
                return True
            
            commit_msg = f"Add blog post: {title}"
            self.commit(commit_msg)
            print(f"✓ Committed: {commit_msg}")
            
            self.push()
            print(f"✓ Pushed to remote")
            
            print(f"\n✅ Successfully published and pushed!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"\n⚠️  Git operation failed: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            print(f"\n   You can manually commit and push with:")
            print(f"     git add content/blog/{post_slug}/")
            print(f"     git commit -m 'Add blog post: {title}'")
            print(f"     git push")
            return False


class BlogPublisher:
    """Main blog publisher class"""
    
    def __init__(self, hugo_root, max_image_width=1920, dry_run=False, verbose=False):
        self.hugo_root = Path(hugo_root)
        self.max_image_width = max_image_width
        self.dry_run = dry_run
        self.verbose = verbose
        
        self.content_dir = self.hugo_root / "content" / "blog"
        self.git = GitOperations(hugo_root)
        
        if not dry_run:
            self.content_dir.mkdir(parents=True, exist_ok=True)
    
    def log(self, message, force=False):
        """Print message if verbose or forced"""
        if self.verbose or force:
            print(message)
    
    def get_post_suggestions(self):
        """Scan existing posts and return common categories/tags and scheduled posts"""
        categories = Counter()
        tags = Counter()
        all_posts = []
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        for md_file in self.content_dir.glob('*/index.md'):
            try:
                content = md_file.read_text(encoding='utf-8')
                fm = FrontmatterParser.parse_frontmatter_section(content)
                
                if not fm:
                    continue
                
                # Collect categories and tags
                if 'categories' in fm and isinstance(fm['categories'], list):
                    for cat in fm['categories']:
                        if cat:
                            categories[str(cat).lower()] += 1
                
                if 'tags' in fm and isinstance(fm['tags'], list):
                    for tag in fm['tags']:
                        if tag:
                            tags[str(tag).lower()] += 1
                
                # Collect post dates
                if 'date' in fm and 'title' in fm and isinstance(fm['date'], str):
                    try:
                        post_date = datetime.strptime(fm['date'][:19], '%Y-%m-%dT%H:%M:%S')
                        post_date = post_date.replace(tzinfo=timezone.utc)
                        
                        all_posts.append({
                            'title': fm['title'],
                            'date': post_date,
                            'date_str': post_date.strftime(DATE_FORMAT_DISPLAY),
                            'is_future': post_date >= today_start
                        })
                    except (ValueError, IndexError):
                        pass
            except Exception:
                continue
        
        # Sort posts and get last 2 past + all future
        all_posts.sort(key=lambda x: x['date'])
        past_posts = [p for p in all_posts if not p['is_future']]
        future_posts = [p for p in all_posts if p['is_future']]
        recent_posts = past_posts[-2:] + future_posts
        
        return {
            'categories': [cat for cat, _ in categories.most_common(5)],
            'tags': [tag for tag, _ in tags.most_common(10)],
            'posts': recent_posts
        }
    
    def parse_date(self, date_str):
        """Parse date from multiple formats and return ISO format"""
        date_str = date_str.strip()
        
        formats = [
            ('%Y-%m-%dT%H:%M:%SZ', lambda d: d.strftime(DATE_FORMAT_ISO)),
            ('%Y-%m-%d', lambda d: d.strftime("%Y-%m-%dT00:00:00Z")),
            ('%Y-%m-%d %H:%M', lambda d: d.strftime("%Y-%m-%dT%H:%M:00Z")),
        ]
        
        for fmt, formatter in formats:
            try:
                return formatter(datetime.strptime(date_str, fmt))
            except ValueError:
                continue
        
        return None
    
    def collect_date(self, existing=None, step_info=None, recent_posts=None):
        """Collect date field with flexible parsing"""
        if step_info:
            print(f"\n[{step_info}/{STEP_COUNT}] Date")
        
        now = datetime.now(timezone.utc)
        default_date = existing.get('date', now.strftime(DATE_FORMAT_ISO)) if existing else now.strftime(DATE_FORMAT_ISO)
        human_date = now.strftime(DATE_FORMAT_DISPLAY)
        
        # Show recent and upcoming posts
        if recent_posts:
            print(f"  📅 Recent and upcoming posts:")
            for post in recent_posts:
                marker = "→" if post['is_future'] else " "
                print(f"     {marker} {post['date_str']}: {post['title']}")
        
        while True:
            print(f"  Example: 2026-01-15 14:30")
            date_input = input(f"  Press Enter for now ({human_date}), or enter date: ").strip()
            if not date_input:
                return default_date
            
            parsed_date = self.parse_date(date_input)
            if parsed_date:
                return parsed_date
            
            print("  ⚠️  Invalid date format. Try: YYYY-MM-DD HH:MM")
    
    def collect_frontmatter(self, existing=None, extracted_title=None, suggestions=None):
        """Interactively collect frontmatter from user"""
        if suggestions is None:
            suggestions = {'categories': [], 'tags': [], 'posts': []}
        
        print("\n" + "="*60)
        print("📝 Front Matter Collection")
        print("="*60 + "\n")
        
        if existing:
            print("Press Enter to keep existing value shown in brackets\n")
        
        default_title = existing.get('title', '') if existing else (extracted_title or '')
        hint = f"✓ Detected from H1: \"{extracted_title}\"" if extracted_title and not existing else None
        
        frontmatter = {
            'title': UserInput.text_field('Title', default_title, required=True, step_info=1, hint=hint),
            'date': self.collect_date(existing, step_info=2, recent_posts=suggestions.get('posts')),
            'categories': UserInput.list_field(
                'Categories',
                existing.get('categories', []) if existing else [],
                required=True,
                step_info=3,
                suggestions=suggestions.get('categories')
            ),
            'tags': UserInput.list_field(
                'Tags',
                existing.get('tags', []) if existing else [],
                required=True,
                step_info=4,
                suggestions=suggestions.get('tags')
            ),
            'type': 'blog',
            'draft': existing.get('draft', False) if existing else False,
        }
        
        return frontmatter
    
    def show_frontmatter(self, frontmatter):
        """Display frontmatter for review"""
        print("\n" + "="*60)
        print("📋 Front Matter Review")
        print("="*60 + "\n")
        
        yaml_str = FrontmatterParser.serialize(frontmatter)
        print("---")
        print(yaml_str.rstrip())
        print("---")
        print()
    
    def confirm_action(self):
        """Ask user to confirm with single-key selection"""
        print("Proceed with publishing?")
        print("  [y] yes  [q] quit  [e] edit  [p] preview")
        print("  Press a key...", end='', flush=True)
        
        char = UserInput.get_single_key()
        print(f"\r  → {char}                                          ")
        
        actions = {
            'y': 'yes',
            'q': 'no',
            'e': 'edit',
            'p': 'preview'
        }
        
        if char in actions:
            return actions[char]
        
        print(f"  ⚠️  Invalid key '{char}'. Please try again.\n")
        return self.confirm_action()
    
    def preview_content(self, frontmatter, body):
        """Preview the full content with glow"""
        full_content = FrontmatterParser.create_markdown(frontmatter, body)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp:
            tmp.write(full_content)
            tmp_path = tmp.name
        
        try:
            result = subprocess.run(['which', 'glow'], capture_output=True, text=True)
            if result.returncode != 0:
                print("\n⚠️  'glow' not found. Install it with: brew install glow")
                print("\nShowing raw content instead:\n")
                print(full_content)
                input("\nPress Enter to continue...")
                return
            
            subprocess.run(['glow', '-p', tmp_path])
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    def generate_slug(self, title, date_str):
        """Generate Hugo slug: YYYYMMDD_slug"""
        date_prefix = date_str[:10].replace('-', '')
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '_', slug).strip('_')
        return f"{date_prefix}_{slug}"
    
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
    
    def find_image(self, draft_dir, img_path, is_in_published):
        """Find image file, checking multiple locations if needed"""
        source = (draft_dir / img_path.strip()).resolve()
        
        if not source.exists() and is_in_published:
            source_parent = (draft_dir.parent / img_path.strip()).resolve()
            if source_parent.exists():
                return source_parent
        
        return source if source.exists() else None
    
    def process_images(self, draft_dir, body, post_slug, post_bundle_dir, is_in_published):
        """Process all images: find, optimize, rename, update references"""
        images_found = re.findall(IMAGE_PATTERN, body)
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
            
            source = self.find_image(draft_dir, img_path, is_in_published)
            if not source:
                print(f"⚠️  Warning: Image not found: {img_path}")
                continue
            
            ext = source.suffix
            clean_name = f"{post_slug}-{counter:02d}{ext}"
            dest = post_bundle_dir / clean_name
            counter += 1
            
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
            
            old_ref = f"![{alt_text}]({img_path})"
            new_ref = f"![{alt_text}]({clean_name})"
            updated_body = updated_body.replace(old_ref, new_ref)
            
            image_renames.append({'old_path': img_path, 'new_name': clean_name, 'alt_text': alt_text})
        
        if image_renames:
            msg = f"[DRY RUN] Would process" if self.dry_run else "✓ Processed"
            self.log(f"{msg} {len(image_renames)} images → {post_slug}/", force=True)
        
        return updated_body, len(image_renames), image_renames
    
    def update_image_refs(self, content, image_renames):
        """Update markdown with cleaned image names"""
        updated = content
        for img in image_renames:
            old_ref = f"![{img['alt_text']}]({img['old_path']})"
            new_ref = f"![{img['alt_text']}]({img['new_name']})"
            updated = updated.replace(old_ref, new_ref)
        return updated
    
    def handle_source_file(self, draft_path, post_slug, content, image_renames, is_already_published):
        """Handle source file in published folder"""
        if is_already_published:
            published_bundle = draft_path.parent
            published_index = draft_path
        else:
            published_base = draft_path.parent / "published"
            published_bundle = published_base / post_slug
            published_index = published_bundle / "index.md"
        
        if not self.dry_run:
            if not is_already_published:
                # First time publishing
                published_bundle.mkdir(parents=True, exist_ok=True)
                source_markdown = self.update_image_refs(content, image_renames)
                published_index.write_text(source_markdown, encoding='utf-8')
                draft_path.unlink()
                self.log(f"✓ Moved to bundle: {draft_path.name} → {post_slug}/index.md", force=True)
                
                # Move images from assets/ to bundle folder
                if image_renames:
                    assets_dir = draft_path.parent.parent / "assets"
                    for img in image_renames:
                        old_img = assets_dir / Path(img['old_path']).name
                        if old_img.exists():
                            new_img = published_bundle / img['new_name']
                            old_img.replace(new_img)
                    
                    if assets_dir.exists() and not list(assets_dir.iterdir()):
                        assets_dir.rmdir()
                    self.log(f"✓ Moved {len(image_renames)} images to {post_slug}/", force=True)
            else:
                # Re-publishing
                source_markdown = self.update_image_refs(content, image_renames)
                published_index.write_text(source_markdown, encoding='utf-8')
                
                if image_renames:
                    for img in image_renames:
                        old_img = draft_path.parent / Path(img['old_path']).name
                        new_img = published_bundle / img['new_name']
                        if old_img.exists() and old_img != new_img:
                            old_img.replace(new_img)
                    self.log(f"✓ Renamed {len(image_renames)} images in bundle", force=True)
                
                self.log(f"✓ File already in published/ - regenerated output files", force=True)
        else:
            if not is_already_published:
                self.log(f"[DRY RUN] Would create bundle: {published_bundle}/", force=True)
    
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
        
        # Parse content
        content = draft_path.read_text(encoding='utf-8')
        front_matter, body, extracted_title = FrontmatterParser.parse(content)
        
        # Get suggestions
        suggestions = self.get_post_suggestions()
        
        # Determine if we need interactive input
        needs_interactive = self._needs_interactive_input(front_matter)
        
        # Collect or validate frontmatter
        if needs_interactive:
            if self.dry_run:
                raise ValueError("Missing frontmatter in dry-run mode")
            
            front_matter = self.collect_frontmatter(
                existing=front_matter,
                extracted_title=extracted_title,
                suggestions=suggestions
            )
            
            # Write frontmatter back to source
            content = FrontmatterParser.create_markdown(front_matter, body)
            draft_path.write_text(content, encoding='utf-8')
            self.log(f"✓ Added frontmatter to {draft_path.name}", force=True)
        else:
            front_matter = FrontmatterValidator.ensure_complete(front_matter)
        
        # Review and confirm loop
        front_matter = self._review_and_confirm_loop(front_matter, body, extracted_title, suggestions)
        
        # Generate and publish
        post_slug = self.generate_slug(front_matter['title'], front_matter['date'])
        self._publish_content(draft_path, post_slug, front_matter, body, content)
        
        # Git operations
        if not self.dry_run:
            self.git.commit_and_push(post_slug, front_matter['title'])
            
            print(f"\n{'='*60}")
            print("Next steps:")
            print(f"  1. Preview: hugo server -D")
            print(f"  2. Visit: http://localhost:1313/")
            print(f"{'='*60}")
    
    def _needs_interactive_input(self, front_matter):
        """Check if interactive frontmatter collection is needed"""
        if front_matter is None:
            self.log("ℹ️  No front matter found - will collect interactively", force=True)
            return True
        
        is_valid, missing_fields = FrontmatterValidator.validate(front_matter)
        
        if not is_valid:
            self.log(f"ℹ️  Missing/invalid fields: {', '.join(missing_fields)}", force=True)
            return True
        
        if not self.dry_run:
            self.log("✓ Front matter validated", force=True)
            self.show_frontmatter(front_matter)
            response = input("\nKeep existing frontmatter? (y/n, default: yes): ").strip().lower()
            if response in ['n', 'no']:
                self.log("\nℹ️  Entering interactive mode to edit frontmatter", force=True)
                return True
            self.log("✓ Using existing frontmatter", force=True)
        else:
            self.log("✓ Front matter validated", force=True)
        
        return False
    
    def _review_and_confirm_loop(self, front_matter, body, extracted_title, suggestions):
        """Handle review and confirmation with edit/preview options"""
        while True:
            self.show_frontmatter(front_matter)
            if self.dry_run:
                break
            
            response = self.confirm_action()
            if response == 'yes':
                break
            elif response == 'no':
                print("\n❌ Publishing cancelled by user")
                sys.exit(0)
            elif response == 'edit':
                front_matter = self.collect_frontmatter(
                    existing=front_matter,
                    extracted_title=extracted_title,
                    suggestions=suggestions
                )
                front_matter['type'] = 'blog'
            elif response == 'preview':
                self.preview_content(front_matter, body)
        
        return front_matter
    
    def _publish_content(self, draft_path, post_slug, front_matter, body, original_content):
        """Publish content to Hugo and handle source files"""
        self.log(f"✓ Generated bundle: {post_slug}/", force=True)
        
        # Create bundle
        post_bundle_dir = self.content_dir / post_slug
        if not self.dry_run:
            post_bundle_dir.mkdir(parents=True, exist_ok=True)
        
        # Process images
        is_already_published = "published" in draft_path.parts
        updated_body, image_count, image_renames = self.process_images(
            draft_path.parent, body, post_slug, post_bundle_dir, is_already_published
        )
        
        # Write Hugo content
        hugo_content = FrontmatterParser.create_markdown(front_matter, updated_body)
        
        if not self.dry_run:
            (post_bundle_dir / "index.md").write_text(hugo_content, encoding='utf-8')
            self.log(f"✓ Created: content/blog/{post_slug}/index.md", force=True)
        else:
            self.log(f"[DRY RUN] Would create: content/blog/{post_slug}/index.md", force=True)
        
        # Handle source file
        self.handle_source_file(draft_path, post_slug, original_content, image_renames, is_already_published)
        
        # Summary
        self._print_summary(post_slug, image_count)
    
    def _print_summary(self, post_slug, image_count):
        """Print publishing summary"""
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
