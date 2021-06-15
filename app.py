import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request

import streamlit as st
import plotly.express as px

st.set_page_config(layout="wide")

asset_path = './assets/'

def get_html_soup(url):
    """Uses Beautiful Soup to extract html from a url. Returns a soup object """
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/56.0.2924.87 Safari/537.36'}
    req = Request(url, headers=headers)
    get_html_soup = BeautifulSoup(urlopen(req).read(), 'html.parser')
    return get_html_soup


def find_group_rows(group_soup):
    group_rows = group_soup.find_all('tr', {'class': 'standing-table__row'})[1:]
    return group_rows


def clean_text(team_row):
    clean_row = [i for i in team_row.text.split('\n') if len(i) > 0]
    return clean_row


def get_table(group_soup_tuple):
    columns = ['group_position', 'country', 'played', 'won', 'drawn', 'lost', 'goals_for',
               'goals_against', 'goal_difference', 'points']

    x = []
    for row in find_group_rows(group_soup_tuple[0]):
        x.append(clean_text(row))

    table = pd.DataFrame(x, columns=columns)
    table['group'] = group_soup_tuple[1]
    return table

# @st.cache
def recent_results_sidebar():
    results_soup = get_html_soup('https://www.skysports.com/euro-2020-results')

    days = results_soup.find_all('div', {'class': 'fixres__item'})

    left_team_class = 'matches__item-col matches__participant matches__participant--side1'
    score_class = 'matches__item-col matches__status'
    right_team_class = 'matches__item-col matches__participant matches__participant--side2'
    res = []
    for day in days:
        left_team = day.find('span', {'class': left_team_class}).find('span', {'class': 'swap-text__target'}).text
        right_team = day.find('span', {'class': right_team_class}).find('span', {'class': 'swap-text__target'}).text
        score_data = day.find('span', {'class': score_class}).find_all('span', {'class': 'matches__teamscores-side'})
        left_score = score_data[0].text.split()[0]
        right_score = score_data[1].text.split()[0]
        result = [left_team, left_score, right_score, right_team]
        res.append(result)

    df_results = pd.DataFrame(res)

    return df_results


def plot_editing(fig, title, x_title, y_title, height=900, width=700):

    fig.update_layout(title=title)
                      # paper_bgcolor='rgba(0,0,0,0)',
                      # plot_bgcolor='rgba(0,0,0,0)',)
    fig.update_layout(margin=dict(l=25, r=25, b=50, t=150, pad=2))
    fig.update_layout(width=width, height=height)
    fig.update_layout(yaxis=dict(title=y_title, titlefont_size=12, tickfont_size=12, tickmode='linear', tick0=1,
                                                                                                dtick=1),
                      xaxis=dict(title=x_title, titlefont_size=12, tickfont_size=12, tickmode='linear', tick0=1,
                                                                                                dtick=1),)
    return fig


# @st.cache
def update_app():
    top_page_soup = get_html_soup('https://www.skysports.com/euro-2020-table')
    group_soup_a = top_page_soup.find_all('div', {"class": 'standing-table standing-table--full block'})[0]
    group_soup_b = top_page_soup.find_all('div', {"class": 'standing-table standing-table--full block'})[1]
    group_soup_c = top_page_soup.find_all('div', {"class": 'standing-table standing-table--full block'})[2]
    group_soup_d = top_page_soup.find_all('div', {"class": 'standing-table standing-table--full block'})[3]
    group_soup_e = top_page_soup.find_all('div', {"class": 'standing-table standing-table--full block'})[4]
    group_soup_f = top_page_soup.find_all('div', {"class": 'standing-table standing-table--full block'})[5]

    groups = [(group_soup_a, 'A'),
              (group_soup_b, 'B'),
              (group_soup_c, 'C'),
              (group_soup_d, 'D'),
              (group_soup_e, 'E'),
              (group_soup_f, 'F')]

    tables = []
    for group in groups:
        tables.append(get_table(group))

    df_team = pd.concat(tables)
    df_team = pd.concat([df_team[df_team.columns[-1]], df_team[df_team.columns[0:2]], df_team[df_team.columns[2:-1]].astype(int)], axis=1)
    return df_team
df_team = update_app()

datasine_dic = {'Austria': ('Jergan'),
                'Belgium': ('Dixon'),
                'Croatia': ('Sofia'),
                'Czech Republic': ('Tim'),
                'Denmark': ('Costas'),
                'England': ('Sam'),
                'Finland': ('Daniel', 'Dixon'),
                'France': ('Sam'),
                'Germany': ('Margarita'),
                'Hungary': ('Stefan'),
                'Italy': ('Aseem', 'Ben'),
                'Netherlands': ('Igor', 'Vitali'),
                'North Macedonia': ('Margarita', 'Tim'),
                'Poland': ('Ismael'),
                'Portugal': ('Igor'),
                'Russia': ('Alfie', 'Franka'),
                'Scotland': ('Sofia', 'Stefan'),
                'Slovakia': ('Jergan'),
                'Spain': ('Costas', 'Vitali'),
                'Sweden': ('Franka'),
                'Switzerland': ('Aseem', 'Chris'),
                'Turkey': ('Alfie'),
                'Ukraine': ('Daniel', 'Ismael'),
                'Wales': ('Ben', 'Chris')}

df_staff = df_team.copy()
df_staff.country = df_staff.country.apply(lambda x: datasine_dic[x])
df_staff = df_staff.explode('country')
df_staff.rename(columns={'country':'datasiner'},inplace=True)


# st.header("Datasine Euros Sweepstake Dashboard")
# st.image(asset_path+'dslogo.png',width=400)
st.sidebar.image(asset_path+'euros.png', width=100)

def teams(col_1, col_2):
    if col_1 == col_2:
        return col_1
    else:
        return str(col_1)+','+str(col_2)


df_allocation = pd.DataFrame(datasine_dic).T
df_allocation['team'] = df_allocation.apply(lambda x: teams(x[0], x[1]), axis=1)
df_allocation = df_allocation.drop(columns=[0, 1])

st.sidebar.subheader('Team Allocation')
st.sidebar.dataframe(df_allocation)

st.sidebar.subheader('Data Source')
st.sidebar.write('https://www.skysports.com/')
st.sidebar.subheader('Last update')
st.sidebar.write(pd.datetime.now())


c1, c2 = st.beta_columns((1.5, 3))


df_recent_results = recent_results_sidebar()


c1.header('Most Recent Results')
c1.dataframe(df_recent_results)




c2.header('Analysis')
analysis_view = c2.selectbox("Choose team or staff view",
                                       ['Team','Staff'])
option = c2.selectbox('Choose analysis..',('Points','Results'))

option_dic = {'Points':'points'}
if analysis_view == 'Team':
    df = df_team

    if option == 'Results':
        fig = px.bar(df, y="country", x=["won", "drawn", "lost"], color_discrete_map={
            'won': 'green',
            'drawn': 'grey',
            'lost': 'red'})

        c2.plotly_chart(plot_editing(fig, title=option, x_title=option, y_title='Team'))
    else:
        fig = px.bar(df, y='country', x=option_dic[option], color='group', orientation='h', height=900, width=700)
        c2.plotly_chart(plot_editing(fig, title=option, x_title=option, y_title='Team'))

else:
    df = df_staff
    if option == 'Results':
        fig = px.bar(df, y="datasiner", x=["won", "drawn", "lost"], color_discrete_map={
            'won': 'green',
            'drawn': 'grey',
            'lost': 'red'})
        c2.plotly_chart(plot_editing(fig, title=option, x_title=option, y_title='Datasiner'))
    else:
        fig = px.bar(df, y='datasiner', x=option_dic[option], orientation='h', height=900, width=700)
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        c2.plotly_chart(plot_editing(fig,title=option, x_title=option, y_title='Datasiner'))












