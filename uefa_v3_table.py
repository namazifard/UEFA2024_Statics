import streamlit as st
import pandas as pd
import base64
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

# Function to load data from the URL
@st.cache_data
def load_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

# Function to parse group data
def parse_group_data(soup):
    groups = soup.find_all('div', class_='group')
    data = []
    for group in groups:
        group_name = group.find('span', class_='group-name').text.strip()
        group_name = group_name.replace('گروه', 'Group').strip()
        team_items = group.find_all('div', class_='team-item')
        for team in team_items:
            team_name = team.find('div', class_='team-name').text.strip()
            team_score = team.find('div', class_='team-score').text.strip()
            data.append([group_name, team_name, team_score])
    df = pd.DataFrame(data, columns=['Group', 'Team', 'Points'])
    return df

# Function to parse detailed group data
def parse_detailed_group_data(soup):
    detailed_groups = soup.find_all('div', class_='group-complete-info')
    data = []
    for group in detailed_groups:
        group_name = group.find('span', class_='group-name').text.strip()
        group_name = group_name.replace('گروه', 'Group').strip()
        rows = group.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            rank = cols[0].text.strip()
            team_name = cols[1].text.strip()
            matches = cols[2].text.strip()
            wins = cols[3].text.strip()
            draws = cols[4].text.strip()
            losses = cols[5].text.strip()
            goals_diff = cols[6].text.strip()
            goal_difference = cols[7].text.strip()
            points = cols[8].text.strip()
            data.append([group_name, rank, team_name, matches, wins, draws, losses, goals_diff, goal_difference, points])
    df = pd.DataFrame(data, columns=['Group', 'Rank', 'Team', 'Matches', 'Wins', 'Draws', 'Losses', 'Goals', 'Goal Difference', 'Points'])
    return df

# Load data
url = "https://www.varzesh3.com/football/%D8%AC%D8%A7%D9%85-%D9%85%D9%84%D8%AA-%D9%87%D8%A7%DB%8C-%D8%A7%D8%B1%D9%88%D9%BE%D8%A7-2024"
soup = load_data(url)
df_all_groups = parse_group_data(soup)
df_detailed_groups = parse_detailed_group_data(soup)

# Sidebar for group selection
group_selection = st.sidebar.selectbox('Choose a Group', sorted(df_detailed_groups['Group'].unique()) + ['All'])

# Filter data based on group selection
if group_selection == 'All':
    df_group_data = df_detailed_groups
else:
    df_group_data = df_detailed_groups[df_detailed_groups['Group'] == group_selection]

# Calculate additional statistics for each group
group_stats = df_detailed_groups.groupby('Group').apply(lambda df: pd.Series({
    'Total Matches': df['Matches'].astype(int).sum() / 2,
    'Total Goals': df['Goals'].str.split('-').apply(lambda x: int(x[0]) + int(x[1]) if len(x) > 1 else 0).sum() / 2,
}))

group_stats['Average Goals per Match'] = group_stats['Total Goals'] / group_stats['Total Matches']

# Display group data and statistics
st.header(f'Teams Stats of {group_selection}')
# st.write(f'Data Dimension: {df_group_data.shape[0]} rows and {df_group_data.shape[1]} columns.')
if group_selection != "All":
    st.dataframe(df_group_data)

st.write(f'Total Matches Played: {int(group_stats["Total Matches"].sum()) if group_selection == "All" else int(group_stats.loc[group_selection, "Total Matches"])}')
st.write(f'Total Goals Scored: {int(group_stats["Total Goals"].sum()) if group_selection == "All" else int(group_stats.loc[group_selection, "Total Goals"])}')
st.write(f'Average Goals per Match: {group_stats["Average Goals per Match"].mean() if group_selection == "All" else group_stats.loc[group_selection, "Average Goals per Match"]:.2f}')

# Plotting the total goals scored in each group
if group_selection == "All":
    fig, ax = plt.subplots()
    group_stats['Total Goals'].plot(kind='bar', ax=ax, color='lightblue')
    ax.set_title('Total Goals Scored in Each Group')
    ax.set_xlabel('')
    ax.set_ylabel('Total Goals')
    ax.set_xticklabels(group_stats.index, rotation=0)  # Ensure group labels are properly displayed
    st.pyplot(fig)

# Plotting the average goals scored per match in each group
if group_selection == "All":
    fig, ax = plt.subplots()
    group_stats['Average Goals per Match'].plot(kind='bar', ax=ax, color='lightgreen')
    ax.set_title('Average Goals Scored per Match in Each Group')
    ax.set_xlabel('')
    ax.set_ylabel('Average Goals per Match')
    ax.set_xticklabels(group_stats.index, rotation=0)  # Ensure group labels are properly displayed
    st.pyplot(fig)

# Function to download data
def filedownload(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV File</a>'
    return href

# st.markdown(filedownload(df_group_data, f'group_{group_selection}_stats'), unsafe_allow_html=True)