import streamlit as st
import pandas as pd
from utils import get_data, id_map, highlight_experiment_dates

st.set_page_config(layout="wide", page_title="Site Deep Dive")

st.title("Site Deep Dive")


st.markdown("""
On this page, we can evaluate site performance for one site, using all metrics. 
The dates highlighted in pink indicate when the new price floor service was active. 

Note that the darker the cell, the more statistically significant the deviation. 
Red indicates a drop, and green indicates an increase. 

Please reference the definitions guide below.
""")

with st.expander("Metric Definitions & Guide"):
    st.markdown("""
        **What is a Z-Score?** A Z-Score measures how far a specific day's performance deviates from its historical average. 
        * A score near **0** means performance is exactly as expected.
        * A score of **+2.0 or higher** (Green) indicates a statistically significant spike.
        * A score of **-2.0 or lower** (Red) indicates a statistically significant drop.

        ###  Revenue Metrics
        * **Z_REV_LIFETIME**: Compares today's total revenue against the *entire* available history of the site. 
        * **Z_REV_30D, 60D, 120D, 180D**: Compares today's revenue against the trailing 30, 60, 120, or 180 days. Using different windows helps distinguish between a short-term trend (30D) vs. a long-term trend (180D).
        * **Z_RPS_30D, 60D, 120D, 180D**: Revenue Per Session. If Revenue is down but RPS is normal, the issue is a traffic drop. If RPS is deeply negative, there could be an issue at hand.

        ###  Traffic & Quality Metrics (30-Day Windows)
        * **Z_SESSIONS_30D**: Identifies abnormal spikes or drops in overall traffic volume compared to the last month.
        * **Z_US_CHROME_MIX_30D**: Tracks shifts in a highly profitable user segment (US Desktop Chrome). A sudden negative Z-score could explain a drop in RPS.
        * **Z_DIRECT_MIX_30D**: Tracks changes direct deals.
        """)

try:
    # 1. Load Data
    raw_df = get_data()
    z_metrics = [col for col in raw_df.columns if col.startswith('z_')]

    # 2. User Input
    all_sites = sorted([name for name in id_map.values() if pd.notna(name)])
    chosen_site = st.selectbox("Select a Website", all_sites)

    # 3. Process Data
    site_df = raw_df[raw_df['site_name'] == chosen_site].copy()
    display_df = site_df[['date_et'] + z_metrics].sort_values('date_et', ascending=False)

    st.subheader(f"All Z-Scores for {chosen_site}")

    # 4. Styling
    styled_df = (display_df.style
                 .background_gradient(cmap='RdYlGn', subset=z_metrics, axis=None, vmin=-4.0, vmax=4.0)
                 .format("{:.2f}", subset=z_metrics, na_rep="-")
                 .map(highlight_experiment_dates, subset=['date_et']))

    # 5. Display
    st.dataframe(styled_df, use_container_width=True, height=700, hide_index=True)

except Exception as e:
    st.error(f"Error: {e}")
