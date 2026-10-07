# Git_Glimpse 📦

[![CI](https://github.com/realMNohgee/Git_Glimpse/actions/workflows/smoke.yml/badge.svg)](https://github.com/realMNohgee/Git_Glimpse/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)

**A one-command GitHub repo snapshot.** Stars, forks, watchers, open issues, top languages, license, last commit, and repo age — all in one glance, straight from the public GitHub REST API. Zero dependencies, pure Python stdlib, no API token required.

## Why it exists

Checking a repo usually means clicking through a GitHub page or scraping several API endpoints by hand. Git_Glimpse collapses the questions you actually ask — how popular is it, how active is it, what language is it, what license, when was it last touched — into a single command with a clean terminal report or machine-readable JSON.

## Install

```bash
git clone git@github.com:realMNohgee/Git_Glimpse.git
cd Git_Glimpse
python3 git_glimpse.py --help
```

Python 3.8+ standard library only. Nothing to pip install. Uses the public GitHub API; unauthenticated requests are rate-limited to 60/hour.

## Quick start

```bash
python3 git_glimpse.py snapshot realMNohgee/Ghost_Writer
```

```
📦 realMNohgee/Ghost_Writer
  ──────────────────────────────────────────────────
  Fingerprints a person's writing style from any text corpus into a reusable voice profile (word habits, sentence rhythm, signature phrases) plus a plain-English style brief. Deterministic stats, no AI.
  ⭐ 0  │  🍴 0  │  👁 0  │  🐛 0 issues
  🔵 Python 100%
  📜 MIT
  🕐 Last commit: Oct 07, 2026 — v2: add audit, ghostwrite, simulate + CI smoke test
  📅 Created: Sep 10, 2026  │  Updated: Oct 07, 2026
  🌿 Branch: main  │  📏 47 KB
  🔗 https://github.com/realMNohgee/Ghost_Writer
```

### Machine-readable output

`--format json` on any subcommand emits JSON instead of the pretty report:

```bash
python3 git_glimpse.py stats realMNohgee/Ghost_Writer --format json
```

```json
{
  "stars": 0,
  "forks": 0,
  "open_issues": 0,
  "watchers": 0
}
```

### Compare several repos side by side

```bash
python3 git_glimpse.py compare realMNohgee/Ghost_Writer realMNohgee/Poly_Watch realMNohgee/RepForge
```

```
  Repo                            ⭐ Stars  🍴 Forks 🐛 Issues   Lang      License
  ────────────────────────────── ──────── ──────── ──────── ────── ────────────
  realMNohgee/Ghost_Writer              0        0        0 Python          MIT
  realMNohgee/Poly_Watch                0        0        0   HTML          MIT
  realMNohgee/RepForge                  0        0        0 Python          MIT
```

## Subcommands

| Command | What it does |
|---|---|
| `snapshot REPO` | Full snapshot: stars, forks, watchers, issues, languages, license, last commit, dates, topics, size |
| `stats REPO` | Just the four counters (stars, forks, open issues, watchers) |
| `compare REPO [REPO ...]` | Side-by-side table of several repos |

All subcommands accept `--format {text,json}`.

## Error handling

A missing repo or a rate-limited request exits non-zero with a clear message:

```bash
python3 git_glimpse.py snapshot owner/does-not-exist
# ❌ Repo not found or rate limited: 404        (exit 1)
```

## License

MIT — see [LICENSE](LICENSE).

---

🧰 **[Tool on Hermtica Marketplace](https://hermtica.com/marketplace)**
