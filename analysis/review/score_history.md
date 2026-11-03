# Score history

Each round, a fresh, independent reviewer graded every chart and the suite as a whole against
[`RUBRIC.md`](RUBRIC.md), without seeing earlier scores. The charts were then fixed based on the
feedback, and the next round started. Full reports: `round_<n>.md` in this folder.

**Overall = 0.7 × average chart score + 0.3 × suite score.** Stop rule: at most 5 rounds, or
stop early at 95+, or when a round gains less than 1 point.

| Round | Charts | Average chart score | Suite score (G / H / I / J) | Overall | Main changes going into the round |
|---|---|---|---|---|---|
| 1 | 15 | 74.5 | 66 (21 / 13 / 19 / 13) | **72.0** | First version |
| 2 | 17 | 84.4 | 83 (25 / 16 / 25 / 17) | **84.0** | Fixed wrong numbers (formation headline, distances), "repeated water-level record" wording, consistent colors, Bernalillo change-vs-change scatters, new depth-by-area and aquifer-sensitivity charts, published San Jose values, docs and report figures generated from the charts |
| 3 | 18 | 86.1 | 87 (27 / 17 / 26 / 17) | **86.3** | Computed every remaining hand-typed count, one "Cuba area" (25 km) everywhere, per-well medians for formations, attributed USGS Ojo Alamo map crop around Cuba, gray ramp for counts, report Results merged, stats unit tests, tested on pandas 2.2 |
| 4 | 18 | 86.1 | 86 (27 / 16 / 26 / 17) | **86.0** | Fixed the formation chart's false finding and headline, merged a duplicated Smelser well test, docs and report consistency sweep (one color ramp, San Jose values worded the same way, report Fig. 3 full width), text-wrapping and overlap fixes in static exports, town labels drawn above data on maps, computed Data-sources counts, Streamlit 1.50 compatibility |

**After round 4:** round 3 (86.3) scored highest, so its files were kept and iteration stopped.

| Pass | Charts | Average chart score | Suite score (G / H / I / J) | Overall | Main changes going into the pass |
|---|---|---|---|---|---|
| Pictograph review | 18 (6 pictograph) | 84.8 | 84 (27 / 15 / 25 / 17) | **84.6** | Round-3 files plus the round-4 fixes for real errors; pictograph versions of six charts (Placitas cross-sections, Cuba-area well pictograms, nearest-record pictograms, river-visit drops, Harvey balls, unit squares) |

The pictograph review was a single pass, as agreed ([`pictograph_review.md`](pictograph_review.md)).
Its top fixes were applied afterwards (most of all a rebuilt Cuba-area pictograph map), without
another grading round. [`round_4_changes.diff`](round_4_changes.diff) is kept for reference; most of
it has since been applied.
