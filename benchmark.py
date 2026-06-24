#!/usr/bin/env python3
"""
Git File Listing Benchmark Lab
Compares git ls-files, find, fd, rg --files, and Python implementations.
"""

import subprocess
import time
import statistics
from pathlib import Path
from datetime import datetime

class ToolAvailability:
    def __init__(self):
        self.tools = {}
        self.check_tools()
    
    def check_tools(self):
        tools = {
            'git': ['git', '--version'],
            'find': ['find', '--version'],
            'fd': ['fd', '--version'],
            'rg': ['rg', '--version'],
            'hyperfine': ['hyperfine', '--version'],
        }
        for tool, cmd in tools.items():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                self.tools[tool] = result.returncode == 0
            except:
                self.tools[tool] = False

class BenchmarkRunner:
    def __init__(self, corpus_dir="corpus"):
        self.corpus_dir = Path(corpus_dir)
        self.tools = ToolAvailability()
        self.results = []
    
    def time_cmd(self, cmd, cwd=None, trials=3):
        times = []
        for _ in range(trials):
            start = time.perf_counter()
            result = subprocess.run(
                cmd, shell=True, cwd=cwd,
                capture_output=True, text=True
            )
            end = time.perf_counter()
            times.append(end - start)
        return {
            'mean': statistics.mean(times) * 1000,
            'min': min(times) * 1000,
            'output': result.stdout,
            'count': len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
        }
    
    def benchmark_repo(self, repo_path):
        repo_name = repo_path.name
        print(f"\n{repo_name} repo:")
        results = {'repo': repo_name}
        
        # git ls-files
        if self.tools.tools['git']:
            r = self.time_cmd("git ls-files", cwd=repo_path)
            print(f"  git ls-files: {r['mean']:.1f}ms ({r['count']} files)")
            results['git_ls_files'] = r
        
        # git ls-files with others
        if self.tools.tools['git']:
            r = self.time_cmd("git ls-files --cached --others --exclude-standard", cwd=repo_path)
            print(f"  git ls-files --cached --others: {r['mean']:.1f}ms ({r['count']} files)")
            results['git_ls_files_all'] = r
        
        # find
        if self.tools.tools['find']:
            r = self.time_cmd("find . -type f -not -path '*/.git/*' | sort", cwd=repo_path)
            print(f"  find: {r['mean']:.1f}ms ({r['count']} files)")
            results['find'] = r
        
        # fd
        if self.tools.tools['fd']:
            r = self.time_cmd("fd --type f --hidden --exclude .git | sort", cwd=repo_path)
            print(f"  fd: {r['mean']:.1f}ms ({r['count']} files)")
            results['fd'] = r
        
        # rg --files
        if self.tools.tools['rg']:
            r = self.time_cmd("rg --files | sort", cwd=repo_path)
            print(f"  rg --files: {r['mean']:.1f}ms ({r['count']} files)")
            results['rg'] = r
        
        self.results.append(results)
        return results
    
    def run_all(self):
        print("=" * 60)
        print("Git File Listing Benchmark")
        print("=" * 60)
        
        for repo in sorted(self.corpus_dir.iterdir()):
            if repo.is_dir() and (repo / ".git").exists():
                self.benchmark_repo(repo)
        
        self.save_results()
    
    def save_results(self):
        with open("RESULTS.md", "w") as f:
            f.write("# Git File Listing Benchmark Results\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write("## Results\n\n")
            f.write("| Repo | Tool | Mean (ms) | Files |\n")
            f.write("|------|------|-----------|-------|\n")
            for r in self.results:
                repo = r['repo']
                for tool in ['git_ls_files', 'git_ls_files_all', 'find', 'fd', 'rg']:
                    if tool in r:
                        f.write(f"| {repo} | {tool} | {r[tool]['mean']:.1f} | {r[tool]['count']} |\n")
        print("\n✓ Results saved to RESULTS.md")

if __name__ == "__main__":
    runner = BenchmarkRunner()
    runner.run_all()
