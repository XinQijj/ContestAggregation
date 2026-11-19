# 复旦机器人学院 · 竞赛速递

依据《复旦大学高水平学科竞赛目录（2026年7月更新）》整理的竞赛信息站，94 项比赛 + 大公司黑客松。

- **按加分等级**（`index.html`）：一类 / 二类分组，可只看机器人学院相关
- **按报名时间**（`timeline.html`）：“现在正在报名”置顶，其余按距开放报名的月数排序
- 点开比赛：官网、B站 / 知乎 / YouTube / GitHub / CSDN 经验搜索跳转，以及自动同步的 GitHub 开源方案（按 Star 排序）
- 页面底部：大公司黑客松 + Devpost 正在报名的黑客松（实时同步）

只依赖 Python 标准库。

## 运行

```bash
python serve.py          # 打开 http://127.0.0.1:8770，后台每 12 小时同步一次
python scripts/sync.py   # 手动全量同步（约 10 分钟；设 GITHUB_TOKEN 可加速）
python scripts/sync.py --quick   # 只更新目录和黑客松
```

## 上线（免服务器）

推到 GitHub 仓库，Settings → Pages → Source 选 “GitHub Actions”。`.github/workflows/sync.yml` 会每天自动同步并重新部署。

## 维护

- 改比赛、报名月份、官网：编辑 `scripts/catalog.py`，再运行 `sync.py`
- 报名月份是按往年整理的大致窗口，**每年会变**，建议学院同学每学期校对一次
