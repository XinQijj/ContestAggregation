# -*- coding: utf-8 -*-
"""同步数据：目录 + GitHub 开源方案 + Devpost 正在报名的黑客松 -> web/data/data.json

用法：
  python scripts/sync.py            # 全量同步（GitHub 未登录约每 7 秒查一个，约 12 分钟）
  python scripts/sync.py --quick    # 只重建目录和黑客松，保留已有的 GitHub 结果
环境变量 GITHUB_TOKEN 可选，配置后更快、更稳定。
只用 Python 标准库。
"""
import sys as _s; _s.stdout.reconfigure(encoding="utf-8", errors="replace")
import json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from catalog import CONTESTS, ROBOT_RELEVANT, HACKATHONS, ROBOT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "web", "data", "data.json")
UA = "ContestAggregation-sync/1.0"
TOKEN = os.environ.get("GITHUB_TOKEN")


def get_json(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def q(s):
    return urllib.parse.quote(s)


def search_links(kw, name):
    return [
        {"site": "B站", "url": f"https://search.bilibili.com/all?keyword={q(kw)}"},
        {"site": "知乎", "url": f"https://www.zhihu.com/search?type=content&q={q(kw)}"},
        {"site": "YouTube", "url": f"https://www.youtube.com/results?search_query={q(kw)}"},
        {"site": "GitHub", "url": f"https://github.com/search?type=repositories&q={q(kw)}"},
        {"site": "CSDN", "url": f"https://so.csdn.net/so/search?q={q(kw)}"},
        {"site": "百度（官网/通知）", "url": f"https://www.baidu.com/s?wd={q(name + ' 2027 报名通知')}"},
    ]


def github_repos(kw):
    # 中文关键词在 GitHub 上命中少，取前两个词
    terms = " ".join(kw.split()[:2])
    url = f"https://api.github.com/search/repositories?q={q(terms)}&sort=stars&order=desc&per_page=6"
    h = {"Accept": "application/vnd.github+json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    data = get_json(url, h)
    return [{"name": it["full_name"], "url": it["html_url"], "stars": it["stargazers_count"],
             "desc": (it.get("description") or "")[:140], "updated": it["pushed_at"][:10]}
            for it in data.get("items", [])]


def devpost():
    out = []
    try:
        for page in (1, 2):
            d = get_json(f"https://devpost.com/api/hackathons?status[]=upcoming&status[]=open&page={page}")
            for h in d.get("hackathons", []):
                out.append({"name": h.get("title"), "url": h.get("url"),
                            "dates": h.get("submission_period_dates"),
                            "org": h.get("organization_name"),
                            "prize": h.get("prize_amount", "").replace("<span data-currency-value>", "").replace("</span>", ""),
                            "online": (h.get("displayed_location") or {}).get("location"),
                            "state": h.get("open_state")})
    except Exception as e:  # noqa: BLE001
        print("devpost 失败:", e)
    return out


def main():
    quick = "--quick" in sys.argv
    old = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            old = {c["id"]: c for c in json.load(f).get("contests", [])}

    contests = []
    for i, (cid, name, dept, url, rs, re_, kw, note) in enumerate(CONTESTS):
        repos = old.get(cid, {}).get("repos", [])
        if not quick:
            try:
                repos = github_repos(kw) or repos
                print(f"[{i+1}/{len(CONTESTS)}] {name}: {len(repos)} repos")
            except Exception as e:  # noqa: BLE001
                print(f"[{i+1}] {name} GitHub 失败: {e}")
            time.sleep(2.2 if TOKEN else 6.5)
        contests.append({
            "id": cid, "tier": 1 if cid.startswith("1-") else 2, "name": name, "dept": dept,
            "url": url, "reg": [rs, re_], "note": note,
            "robot": cid in ROBOT_RELEVANT, "robotDept": ROBOT in dept,
            "links": search_links(kw, name), "repos": repos,
        })

    hk = [{"name": n, "org": o, "url": u, "note": t} for n, o, u, t in HACKATHONS]
    live = devpost()
    if not live and os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            live = json.load(f).get("devpost", [])

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "contests": contests, "hackathons": hk, "devpost": live}, f, ensure_ascii=False, indent=1)
    print("写入", OUT, f"({len(contests)} 个比赛, {len(live)} 个 Devpost 黑客松)")


if __name__ == "__main__":
    main()
