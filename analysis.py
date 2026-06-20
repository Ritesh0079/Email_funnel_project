"""
Steps 2-8 — Funnel metrics, A/B testing, segmentation, time series,
visualizations, and an auto-generated insights report.

Saves all charts to ../visuals as PNG and prints metrics to stdout.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from scipy import stats

sns.set_theme(style="whitegrid")
PALETTE = ["#2E5EAA", "#5BC0BE", "#F4A259", "#E76F51"]
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.bbox"] = "tight"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
VIS_DIR = os.path.join(BASE_DIR, "visuals")
os.makedirs(VIS_DIR, exist_ok=True)

df = pd.read_csv(os.path.join(DATA_DIR, "cleaned_email_data.csv"), parse_dates=["sent_date", "sent_week"])


# ----------------------------------------------------------------------
# STEP 2 — FUNNEL METRICS
# ----------------------------------------------------------------------
def funnel_metrics(d):
    sent = len(d)
    delivered = d["delivered"].sum()
    opened = d["opened"].sum()
    clicked = d["clicked"].sum()
    converted = d["converted"].sum()
    unsub = d["unsubscribed"].sum()
    bounced = sent - delivered
    return {
        "Sent": sent,
        "Delivered": delivered,
        "Opened": opened,
        "Clicked": clicked,
        "Converted": converted,
        "Delivery Rate": delivered / sent,
        "Open Rate": opened / delivered,
        "CTR": clicked / delivered,
        "CTOR": clicked / opened,
        "Conversion Rate": converted / clicked,
        "Unsubscribe Rate": unsub / delivered,
        "Bounce Rate": bounced / sent,
    }


overall = funnel_metrics(df)
print("\n===== STEP 2: Overall Funnel Metrics =====")
for k in ["Delivery Rate", "Open Rate", "CTR", "CTOR", "Conversion Rate", "Unsubscribe Rate", "Bounce Rate"]:
    print(f"{k:18}: {overall[k]:.2%}")

by_campaign = (
    df.groupby("campaign_type")
    .apply(lambda g: pd.Series(funnel_metrics(g)), include_groups=False)
    .reset_index()
)
print("\n===== STEP 2: Metrics by Campaign Type =====")
print(by_campaign[["campaign_type", "Open Rate", "CTR", "Conversion Rate", "Unsubscribe Rate"]].to_string(index=False))
by_campaign.to_csv(os.path.join(DATA_DIR, "metrics_by_campaign.csv"), index=False)


# ----------------------------------------------------------------------
# STEP 3 — FUNNEL VISUALIZATION (Plotly interactive + PNG)
# ----------------------------------------------------------------------
stages = ["Sent", "Delivered", "Opened", "Clicked", "Converted"]
values = [overall[s] for s in stages]
drop = [0] + [(values[i] - values[i - 1]) / values[i - 1] for i in range(1, len(values))]

fig = go.Figure(
    go.Funnel(
        y=stages,
        x=values,
        textposition="inside",
        textinfo="value+percent initial",
        marker={"color": ["#2E5EAA", "#3A7CA5", "#5BC0BE", "#F4A259", "#E76F51"]},
        connector={"line": {"color": "#888", "width": 1}},
    )
)
fig.update_layout(
    title="Email Marketing Funnel: Sent → Delivered → Opened → Clicked → Converted",
    font=dict(size=14),
    width=900,
    height=550,
)
fig.write_image(os.path.join(VIS_DIR, "funnel_chart.png"), scale=2)
fig.write_html(os.path.join(VIS_DIR, "funnel_chart.html"))
print("\n===== STEP 3: Funnel Drop-off =====")
for s, v, d_ in zip(stages, values, drop):
    print(f"{s:11}: {v:6,}  ({d_:+.1%} vs previous)")


# ----------------------------------------------------------------------
# STEP 4 — CAMPAIGN TYPE ANALYSIS (grouped bar)
# ----------------------------------------------------------------------
metrics_plot = by_campaign.set_index("campaign_type")[["Open Rate", "CTR", "Conversion Rate"]]
ax = metrics_plot.plot(kind="bar", figsize=(9, 5.5), color=PALETTE[:3], edgecolor="white")
ax.set_title("Campaign Type Performance Comparison", fontsize=14, weight="bold")
ax.set_ylabel("Rate")
ax.set_xlabel("Campaign Type")
ax.set_xticklabels(metrics_plot.index, rotation=0)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
for c in ax.containers:
    ax.bar_label(c, fmt="%.1f%%", labels=[f"{v*100:.1f}%" for v in c.datavalues], fontsize=8, padding=2)
ax.legend(title="Metric")
plt.tight_layout()
plt.savefig(os.path.join(VIS_DIR, "campaign_comparison.png"))
plt.close()
best_campaign = by_campaign.loc[by_campaign["Conversion Rate"].idxmax(), "campaign_type"]
print(f"\n===== STEP 4: Best converting campaign: {best_campaign} =====")


# ----------------------------------------------------------------------
# STEP 5 — A/B TEST (Chi-Square on open rate)
# ----------------------------------------------------------------------
print("\n===== STEP 5: A/B Test on Subject Line (Open Rate) =====")
ab = df[df["delivered"] == 1]
contingency = pd.crosstab(ab["subject_line"], ab["opened"])
chi2, p, dof, expected = stats.chi2_contingency(contingency)
open_rates = ab.groupby("subject_line")["opened"].mean()
print(contingency.to_string())
print(f"Version_A open rate: {open_rates['Version_A']:.2%}")
print(f"Version_B open rate: {open_rates['Version_B']:.2%}")
print(f"Chi2 = {chi2:.3f} | p-value = {p:.5f} | dof = {dof}")
significant = p < 0.05
print(f"Conclusion: {'STATISTICALLY SIGNIFICANT (p < 0.05)' if significant else 'NOT significant (p >= 0.05)'}")
winner = open_rates.idxmax()

# A/B bar chart
fig2, ax2 = plt.subplots(figsize=(7, 5))
bars = ax2.bar(open_rates.index, open_rates.values, color=[PALETTE[0], PALETTE[1]], edgecolor="white")
ax2.set_title(f"A/B Test: Subject Line Open Rate\nChi2={chi2:.2f}, p={p:.4f} "
              f"({'significant' if significant else 'not significant'})", fontsize=12, weight="bold")
ax2.set_ylabel("Open Rate")
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
ax2.bar_label(bars, labels=[f"{v:.2%}" for v in open_rates.values], padding=3)
plt.tight_layout()
plt.savefig(os.path.join(VIS_DIR, "ab_test_open_rate.png"))
plt.close()


# ----------------------------------------------------------------------
# STEP 6 — SEGMENTATION ANALYSIS
# ----------------------------------------------------------------------
print("\n===== STEP 6: Segmentation (overall conversion = converted/delivered) =====")


def conv_rate(g):
    return g["converted"].sum() / g["delivered"].sum()


for dim in ["device_type", "region", "customer_segment"]:
    seg = df.groupby(dim).apply(conv_rate, include_groups=False)
    print(f"\nBy {dim}:")
    print((seg * 100).round(2).to_string())

# Heatmap: device x region conversion rate
pivot = df.pivot_table(index="device_type", columns="region", values="converted", aggfunc="sum") / \
        df.pivot_table(index="device_type", columns="region", values="delivered", aggfunc="sum")
fig3, ax3 = plt.subplots(figsize=(8, 5))
sns.heatmap(pivot * 100, annot=True, fmt=".2f", cmap="YlGnBu", cbar_kws={"label": "Conversion Rate (%)"}, ax=ax3)
ax3.set_title("Conversion Rate (%) by Device & Region", fontsize=13, weight="bold")
ax3.set_xlabel("Region")
ax3.set_ylabel("Device Type")
plt.tight_layout()
plt.savefig(os.path.join(VIS_DIR, "heatmap_device_region.png"))
plt.close()

# Segment bar chart (customer_segment)
seg_conv = df.groupby("customer_segment").apply(conv_rate, include_groups=False).sort_values(ascending=False)
fig4, ax4 = plt.subplots(figsize=(7, 5))
b = ax4.bar(seg_conv.index, seg_conv.values * 100, color=PALETTE[:3], edgecolor="white")
ax4.set_title("Conversion Rate by Customer Segment", fontsize=13, weight="bold")
ax4.set_ylabel("Conversion Rate (%)")
ax4.bar_label(b, fmt="%.2f%%", padding=3)
plt.tight_layout()
plt.savefig(os.path.join(VIS_DIR, "segment_conversion.png"))
plt.close()

best_device = (df.groupby("device_type").apply(conv_rate, include_groups=False)).idxmax()
best_region = (df.groupby("region").apply(conv_rate, include_groups=False)).idxmax()
worst_region = (df.groupby("region").apply(conv_rate, include_groups=False)).idxmin()
best_segment = seg_conv.index[0]


# ----------------------------------------------------------------------
# STEP 7 — TIME SERIES ANALYSIS
# ----------------------------------------------------------------------
weekly = df.groupby("sent_week").agg(
    delivered=("delivered", "sum"),
    opened=("opened", "sum"),
    converted=("converted", "sum"),
).reset_index()
weekly["open_rate"] = weekly["opened"] / weekly["delivered"]
weekly["conv_rate"] = weekly["converted"] / weekly["delivered"]

fig5, ax5 = plt.subplots(figsize=(11, 5.5))
ax5.plot(weekly["sent_week"], weekly["open_rate"] * 100, marker="o", color=PALETTE[0], label="Open Rate")
ax5.set_ylabel("Open Rate (%)", color=PALETTE[0])
ax5.tick_params(axis="y", labelcolor=PALETTE[0])
ax6 = ax5.twinx()
ax6.plot(weekly["sent_week"], weekly["conv_rate"] * 100, marker="s", color=PALETTE[3], label="Conversion Rate")
ax6.set_ylabel("Conversion Rate (%)", color=PALETTE[3])
ax6.tick_params(axis="y", labelcolor=PALETTE[3])
ax5.set_title("Weekly Open Rate & Conversion Rate (Last 6 Months)", fontsize=13, weight="bold")
ax5.set_xlabel("Week")
fig5.autofmt_xdate()
plt.tight_layout()
plt.savefig(os.path.join(VIS_DIR, "time_series_trend.png"))
plt.close()
weekly.to_csv(os.path.join(DATA_DIR, "weekly_trends.csv"), index=False)


# ----------------------------------------------------------------------
# STEP 8 — INSIGHTS & RECOMMENDATIONS
# ----------------------------------------------------------------------
insights = f"""# Insights & Recommendations

1. **Prioritize {best_campaign} campaigns** — they deliver the highest
   click-to-conversion rate, making them the most efficient use of send volume.
2. **Optimize for {best_device}** — {best_device} users convert at the highest
   rate; ensure templates are fully responsive and CTAs render well on this device.
3. **Targeted push needed in the {worst_region} region** — it has the lowest
   conversion rate; test localized offers and send-time optimization there, while
   the {best_region} region is the current top performer.
4. **A/B test verdict** — {winner} won the subject-line test with a
   {open_rates[winner]:.2%} open rate (chi2={chi2:.2f}, p={p:.4f}). The result is
   {'statistically significant, so roll out ' + winner + ' broadly.' if significant else 'not statistically significant; keep testing before committing.'}
5. **Focus retention on the {best_segment} segment** — it converts best; build a
   loyalty / VIP nurture track, and design a re-engagement series for lower-converting
   segments to lift overall funnel performance.

## Resume Bullet Points

- Analyzed 10,000+ simulated email campaign records using Python (pandas, NumPy, scipy) to map funnel drop-off across five stages, surfacing the largest leakage point between open and click.
- Built an interactive Plotly funnel and a Chi-Square A/B test on subject lines, identifying a statistically{'' if significant else ' in'}significant winner and producing data-backed creative recommendations.
- Delivered segmentation and time-series analysis (device, region, customer segment) with Matplotlib/Seaborn heatmaps, pinpointing the top-converting device and segment to guide budget allocation.
"""
with open(os.path.join(BASE_DIR, "INSIGHTS.md"), "w") as f:
    f.write(insights)
print("\n===== STEP 8: Insights written to INSIGHTS.md =====")
print(insights)
print("\nAll visuals saved to:", VIS_DIR)
