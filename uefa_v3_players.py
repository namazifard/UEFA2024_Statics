import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import requests
from bs4 import BeautifulSoup

# App title and description
st.title('UEFA Euro 2024 Football Stats Explorer by Danial Namazifard')
st.markdown("""
This app performs simple webscraping of UEFA Euro 2024 football player stats!
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, requests, BeautifulSoup
* **Data source:** [varzesh3.com](https://www.varzesh3.com/football/%D8%AC%D8%A7%D9%85-%D9%85%D9%84%D8%AA-%D9%87%D8%A7%DB%8C-%D8%A7%D8%B1%D9%88%D9%BE%D8%A7-2024).
""")

# Function to load data
@st.cache_data
def load_data():
    url = "https://www.varzesh3.com/football/%D8%AC%D8%A7%D9%85-%D9%85%D9%84%D8%AA-%D9%87%D8%A7%DB%8C-%D8%A7%D8%B1%D9%88%D9%BE%D8%A7-2024"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract player data
    player_sections = soup.find_all('div', class_='top-player')
    data = []
    for section in player_sections:
        player_name = section.find('div', class_='player-name').text.strip()
        country_name = section.find('div', class_='player-country-name').text.strip()
        goals = section.find('div', class_='player-score').text.strip().split()[0]
        data.append([player_name, country_name, goals])

    df = pd.DataFrame(data, columns=['Player', 'Country', 'Goals'])
    return df

playerstats = load_data()

# Sidebar for team selection
st.sidebar.header('Select Teams')
sorted_unique_team = sorted(playerstats['Country'].unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)

# Filter data based on selections
df_selected_team = playerstats[playerstats['Country'].isin(selected_team)]

# Display filtered data
st.header('Display Player Stats of Selected Team(s)')
st.write(f'Data Dimension: {df_selected_team.shape[0]} rows and {df_selected_team.shape[1]} columns.')
st.dataframe(df_selected_team)

# Function to calculate and display statistics
def display_statistics(df):
    df['Goals'] = pd.to_numeric(df['Goals'], errors='coerce')
    total_goals = df.groupby('Country')['Goals'].sum().reset_index()
    total_goals.columns = ['Country', 'Total Goals']
    
    st.header('Total Goals by Team')
    st.dataframe(total_goals)
    
    overall_total_goals = df['Goals'].sum()
    st.header(f'Total Number of Goals Scored: {overall_total_goals}')
    
    return total_goals, overall_total_goals

# Display statistics
if not df_selected_team.empty:
    total_goals_df, overall_total_goals = display_statistics(df_selected_team)

# Function to download data
def filedownload(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team, 'playerstats'), unsafe_allow_html=True)
if not df_selected_team.empty:
    st.markdown(filedownload(total_goals_df, 'total_goals'), unsafe_allow_html=True)

# # Heatmap
# if st.button('Intercorrelation Heatmap'):
#     st.header('Intercorrelation Matrix Heatmap')
#     df_selected_team.to_csv('output.csv', index=False)
#     df = pd.read_csv('output.csv')

#     # Convert Goals column to numeric for correlation calculation
#     df['Goals'] = pd.to_numeric(df['Goals'], errors='coerce')

#     corr = df.corr()
#     mask = np.zeros_like(corr)
#     mask[np.triu_indices_from(mask)] = True
#     with sns.axes_style("white"):
#         f, ax = plt.subplots(figsize=(7, 5))
#         ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
#     st.pyplot()
