# Git File Listing Benchmark Lab

A practical comparison of file listing tools, inspired by the [Hacker News discussion](https://news.ycombinator.com/item?id=29298017) on `git ls-files` being faster than `fd` and `find`.

## Quick Start

```bash
python3 generate_corpus.py
python3 benchmark.py
cat RESULTS.md
```

## Tools Compared

- `git ls-files` - Git index lookup
- `find` - Traditional Unix file finder  
- `fd` - Modern Rust alternative
- `rg --files` - Ripgrep file listing

## Key Finding

`git ls-files` is **2-4x faster** than filesystem walkers because it reads a pre-computed index instead of traversing directories.

Repository: https://github.com/necat101/git-file-listing-benchmark-lab
