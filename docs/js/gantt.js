// Draws the Gantt chart on the Timeline page from the task list written in timeline.md.
// Each line inside <div class="gantt"> is either a task or a checkpoint:
//   Task name (owner) | start (YYYY-MM-DD) | end (YYYY-MM-DD)
//   Checkpoint: Name | date (YYYY-MM-DD)
// Bars are colored by the owner in parentheses: "all" is the whole team.
// It matches the timeline slide in the presentation.
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
  const ownerColor = (name) => {
    const m = name.match(/\(([^)]+)\)\s*$/);
    const hit = m && OWNERS.find(([key]) => m[1].trim().toLowerCase() === key);
    return hit ? hit[2] : COLORS.other;
  };

  function draw(box) {
    const tasks = [], checkpoints = [];
    box.textContent.split("\n").map((l) => l.trim()).filter(Boolean).forEach((line) => {
      const parts = line.split("|").map((p) => p.trim());
      if (/^checkpoint:/i.test(parts[0]) && parts.length >= 2) {
        checkpoints.push({ name: parts[0].replace(/^checkpoint:\s*/i, ""), date: parseDate(parts[1]) });
      } else if (parts.length >= 3) {
        tasks.push({ name: parts[0], start: parseDate(parts[1]), end: parseDate(parts[2]), color: ownerColor(parts[0]) });
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
      s += `<rect x="${x(t.start)}" y="${y}" width="${w}" height="${rowH - 14}" rx="4" fill="${t.color}"><title>${esc(t.name)}: ${fmt(t.start, { month: "short", day: "numeric" })} to ${fmt(t.end, { month: "short", day: "numeric" })}</title></rect>`;
    });
    // Checkpoint lines with a diamond at the top
    checkpoints.forEach((c) => {
      const cx = x(c.date + DAY / 2);
      s += `<line x1="${cx}" y1="${top - 8}" x2="${cx}" y2="${rowsEnd}" stroke="${COLORS.checkpoint}" stroke-width="1.5" stroke-dasharray="5 4"/>`;
      s += `<g><title>${esc(c.name)}: ${fmt(c.date, { month: "short", day: "numeric" })}</title>${diamond(cx, top - 22, 12, COLORS.checkpoint)}</g>`;
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

    const summary = tasks.map((t) => `${t.name}, ${fmt(t.start, { month: "short", day: "numeric" })} to ${fmt(t.end, { month: "short", day: "numeric" })}`).join("; ");
    box.innerHTML = `<div style="overflow-x:auto"><svg viewBox="0 0 ${W} ${H}" style="min-width:680px;width:100%;height:auto;font-family:inherit" role="img" aria-label="Project Gantt chart. ${esc(summary)}">${s}</svg></div>`;
  }

  document.addEventListener("DOMContentLoaded", () => document.querySelectorAll("div.gantt").forEach(draw));
})();
