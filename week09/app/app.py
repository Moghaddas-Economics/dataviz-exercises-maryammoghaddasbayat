#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 19:33:35 2026

@author: dina.deifallah
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# Page configuration, title and data source
st.set_page_config(page_title="World Happiness Report", page_icon="🌐", layout='wide')
st.title("🌍 World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

# Data Ingestion
DATA = Path(__file__).resolve().parent.parent / "data" / "world_happiness_2023.csv"


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df.columns = ['Country','Region','Score','GDP','Social_Support',
                  'Life_Expectancy','Freedom','Generosity','Corruption']
    return df


df = load_data(DATA)

FACTORS = {'GDP': 'Logged GDP per Capita',
           'Social_Support': 'Social Support',
           'Life_Expectancy': 'Healthy Life Expectancy',
           'Freedom': 'Freedom to Make Life Choices',
           'Generosity': 'Generosity',
           'Corruption': 'Perceptions of Corruption'}

# Side bar filters
with st.sidebar:
    st.header("Filters")
    regions = ['All Regions'] + sorted(df['Region'].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Show top N", 5, 25, 15)
    factor = st.selectbox("Compare score with", list(FACTORS), format_func=FACTORS.get)


# filter data by region and top_n
filtered = df if selected_region == 'All Regions' else df[df['Region'] == selected_region]
top = filtered.nlargest(top_n, 'Score').sort_values('Score')

# KPI row
col1, col2, col3 = st.columns(3)
col1.metric("Countries", len(filtered))
col2.metric("Avg Score", f"{filtered['Score'].mean():.2f}",
            f"{filtered['Score'].mean()-df['Score'].mean():+.2f} vs global")
col3.metric("Happiest", filtered.nlargest(1,'Score')['Country'].values[0])

st.divider()

# create top bar chart
fig = px.bar(top, x='Score', y='Country', orientation='h',
             labels={'Score': 'Happiness Score (0–10)', 'Country': ''},
             template='plotly_white',
             title=f'Happiest {len(top)} Countries in 2023 - {selected_region}')

fig.update_layout(title_font=dict(family='Arial', size=13, color='slategrey'),
                  xaxis=dict(range=[0, 8.0]), height=600)

st.plotly_chart(fig, width='stretch')

st.divider()

# New feature: relationship between happiness score and a chosen factor
st.subheader(f"Happiness Score vs {FACTORS[factor]}")

fig2 = px.scatter(filtered, x=factor, y='Score', hover_name='Country',
                  color='Region',
                  labels={factor: FACTORS[factor], 'Score': 'Happiness Score (0–10)'},
                  template='plotly_white')
fig2.update_traces(marker=dict(size=10))

st.plotly_chart(fig2, width='stretch')

if len(filtered) > 2:
    corr = filtered[factor].corr(filtered['Score'])
    st.write(f"Correlation: **{corr:+.2f}** across {len(filtered)} countries "
             "(+1 or -1 is a strong linear link, 0 is none). "
             "Correlation does not show cause.")

# New feature: view and download the filtered data
with st.expander("View filtered data"):
    st.dataframe(filtered, width='stretch', hide_index=True)
    st.download_button("Download CSV", filtered.to_csv(index=False),
                       file_name="happiness_filtered.csv", mime="text/csv")

st.divider()
st.caption("Built with Streamlit + Plotly")
