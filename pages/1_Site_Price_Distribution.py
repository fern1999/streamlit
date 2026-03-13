import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_price_data, id_map, get_session_data, get_arm_data

st.set_page_config(layout="wide", page_title="Site Price Distribution")

st.title("Price Floor Distribution by Website")
st.markdown("""
#### Distribution of Price Floors between March 2, 2026 and March 9, 2026
After running the new price floor service for a week on a select number of sites, we wanted to determine 
how price floors were being distributed for each site. We used first-party data for this analysis. 

Some notable findings were that the price floor service was recommending particularly low floors on a select 
number of sites. Most notably **fortnite.gg** and **monkeytype.com**, where the lowest bin of price floors 
(all floors between \$0.04 and \$0.06 inclusive) accounted for 79% and 70% of all floors, respectively.
Questions were raised about whether or not this was enough price pressure.

For other sites, such as **futurism.com** and **thedrive.com**, floors were more evenly distributed across all bin types.

""")
try:
    # 1. Load Data
    price_df, bin_labels = get_price_data()

    # --- SECTION 1: USER SELECTED SITE ---
    all_sites = sorted([name for name in id_map.values() if pd.notna(name)])
    chosen_site = st.selectbox(
        "Select a Website to View its Distribution of Price Floors between March 2 and March 9, 2026", all_sites)
    # --- THE FIX: Add the date filter here so it matches the text and the bottom graph ---
    site_df = price_df[
        (price_df['site_name'] == chosen_site) &
        (price_df['date_et'] >= '2026-03-02') &
        (price_df['date_et'] <= '2026-03-09')
        ]

    if site_df.empty:
        st.warning(f"No data available for {chosen_site}.")
    else:
        # Sum the raw auctions for each bin across the ENTIRE dataset for this site
        dist_df = site_df.groupby('price_bin', observed=False)['auctions'].sum().reset_index()

        # Calculate the true weighted percentage
        total_site_auctions = dist_df['auctions'].sum()
        if total_site_auctions > 0:
            dist_df['perc_makeup_pct'] = (dist_df['auctions'] / total_site_auctions) * 100
        else:
            dist_df['perc_makeup_pct'] = 0

        fig1 = px.bar(
            dist_df,
            x="price_bin",
            y="perc_makeup_pct",
            category_orders={"price_bin": bin_labels},
            range_y=[0, 100],  # --- ADDED: Locks Y-axis to 100 ---
            labels={"price_bin": "Price Floor Range", "perc_makeup_pct": "Percentage of Total Auctions (%)"},
            title=f"Price Floor Distribution for {chosen_site} - March 2 - March 9, 2026"
        )

        fig1.update_traces(marker_color='#1f77b4')
        fig1.update_xaxes(tickangle=-45)

        st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    st.markdown("""
    We wanted to determine what could be causing low floors. We came up with several hypotheses:

    1. The multi-arm bandit could be assigning an excessive amount of traffic to our control arm.
    2. The risk level for each arm could be too low.
    3. Potentially, there could be a client-side bug resulting in GAM ignoring the recommended floor.
    """)

    st.markdown("""
    #### Investigating First Hypothesis
    As mentioned, a possible reason for the low floors could be that the multi-arm bandit was allocating an excessive amount of traffic to our control arm.
    Our control arm is set to use the minimum floors - which is \$0.04 for display and \$0.16 for video.
    To determine if this was the case, we determined the percentage each arm accounted for the site's traffic.

    Generally, we saw that the control arm ("case0") was not dominating the majority of traffic. This was also true for fortnite.gg and monkeytype.com - which were the sites that saw the highest frequency of low floors.
    """)
    # Load the new data
    session_df = get_session_data()

    # --- NEW: Independent Dropdown ---
    # We use a unique label and a specific 'key' so it doesn't sync with Section 1
    chosen_session_site = st.selectbox(
        "Select a Website for Session Analysis",
        all_sites,
        key="session_site_dropdown"
    )

    # Filter by the newly selected, independent site
    site_session_df = session_df[session_df['site_name'] == chosen_session_site].copy()

    if site_session_df.empty:
        st.warning(f"No session data available for {chosen_session_site}.")
    else:
        # Plotly Area Chart
        fig3 = px.area(
            site_session_df,
            x="dt_et",
            y="perc_makeup",
            color="session_type",
            labels={
                "dt_et": "Date / Time",
                "perc_makeup": "Percentage Makeup (%)",
                "session_type": "Session Type"
            },
            title=f"Area Chart of Session Distribution for {chosen_session_site} - March 2 - March 9, 2026"
        )

        # Lock Y-axis to 100% for a clean, full-height area chart
        fig3.update_layout(yaxis_range=[0, 100])

        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    #### Summary for Investigating the First Hypothesis
    The amount of traffic being allocated to the control arm ("case0") did not account for the high percentage of low price floors for fortnite.gg and monkeytype.com.
    This led us to think that perhaps the low floors were not only a result of the control arm, but potentially from the other arms as well.
    In the second investigation, we determined the distribution of floors by each arm and whether or not the preset risk level was too low.
    """)

    ####-----
    st.divider()

    st.markdown("""
    #### Investigating Second Hypothesis
    From our first hypothesis, we saw that the control arm was not dominating traffic. We hypothesized that potentially the other arms ("case1", "case2", "case3") were outputting low price floors.
    For this analysis, we compared the distribution of price floors for each website x arm. 
    """)

    # Load the new arm dataset
    arm_df = get_arm_data()

    if arm_df.empty:
        st.warning("No ML Arm data available.")
    else:
        # # --- THE TABLE ---
        # st.subheader("Tabular View: Distribution of Floors for Each Arm")
        #
        # # Pivot the data: Rows = Site & Bin, Columns = Arm, Values = Percentage
        # pivot_df = arm_df.pivot_table(
        #     index=['site_name', 'price_bin'],
        #     columns='arm',
        #     values='perc_makeup',
        #     fill_value=0
        # )
        #
        # # Apply a background gradient so differences pop out immediately
        # styled_table = (pivot_df.style
        #                 .background_gradient(cmap='Blues', axis=1)  # Highlights the highest value in each row
        #                 .format("{:.2f}%")
        #                 )
        #
        # st.dataframe(styled_table, use_container_width=True, height=400)

        # --- THE VISUAL CHART ---
        st.markdown("""
        ###### Visual View: Compare Arms by Site""")

        # Re-use the all_sites list to let the user pick a site to inspect
        chosen_arm_site = st.selectbox(
            "Select a Website to compare ML Arms",
            all_sites,
            key="arm_site_dropdown"
        )

        site_arm_df = arm_df[arm_df['site_name'] == chosen_arm_site].copy()

        if site_arm_df.empty:
            st.warning(f"No ML Arm data for {chosen_arm_site}.")
        else:
            # Grouped Bar Chart to show the arms side-by-side per bin
            fig4 = px.bar(
                site_arm_df,
                x="price_bin",
                y="perc_makeup",
                color="arm",  # This creates the side-by-side columns!
                barmode="group",  # Groups them together by bin
                labels={
                    "price_bin": "Price Floor Range",
                    "perc_makeup": "Percentage of Auctions (%)",
                    "arm": "ML Arm (Session Type)"
                },
                title=f"Arm Distribution Comparison for {chosen_arm_site}"
            )

            fig4.update_layout(yaxis_range=[0, 100])
            fig4.update_xaxes(tickangle=-45)

            st.plotly_chart(fig4, use_container_width=True)

            st.markdown("""
            If we compare the distribution of price floors between arms, we can see the following expected pattern:
            * The control has a really high percentage of low price floors (+90%). This is expected as the control arm is only outputting \$0.04 and \$0.16 price floors.
            * For fortnite.gg, we see that all 3 test arms ("case1", "case2", "case3") are outputting low-bin price floors at least 60% of the time. 

            """)

            st.markdown("""
            If we look at the distribution of price floors for US traffic, we see about 45% of auctions were using low-bin price floors.
            Conversely, if we look at the distribution of price floors for GDPR traffic, we see about 91% of auctions were using low-bin price floors.
            This suggests that segments under GDPR countries were responsible for the really high percentage of low-bin price floors.
            """)
            # 1. Create two columns
            col1, col2 = st.columns(2)  # Passing 2 creates two equal-width columns

            # 2. Place the US image in the first column
            with col1:
                # Display the US image
                st.image(
                    "fortnite_x_us_x_price_floor_distribution_march7.png",
                    caption="Distribution of winning bids for Fortnite.gg in the USA.",
                    use_container_width=True  # This is crucial! Makes the image scale to the column width.
                )
                # optional: add the commentary text directly in the column
                # st.write("""When you isolate USA traffic, we see that percentage of low-bin price floors decreases to about 46%.  """)

            # 3. Place the GDPR image in the second column
            with col2:
                # Display the GDPR image
                st.image(
                    "fortnite_x_gdpr_x_price_floor_distribution_march7.png",
                    caption="Distribution of winning bids for Fortnite.gg in GDPR countries.",
                    use_container_width=True  # This is crucial! Makes the image scale to the column width.
                )
            # st.write(
            #     """When you isolate traffic from GDPR countries, we see that percentage of low-bin price floors increases to 91%.""")

            st.markdown("""
            ###### Why are price floors for segments under GDPR countries low?
            The reason why the price floors for segments under GDPR countries are low is that a lot of these countries have a lot of revenue concentrated at the lower end of price point values (winning bid values, not price floors).
            The top graph in the static image below shows the distribution of revenue for a GDPR country - Poland - at various different price point values (winning bid values).
            Notice how there is a large peak at the \$0.04 price point.

            If we look at the corresponding risk-curve chart (which shows the accumulation of revenue as price points increase), we see that historically 3% of revenue
            was obtained at the \$0.04 price point. The implication of this is that this segment has revenue front-loaded to the lowest price points; therefore, in order to apply pressure,
            we must increase the risk level.
            """)
            # Display the image
            st.image(
                "fortnite_poland_winning_bid_distribution.png",
                caption="Distribution of winning bids for Fortnite.gg in Poland.",
                use_container_width=True  # This makes the image cleanly fill the column/screen width!
            )

            # --- NEW SECTION: PRE VS POST INCREASE COMPARISON ---
            st.divider()
            st.header("Price Floor Comparison: Pre vs. Post Increase")
            st.markdown("""
            After identifying that certain segments required more price pressure, we increased the risk levels. 
            The charts below compare the distribution of price floors **before** the increase (March 2–9) 
            and **after** the increase (March 10–12).
            Notice how for the site fortnite.gg, the usage of the lowest price floor bin decreased from 78% to 42%, and 
            for the site monkeytype.com, the usage decreased from 70% to 50%.
            We also see an increase in usage of higher price floor bins.
            """)

            # User selection for the comparison
            chosen_compare_site = st.selectbox(
                "Select a Website to Compare Date Ranges",
                all_sites,
                key="compare_site_dropdown"
            )

            # Filter Data for the two specific periods
            pre_increase_df = price_df[
                (price_df['site_name'] == chosen_compare_site) &
                (price_df['date_et'] >= '2026-03-02') &
                (price_df['date_et'] <= '2026-03-09')
                ]

            post_increase_df = price_df[
                (price_df['site_name'] == chosen_compare_site) &
                (price_df['date_et'] >= '2026-03-10') &
                (price_df['date_et'] <= '2026-03-12')
                ]


            # Helper function to process the distribution
            def get_dist(df):
                if df.empty:
                    return pd.DataFrame()
                dist = df.groupby('price_bin', observed=False)['auctions'].sum().reset_index()
                total = dist['auctions'].sum()
                dist['perc_makeup_pct'] = (dist['auctions'] / total) * 100 if total > 0 else 0
                return dist


            pre_dist = get_dist(pre_increase_df)
            post_dist = get_dist(post_increase_df)

            # Layout: Two columns for side-by-side graphs
            comp_col1, comp_col2 = st.columns(2)

            with comp_col1:
                if not pre_dist.empty:
                    fig_pre = px.bar(
                        pre_dist,
                        x="price_bin",
                        y="perc_makeup_pct",
                        category_orders={"price_bin": bin_labels},
                        range_y=[0, 100],
                        title="March 2 - March 9 (Baseline)",
                        labels={"price_bin": "Price Bin", "perc_makeup_pct": "% of Auctions"}
                    )
                    fig_pre.update_traces(marker_color='#1f77b4')
                    st.plotly_chart(fig_pre, use_container_width=True)
                else:
                    st.info("No data for March 2-9")

            with comp_col2:
                if not post_dist.empty:
                    fig_post = px.bar(
                        post_dist,
                        x="price_bin",
                        y="perc_makeup_pct",
                        category_orders={"price_bin": bin_labels},
                        range_y=[0, 100],
                        title="March 10 - March 12 (Post-Increase)",
                        labels={"price_bin": "Price Bin", "perc_makeup_pct": "% of Auctions"}
                    )
                    fig_post.update_traces(marker_color='#2ca02c')  # Different color for distinction
                    st.plotly_chart(fig_post, use_container_width=True)
                else:
                    st.info("No data for March 10-12")


except Exception as e:
    st.error(f"Error: {e}")