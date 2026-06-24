#!/usr/bin/env python3
"""
Git File Listing Benchmark Lab - Corpus Generator
Generates reproducible git repositories with various file scenarios.
"""

import os
import subprocess
import random
from pathlib import Path

def run_cmd(cmd, cwd=None):
    """Run shell command"""
    result = subprocess.run(
        cmd, shell=True, cwd=cwd,
        capture_output=True, text=True
    )
    return result.returncode == 0, result.stdout, result.stderr

def generate_corpus(base_dir="corpus"):
    """Generate test git repositories"""
    base = Path(base_dir)
    base.mkdir(exist_ok=True)
    
    print("Generating git file listing benchmark corpus...")
    
    # Small repo
    print("\n1. Small repo (50 files)")
    small_dir = base / "small"
    small_dir.mkdir(exist_ok=True)
    run_cmd("git init", cwd=small_dir)
    run_cmd("git config user.email 'test@example.com'", cwd=small_dir)
    run_cmd("git config user.name 'Test'", cwd=small_dir)
    
    # Create files
    for i in range(30):
        (small_dir / f"file_{i:03d}.txt").write_text(f"Content {i}\n")
    
    # Create nested dirs
    (small_dir / "src").mkdir(exist_ok=True)
    for i in range(10):
        (small_dir / "src" / f"module_{i}.py").write_text(f"# Module {i}\n")
    
    (small_dir / "docs").mkdir(exist_ok=True)
    for i in range(10):
        (small_dir / "docs" / f"doc_{i}.md").write_text(f"# Doc {i}\n")
    
    run_cmd("git add .", cwd=small_dir)
    run_cmd("git commit -m 'Initial commit'", cwd=small_dir)
    
    # Add untracked files
    (small_dir / "untracked.txt").write_text("untracked\n")
    (small_dir / "build.log").write_text("build output\n")
    
    # Create .gitignore
    (small_dir / ".gitignore").write_text("*.log\nbuild/\n")
    run_cmd("git add .gitignore && git commit -m 'Add gitignore'", cwd=small_dir)
    
    # Medium repo
    print("\n2. Medium repo (500 files)")
    med_dir = base / "medium"
    med_dir.mkdir(exist_ok=True)
    run_cmd("git init", cwd=med_dir)
    run_cmd("git config user.email 'test@example.com'", cwd=med_dir)
    run_cmd("git config user.name 'Test'", cwd=med_dir)
    
    for i in range(100):
        subdir = med_dir / f"pkg_{i//20}"
        subdir.mkdir(exist_ok=True)
        for j in range(5):
            (subdir / f"file_{i}_{j}.txt").write_text(f"Content {i}-{j}\n")
    
    run_cmd("git add . && git commit -m 'Initial'", cwd=med_dir)
    
    # Large repo - FIXED: was creating only 100 files due to dir reuse bug
    print("\n3. Large repo (2000 files)")
    large_dir = base / "large"
    large_dir.mkdir(exist_ok=True)
    run_cmd("git init", cwd=large_dir)
    run_cmd("git config user.email 'test@example.com'", cwd=large_dir)
    run_cmd("git config user.name 'Test'", cwd=large_dir)
    
    for i in range(200):
        subdir = large_dir / f"dir_{i:02d}"
        subdir.mkdir(exist_ok=True)
        for j in range(10):
            (subdir / f"f_{j:02d}.dat").write_text("x" * 100)
    
    run_cmd("git add . && git commit -m 'Initial'", cwd=large_dir)
    
    # Special cases repo
    print("\n4. Special cases repo")
    special_dir = base / "special"
    special_dir.mkdir(exist_ok=True)
    run_cmd("git init", cwd=special_dir)
    run_cmd("git config user.email 'test@example.com'", cwd=special_dir)
    run_cmd("git config user.name 'Test'", cwd=special_dir)
    
    # Unicode filenames
    (special_dir / "café.txt").write_text("unicode\n")
    (special_dir / "naïve.py").write_text("# unicode\n")
    
    # Files with spaces
    (special_dir / "file with spaces.txt").write_text("spaces\n")
    
    # Hidden files
    (special_dir / ".hidden").write_text("hidden\n")
    (special_dir / ".config").mkdir(exist_ok=True)
    (special_dir / ".config" / "settings.json").write_text("{}\n")
    
    # Empty dirs
    (special_dir / "empty1").mkdir(exist_ok=True)
    (special_dir / "empty2").mkdir(exist_ok=True)
    
    run_cmd("git add . && git commit -m 'Initial'", cwd=special_dir)
    
    # Untracked and ignored
    (special_dir / "untracked.tmp").write_text("temp\n")
    (special_dir / ".gitignore").write_text("*.tmp\n")
    
    print(f"\n✓ Corpus generated in '{base_dir}/'")
    for repo in ["small", "medium", "large", "special"]:
        repo_path = base / repo
        if repo_path.exists():
            count = sum(1 for _ in repo_path.rglob("*") if _.is_file())
            print(f"  {repo}: {count} files")

if __name__ == "__main__":
    generate_corpus()
