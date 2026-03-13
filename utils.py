import streamlit as st
import pandas as pd
import datetime

# --- SITE MAPPING ---
id_map = {
    75022: 'metasrc.com',
    75195: 'futurism.com',
    76970: 'fortnite.gg',
    74058: 'monkeytype.com',
    75188: 'popsci.com',
    75190: 'thedrive.com',
    75946: 'wordplays.com',
    74804: 'twistedsifter.com'
}


# --- DATA LOADERS ---

@st.cache_data
def get_data():
    """Loads and cleans the primary Z-score metrics data."""
    df = pd.read_csv("data.csv", encoding='utf-8-sig')
    df.columns = [col.lower() for col in df.columns]

    # Clean up dates and map IDs
    df['date_et'] = pd.to_datetime(df['date_et']).dt.date
    df['website_id'] = pd.to_numeric(df['website_id'], errors='coerce')
    df['site_name'] = df['website_id'].map(id_map)

    return df

#
# @st.cache_data
# def get_price_data():
#     """Loads, cleans, and bins the price floor animation data."""
#     df = pd.read_csv("price_floor_data.csv", encoding='utf-8-sig')
#     df.columns = [col.lower() for col in df.columns]
#
#     df['website_id'] = pd.to_numeric(df['website_id'], errors='coerce')
#     df['site_name'] = df['website_id'].map(id_map)
#     df['price_floor'] = pd.to_numeric(df['price_floor'], errors='coerce')
#
#     # 1. Define the exact numeric boundaries for your bins
#     bins = [0, 0.06, 0.15, 0.30, 0.40, 0.60, 1.50, 3.00, float('inf')]
#
#     # 2. Define the clean text labels for the chart X-axis
#     labels = [
#         '$0.04 - $0.06',
#         '$0.07 - $0.15',
#         '$0.16 - $0.30',
#         '$0.31 - $0.40',
#         '$0.41 - $0.60',
#         '$0.61 - $1.50',
#         '$1.51 - $3.00',
#         '$3.01+'
#     ]
#
#     # 3. Assign every row to a bin
#     df['price_bin'] = pd.cut(df['price_floor'], bins=bins, labels=labels, right=True)
#
#     # 4. Group by Date, Site, Country, and the Bin, then SUM the percentages
#     grouped_df = df.groupby(
#         ['date_et', 'website_id', 'site_name', 'country_group', 'price_bin'],
#         observed=False
#     )['perc_makeup'].sum().reset_index()
#
#     # 5. Convert to 0-100 scale for the chart
#     grouped_df['perc_makeup_pct'] = grouped_df['perc_makeup'] * 100
#
#     # Sort chronologically for the animation
#     grouped_df['date_et'] = grouped_df['date_et'].astype(str)
#     grouped_df = grouped_df.sort_values(by=['date_et', 'price_bin'])
#
#     return grouped_df, labels
@st.cache_data
def get_price_data():
    """Loads, cleans, and bins the price floor animation data using AUCTIONS."""
    df = pd.read_csv("price_floor_data.csv", encoding='utf-8-sig')
    df.columns = [col.lower() for col in df.columns]

    df['website_id'] = pd.to_numeric(df['website_id'], errors='coerce')
    df['site_name'] = df['website_id'].map(id_map)
    df['price_floor'] = pd.to_numeric(df['price_floor'], errors='coerce')

    # --- NEW: Ensure auctions are numeric ---
    df['auctions'] = pd.to_numeric(df['auctions'], errors='coerce').fillna(0)

    # 1. Define the exact numeric boundaries for your bins
    bins = [0, 0.06, 0.15, 0.30, 0.40, 0.60, 1.50, 3.00, float('inf')]

    # 2. Define the clean text labels for the chart X-axis
    labels = [
        '$0.04 - $0.06',
        '$0.07 - $0.15',
        '$0.16 - $0.30',
        '$0.31 - $0.40',
        '$0.41 - $0.60',
        '$0.61 - $1.50',
        '$1.51 - $3.00',
        '$3.01+'
    ]

    # 3. Assign every row to a bin
    df['price_bin'] = pd.cut(df['price_floor'], bins=bins, labels=labels, right=True)

    # 4. Group by Date, Site, Country, and Bin, then SUM the AUCTIONS
    grouped_df = df.groupby(
        ['date_et', 'website_id', 'site_name', 'country_group', 'price_bin'],
        observed=False
    )['auctions'].sum().reset_index()

    # 5. --- NEW: Calculate True Daily Percentage ---
    # Find the total auctions for that specific day/site/country combination
    grouped_df['total_auctions'] = grouped_df.groupby(
        ['date_et', 'website_id', 'country_group']
    )['auctions'].transform('sum')

    # Divide the bin auctions by the total daily auctions
    # We use .fillna(0) to prevent division-by-zero errors on days with 0 traffic
    grouped_df['perc_makeup_pct'] = (grouped_df['auctions'] / grouped_df['total_auctions'] * 100).fillna(0)

    # Sort chronologically for the animation
    grouped_df['date_et'] = grouped_df['date_et'].astype(str)
    grouped_df = grouped_df.sort_values(by=['date_et', 'price_bin'])

    return grouped_df, labels


@st.cache_data
def get_session_data():
    """Loads the hourly session type distribution data."""
    df = pd.read_csv("session_data.csv", encoding='utf-8-sig')
    df.columns = [col.lower() for col in df.columns]

    # Map the IDs to names so our dropdowns work
    df['website_id'] = pd.to_numeric(df['website_id'], errors='coerce')
    df['site_name'] = df['website_id'].map(id_map)

    # Ensure dt_et is treated as a true Datetime object for the X-axis
    df['dt_et'] = pd.to_datetime(df['dt_et'])

    return df


@st.cache_data
def get_arm_data():
    """Loads the ML Arm price floor distribution data."""
    df = pd.read_csv("arm_distribution_data.csv", encoding='utf-8-sig')
    df.columns = [col.lower() for col in df.columns]

    # Map IDs to site names
    df['website_id'] = pd.to_numeric(df['website_id'], errors='coerce')
    df['site_name'] = df['website_id'].map(id_map)

    # Define standard sorting order for the bins so they don't get scrambled
    bin_order = [
        '$0.04 - $0.06', '$0.07 - $0.15', '$0.16 - $0.30',
        '$0.31 - $0.40', '$0.41 - $0.60', '$0.61 - $1.50',
        '$1.51 - $3.00', '$3.01+'
    ]
    df['price_bin'] = pd.Categorical(df['price_bin'], categories=bin_order, ordered=True)

    return df

# --- HELPER FUNCTIONS ---

def highlight_experiment_dates(val):
    """Highlights dates on or after March 2, 2026, in bright pink."""
    try:
        val_date = pd.to_datetime(val).date()
        experiment_start = datetime.date(2026, 3, 2)

        if val_date >= experiment_start:
            # Bright pink background, white text
            return 'background-color: #FF1493; color: white; font-weight: bold;'
    except:
        pass
    return ''