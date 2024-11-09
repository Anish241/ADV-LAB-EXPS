import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(page_title="Cholera Analysis Dashboard", layout="wide")

# Function to load data
@st.cache_data
def load_data():
    # In practice, you would read from a CSV file
    data = pd.read_csv("data.csv")
    return data

# Load the data
df = load_data()

# Dashboard Title
st.title("📊 Cholera Analysis Dashboard")
st.markdown("---")

# Sidebar filters
st.sidebar.header("Filters")
selected_years = st.sidebar.multiselect(
    "Select Years",
    options=df['Year'].unique(),
    default=df['Year'].unique()
)

# Filter the dataframe
filtered_df = df[df['Year'].isin(selected_years)]

# Create two columns for the first row
col1, col2 = st.columns(2)

with col1:
    st.subheader("Cases Over Time")
    fig_cases = px.line(filtered_df, 
                       x='Year', 
                       y='Number of reported cases of cholera',
                       markers=True,
                       title='Reported Cholera Cases Trend')
    fig_cases.update_layout(height=400)
    st.plotly_chart(fig_cases, use_container_width=True)
    
    # Observations
    st.markdown("""
    **Key Observations:**
    - Dramatic spike in cases during 2011 (~340k cases)
    - Second highest peak in 1991 (~322k cases)
    - Generally lower cases in other years
    """)

with col2:
    st.subheader("Deaths Over Time")
    fig_deaths = px.bar(filtered_df, 
                       x='Year', 
                       y='Number of reported deaths from cholera',
                       title='Reported Deaths by Year')
    fig_deaths.update_layout(height=400)
    st.plotly_chart(fig_deaths, use_container_width=True)
    
    st.markdown("""
    **Key Observations:**
    - Highest number of deaths (~124k) recorded in 1953
    - Despite high cases in 1953, deaths remained relatively low
    """)

# Create two columns for the second row
col3, col4 = st.columns(2)

with col3:
    st.subheader("Cases vs Deaths Scatter Plot")
    fig_scatter = px.scatter(filtered_df, 
                           x='Number of reported cases of cholera',
                           y='Number of reported deaths from cholera',
                           size='Cholera case fatality rate',
                           hover_data=['Year'],
                           title='Correlation between Cases and Deaths')
    fig_scatter.update_layout(height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("""
    **Key Observations:**
    - No clear linear relationship between cases and deaths
    - Higher number of cases doesn't necessarily lead to higher deaths
    - Bubble size represents fatality rate
    """)

with col4:
    st.subheader("Fatality Rate Analysis")
    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(
        x=filtered_df['Year'],
        y=filtered_df['Cholera case fatality rate'],
        fill='tozeroy',
        name='Fatality Rate'
    ))
    fig_area.update_layout(title='Fatality Rate Trend Over Time',
                          height=400)
    st.plotly_chart(fig_area, use_container_width=True)
    
    st.markdown("""
    **Key Observations:**
    - Highest fatality rate observed in 1998
    - Sharp decline in fatality rate during 2014-2015 despite high cases
    - Variable trend throughout the years
    """)

# Advanced Visualizations
st.markdown("---")
st.header("Advanced Visualizations")

col5, col6 = st.columns(2)

with col5:
    st.subheader("Box Plot of Cases by Year Range")
    fig_box = px.box(filtered_df, 
                     y='Number of reported cases of cholera',
                     title='Distribution of Cases')
    fig_box.update_layout(height=400)
    st.plotly_chart(fig_box, use_container_width=True)

with col6:
    st.subheader("3D Scatter Plot")
    fig_3d = px.scatter_3d(filtered_df, 
                          x='Year',
                          y='Number of reported cases of cholera',
                          z='Number of reported deaths from cholera',
                          color='Cholera case fatality rate',
                          title='3D Analysis of Cases, Deaths, and Fatality Rate')
    fig_3d.update_layout(height=400)
    st.plotly_chart(fig_3d, use_container_width=True)

# Summary Statistics
st.markdown("---")
st.header("Summary Statistics")
col7, col8, col9 = st.columns(3)

with col7:
    st.metric("Average Cases per Year", 
              f"{int(filtered_df['Number of reported cases of cholera'].mean()):,}")

with col8:
    st.metric("Average Deaths per Year", 
              f"{filtered_df['Number of reported deaths from cholera'].mean():.2f}")

with col9:
    st.metric("Average Fatality Rate", 
              f"{filtered_df['Cholera case fatality rate'].mean():.2%}")

# Show raw data
st.markdown("---")
if st.checkbox("Show Raw Data"):
    st.dataframe(filtered_df)