"""Two report charts, three scenarios only (Pilot A, Pilot C, Ours). The free rule is a grey reference.

Run: /opt/anaconda3/bin/python analysis/report_charts.py -> docs/report/fig-soc.png, fig-tradeoff.png
Ours = demo/out/run_conservative_0.1.json (run C inputs). Scatter values = data/ours_ministral.json + workbook.
"""
import json
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from kpis import FILES, ROOT, load

OUT = ROOT / "docs/report"
INK, BLUE, MUTE, RULE = "#151F27", "#3A7DDA", "#8A949E", "#B9C0C6"
plt.rcParams.update({"font.family": "Arial", "font.size": 11, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": "#9aa3ab"})


def by_hour(pairs):
    acc = defaultdict(list)
    for t, soc in pairs:
        acc[int(t[11:13])].append(soc)
    return [100 * sum(acc[h]) / len(acc[h]) for h in range(24)]


def soc_chart():
    a = load(ROOT / "data/DatasetV4" / FILES["A"])
    c = load(ROOT / "data/DatasetV4" / FILES["C"])
    ours = json.loads((ROOT / "demo/out/run_conservative_0.1.json").read_text())["schedule"]
    series = [("Pilot A (cost agent)", by_hour((r["dt"], r["bess"]["soc"]) for r in a), MUTE, "-"),
              ("Pilot C (cost + sustainability)", by_hour((r["dt"], r["bess"]["soc"]) for r in c), INK, "-"),
              ("Ours (one agent, Ministral 3)", by_hour((r["t"], r["soc"]) for r in ours), BLUE, "-")]
    assert all(len(s[1]) == 24 for s in series)
    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=200)
    ax.axvspan(18, 21, color="#EEF0F2", zorder=0)
    ax.text(19.5, 96, "evening peak", ha="center", color="#47525C", fontsize=10)
    for y, lbl in ((90, "90% limit"), (80, "80% target in the pilots' prompt"), (10, "10% limit")):
        ax.axhline(y, ls="--", lw=0.8, color=RULE)
        ax.text(0.2, y + (1.5 if y > 10 else -5), lbl, color="#47525C", fontsize=9)
    for name, ys, col, ls in series:
        ax.plot(range(24), ys, ls, color=col, lw=2.4 if col == BLUE else 1.8, label=name)
    ax.set_xticks(range(0, 24, 3), [f"{h:02d}:00" for h in range(0, 24, 3)])
    ax.set_ylim(0, 100)
    ax.set_ylabel("battery charge, % (7-day average)")
    ax.set_title("The pilots stall at 80% by noon; ours fills to 90% for the evening", loc="left",
                 fontsize=13, fontweight="bold")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0, -0.12), ncol=3, fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / "fig-soc.png")


def tradeoff_chart():
    k = json.loads((ROOT / "data/ours_ministral.json").read_text())
    ours = (k["kpis"]["S1"]["value"], k["kpis"]["S_net"]["value"])
    pts = [("Pilot A", 21.9475, 0.4071, MUTE), ("Pilot C", 21.2553, 0.4026, INK), ("Ours", *ours, BLUE)]
    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=200)
    ax.scatter([11.8983], [1.034], s=120, facecolors="none", edgecolors=MUTE, lw=1.5, zorder=3)
    ax.annotate("free static rule (yardstick)", (11.8983, 1.034), (12.3, 0.80), color="#47525C", fontsize=10,
                arrowprops={"arrowstyle": "-", "color": RULE})
    for name, x, y, col in pts:
        ax.scatter([x], [y], s=140, color=col, zorder=4)
        off = (-60, -22) if name == "Pilot C" else (8, 8)
        ax.annotate(name, (x, y), off, textcoords="offset points", fontweight="bold", color=col)
    ax.set_xlim(10, 24)
    ax.set_ylim(0, 1.5)
    ax.set_xlabel("grid CO2, kg per week (lower is better)")
    ax.set_ylabel("saving net of wear, € per week")
    ax.set_title("Ours saves almost 3x the pilots and emits 43% less CO2 than pilot C", loc="left",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "fig-tradeoff.png")
    return ours


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    soc_chart()
    co2, s_net = tradeoff_chart()
    assert abs(1 - co2 / 21.2553 - 0.428) < 0.01, co2  # title claim: -43% CO2 vs pilot C
    assert 2.8 < s_net / 0.4026 < 2.9, s_net  # title claim: ~3x pilot C's saving
    print("charts ok", OUT)
