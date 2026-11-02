// Draws the Gantt chart on the Timeline page from the task list written in timeline.md.
// Each line inside <div class="gantt"> is either a task or a checkpoint:
//   Task name (owner) | start (YYYY-MM-DD) | end (YYYY-MM-DD)
//   Checkpoint: Name | date (YYYY-MM-DD)
// Bars are colored by the owner in parentheses: "all" is the whole team.
// It matches the timeline slide in the presentation. Hovering over, tapping, or tabbing to a task
// or checkpoint shows its dates.
(function () {
  const COLORS = { text: "#0E2A3B", muted: "#5F7380", grid: "#D5E2E6", band: "#EEF5F7",
                   checkpoint: "#C2703D", today: "#12455C", other: "#8A9AA5" };
  // One color per owner, in legend order. Same colors as the slide.
  const OWNERS = [
    ["all", "Team (all)", "#2a78d6"],
    ["dylan", "Dylan", "#1baf7a"],
    ["james", "James", "#eda100"],
    ["micah", "Micah", "#6250d6"],
    ["meckrem", "Meckrem", "#e87ba4"],
    ["petar", "Petar", "#008300"],
  ];
  const DAY = 86400000;
  const parseDate = (s) => { const [y, m, d] = s.trim().split("-").map(Number); return Date.UTC(y, m - 1, d); };
  const fmt = (t, opts) => new Date(t).toLocaleDateString("en-US", Object.assign({ timeZone: "UTC" }, opts));
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const ownerOf = (name) => {
    const m = name.match(/\(([^)]+)\)\s*$/);
    const hit = m && OWNERS.find(([key]) => m[1].trim().toLowerCase() === key);
    return { title: m ? name.slice(0, m.index).trim() : name,
             who: hit ? (hit[0] === "all" ? "Whole team" : hit[1]) : (m ? m[1].trim() : ""),
             color: hit ? hit[2] : COLORS.other };
  };
  const short = (t) => fmt(t, { month: "short", day: "numeric" });

  // Tooltip styles, added once
  const css = `
    .gantt-wrap { position: relative; }
    .gantt-hit { fill: transparent; pointer-events: all; cursor: default; outline: none; }
    .gantt-hit:hover, .gantt-hit.on { fill: rgba(18, 69, 92, 0.08); }
    .gantt-hit:focus-visible { fill: rgba(18, 69, 92, 0.08); stroke: #12455C; stroke-width: 1.5; }
    .gantt-tip { position: absolute; z-index: 10; pointer-events: none; display: none; max-width: 260px;
      background: #FFFFFF; color: #0E2A3B; border: 1px solid #D5E2E6; border-radius: 6px;
      box-shadow: 0 4px 14px rgba(14, 42, 59, 0.16); padding: 7px 10px; font-size: 13px; line-height: 1.4; }
    .gantt-tip strong { display: block; font-size: 14px; }
    .gantt-tip .who { display: flex; align-items: center; gap: 6px; color: #5F7380; }
    .gantt-tip .sw { width: 10px; height: 10px; border-radius: 2px; flex: none; }`;
  if (!document.getElementById("gantt-css")) {
    const st = document.createElement("style"); st.id = "gantt-css"; st.textContent = css; document.head.appendChild(st);
  }

  function draw(box) {
    const tasks = [], checkpoints = [];
    box.textContent.split("\n").map((l) => l.trim()).filter(Boolean).forEach((line) => {
      const parts = line.split("|").map((p) => p.trim());
      if (/^checkpoint:/i.test(parts[0]) && parts.length >= 2) {
        checkpoints.push({ name: parts[0].replace(/^checkpoint:\s*/i, ""), date: parseDate(parts[1]) });
      } else if (parts.length >= 3) {
        tasks.push(Object.assign({ name: parts[0], start: parseDate(parts[1]), end: parseDate(parts[2]) }, ownerOf(parts[0])));
      }
    });
    if (!tasks.length) return;

    // Date range: from the Monday on or before the first date to the day after the last date
    const all = tasks.flatMap((t) => [t.start, t.end]).concat(checkpoints.map((c) => c.date));
    let d0 = Math.min(...all); d0 -= ((new Date(d0).getUTCDay() + 6) % 7) * DAY;
    const d1 = Math.max(...all) + DAY;

    const W = 860, labelW = 250, bx0 = labelW + 8, bx1 = 650, msX = 680;
    const top = 44, rowH = 30, rowsEnd = top + tasks.length * rowH, H = rowsEnd + 54;
    const x = (t) => bx0 + ((t - d0) / (d1 - d0)) * (bx1 - bx0);
    const now = new Date(), todayUTC = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate());
    const diamond = (cx, cy, size, fill) =>
      `<rect x="${cx - size / 2}" y="${cy - size / 2}" width="${size}" height="${size}" fill="${fill}" transform="rotate(45 ${cx} ${cy})"/>`;
    let s = "";

    // Row bands and task labels
    tasks.forEach((t, i) => {
      const y = top + i * rowH;
      if (i % 2 === 0) s += `<rect x="0" y="${y}" width="${bx1 + 6}" height="${rowH}" fill="${COLORS.band}" opacity="0.7"/>`;
      s += `<text x="6" y="${y + rowH / 2}" dominant-baseline="central" font-size="13" fill="${COLORS.text}">${esc(t.name)}</text>`;
    });
    // Weekly gridlines and date labels (Mondays)
    for (let t = d0; t <= d1; t += 7 * DAY) {
      s += `<line x1="${x(t)}" y1="${top - 6}" x2="${x(t)}" y2="${rowsEnd}" stroke="${COLORS.grid}" stroke-width="1"/>`;
      s += `<text x="${x(t)}" y="14" text-anchor="middle" font-size="11" fill="${COLORS.muted}">${fmt(t, { month: "short", day: "numeric" })}</text>`;
    }
    // Bars (end date included), colored by owner
    tasks.forEach((t, i) => {
      const y = top + i * rowH + 7, w = Math.max(4, x(t.end + DAY) - x(t.start));
      s += `<rect x="${x(t.start)}" y="${y}" width="${w}" height="${rowH - 14}" rx="4" fill="${t.color}"/>`;
    });
    // Checkpoint lines with a diamond at the top
    checkpoints.forEach((c) => {
      const cx = x(c.date + DAY / 2);
      s += `<line x1="${cx}" y1="${top - 8}" x2="${cx}" y2="${rowsEnd}" stroke="${COLORS.checkpoint}" stroke-width="1.5" stroke-dasharray="5 4"/>`;
      s += diamond(cx, top - 22, 12, COLORS.checkpoint);
    });
    // Today line
    if (todayUTC >= d0 && todayUTC <= d1) {
      const tx = x(todayUTC + DAY / 2);
      s += `<line x1="${tx}" y1="${top}" x2="${tx}" y2="${rowsEnd + 6}" stroke="${COLORS.today}" stroke-width="1.5"/>`;
      s += `<text x="${tx}" y="${rowsEnd + 18}" text-anchor="middle" font-size="11" font-weight="600" fill="${COLORS.today}">Today</text>`;
    }
    // Milestones list on the right
    s += `<text x="${msX}" y="${top - 18}" font-size="16" font-weight="700" fill="${COLORS.text}">Milestones</text>`;
    checkpoints.forEach((c, i) => {
      const y = top + 12 + i * 50, passed = c.date < todayUTC;
      s += diamond(msX + 7, y + 6, 12, COLORS.checkpoint);
      s += `<text x="${msX + 24}" y="${y + 10}" font-size="13" font-weight="700" fill="${COLORS.text}">${fmt(c.date, { weekday: "short", month: "short", day: "numeric" })}</text>`;
      s += `<text x="${msX + 24}" y="${y + 28}" font-size="13" fill="${COLORS.muted}">${esc(c.name)}${passed ? " · done" : ""}</text>`;
    });
    // Legend: one swatch per owner, then the checkpoint marker
    let lx = 6;
    const ly = rowsEnd + 36;
    OWNERS.forEach(([, label, color]) => {
      s += `<rect x="${lx}" y="${ly - 7}" width="22" height="14" rx="3" fill="${color}"/>`;
      s += `<text x="${lx + 28}" y="${ly}" dominant-baseline="central" font-size="12" fill="${COLORS.muted}">${label}</text>`;
      lx += 28 + label.length * 6.6 + 18;
    });
    s += diamond(lx + 5, ly, 10, COLORS.checkpoint);
    s += `<text x="${lx + 18}" y="${ly}" dominant-baseline="central" font-size="12" fill="${COLORS.muted}">Course checkpoint</text>`;

    // Hover targets: each whole row (label and bar), and each checkpoint marker. Drawn last so they sit on top.
    const tips = [];
    tasks.forEach((t, i) => {
      const days = Math.round((t.end - t.start) / DAY) + 1;
      tips.push({ html: `<strong>${esc(t.title)}</strong>` +
        (t.who ? `<span class="who"><span class="sw" style="background:${t.color}"></span>${esc(t.who)}</span>` : "") +
        `${short(t.start)} – ${short(t.end)} · ${days} days`, bar: i });
      s += `<rect class="gantt-hit" data-tip="${tips.length - 1}" x="0" y="${top + i * rowH}" width="${bx1 + 6}" height="${rowH}" tabindex="0" role="img" aria-label="${esc(t.name)}: ${short(t.start)} to ${short(t.end)}"/>`;
    });
    checkpoints.forEach((c) => {
      const cx = x(c.date + DAY / 2);
      tips.push({ html: `<strong>${esc(c.name)}</strong>Course checkpoint · ${fmt(c.date, { weekday: "short", month: "short", day: "numeric" })}` });
      s += `<rect class="gantt-hit" data-tip="${tips.length - 1}" x="${cx - 11}" y="${top - 34}" width="22" height="24" tabindex="0" role="img" aria-label="${esc(c.name)} checkpoint: ${short(c.date)}"/>`;
    });

    box.innerHTML = `<div class="gantt-wrap"><div style="overflow-x:auto"><svg viewBox="0 0 ${W} ${H}" style="min-width:680px;width:100%;height:auto;font-family:inherit">${s}</svg></div><div class="gantt-tip" role="tooltip"></div></div>`;

    const wrap = box.querySelector(".gantt-wrap"), tip = box.querySelector(".gantt-tip");
    let active = null;
    const show = (el, px, py) => {
      if (active && active !== el) active.classList.remove("on");
      active = el; el.classList.add("on");
      tip.innerHTML = tips[+el.dataset.tip].html; tip.style.display = "block";
      const r = wrap.getBoundingClientRect();
      let left = px - r.left + 14, topPx = py - r.top + 16;
      if (left + tip.offsetWidth > r.width) left = Math.max(0, px - r.left - tip.offsetWidth - 14);
      tip.style.left = left + "px"; tip.style.top = topPx + "px";
    };
    const hide = () => { if (active) active.classList.remove("on"); active = null; tip.style.display = "none"; };
    box.querySelectorAll(".gantt-hit").forEach((el) => {
      el.addEventListener("pointermove", (e) => { if (e.pointerType !== "touch") show(el, e.clientX, e.clientY); });
      el.addEventListener("pointerleave", (e) => { if (e.pointerType !== "touch") hide(); });
      el.addEventListener("pointerdown", (e) => { if (e.pointerType === "touch") show(el, e.clientX, e.clientY); });
      el.addEventListener("focus", () => { const b = el.getBoundingClientRect(); show(el, b.left + Math.min(b.width, 300) / 2, b.bottom - 8); });
      el.addEventListener("blur", hide);
    });
    document.addEventListener("pointerdown", (e) => { if (!e.target.closest || !e.target.closest(".gantt-hit")) hide(); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") hide(); });
  }

  document.addEventListener("DOMContentLoaded", () => document.querySelectorAll("div.gantt").forEach(draw));
})();
