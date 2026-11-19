// 共享逻辑：加载数据、卡片、详情弹窗、黑客松
const NOW = new Date();
const MONTH = NOW.getMonth() + 1;
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

function inWindow(m, [s, e]) { return s <= e ? m >= s && m <= e : m >= s || m <= e; }
function monthsUntil(target) { return (target - MONTH + 12) % 12; }
function regStatus(c) {
  if (inWindow(MONTH, c.reg)) {
    const left = monthsUntil(c.reg[1]);
    return { open: true, order: left, label: left === 0 ? "报名中 · 本月截止" : `报名中 · 约 ${left} 个月后截止` };
  }
  const n = monthsUntil(c.reg[0]);
  return { open: false, order: 12 + n, label: n === 1 ? "下月开放报名" : `约 ${n} 个月后开放` };
}
const regText = c => `每年约 ${c.reg[0]} 月 – ${c.reg[1]} 月报名`;

async function loadData() {
  const r = await fetch("data/data.json?ts=" + Date.now());
  const d = await r.json();
  document.getElementById("updated").textContent =
    "数据更新于 " + new Date(d.updated).toLocaleString("zh-CN", { hour12: false });
  return d;
}

function card(c) {
  const st = regStatus(c);
  return `<div class="card" data-id="${c.id}">
    <div class="row"><span class="tag t${c.tier}">${c.tier === 1 ? "一类" : "二类"}</span>
      <span class="no">${c.id}</span>
      ${c.robotDept ? '<span class="tag robot">机器人学院推荐</span>' : c.robot ? '<span class="tag rel">工科相关</span>' : ""}</div>
    <h3>${esc(c.name)}</h3>
    <div class="meta">${esc(c.dept)}</div>
    <div class="meta"><span class="st ${st.open ? "open" : ""}">${st.label}</span> · ${regText(c)}</div>
  </div>`;
}

function bindCards(root, data) {
  root.addEventListener("click", e => {
    const el = e.target.closest(".card[data-id]");
    if (el) openDetail(data.contests.find(c => c.id === el.dataset.id));
  });
}

function openDetail(c) {
  const st = regStatus(c);
  const repos = c.repos.length
    ? c.repos.map(r => `<li><a href="${esc(r.url)}" target="_blank">${esc(r.name)}</a> ★${r.stars}
        <span class="dim">· 更新 ${r.updated}</span><div class="dim">${esc(r.desc)}</div></li>`).join("")
    : '<li class="dim">暂未同步到相关仓库，可点上方 GitHub 搜索。</li>';
  document.getElementById("modal-body").innerHTML = `
    <span class="tag t${c.tier}">${c.tier === 1 ? "一类竞赛" : "二类竞赛"}</span> <span class="no">${c.id}</span>
    <h2>${esc(c.name)}</h2>
    <p>推荐院系：${esc(c.dept)}</p>
    <p><span class="st ${st.open ? "open" : ""}">${st.label}</span> · ${regText(c)}${c.note ? " · " + esc(c.note) : ""}</p>
    <p class="dim">报名时间按往年整理，仅供参考，以官网和学院通知为准。</p>
    ${c.url ? `<p>官网：<a href="${esc(c.url)}" target="_blank">${esc(c.url)}</a></p>` : ""}
    <h4>经验分享 / 往届方案（点击跳转搜索）</h4>
    <div class="links">${c.links.map(l => `<a class="btn" href="${esc(l.url)}" target="_blank">${esc(l.site)}</a>`).join("")}</div>
    <h4>GitHub 开源方案（自动同步，按 Star 排序）</h4>
    <ul class="repos">${repos}</ul>`;
  document.getElementById("modal").classList.add("show");
}

function renderHackathons(data) {
  const el = document.getElementById("hackathons");
  if (!el) return;
  el.innerHTML = `
    <h2>大公司 / 知名黑客松</h2>
    <div class="grid">${data.hackathons.map(h => `<a class="card" href="${esc(h.url)}" target="_blank">
      <div class="row"><span class="tag hk">${esc(h.org)}</span></div><h3>${esc(h.name)}</h3><div class="meta">${esc(h.note)}</div></a>`).join("")}</div>
    <h2>正在报名的线上黑客松 <small class="dim">（Devpost 实时同步）</small></h2>
    <div class="grid">${data.devpost.map(h => `<a class="card" href="${esc(h.url)}" target="_blank">
      <div class="row"><span class="tag ${h.state === "open" ? "openTag" : "hk"}">${h.state === "open" ? "报名中" : "即将开始"}</span>
      <span class="no">${esc(h.online || "")}</span></div>
      <h3>${esc(h.name)}</h3><div class="meta">${esc(h.org || "")} · ${esc(h.dates || "")}</div>
      <div class="meta">奖金 ${esc(h.prize || "-")}</div></a>`).join("") || '<p class="dim">暂无数据</p>'}</div>`;
}

document.addEventListener("click", e => {
  if (e.target.id === "modal" || e.target.classList.contains("close")) document.getElementById("modal").classList.remove("show");
});
document.addEventListener("keydown", e => e.key === "Escape" && document.getElementById("modal").classList.remove("show"));

function searchFilter(list, kw, robotOnly) {
  kw = kw.trim().toLowerCase();
  return list.filter(c => (!robotOnly || c.robot || c.robotDept) &&
    (!kw || (c.name + c.dept + c.id).toLowerCase().includes(kw)));
}
