# Git File Listing Benchmark Results

Generated: 2026-06-24T19:55:02.630237
Regenerated: 2026-06-24T20:03:00 (after bug fix)

## Test Environment
- **OS**: Linux 6.17.0-1009-aws x86_64
- **Python**: 3.12.3
- **Tools**: git 2.43.0, find (GNU findutils 4.9.0), ripgrep 13.0.0
- **Corpus**: 4 test repositories with CORRECTED file counts

## Results (After Bug Fix)

| Repo | Tool | Mean (ms) | Files | Notes |
|------|------|-----------|-------|-------|
| large | git ls-files | 14.8 | 2000 | Tracked files only - reads index |
| large | git ls-files --cached --others | 33.5 | 2000 | Tracked + untracked, respects .gitignore |
| large | find | 82.8 | 2000 | Walks filesystem, makes syscalls |
| large | rg --files | 78.0 | 2000 | Ripgrep file discovery |
| medium | git ls-files | 10.7 | 500 | Tracked files only |
| medium | git ls-files --cached --others | 11.8 | 500 | Tracked + untracked |
| medium | find | 86.8 | 500 | Filesystem walk |
| medium | rg --files | 21.9 | 500 | Ripgrep file discovery |
| small | git ls-files | 10.3 | 51 | Tracked files only |
| small | git ls-files --cached --others | 10.7 | 52 | Tracked + untracked |
| small | find | 34.6 | 53 | Filesystem walk |
| small | rg --files | 21.4 | 51 | Ripgrep file discovery |
| special | git ls-files | 10.0 | 5 | Tracked files only |
| special | git ls-files --cached --others | 10.6 | 6 | Tracked + untracked |
| special | find | 26.8 | 7 | Filesystem walk |
| special | rg --files | 19.5 | 3 | Ripgrep file discovery |

## Bug Fix Notice

**Previous version** (before commit bcab1b2):
- Large repo incorrectly showed 100 files
- Root cause: Directory name collision in generator (`dir_{i//20}` created only 10 unique dirs)
- Each iteration overwrote files in existing directories

**Fixed version** (current):
- Large repo correctly shows 2000 files
- Fix: Changed to `dir_{i:02d}` to create 200 unique directories
- Verified: `find corpus/large -type f | wc -l` = 2000
- All benchmark data above reflects corrected corpus

## Key Findings

### Performance Comparison
- **git ls-files is 2-8x faster** than filesystem walkers
- **Large repo (2000 files)**: git ls-files 14.8ms vs find 82.8ms (**5.6x faster**)
- **Medium repo (500 files)**: git ls-files 10.7ms vs find 86.8ms (**8.1x faster**)
- Performance advantage holds across all repo sizes
- git ls-files time is nearly constant (~10-15ms) regardless of repo size

### Why git ls-files is Faster
1. **Reads pre-computed index** (`.git/index`) - O(1) operation, ~100KB read
2. **No directory traversal** - index contains flat file list
3. **No syscalls per file** - single sequential read vs thousands of `stat()`/`getdents()` calls
4. **No filesystem cache misses** - index file is small and likely cached

### Correctness Notes
File counts differ because tools answer different questions:
- `git ls-files`: Only files tracked by Git (respects .gitignore for untracked)
- `git ls-files --cached --others --exclude-standard`: Tracked + untracked files, respects .gitignore
- `find`: All files on filesystem (including .git directory unless excluded)
- `rg --files`: Respects .gitignore by default, similar to git but walks filesystem

### Missing Features (Not Yet Implemented)
The following benchmark scenarios from the original specification are **not implemented** in this version:
- ❌ Python `os.walk`/`os.scandir` baseline implementations
- ❌ Extension filtering benchmarks (`*.py`, `*.rs`)
- ❌ Name-pattern filtering (glob patterns)
- ❌ Symlink handling verification
- ❌ Empty directory behavior tests
- ❌ Cold vs warm filesystem cache comparisons
- ❌ `fd` and `hyperfine` integration
- ❌ Sorted-output checksums for correctness verification
- ❌ Detailed inclusion/exclusion analysis for tracked/untracked/ignored/hidden files
- ❌ Unicode filename preservation tests

## Verification
- ✅ Python files compile: `python3 -m py_compile generate_corpus.py benchmark.py`
- ✅ Corpus generates correctly with expected file counts (2000 in large repo)
- ✅ All tools run successfully and produce output
- ✅ Results are reproducible across multiple runs (3 trials each)
- ✅ Bug fix verified and documented

## Conclusion
The benchmark confirms the HN article's claim: `git ls-files` is significantly faster (2-8x) than filesystem walkers when listing files Git knows about. The performance comes from reading a pre-built index rather than traversing the filesystem.

**Important caveat**: This compares different operations. Use `git ls-files` when you want "files Git tracks" and `find`/`fd` when you need "all files on disk." Choose based on your actual requirements, not just speed.
