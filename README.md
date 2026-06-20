# 📧 Email Marketing Funnel Analysis

> An end-to-end data-analytics portfolio project that simulates, cleans, analyzes,
> A/B-tests, and visualizes a 10,000-record email marketing campaign — from raw data
> to actionable business recommendations.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![pandas](https://img.shields.io/badge/pandas-data--wrangling-150458)
![scipy](https://img.shields.io/badge/scipy-A%2FB%20testing-8CAAE6)
![plotly](https://img.shields.io/badge/plotly-interactive%20viz-3F4F75)

---

## 📌 Project Description
This project analyzes an email marketing campaign to understand how users move through
the marketing funnel (**Sent → Delivered → Opened → Clicked → Converted**), where they
drop off, and which campaigns, devices, regions, and customer segments perform best.
It also runs a statistical **A/B test** on subject lines and produces data-backed
recommendations.

## 🧩 Business Problem
Email marketing teams send thousands of emails but struggle to answer:
- Where in the funnel are we losing the most users?
- Which campaign type, device, and region deliver the best ROI?
- Does changing the subject line actually improve open rates (statistically)?
- Which customer segment should we prioritize for retention?

This project answers those questions with reproducible, code-driven analysis.

## 🗂️ Dataset Description
A simulated dataset of **10,000 emails** with the following columns:

| Column | Description |
|---|---|
| `email_id` | Unique ID for each email sent |
| `campaign_type` | Welcome / Promotional / Newsletter |
| `subject_line` | Version_A or Version_B (A/B test) |
| `sent_date` | Date email was sent (last 6 months) |
| `delivered` | 1 if delivered, 0 if bounced |
| `opened` | 1 if opened, 0 if not |
| `clicked` | 1 if a link was clicked |
| `converted` | 1 if purchased / signed up |
| `unsubscribed` | 1 if unsubscribed |
| `device_type` | Mobile / Desktop / Tablet |
| `region` | North / South / East / West |
| `customer_segment` | New / Returning / VIP |

**Realistic probabilities used:** Delivery ~95% · Open 28–35% · CTR 8–12% ·
Conversion 2–5% · Unsubscribe 1–2%.

## 🛠️ Tools & Libraries
- **Python** — pandas, NumPy (data generation & cleaning)
- **scipy.stats** — Chi-Square A/B test
- **matplotlib, seaborn, plotly** — static & interactive visualizations
- **Jupyter Notebook** — analysis environment
- **Power BI / Tableau** — optional dashboard layer (see `dashboard/`)
- **Git / GitHub** — version control & portfolio hosting

## 🔑 Key Findings
1. **Welcome campaigns win** — highest open rate (~36%), CTR, and conversion; the most
   efficient campaign type to scale.
2. **Desktop converts best** — ~4% conversion vs ~2.6% on mobile; optimize templates &
   CTAs for desktop while improving the mobile experience.
3. **A/B test is significant** — Version_B beat Version_A on open rate (33.7% vs 30.3%),
   Chi² ≈ 12.1, **p ≈ 0.0005 (< 0.05)** → roll out Version_B.
4. **Biggest funnel leak** is *Delivered → Opened* (~68% drop) — subject lines and
   send-time are the highest-leverage fixes.
5. **Returning & VIP segments** convert ~40% better than New customers — prioritize
   loyalty and re-engagement programs.

> Full insights and resume bullet points are in [`INSIGHTS.md`](INSIGHTS.md).

## 🚀 How to Run
```bash
# 1. Clone and enter the project
git clone <your-repo-url>
cd email_funnel_project

# 2. Install dependencies
pip install -r requirements.txt

# 3a. Reproduce everything from scripts
python scripts/generate_data.py      # Step 1 — data + cleaning
python scripts/analysis.py           # Steps 2–8 — metrics, A/B, viz, insights

# 3b. OR run the notebooks in order
jupyter notebook
#   notebooks/01_data_generation.ipynb
#   notebooks/02_funnel_analysis.ipynb
#   notebooks/03_ab_testing.ipynb
#   notebooks/04_segmentation_analysis.ipynb
```

## 📊 Visualizations
| | |
|---|---|
| **Funnel chart** | ![funnel](visuals/funnel_chart.png) |
| **Campaign comparison** | ![campaign](visuals/campaign_comparison.png) |
| **A/B test** | ![ab](visuals/ab_test_open_rate.png) |
| **Device × Region heatmap** | ![heatmap](visuals/heatmap_device_region.png) |
| **Segment conversion** | ![segment](visuals/segment_conversion.png) |
| **Weekly trend** | ![trend](visuals/time_series_trend.png) |

> The funnel is also available as an interactive HTML file: `visuals/funnel_chart.html`.

## 📁 Project Structure
```
email_funnel_project/
├── data/
│   ├── raw_email_data.csv
│   ├── cleaned_email_data.csv
│   ├── metrics_by_campaign.csv
│   └── weekly_trends.csv
├── notebooks/
│   ├── 01_data_generation.ipynb
│   ├── 02_funnel_analysis.ipynb
│   ├── 03_ab_testing.ipynb
│   └── 04_segmentation_analysis.ipynb
├── scripts/
│   ├── generate_data.py
│   ├── analysis.py
│   └── build_notebooks.py
├── visuals/
│   ├── funnel_chart.png / .html
│   ├── campaign_comparison.png
│   ├── ab_test_open_rate.png
│   ├── heatmap_device_region.png
│   ├── segment_conversion.png
│   └── time_series_trend.png
├── dashboard/
│   └── README.md   (Power BI / Tableau build guide)
├── INSIGHTS.md
├── requirements.txt
└── README.md
```

## 🔗 Connect
- **GitHub:** https://github.com/your-username
- **LinkedIn:** https://linkedin.com/in/your-profile

*Replace the links above with your own profile URLs.*
