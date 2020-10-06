# -*- coding: utf-8 -*-
"""IO Tables.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pTqJqaarCemDbtWklP1t-BsVWd-Gy2Qf

# Input-Output Analysis
"""

import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt
import plotly.graph_objects as go

!pip install chart_studio

import chart_studio
import chart_studio.plotly as py
username = 'schandar'
api_key = 'C97wfbyw53eqkApqPWSP'
chart_studio.tools.set_credentials_file(username=username, api_key=api_key)

z = pd.read_csv("https://raw.githubusercontent.com/schandar/IO-Tables/master/Z_matrix.csv", header=[0,1], index_col=[0,1])
x = pd.read_csv("https://raw.githubusercontent.com/schandar/IO-Tables/master/X_vector.csv", header = None, index_col = [0, 1])
y = pd.read_csv("https://raw.githubusercontent.com/schandar/IO-Tables/master/Y_vector.csv", header=[0], index_col=[0,1])

z.head()

x.head()

y.head()

x[2]

"""Generate A matrix, aij = zij/xj. Aij = amount of inputs required from industry i to industry j, in order to produce one unit of output from industry j."""

x_transpose = x.transpose()
a = z.div(x_transpose.iloc[0])
a.fillna(0, inplace=True)
a.head()

"""Create Leontief Inverse matrix, L = (I-A)^(-1)"""

i = a.copy()
i[:] = np.identity(2464)
i_a = i.subtract(a)
l = pd.DataFrame(np.linalg.pinv(i_a.values), i_a.columns, i_a.index)
l.head()

"""Baseline X and Y:"""

y_baseline = pd.DataFrame(y.sum(axis = 1))
y_baseline.index.set_names(["country", "code"], inplace=True)
y_baseline.head()
x_baseline = pd.DataFrame(l.dot(y.sum(axis = 1)))
x_baseline.columns = ['output']
x_baseline.index.set_names(["country", "code"], inplace=True)

"""Industry Codes:"""

codes = pd.read_csv("https://raw.githubusercontent.com/schandar/IO-Tables/master/industry_codes.csv", header = 0, index_col = 0)
code_dict = codes.to_dict()['industry']
code_dict

fig = go.Figure(data=[go.Table(columnwidth = [80,400],
    header=dict(values=['Industry Code', 'Description'],
                fill_color='lightskyblue',
                align='left'),
    cells=dict(values=[list(code_dict.keys()), list(code_dict.values())],
               fill_color='white',
               align='left'))
])

fig.show()

py.plot(fig, filename = 'industry', auto_open=True)

"""Country Code + Above or Below World Average in Corona Cases per 1M population 
** data sourced from Worldometer **
"""

ab_df = pd.read_csv("https://raw.githubusercontent.com/schandar/IO-Tables/master/CoronaCasesCountry.csv", index_col = 0, header = None, names = ['country', 'full', 'above'])
ab_df.head()

y_baseline = y_baseline.join(ab_df, how = 'inner')

y_baseline.columns = ['fd', 'name', 'above']
y_baseline.head()

def adjust_df(df, perc_above, perc_below, c_code):
  df.fd = np.where((df.above == 1) & (df.index.get_level_values('code') == c_code), df.fd*(1-perc_above), df.fd)
  df.fd = np.where((df.above == 0) & (df.index.get_level_values('code') == c_code), df.fd*(1-perc_below), df.fd)

x_baseline.head()

td = x_baseline.groupby(["country"]).sum()

td.columns = ['total']
td.head()

td[td.index == "MEX"]

def create_diff_df(y_scenario):
  x_scenario = pd.DataFrame(l.dot(y_scenario))
  x_scenario.columns = ['output']
  diff_scenario = x_scenario.subtract(x_baseline)
  diff_scenario = diff_scenario.join(td, how = 'inner')
  diff_scenario['output'] = diff_scenario.output/diff_scenario.total
  diff_scenario.index.set_names(["country", "code"], inplace=True)
  diff_scenario = diff_scenario.join(ab_df, how = 'inner')
  return diff_scenario

countries = ab_df.full.tolist()
industries = list(code_dict.keys())

countries[16] = "United Kingdom"

def create_plot(diff_scenario):
  outputs = diff_scenario.output.tolist()
  data_ls = []
  for k in code_dict:
    outputs = diff_scenario[diff_scenario.index.get_level_values('code') == k].output.tolist()
    data_ls.append(go.Bar(name = k, x = countries, y = outputs))

  fig = go.Figure(data=data_ls)
  # Change the bar mode
  fig.update_layout(barmode='stack')
  fig.show()
  return fig

x_baseline.index.set_names(["country", "code"], inplace=True)
fig = create_plot(x_baseline)

py.plot(fig, filename = 'baseline', auto_open=True)

code_dict['Q']

"""Scenario 1: Real Estate spending declines by 30%"""

y_scenario1 = y_baseline.copy()
adjust_df(y_scenario1, .3, .3, "L68")
y_scenario1 = y_scenario1[['fd']]
diff_scenario1 = create_diff_df(y_scenario1)
fig = create_plot(diff_scenario1)
py.plot(fig, filename = 'scenario1', auto_open=True)

"""Scenario 2: Tourism spending declines 50%"""

y_scenario2 = y_baseline.copy()
adjust_df(y_scenario2, .5, .5, "I")
y_scenario2 = y_scenario2[['fd']]
diff_scenario2 = create_diff_df(y_scenario2)
fig = create_plot(diff_scenario2)
py.plot(fig, filename = 'scenario2', auto_open=True)

code_dict["C10-C12"]

"""Scenario 3: Retail spending declines by 12%"""

y_scenario3 = y_baseline.copy()
adjust_df(y_scenario3, .12, .12, "G47")
y_scenario3 = y_scenario3[['fd']]
diff_scenario3 = create_diff_df(y_scenario3)
fig = create_plot(diff_scenario3)
py.plot(fig, filename = 'scenario3', auto_open=True)

"""Scenario 4: Tech sector increases by 25%"""

y_scenario4 = y_baseline.copy()
adjust_df(y_scenario4, -.25, -.25, "J62_J63")
y_scenario4 = y_scenario4[['fd']]
diff_scenario4 = create_diff_df(y_scenario4)
fig = create_plot(diff_scenario4)
py.plot(fig, filename = 'scenario4', auto_open=True)

code_dict['N']

"""Scenario 5: All scenarios happen at once"""

y_scenario5 = y_baseline.copy()
adjust_df(y_scenario5, .3, .3, "L68")
adjust_df(y_scenario5, .5, .5, "I")
adjust_df(y_scenario5, .12, .12, "G47")
adjust_df(y_scenario5, -.25, -.25, "J62_J63")
y_scenario5 = y_scenario5[['fd']]
diff_scenario5 = create_diff_df(y_scenario5)
fig = create_plot(diff_scenario5)
py.plot(fig, filename = 'scenario5', auto_open=True)