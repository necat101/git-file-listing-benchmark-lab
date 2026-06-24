# Git File Listing Benchmark Results

Generated: 2026-06-24T19:55:02.630237

## Test Environment
- **OS**: Linux 6.17.0-1009-aws x86_64
- **Python**: 3.12.3
- **Tools**: git 2.43.0, find (GNU findutils 4.9.0), ripgrep 13.0.0
- **Corpus**: 4 test repositories with corrected file counts

## Results

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

## Key Findings

### Performance Comparison
- **git ls-files is 2-8x faster** than filesystem walkers
- **Large repo (2000 files)**: git ls-files 14.8ms vs find 82.8ms (**5.6x faster**)
- **Medium repo (500 files)**: git ls-files 10.7ms vs find 86.8ms (**8.1x faster**)
- Performance advantage holds across all repo sizes

### Why git ls-files is Faster
1. **Reads pre-computed index** (`.git/index`) - O(1) operation
2. **No directory traversal** - index contains flat file list
3. **No syscalls per file** - single sequential read vs thousands of `stat()` calls
4. **No filesystem cache misses** - index file is small and likely cached

### Correctness Notes
File counts differ because tools answer different questions:
- `git ls-files`: Files tracked by Git
- `git ls-files --cached --others --exclude-standard`: Tracked + untracked, respecting .gitignore
- `find`: All files on filesystem (excluding .git)
- `rg --files`: Respects .gitignore by default, may exclude files

### Bug Fix
**Previous version** had a bug where large repo created only 100 files instead of 2000 due to directory name collision (`dir_{i//20}` reused same 10 directories). **Fixed in current version** - now correctly creates 200 directories with 10 files each = 2000 files.

## Verification
- ✅ Python files compile: `python3 -m py_compile generate_corpus.py benchmark.py`
- ✅ Corpus generates correctly with expected file counts
- ✅ All tools run successfully and produce output
- ✅ Results are reproducible across multiple runs (3 trials each)

## Limitations
This benchmark tests **warm cache** performance only. Cold cache behavior (first run after boot) would show different characteristics, with filesystem walkers penalized more heavily due to disk I/O.
