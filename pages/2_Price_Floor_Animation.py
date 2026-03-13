import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_price_data, id_map

st.set_page_config(layout="wide", page_title="Price Floor Animation")

st.title("Price Floor Distribution Over Time")

try:
    # 1. Load Data (Returns the dataframe AND the bin labels)
    price_df, bin_labels = get_price_data()

    # 2. User Inputs
    all_sites = sorted([name for name in id_map.values() if pd.notna(name)])

    col1, col2 = st.columns(2)
    with col1:
        chosen_site = st.selectbox("Select a Website", all_sites)

    site_price_df = price_df[price_df['site_name'] == chosen_site]

    if site_price_df.empty:
        st.warning(f"No price floor data available for {chosen_site}.")
    else:
        with col2:
            country_groups = sorted(site_price_df['country_group'].dropna().unique())
            chosen_country = st.selectbox("Select Country Group", country_groups)

        # 3. Process Data
        filtered_df = site_price_df[site_price_df['country_group'] == chosen_country]

        if filtered_df.empty:
            st.warning("No data available for this specific combination.")
        else:
            st.subheader(f"{chosen_country} Binned Price Floors for {chosen_site}")

            # 4. Build the Plotly Animation
            fig = px.bar(
                filtered_df,
                x="price_bin",
                y="perc_makeup_pct",
                animation_frame="date_et",
                range_y=[0, 100],
                category_orders={"price_bin": bin_labels},
                labels={
                    "price_bin": "Price Floor Range",
                    "perc_makeup_pct": "Percentage (%)",
                    "date_et": "Date"
                }
            )

            # Animation Speed Control (1000ms frame, 500ms transition)
            fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 200
            fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 200

            # Styling
            fig.update_traces(marker_color='#1f77b4')
            fig.update_xaxes(
                type='category',
                categoryorder='array',
                categoryarray=bin_labels,
                tickangle=-45
            )

            # 5. Display
            st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")