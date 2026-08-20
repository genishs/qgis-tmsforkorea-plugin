#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a deterministic dev zip file for the QGIS TMS for Korea plugin.
"""
import os
import sys
import zipfile
import argparse

# Constants
SOURCE_DIR = 'tmsforkorea'
OUTPUT_ZIP_NAME = 'tmsforkorea-osm-variants-dev.zip'
ZIP_PREFIX = 'tmsforkorea/'

def should_exclude(filename, dirname):
    """
    Returns (True, reason) if the file/dir should be excluded, else (False, None).
    """
    # Exclude __pycache__ directories
    if filename == '__pycache__' or '__pycache__' in dirname.split(os.sep):
        return True, "matches __pycache__"
    
    # Exclude compiled python files
    if filename.endswith('.pyc'):
        return True, "extension .pyc"
    if filename.endswith('.pyo'):
        return True, "extension .pyo"
    
    # Exclude nested zip files (e.g. tmsforkorea-3.0.5.zip inside plugin folder)
    if filename.endswith('.zip'):
        return True, "extension .zip"
        
    # Exclude git-related files (.gitignore, .gitattributes, etc)
    if filename.startswith('.git'):
        return True, "prefix .git"
        
    # Exclude OS specific files
    if filename in ('.DS_Store', 'Thumbs.db'):
        return True, "OS specific file (.DS_Store / Thumbs.db)"
        
    return False, None

def build_zip(list_only=False):
    output_path = os.path.abspath(OUTPUT_ZIP_NAME)
    
    included_files = []
    excluded_files = []
    
    # Deterministic traversal
    for root, dirs, files in os.walk(SOURCE_DIR):
        dirs.sort()
        files.sort()
        
        for file in files:
            full_path = os.path.join(root, file)
            # determine relative path inside zip
            rel_path = os.path.relpath(full_path, SOURCE_DIR)
            zip_path = ZIP_PREFIX + rel_path.replace(os.sep, '/')
            
            excl, reason = should_exclude(file, root)
            if excl:
                excluded_files.append((zip_path, reason))
            else:
                included_files.append((full_path, zip_path))
                
    if list_only:
        print("List only mode - not building zip.")
        print(f"Would include {len(included_files)} items.")
        return 0
        
    # Create the zip deterministically
    with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for full_path, zip_path in included_files:
            # Fixed timestamp: 1980-01-01 00:00:00
            zinfo = zipfile.ZipInfo(zip_path, (1980, 1, 1, 0, 0, 0))
            # Fixed external_attr: -rw-r--r--
            zinfo.external_attr = 0o644 << 16
            
            with open(full_path, 'rb') as f:
                zf.writestr(zinfo, f.read())
                
    # Output results
    file_size = os.path.getsize(output_path)
    print(f"Built zip: {output_path} ({file_size} bytes)")
    print(f"Included items: {len(included_files)}")
    print(f"Excluded items: {len(excluded_files)}")
    for zpath, reason in excluded_files:
        print(f"  - Excluded: {zpath} ({reason})")
        
    print("\nStarting self-verification...")
    return verify_zip(output_path, len(included_files))

def verify_zip(zip_path, expected_count):
    errors = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            namelist = zf.namelist()
            
            # (a) Check top-level folder
            top_levels = set()
            for name in namelist:
                parts = name.split('/')
                if parts:
                    top_levels.add(parts[0])
            
            if len(top_levels) != 1 or 'tmsforkorea' not in top_levels:
                errors.append(f"Top-level folder check failed. Found: {top_levels}")
            else:
                print("Self-verification (a) Top-level folder 'tmsforkorea/': OK")
                
            # (b) Check exclusion patterns
            exclusion_found = []
            for name in namelist:
                filename = name.split('/')[-1]
                dirname = os.path.dirname(name)
                # simulate os.sep for should_exclude which expects system sep sometimes, but we pass the raw filename
                excl, reason = should_exclude(filename, name) 
                if excl:
                    exclusion_found.append((name, reason))
                    
            if exclusion_found:
                errors.append(f"Exclusion check failed. Found excluded items: {exclusion_found}")
            else:
                print("Self-verification (b) Exclusion patterns: OK")
                
            # (c) Item count
            print(f"Self-verification (c) Item count: {len(namelist)} items (Expected: {expected_count}): OK")
            if len(namelist) != expected_count:
                errors.append(f"Item count mismatch: found {len(namelist)}, expected {expected_count}")
                
            # (d) Backslashes
            backslashes = [name for name in namelist if '\\' in name]
            if backslashes:
                errors.append(f"Backslash check failed. Found in: {backslashes}")
            else:
                print("Self-verification (d) No backslashes in paths: OK")
                
    except Exception as e:
        errors.append(f"Exception during verification: {str(e)}")
        
    if errors:
        print("\nVerification FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1
        
    print("\nVerification SUCCESS.")
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Build QGIS plugin zip.")
    parser.add_argument('--list', action='store_true', help="List only, do not build.")
    args = parser.parse_args()
    
    sys.exit(build_zip(list_only=args.list))
