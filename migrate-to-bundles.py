#!/usr/bin/env python3
"""
One-time migration script: Convert blog posts to page bundles
Converts TOML front matter to YAML in the process
"""

import re
from pathlib import Path


def dict_to_yaml(data):
    """Convert dict to simple YAML string"""
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        elif isinstance(value, bool):
            lines.append(f"{key}: {str(value).lower()}")
        elif isinstance(value, str):
            # Quote if contains special chars
            if ':' in value or value.startswith('-'):
                lines.append(f'{key}: "{value}"')
            else:
                lines.append(f"{key}: {value}")
        else:
            lines.append(f"{key}: {value}")
    return '\n'.join(lines) + '\n'


def toml_to_dict(toml_content):
    """Parse simple TOML front matter to dict"""
    result = {}
    for line in toml_content.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Handle different value types
            if value.startswith('[') and value.endswith(']'):
                # List
                items = value[1:-1].split(',')
                result[key] = [item.strip().strip("'\"") for item in items if item.strip()]
            elif value.startswith("'") or value.startswith('"'):
                # String
                result[key] = value.strip("'\"")
            elif value.lower() in ('true', 'false'):
                # Boolean
                result[key] = value.lower() == 'true'
            elif value.isdigit():
                # Integer
                result[key] = int(value)
            else:
                # Default to string
                result[key] = value.strip("'\"")
    
    return result


def convert_front_matter(content):
    """Convert TOML or YAML front matter to YAML, return (front_matter_dict, body)"""
    # Try TOML format (+++...+++)
    toml_match = re.match(r'^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n(.*)$', content, re.DOTALL)
    if toml_match:
        toml_content = toml_match.group(1)
        body = toml_match.group(2)
        front_matter = toml_to_dict(toml_content)
        return front_matter, body
    
    # Try YAML format (---...---)
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if yaml_match:
        # Already YAML, parse it simply
        yaml_content = yaml_match.group(1)
        body = yaml_match.group(2)
        # Simple YAML parsing for our needs
        front_matter = {}
        current_list_key = None
        for line in yaml_content.split('\n'):
            line = line.rstrip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('  - '):
                # List item
                if current_list_key:
                    front_matter[current_list_key].append(line[4:].strip().strip('"\''))
            elif ': ' in line:
                key, value = line.split(': ', 1)
                key = key.strip()
                value = value.strip()
                if not value:
                    # Start of a list
                    front_matter[key] = []
                    current_list_key = key
                else:
                    current_list_key = None
                    # Parse value
                    if value.startswith('"') or value.startswith("'"):
                        front_matter[key] = value.strip('"\'')
                    elif value.lower() in ('true', 'false'):
                        front_matter[key] = value.lower() == 'true'
                    elif value.isdigit():
                        front_matter[key] = int(value)
                    else:
                        front_matter[key] = value
        return front_matter, body
    
    raise ValueError("Could not parse front matter")


def migrate_post(md_file):
    """Convert a single .md file to page bundle"""
    print(f"Migrating: {md_file.name}")
    
    # Read content
    content = md_file.read_text(encoding='utf-8')
    
    # Parse front matter
    front_matter, body = convert_front_matter(content)
    
    # Create bundle folder (remove .md extension)
    bundle_name = md_file.stem
    bundle_dir = md_file.parent / bundle_name
    bundle_dir.mkdir(exist_ok=True)
    
    # Write index.md with YAML front matter
    yaml_fm = dict_to_yaml(front_matter)
    new_content = f"---\n{yaml_fm}---\n{body}"
    
    index_file = bundle_dir / "index.md"
    index_file.write_text(new_content, encoding='utf-8')
    
    # Remove old .md file
    md_file.unlink()
    
    print(f"  ✓ Created: {bundle_name}/index.md")
    print(f"  ✓ Removed: {md_file.name}")


def main():
    content_dir = Path("content/blog")
    
    if not content_dir.exists():
        print("❌ Error: content/blog directory not found")
        print("   Run this script from Hugo root directory")
        return 1
    
    # Find all .md files (not index.md or _index.md)
    md_files = [f for f in content_dir.glob("*.md") if f.name not in ("index.md", "_index.md")]
    
    if not md_files:
        print("No markdown files found to migrate")
        return 0
    
    print(f"Found {len(md_files)} posts to migrate\n")
    
    for md_file in sorted(md_files):
        try:
            migrate_post(md_file)
        except Exception as e:
            print(f"  ❌ Error migrating {md_file.name}: {e}")
            return 1
    
    print(f"\n✅ Successfully migrated {len(md_files)} posts to page bundles")
    print(f"   All posts now use YAML front matter")
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
