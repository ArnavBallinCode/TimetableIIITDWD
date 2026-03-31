#!/usr/bin/env python3
"""
Helper to create issues using the GitHub CLI `gh` by importing the ISSUES
list from `docs/create_github_issues.py`.

Usage:
    python docs/create_issues_with_gh.py

This will create each issue in the repository `ArnavBallinCode/TimetableIIITDWD`
using the currently-authenticated `gh` user.
"""

import subprocess
import tempfile
import os
import sys

# Import the ISSUES list from the existing script
sys.path.insert(0, os.path.dirname(__file__))
try:
    import create_github_issues as cg
except Exception as exc:
    print("Failed to import docs/create_github_issues.py:", exc)
    sys.exit(2)

REPO = "ArnavBallinCode/TimetableIIITDWD"

created = []
for i, issue in enumerate(cg.ISSUES, start=1):
    title = issue.get("title", "(no title)")
    body = issue.get("body", "")
    print(f"[{i}/{len(cg.ISSUES)}] Creating: {title}")
    # Write body to a temp file and pass via --body-file to avoid quoting issues
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".md") as tf:
        tf.write(body)
        tf.flush()
        tfname = tf.name
    cmd = [
        "gh",
        "issue",
        "create",
        "--repo",
        REPO,
        "--title",
        title,
        "--body-file",
        tfname,
    ]
    try:
        proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
        if proc.returncode == 0:
            # gh prints the URL of the created issue to stdout
            url = proc.stdout.strip()
            print(f"  Created: {url}")
            created.append(url)
        else:
            print(f"  ERROR (exit {proc.returncode}):", proc.stderr.strip())
    except FileNotFoundError:
        print("ERROR: `gh` CLI not found in PATH.")
        os.unlink(tfname)
        sys.exit(3)
    finally:
        try:
            os.unlink(tfname)
        except Exception:
            pass

print(f"\nDone. Created {len(created)}/{len(cg.ISSUES)} issues.")
for u in created:
    print("  ", u)
