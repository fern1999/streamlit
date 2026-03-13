import streamlit as st

st.set_page_config(layout="wide", page_title="Executive Summary")

st.title("Price Floor Service Test: March 2-12")

st.markdown("""
### Executive Summary
Between March 2 and March 12, 2026, we ran a test of the new price floor service across a select group of sites. 
This dashboard provides a high-level overview of the test's impact on yield and how the multi-arm bandit distributed price floors. 

Initially, we saw that the service was recommending particularly low floors (between \$0.04 and \$0.06) for a high percentage of traffic on sites like **fortnite.gg** and **monkeytype.com**, specifically for segments in GDPR countries. After investigating, we determined the risk levels for these segments needed to be increased to apply enough price pressure. We applied these changes on March 10.
Afterward, we saw a wider distribution of price floors.

When looking at the global comparison, there have generally been no statistically significant changes in performance before and after the test. Pre-test, we can see that general long-term and medium-term trends have continued.

Please select a tool from the sidebar on the left, or click one of the quick-links below to explore the analysis.
""")

st.divider()

# Create clean, clickable cards on the landing page in the requested order
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("1. Site Price Distribution")
    st.write("Analyze how price floors were distributed for each site, and compare the distributions before and after we increased the risk levels.")
    st.page_link("pages/1_Site_Price_Distribution.py", label="Go to Distributions")

with col2:
    st.subheader("2. Animations")
    st.write("Watch an animated view of how price floor distributions shifted day by day. This helps visualize how the models adjusted over time for specific country groups.")
    st.page_link("pages/2_Price_Floor_Animation.py", label="Go to Animations")

with col3:
    st.subheader("3. Global View")
    st.write("Get a high-level view of site performance across different revenue and traffic metrics to easily spot anomalies. Generally, green is good (a spike) and red is bad (a drop).")
    st.page_link("pages/3_Global_Comparison.py", label="Go to Global")

with col4:
    st.subheader("4. Site Deep Dive")
    st.write("Look at all Z-Score metrics for a single specific property. Useful for isolating if a drop in revenue was caused by a drop in yield (RPS) or just a drop in traffic.")
    st.page_link("pages/4_Site_Deep_Dive.py", label="Go to Deep Dive")