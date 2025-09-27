#!/usr/bin/env python3
"""
Fix encoding issues in FADO CRM codebase
"""

import os
import re
from pathlib import Path

def fix_file_encoding(file_path):
    """Fix encoding issues in a single file"""
    try:
        # Try to read with various encodings
        content = None
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"Successfully read {file_path} with {encoding}")
                break
            except UnicodeDecodeError:
                continue

        if content is None:
            print(f"ERROR: Could not decode {file_path}")
            return False

        # Replace problematic Vietnamese characters with ASCII equivalents
        replacements = {
            # Common Vietnamese characters that cause issues
            'ã': 'a', 'á': 'a', 'à': 'a', 'ả': 'a', 'ạ': 'a',
            'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
            'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
            'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
            'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
            'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
            'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
            'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
            'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
            'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
            'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
            'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
            'đ': 'd', 'Đ': 'D',
        }

        # Apply replacements
        for vietnamese, ascii_char in replacements.items():
            content = content.replace(vietnamese, ascii_char)

        # Fix common broken character sequences
        content = re.sub(r'[^\x00-\x7F]+', ' ', content)  # Remove non-ASCII
        content = re.sub(r'\s+', ' ', content)  # Normalize spaces

        # Write back as UTF-8
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Fixed encoding in {file_path}")
        return True

    except Exception as e:
        print(f"ERROR fixing {file_path}: {e}")
        return False

def main():
    """Fix encoding in all Python files"""
    backend_dir = Path("backend")

    if not backend_dir.exists():
        print("ERROR: Backend directory not found!")
        return

    python_files = list(backend_dir.rglob("*.py"))
    print(f"Found {len(python_files)} Python files")

    fixed_count = 0
    for file_path in python_files:
        if fix_file_encoding(file_path):
            fixed_count += 1

    print(f"\nFixed {fixed_count}/{len(python_files)} files")
    print("Encoding fix complete!")

if __name__ == "__main__":
    main()