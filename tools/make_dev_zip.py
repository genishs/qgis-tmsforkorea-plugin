#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the installable dev zip for the QGIS "TMS for Korea" plugin.

Why this exists
---------------
The dev zip used to be assembled by hand, so junk kept leaking into it:
``__pycache__`` trees, ``.pyc`` files, and — worst — a 443 KB copy of the old
``tmsforkorea-3.0.5.zip`` nested inside the plugin folder. This script makes
the contents a function of explicit include/exclude rules instead of whatever
happened to be sitting in the working tree.

Guarantees
----------
* Single top-level folder ``tmsforkorea/`` — what QGIS's
  "Install from ZIP" expects.
* Deterministic: sorted traversal, fixed timestamps and permission bits, so
  the same source tree yields a byte-identical zip.
* Self-verifying: the finished zip is reopened and re-checked, and any failed
  check makes the process exit non-zero.

Usage
-----
    python tools/make_dev_zip.py            # build + verify
    python tools/make_dev_zip.py --list     # show the file list, build nothing
"""
import argparse
import os
import sys
import zipfile

# Anchor everything to the repo root derived from this file's location, not to
# the caller's cwd — otherwise running the script from tools/ silently builds
# from the wrong place.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(REPO_ROOT, 'tmsforkorea')
DEFAULT_OUTPUT = os.path.join(REPO_ROOT, 'tmsforkorea-osm-variants-dev.zip')
ZIP_PREFIX = 'tmsforkorea/'

# Directory names dropped wholesale, together with everything beneath them.
EXCLUDED_DIR_NAMES = (
    '__pycache__',   # CPython bytecode cache; machine-specific, never shipped
)

# File-name rules. Each entry is (predicate, human-readable reason).
EXCLUDED_FILE_RULES = (
    (lambda n: n.endswith('.pyc'), 'compiled bytecode (.pyc)'),
    (lambda n: n.endswith('.pyo'), 'optimised bytecode (.pyo)'),
    # A nested zip inside the plugin folder would ship a stale duplicate of the
    # whole plugin (tmsforkorea/tmsforkorea-3.0.5.zip, 443 KB) inside the new
    # release. QGIS does not need it and it quadrupled the download.
    (lambda n: n.endswith('.zip'), 'nested archive (.zip)'),
    # .gitignore / .gitattributes / .gitkeep — VCS metadata, not plugin content.
    (lambda n: n.startswith('.git'), 'VCS metadata (.git*)'),
    (lambda n: n in ('.DS_Store', 'Thumbs.db'), 'OS metadata'),
)

# Fixed zip metadata, so two builds of the same tree are byte-identical.
FIXED_DATE_TIME = (1980, 1, 1, 0, 0, 0)
FIXED_EXTERNAL_ATTR = 0o644 << 16


def file_exclusion_reason(name):
    """Return why *name* (a bare file name) is excluded, or None to keep it."""
    for predicate, reason in EXCLUDED_FILE_RULES:
        if predicate(name):
            return reason
    return None


def collect():
    """Walk the source tree and return (included, excluded).

    ``included`` is a list of (absolute_path, zip_path); ``excluded`` is a list
    of (zip_path, reason). Both are sorted, so the result does not depend on
    filesystem ordering.
    """
    included = []
    excluded = []

    for root, dirnames, filenames in os.walk(SOURCE_DIR):
        dirnames.sort()
        filenames.sort()

        # Prune excluded directories in place so os.walk does not descend into
        # them; record each one so the report says what was dropped and why.
        kept_dirs = []
        for dirname in dirnames:
            if dirname in EXCLUDED_DIR_NAMES:
                rel = os.path.relpath(os.path.join(root, dirname), SOURCE_DIR)
                excluded.append((ZIP_PREFIX + rel.replace(os.sep, '/') + '/',
                                 'excluded directory (%s)' % dirname))
            else:
                kept_dirs.append(dirname)
        dirnames[:] = kept_dirs

        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel = os.path.relpath(full_path, SOURCE_DIR)
            # Zip entries always use forward slashes, on every platform.
            zip_path = ZIP_PREFIX + rel.replace(os.sep, '/')

            reason = file_exclusion_reason(filename)
            if reason:
                excluded.append((zip_path, reason))
            else:
                included.append((full_path, zip_path))

    included.sort(key=lambda pair: pair[1])
    excluded.sort()
    return included, excluded


def build(output_path, included):
    with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for full_path, zip_path in included:
            info = zipfile.ZipInfo(zip_path, FIXED_DATE_TIME)
            # writestr() honours the ZipInfo's compress_type, NOT the
            # ZipFile's `compression` argument. Leaving it at the ZipInfo
            # default (ZIP_STORED) silently ships an uncompressed archive.
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = FIXED_EXTERNAL_ATTR
            # Fix the creating-system byte too, so Windows and Linux builds of
            # the same tree agree byte for byte.
            info.create_system = 3  # Unix
            with open(full_path, 'rb') as handle:
                zf.writestr(info, handle.read())


def verify(output_path, expected_count):
    """Reopen the finished zip and re-check it. Returns a list of failures."""
    failures = []
    with zipfile.ZipFile(output_path, 'r') as zf:
        names = zf.namelist()
        infos = zf.infolist()

    # (a) exactly one top-level folder, named tmsforkorea
    top_levels = sorted({name.split('/')[0] for name in names})
    if top_levels == ['tmsforkorea']:
        print("  (a) single top-level folder 'tmsforkorea/' : OK")
    else:
        print("  (a) single top-level folder 'tmsforkorea/' : FAIL")
        failures.append('expected exactly one top-level folder '
                        "'tmsforkorea', found %s" % top_levels)

    # (b) no forbidden pattern survived.
    #
    # These literals are deliberately NOT the EXCLUDED_* constants used to
    # build. Re-using the build rules here would make the check tautological:
    # if a rule were wrong or accidentally disabled, the builder would ship the
    # junk and the verifier would use the same broken rule to declare it clean.
    # An independent restatement of "what must never ship" is the whole point
    # of verifying, so keep these spelled out literally.
    #
    # Split on '/', not os.sep — these are zip paths. Splitting on os.sep would
    # never match a directory separator on Windows and the check would pass
    # vacuously.
    leaked = []
    for name in names:
        parts = name.split('/')
        base = parts[-1]
        if '__pycache__' in parts[:-1] or base == '__pycache__':
            leaked.append((name, 'bytecode cache directory'))
        elif base.endswith(('.pyc', '.pyo')):
            leaked.append((name, 'compiled bytecode'))
        elif base.endswith('.zip'):
            leaked.append((name, 'nested archive'))
        elif base.startswith('.git'):
            leaked.append((name, 'VCS metadata'))
        elif base in ('.DS_Store', 'Thumbs.db'):
            leaked.append((name, 'OS metadata'))
    if not leaked:
        print("  (b) no excluded pattern present            : OK")
    else:
        print("  (b) no excluded pattern present            : FAIL")
        for name, reason in leaked:
            failures.append('excluded item present: %s (%s)' % (name, reason))

    # (c) item count matches what we intended to write
    if len(names) == expected_count:
        print("  (c) item count %d == intended %d           : OK"
              % (len(names), expected_count))
    else:
        print("  (c) item count %d != intended %d           : FAIL"
              % (len(names), expected_count))
        failures.append('item count %d does not match intended %d'
                        % (len(names), expected_count))

    # (d) no backslashes in entry names
    backslashed = [name for name in names if '\\' in name]
    if not backslashed:
        print("  (d) no backslashes in entry names          : OK")
    else:
        print("  (d) no backslashes in entry names          : FAIL")
        failures.append('backslash in entry names: %s' % backslashed)

    # (e) everything is actually deflated. A stored-only archive still installs
    # but is ~4x the size, which is how the hand-made zips got so heavy.
    stored = [i.filename for i in infos if i.compress_type != zipfile.ZIP_DEFLATED]
    if not stored:
        print("  (e) all entries DEFLATE-compressed         : OK")
    else:
        print("  (e) all entries DEFLATE-compressed         : FAIL")
        failures.append('%d entries not deflated, e.g. %s'
                        % (len(stored), stored[:3]))

    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument('--list', action='store_true',
                        help='print the resolved file list and exit without building')
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT,
                        help='output zip path (default: %s)' % DEFAULT_OUTPUT)
    args = parser.parse_args()

    if not os.path.isdir(SOURCE_DIR):
        sys.stderr.write('ERROR: source directory not found: %s\n' % SOURCE_DIR)
        return 2

    included, excluded = collect()

    if args.list:
        print('Would include %d item(s):' % len(included))
        for _, zip_path in included:
            print('  %s' % zip_path)
        print('\nWould exclude %d item(s):' % len(excluded))
        for zip_path, reason in excluded:
            print('  %s  (%s)' % (zip_path, reason))
        return 0

    build(args.output, included)

    size = os.path.getsize(args.output)
    print('Built  : %s (%d bytes)' % (args.output, size))
    print('Included: %d item(s)' % len(included))
    print('Excluded: %d item(s)' % len(excluded))
    for zip_path, reason in excluded:
        print('  - %s  (%s)' % (zip_path, reason))

    print('\nSelf-verification:')
    failures = verify(args.output, len(included))
    if failures:
        print('\nVERIFICATION FAILED:')
        for failure in failures:
            print('  - %s' % failure)
        return 1

    print('\nVERIFICATION PASSED.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
