#!/usr/bin/env python3
"""Git_Glimpse — one-command GitHub repo snapshot.

Zero dependencies, pure Python stdlib. Stars, forks, top languages,
last commit, open issues, license — all in one glance.
"""
from __future__ import annotations
import argparse, json, sys, urllib.request, urllib.error
from datetime import datetime

API = "https://api.github.com"
HEADERS = {"User-Agent": "git-glimpse/1.0", "Accept": "application/vnd.github+json"}

def _get(path: str) -> dict:
    req = urllib.request.Request(f"{API}{path}", headers=HEADERS)
    return json.loads(urllib.request.urlopen(req).read())

def _lang_color(lang: str) -> str:
    colors = {"Python": "🔵", "JavaScript": "🟡", "TypeScript": "🔷",
              "Rust": "🟤", "Go": "🩵", "Java": "🟠", "C++": "🩷",
              "Ruby": "🔴", "Shell": "⚫", "HTML": "🟧", "CSS": "🟪"}
    return colors.get(lang, "⚪")

def _fmt_date(s: str) -> str:
    try:
        dt = datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%b %d, %Y")
    except Exception:
        return s[:10] if s else "—"

def cmd_snapshot(args):
    """Full snapshot of a GitHub repo."""
    owner, repo = args.repo.split("/")
    try:
        r = _get(f"/repos/{owner}/{repo}")
        langs = _get(f"/repos/{owner}/{repo}/languages")
        commits = _get(f"/repos/{owner}/{repo}/commits?per_page=1")
    except urllib.error.HTTPError as e:
        _error(f"Repo not found or rate limited: {e.code}")
        return 1
    
    total_bytes = sum(langs.values())
    top_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:3]
    
    if args.format == "json":
        out = {
            "name": r.get("full_name"),
            "description": r.get("description"),
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "watchers": r.get("subscribers_count", 0),
            "open_issues": r.get("open_issues_count", 0),
            "license": r.get("license", {}).get("spdx_id", "None"),
            "language": r.get("language"),
            "languages": {k: round(v/total_bytes*100, 1) for k, v in top_langs},
            "last_commit": commits[0]["commit"]["author"]["date"] if commits else None,
            "last_commit_msg": commits[0]["commit"]["message"].split("\n")[0] if commits else None,
            "created": r.get("created_at"),
            "updated": r.get("updated_at"),
            "size_kb": r.get("size", 0),
            "default_branch": r.get("default_branch"),
            "topics": r.get("topics", []),
        }
        json.dump(out, sys.stdout, indent=2)
        print()
        return 0
    
    last_commit = commits[0] if commits else None
    stars = r.get("stargazers_count", 0)
    forks = r.get("forks_count", 0)
    issues = r.get("open_issues_count", 0)
    lic = r.get("license", {})
    
    print(f"\n  📦 {owner}/{repo}")
    print(f"  {'─'*50}")
    if r.get("description"):
        print(f"  {r['description']}")
    print(f"  ⭐ {stars:,}  │  🍴 {forks:,}  │  👁 {r.get('subscribers_count', 0):,}  │  🐛 {issues:,} issues")
    if top_langs:
        lang_str = "  │  ".join(f"{_lang_color(l)} {l} {v/total_bytes*100:.0f}%" for l, v in top_langs)
        print(f"  {lang_str}")
    if lic:
        print(f"  📜 {lic.get('spdx_id', lic.get('name', 'Unknown'))}")
    if last_commit:
        msg = last_commit["commit"]["message"].split("\n")[0]
        date = last_commit["commit"]["author"]["date"]
        print(f"  🕐 Last commit: {_fmt_date(date)} — {msg[:60]}")
    print(f"  📅 Created: {_fmt_date(r.get('created_at', ''))}  │  Updated: {_fmt_date(r.get('updated_at', ''))}")
    print(f"  🌿 Branch: {r.get('default_branch', 'main')}  │  📏 {r.get('size', 0)} KB")
    if r.get("topics"):
        print(f"  🏷  {' · '.join(r['topics'][:8])}")
    print(f"  🔗 https://github.com/{owner}/{repo}")
    print()

def cmd_stats(args):
    """Numeric stats only."""
    owner, repo = args.repo.split("/")
    try:
        r = _get(f"/repos/{owner}/{repo}")
    except urllib.error.HTTPError as e:
        _error(f"Repo not found: {e.code}")
        return 1
    
    if args.format == "json":
        json.dump({
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "open_issues": r.get("open_issues_count", 0),
            "watchers": r.get("subscribers_count", 0),
        }, sys.stdout, indent=2)
        print()
    else:
        print(f"{r.get('stargazers_count',0):>6} ⭐  "
              f"{r.get('forks_count',0):>5} 🍴  "
              f"{r.get('open_issues_count',0):>5} 🐛  "
              f"{r.get('subscribers_count',0):>4} 👁  "
              f"{owner}/{repo}")

def cmd_compare(args):
    """Side-by-side comparison of multiple repos."""
    repos_data = []
    for repo_path in args.repos:
        try:
            owner, repo = repo_path.split("/")
            r = _get(f"/repos/{owner}/{repo}")
            repos_data.append({
                "name": repo_path,
                "stars": r.get("stargazers_count", 0),
                "forks": r.get("forks_count", 0),
                "issues": r.get("open_issues_count", 0),
                "lang": r.get("language", "?"),
                "license": (r.get("license") or {}).get("spdx_id", "—"),
                "desc": (r.get("description") or "")[:40],
            })
        except Exception as e:
            repos_data.append({"name": repo_path, "stars": "ERR", "forks": "ERR",
                              "issues": "ERR", "lang": "?", "license": "—", "desc": str(e)[:40]})
    
    if args.format == "json":
        json.dump(repos_data, sys.stdout, indent=2)
        print()
        return 0
    
    print(f"\n  {'Repo':<30} {'⭐ Stars':>8} {'🍴 Forks':>8} {'🐛 Issues':>8} {'Lang':>6} {'License':>12}")
    print(f"  {'─'*30} {'─'*8} {'─'*8} {'─'*8} {'─'*6} {'─'*12}")
    for r in repos_data:
        print(f"  {r['name']:<30} {str(r['stars']):>8} {str(r['forks']):>8} "
              f"{str(r['issues']):>8} {r['lang']:>6} {r['license']:>12}")
    print()

def _error(msg: str):
    print(f"  ❌ {msg}", file=sys.stderr)

def build_parser():
    p = argparse.ArgumentParser(prog="git_glimpse", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--format", choices=["text","json"], default="text")
    
    sub = p.add_subparsers(dest="cmd", required=True)
    
    sn = sub.add_parser("snapshot", parents=[common], help="Full repo snapshot")
    sn.add_argument("repo", help="owner/repo (e.g. 'torvalds/linux')")
    sn.set_defaults(func=cmd_snapshot)
    
    st = sub.add_parser("stats", parents=[common], help="Numeric stats only")
    st.add_argument("repo")
    st.set_defaults(func=cmd_stats)
    
    cp = sub.add_parser("compare", parents=[common], help="Compare multiple repos")
    cp.add_argument("repos", nargs="+", help="owner/repo [owner/repo ...]")
    cp.set_defaults(func=cmd_compare)
    
    return p

def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
