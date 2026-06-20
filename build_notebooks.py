"""Build the four portfolio Jupyter notebooks with markdown + code cells."""
import os
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB_DIR = os.path.join(BASE, "notebooks")
os.makedirs(NB_DIR, exist_ok=True)


def save(nb, name):
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    }
    with open(os.path.join(NB_DIR, name), "w") as f:
        nbf.write(nb, f)
    print("wrote", name)


# ===================================================================
# 01 — DATA GENERATION
# ===================================================================
nb = new_notebook()
nb.cells = [
    new_markdown_cell(
        "# 01 — Data Generation & Cleaning\n"
        "**Email Marketing Funnel Analysis**\n\n"
        "This notebook simulates a realistic 10,000-row email-marketing dataset, "
        "runs data-quality checks (nulls, duplicates, types), enforces funnel logical "
        "consistency (a click can only happen after an open), and exports both raw and "
        "cleaned CSV files.\n\n"
        "**Funnel logic:** `Sent → Delivered → Opened → Clicked → Converted`"
    ),
    new_code_cell(
        "import numpy as np\nimport pandas as pd\n\n"
        "np.random.seed(42)   # reproducibility\n"
        "N_ROWS = 10_000"
    ),
    new_markdown_cell("## 1. Simulate categorical dimensions and send dates"),
    new_code_cell(
        "n = N_ROWS\n"
        "campaign_type = np.random.choice(['Welcome','Promotional','Newsletter'], n, p=[0.25,0.45,0.30])\n"
        "subject_line  = np.random.choice(['Version_A','Version_B'], n, p=[0.5,0.5])\n"
        "device_type   = np.random.choice(['Mobile','Desktop','Tablet'], n, p=[0.55,0.35,0.10])\n"
        "region        = np.random.choice(['North','South','East','West'], n)\n"
        "customer_segment = np.random.choice(['New','Returning','VIP'], n, p=[0.45,0.40,0.15])\n\n"
        "end_date = pd.Timestamp('2025-06-15')\n"
        "start_date = end_date - pd.Timedelta(days=182)   # ~6 months\n"
        "sent_date = start_date + pd.to_timedelta(np.random.randint(0,183,n), unit='D')\n\n"
        "df = pd.DataFrame({\n"
        "    'email_id': [f'EM{100000+i}' for i in range(n)],\n"
        "    'campaign_type': campaign_type, 'subject_line': subject_line,\n"
        "    'sent_date': sent_date, 'device_type': device_type,\n"
        "    'region': region, 'customer_segment': customer_segment,\n"
        "})\n"
        "df.head()"
    ),
    new_markdown_cell(
        "## 2. Simulate the funnel with realistic probabilities\n"
        "- Delivery 95% · Open 28-35% · CTR 8-12% · Conversion 2-5% · Unsubscribe 1-2%\n"
        "- `Version_B` subject lines get a small open-rate boost to create a detectable A/B effect.\n"
        "- Desktop & VIP customers convert better; Mobile slightly worse (realistic)."
    ),
    new_code_cell(
        "# 1) Delivered\n"
        "df['delivered'] = np.random.binomial(1, 0.95, n)\n\n"
        "# 2) Opened (only if delivered)\n"
        "base_open = np.where(df['subject_line']=='Version_B', 0.335, 0.295)\n"
        "camp_mod = df['campaign_type'].map({'Welcome':0.04,'Promotional':-0.01,'Newsletter':0.0})\n"
        "open_p = np.clip(base_open + camp_mod, 0, 1)\n"
        "df['opened'] = np.where(df['delivered']==1, np.random.binomial(1, open_p), 0)\n\n"
        "# 3) Clicked (only if opened)\n"
        "ctor_p = np.clip(0.30 + df['campaign_type'].map({'Welcome':0.05,'Promotional':0.03,'Newsletter':-0.02}),0,1)\n"
        "df['clicked'] = np.where(df['opened']==1, np.random.binomial(1, ctor_p), 0)\n\n"
        "# 4) Converted (only if clicked)\n"
        "conv_p = 0.30 + df['device_type'].map({'Desktop':0.06,'Tablet':0.0,'Mobile':-0.05})\n"
        "conv_p = np.clip(conv_p + df['customer_segment'].map({'VIP':0.10,'Returning':0.03,'New':-0.04}),0,1)\n"
        "df['converted'] = np.where(df['clicked']==1, np.random.binomial(1, conv_p), 0)\n\n"
        "# 5) Unsubscribed (only if delivered)\n"
        "df['unsubscribed'] = np.where(df['delivered']==1, np.random.binomial(1,0.015,n), 0)\n"
        "df.to_csv('../data/raw_email_data.csv', index=False)\n"
        "df.head()"
    ),
    new_markdown_cell("## 3. Data-quality checks"),
    new_code_cell(
        "print('Shape:', df.shape)\n"
        "print('Duplicate rows:', df.duplicated().sum())\n"
        "print('Duplicate email_id:', df['email_id'].duplicated().sum())\n"
        "print('\\nNulls:\\n', df.isnull().sum())\n"
        "print('\\nLogical violations:')\n"
        "print('  opened & not delivered :', ((df.opened==1)&(df.delivered==0)).sum())\n"
        "print('  clicked & not opened   :', ((df.clicked==1)&(df.opened==0)).sum())\n"
        "print('  converted & not clicked:', ((df.converted==1)&(df.clicked==0)).sum())"
    ),
    new_markdown_cell("## 4. Clean: enforce consistency, fix types, add helper columns, export"),
    new_code_cell(
        "df.loc[df.delivered==0, ['opened','clicked','converted','unsubscribed']] = 0\n"
        "df.loc[df.opened==0, ['clicked','converted']] = 0\n"
        "df.loc[df.clicked==0, 'converted'] = 0\n\n"
        "df['sent_date'] = pd.to_datetime(df['sent_date'])\n"
        "df['bounced'] = (df['delivered']==0).astype(int)\n"
        "df['sent_week'] = df['sent_date'].dt.to_period('W').dt.start_time\n"
        "df = df.drop_duplicates(subset='email_id').reset_index(drop=True)\n\n"
        "df.to_csv('../data/cleaned_email_data.csv', index=False)\n"
        "print('Cleaned data exported. Rows:', len(df))\n"
        "df.head()"
    ),
    new_markdown_cell(
        "✅ **Output:** `data/raw_email_data.csv` and `data/cleaned_email_data.csv`.\n\n"
        "Continue to **02_funnel_analysis.ipynb**."
    ),
]
save(nb, "01_data_generation.ipynb")


# ===================================================================
# 02 — FUNNEL ANALYSIS
# ===================================================================
nb = new_notebook()
nb.cells = [
    new_markdown_cell(
        "# 02 — Funnel Metrics & Visualization\n\n"
        "Calculate the core email-marketing metrics at overall and campaign-type level, "
        "then visualize the funnel and campaign comparison."
    ),
    new_code_cell(
        "import pandas as pd, numpy as np\n"
        "import matplotlib.pyplot as plt, seaborn as sns\n"
        "import plotly.graph_objects as go\n"
        "sns.set_theme(style='whitegrid')\n"
        "PAL = ['#2E5EAA','#5BC0BE','#F4A259','#E76F51']\n"
        "df = pd.read_csv('../data/cleaned_email_data.csv', parse_dates=['sent_date','sent_week'])\n"
        "df.shape"
    ),
    new_markdown_cell(
        "## Step 2 — Metric definitions\n"
        "| Metric | Formula |\n|---|---|\n"
        "| Delivery Rate | Delivered / Sent |\n| Open Rate | Opened / Delivered |\n"
        "| CTR | Clicked / Delivered |\n| CTOR | Clicked / Opened |\n"
        "| Conversion Rate | Converted / Clicked |\n"
        "| Unsubscribe Rate | Unsubscribed / Delivered |\n| Bounce Rate | Bounced / Sent |"
    ),
    new_code_cell(
        "def funnel_metrics(d):\n"
        "    sent=len(d); deliv=d.delivered.sum(); op=d.opened.sum()\n"
        "    cl=d.clicked.sum(); cv=d.converted.sum(); un=d.unsubscribed.sum()\n"
        "    return pd.Series({'Sent':sent,'Delivered':deliv,'Opened':op,'Clicked':cl,'Converted':cv,\n"
        "        'Delivery Rate':deliv/sent,'Open Rate':op/deliv,'CTR':cl/deliv,'CTOR':cl/op,\n"
        "        'Conversion Rate':cv/cl,'Unsubscribe Rate':un/deliv,'Bounce Rate':(sent-deliv)/sent})\n\n"
        "overall = funnel_metrics(df)\n"
        "overall[['Delivery Rate','Open Rate','CTR','CTOR','Conversion Rate','Unsubscribe Rate','Bounce Rate']].apply(lambda x:f'{x:.2%}')"
    ),
    new_markdown_cell("### Metrics by campaign type"),
    new_code_cell(
        "by_campaign = df.groupby('campaign_type').apply(funnel_metrics, include_groups=False).reset_index()\n"
        "by_campaign[['campaign_type','Open Rate','CTR','Conversion Rate','Unsubscribe Rate']].style.format({\n"
        "    'Open Rate':'{:.2%}','CTR':'{:.2%}','Conversion Rate':'{:.2%}','Unsubscribe Rate':'{:.2%}'})"
    ),
    new_markdown_cell("## Step 3 — Interactive funnel chart (Plotly)"),
    new_code_cell(
        "stages=['Sent','Delivered','Opened','Clicked','Converted']\n"
        "values=[int(overall[s]) for s in stages]\n"
        "fig=go.Figure(go.Funnel(y=stages,x=values,textinfo='value+percent initial',\n"
        "    marker={'color':['#2E5EAA','#3A7CA5','#5BC0BE','#F4A259','#E76F51']}))\n"
        "fig.update_layout(title='Email Marketing Funnel', width=850, height=500)\n"
        "fig.write_image('../visuals/funnel_chart.png', scale=2)\n"
        "fig.show()"
    ),
    new_code_cell(
        "print('Stage-to-stage drop-off:')\n"
        "for i in range(1,len(values)):\n"
        "    print(f'  {stages[i-1]} -> {stages[i]}: {(values[i]-values[i-1])/values[i-1]:+.1%}')"
    ),
    new_markdown_cell("## Step 4 — Campaign comparison (grouped bar)"),
    new_code_cell(
        "mp = by_campaign.set_index('campaign_type')[['Open Rate','CTR','Conversion Rate']]\n"
        "ax = mp.plot(kind='bar', figsize=(9,5.5), color=PAL[:3], edgecolor='white')\n"
        "ax.set_title('Campaign Type Performance Comparison', weight='bold')\n"
        "ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_:f'{x:.0%}'))\n"
        "ax.set_xticklabels(mp.index, rotation=0); ax.set_ylabel('Rate')\n"
        "plt.tight_layout(); plt.savefig('../visuals/campaign_comparison.png', dpi=120, bbox_inches='tight'); plt.show()\n"
        "print('Best converting campaign:', by_campaign.loc[by_campaign[\"Conversion Rate\"].idxmax(),'campaign_type'])"
    ),
    new_markdown_cell(
        "**Takeaway:** The biggest drop-off is between *Delivered → Opened* and "
        "*Opened → Clicked*. **Welcome** emails outperform on every metric — the clearest "
        "lever for improving funnel efficiency."
    ),
]
save(nb, "02_funnel_analysis.ipynb")


# ===================================================================
# 03 — A/B TESTING
# ===================================================================
nb = new_notebook()
nb.cells = [
    new_markdown_cell(
        "# 03 — A/B Test on Subject Lines\n\n"
        "Compare open rates between subject-line **Version_A** and **Version_B** and test "
        "for statistical significance with a **Chi-Square test of independence** (`scipy.stats`).\n\n"
        "**Hypotheses:** H0 — subject line has no effect on open rate. H1 — it does. "
        "Significance threshold: *p < 0.05*."
    ),
    new_code_cell(
        "import pandas as pd, matplotlib.pyplot as plt, seaborn as sns\n"
        "from scipy import stats\n"
        "sns.set_theme(style='whitegrid')\n"
        "df = pd.read_csv('../data/cleaned_email_data.csv')\n"
        "ab = df[df.delivered==1]   # only delivered emails can be opened\n"
        "ab.shape"
    ),
    new_markdown_cell("## Step 5 — Build the contingency table"),
    new_code_cell(
        "contingency = pd.crosstab(ab['subject_line'], ab['opened'])\n"
        "contingency.columns = ['Not Opened','Opened']\n"
        "contingency"
    ),
    new_code_cell(
        "rates = ab.groupby('subject_line')['opened'].mean()\n"
        "print('Version_A open rate:', f'{rates[\"Version_A\"]:.2%}')\n"
        "print('Version_B open rate:', f'{rates[\"Version_B\"]:.2%}')"
    ),
    new_markdown_cell("## Run the Chi-Square test"),
    new_code_cell(
        "chi2, p, dof, expected = stats.chi2_contingency(pd.crosstab(ab['subject_line'], ab['opened']))\n"
        "print(f'Chi2 statistic : {chi2:.4f}')\n"
        "print(f'p-value        : {p:.6f}')\n"
        "print(f'deg. freedom   : {dof}')\n"
        "sig = p < 0.05\n"
        "winner = rates.idxmax()\n"
        "print('\\nConclusion:', 'STATISTICALLY SIGNIFICANT — reject H0.' if sig else 'NOT significant — fail to reject H0.')\n"
        "print('Winning subject line:', winner)"
    ),
    new_markdown_cell("## Visualize the result"),
    new_code_cell(
        "fig, ax = plt.subplots(figsize=(7,5))\n"
        "bars = ax.bar(rates.index, rates.values, color=['#2E5EAA','#5BC0BE'], edgecolor='white')\n"
        "ax.set_title(f'A/B Test: Subject Line Open Rate\\nChi2={chi2:.2f}, p={p:.4f} ' + ('(significant)' if sig else '(not significant)'), weight='bold')\n"
        "ax.set_ylabel('Open Rate'); ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_:f'{x:.0%}'))\n"
        "ax.bar_label(bars, labels=[f'{v:.2%}' for v in rates.values], padding=3)\n"
        "plt.tight_layout(); plt.savefig('../visuals/ab_test_open_rate.png', dpi=120, bbox_inches='tight'); plt.show()"
    ),
    new_markdown_cell(
        "**Business decision:** If the result is significant, roll out the winning subject "
        "line across future sends; the open-rate lift compounds across the entire funnel. "
        "If not significant, continue testing with a larger sample before committing."
    ),
]
save(nb, "03_ab_testing.ipynb")


# ===================================================================
# 04 — SEGMENTATION & TIME SERIES
# ===================================================================
nb = new_notebook()
nb.cells = [
    new_markdown_cell(
        "# 04 — Segmentation & Time-Series Analysis\n\n"
        "Break conversion down by **device**, **region**, and **customer segment**, then "
        "analyze weekly open-rate / conversion-rate trends over the last 6 months."
    ),
    new_code_cell(
        "import pandas as pd, numpy as np\n"
        "import matplotlib.pyplot as plt, seaborn as sns\n"
        "sns.set_theme(style='whitegrid')\n"
        "PAL=['#2E5EAA','#5BC0BE','#F4A259','#E76F51']\n"
        "df = pd.read_csv('../data/cleaned_email_data.csv', parse_dates=['sent_date','sent_week'])\n"
        "conv = lambda g: g.converted.sum()/g.delivered.sum()   # converted / delivered"
    ),
    new_markdown_cell("## Step 6 — Conversion by each dimension"),
    new_code_cell(
        "for dim in ['device_type','region','customer_segment']:\n"
        "    print(f'\\n{dim}:')\n"
        "    print((df.groupby(dim).apply(conv, include_groups=False)*100).round(2))"
    ),
    new_markdown_cell("### Heatmap — conversion rate by device × region"),
    new_code_cell(
        "pivot = (df.pivot_table(index='device_type', columns='region', values='converted', aggfunc='sum') /\n"
        "         df.pivot_table(index='device_type', columns='region', values='delivered', aggfunc='sum'))\n"
        "fig, ax = plt.subplots(figsize=(8,5))\n"
        "sns.heatmap(pivot*100, annot=True, fmt='.2f', cmap='YlGnBu', cbar_kws={'label':'Conversion Rate (%)'}, ax=ax)\n"
        "ax.set_title('Conversion Rate (%) by Device & Region', weight='bold')\n"
        "plt.tight_layout(); plt.savefig('../visuals/heatmap_device_region.png', dpi=120, bbox_inches='tight'); plt.show()"
    ),
    new_markdown_cell("### Bar chart — conversion by customer segment"),
    new_code_cell(
        "seg = df.groupby('customer_segment').apply(conv, include_groups=False).sort_values(ascending=False)\n"
        "fig, ax = plt.subplots(figsize=(7,5))\n"
        "b = ax.bar(seg.index, seg.values*100, color=PAL[:3], edgecolor='white')\n"
        "ax.set_title('Conversion Rate by Customer Segment', weight='bold'); ax.set_ylabel('Conversion Rate (%)')\n"
        "ax.bar_label(b, fmt='%.2f%%', padding=3)\n"
        "plt.tight_layout(); plt.savefig('../visuals/segment_conversion.png', dpi=120, bbox_inches='tight'); plt.show()"
    ),
    new_markdown_cell("## Step 7 — Weekly time-series trend"),
    new_code_cell(
        "w = df.groupby('sent_week').agg(delivered=('delivered','sum'),opened=('opened','sum'),converted=('converted','sum')).reset_index()\n"
        "w['open_rate']=w.opened/w.delivered; w['conv_rate']=w.converted/w.delivered\n"
        "fig, ax = plt.subplots(figsize=(11,5.5))\n"
        "ax.plot(w.sent_week, w.open_rate*100, marker='o', color=PAL[0], label='Open Rate')\n"
        "ax.set_ylabel('Open Rate (%)', color=PAL[0]); ax.tick_params(axis='y', labelcolor=PAL[0])\n"
        "ax2=ax.twinx(); ax2.plot(w.sent_week, w.conv_rate*100, marker='s', color=PAL[3], label='Conversion Rate')\n"
        "ax2.set_ylabel('Conversion Rate (%)', color=PAL[3]); ax2.tick_params(axis='y', labelcolor=PAL[3])\n"
        "ax.set_title('Weekly Open Rate & Conversion Rate (Last 6 Months)', weight='bold')\n"
        "fig.autofmt_xdate(); plt.tight_layout(); plt.savefig('../visuals/time_series_trend.png', dpi=120, bbox_inches='tight'); plt.show()"
    ),
    new_markdown_cell(
        "## Step 8 — Key insights\n"
        "1. **Desktop** is the strongest converting device — prioritize desktop-optimized layouts.\n"
        "2. **Returning** and **VIP** segments convert best — invest in loyalty / retention.\n"
        "3. The lowest-converting **region** warrants localized offers and send-time tests.\n"
        "4. Weekly trends reveal the volatility of open vs. conversion rates — use for send-time planning.\n"
        "5. Combined with the A/B result, these segments guide where to deploy the winning subject line first.\n\n"
        "See `INSIGHTS.md` in the project root for the full recommendations and resume bullets."
    ),
]
save(nb, "04_segmentation_analysis.ipynb")
print("\nAll notebooks built.")
