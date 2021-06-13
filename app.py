import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import os
import sys
# sys.path.append(os.getenv('SAM_PATH'))
from samutil import get_html_soup


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


top_page_soup = get_html_soup('https://www.skysports.com/euro-2020-table')
group_soup_a = top_page_soup.find_all('div', {"class": 'standing-table standing-table--full block'})[0]
group_soup_b = top_page_soup.find_all('div', {"class": 'standing-table standing-table--full block'})[1]
group_soup_c = top_page_soup.find_all('div', {"class": 'standing-table standing-table--full block'})[2]
group_soup_d = top_page_soup.find_all('div', {"class": 'standing-table standing-table--full block'})[3]
group_soup_e = top_page_soup.find_all('div', {"class": 'standing-table standing-table--full block'})[4]
group_soup_f = top_page_soup.find_all('div', {"class": 'standing-table standing-table--full block'})[5]

groups = [(group_soup_a, 'a'),
          (group_soup_b, 'b'),
          (group_soup_c, 'c'),
          (group_soup_d, 'd'),
          (group_soup_e, 'e'),
          (group_soup_f, 'f')]

tables = []
for group in groups:
    tables.append(get_table(group))

df = pd.concat(tables)

df_team = pd.concat([df[df.columns[-1]], df[df.columns[0:2]], df[df.columns[2:-1]].astype(int)], axis=1)

"""
Staff Data Prep
"""
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













