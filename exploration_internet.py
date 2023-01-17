# %% [markdown]
# # What's this projevt about?

# %% [markdown]
# ## Objectives
# - Cats 
# - Dogs
# -
# 

# %% [markdown]
# # Setup

# %%
# Installs
# %pip install geopandas
# %pip install folium  
# %pip install plotly==5.11.0
# %pip install dash
# %pip install plotly.express

# %%
# Imports
import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

import chart_studio.plotly as py
import plotly.express as px
import plotly.offline as po
import plotly.graph_objs as pg
import plotly.graph_objects as go


# %%
# Pandas options
pd.set_option('display.max_rows', 30) # Display 70 rows
pd.set_option('display.float_format', lambda x: '%.5f' % x) # Suppress scientific notation in Pandas

# %% [markdown]
# # Data

# %% [markdown]
# ## Import data

# %%
# Data source: World Bank

# Population = SP.POP.TOTL
# https://data.worldbank.org/indicator/SP.POP.TOTL
df_population_raw = pd.read_csv('Data Population/API_SP.POP.TOTL_DS2_en_csv_v2_4770387.csv', skiprows=4)

# Individuals using the Internet (% of population) = IT.NET.USER.ZS
# https://data.worldbank.org/indicator/IT.NET.USER.ZS
df_users_raw = pd.read_csv('Data internet/individuals_using_the_Internet_percentage_of_population.csv', skiprows=4)
df_metadata_country_raw = pd.read_csv('Data internet/Metadata_Country_individuals_using_the_Internet_percentage_of_population.csv')
df_metadata_indicator_raw= pd.read_csv('Data internet/Metadata_Indicator_individuals_using_the_Internet_percentage_of_population.csv')

# %%
df_users_1 = df_users_raw.copy()
df_metadata_country = df_metadata_country_raw.copy()
df_metadata_indicator = df_metadata_indicator_raw.copy()
df_population = df_population_raw.copy()

# %% [markdown]
# ## Clean data

# %% [markdown]
# ### Population

# %%
# Drop unnecessary columns
drop_columns_population = ['Indicator Name', 'Indicator Code', 'Unnamed: 66']
df_population.drop(columns = drop_columns_population, inplace = True)

# Wide to long
# Get years columns
years = df_population.columns[2:]

# Use melt to unpivot the DataFrame
df_population = df_population.melt(id_vars=['Country Name', 'Country Code'], value_vars=years, var_name='Year', value_name='SP.POP.TOTL')


# Sort by country and year
df_population.sort_values(by=['Country Name', 'Year'], inplace=True)

# Rename columns
df_population.rename(columns={"SP.POP.TOTL": "Population"}, inplace = True)


# %%
# To-do

# Correct dadatypes
# Ugly alternative
df_population['Year'] = df_population['Year'].astype(int)

# %%
df_population.head(5)

# %%
df_population.info()

# %% [markdown]
# ### Users

# %%
# Drop unnecessary columns
drop_columns_users = ['Indicator Name', 'Indicator Code', 'Unnamed: 66']
df_users_1.drop(columns = drop_columns_users, inplace = True)

# Wide to long
# Get years columns
years = df_users_1.columns[2:]

# Use melt to unpivot the DataFrame
df_users_1 = df_users_1.melt(id_vars=['Country Name', 'Country Code'], value_vars=years, var_name='Year', value_name='IT.NET.USER.ZS')

# Sort by country and year
df_users_1.sort_values(by=['Country Name', 'Year'], inplace=True)

# Rename columns
df_users_1.rename(columns={"IT.NET.USER.ZS": "Users percentage"}, inplace = True)


# %%
# To-do

# Correct dadatypes
# I cn't make this work correctly
# df_users_1['Year'] = pd.to_datetime(df_users_1['Year'], format='%Y')

# Ugly alternative
df_users_1['Year'] = df_users_1['Year'].astype(int)

# %%
# Decide on timespan to analize
which_years_to_keep = df_users_1.groupby('Year')['Users percentage'].count().reset_index()

# VIZ Year vs IT.NET.USER.ZS
fig = px.line(which_years_to_keep, x="Year", y="Users percentage", title="Individuals using the Internet (% of population)")
fig.show()

# %%
# Keep data from 1990 to 2020
df_users_1 = df_users_1[df_users_1['Year'].between(1990, 2020, inclusive='both')]
df_users_1

# %%
df_users_1.info()

# %% [markdown]
# ### metadata_country

# %%
df_metadata_country.head(3)

# %%
# Drop unnecessary columns
drop_columns_metadata_country = ['TableName', 'Unnamed: 5']
df_metadata_country.drop(columns = drop_columns_metadata_country, inplace=True)


# %%
df_metadata_country.head(3)

# %% [markdown]
# ### metadata_indicator

# %%
df_metadata_indicator.head()

# %% [markdown]
# ### Merge users_1 and metadata

# %%
# Merge users and metadata
users_metadata = df_users_1.merge(df_metadata_country, how='left', on='Country Code')
users_metadata.head(3)


# %%
users_metadata[users_metadata['Country Code'] == 'WLD']

# %%
# Replace values in column 'Region' with 'World where 'Region' is 'North'
users_metadata.loc[users_metadata['Country Name'] == 'World', 'Region'] = 'World'

# %%
users_metadata.head(3)

# %%
users_metadata.info()

# %% [markdown]
# ### Merge  users_metadata & df_population

# %%
# Merge users and metadata
users_population = users_metadata.merge(df_population, how='left', on=['Country Name', 'Country Code', 'Year'])

# %%
# Add column 'Users Total': total number of people using the internet
# The total number of people using the internet is calculated by multiplying the 
# % of population using the Internet['Users percentage']  
# with the population estimate ['Population']

users_population['Users Total'] = (users_population['Users percentage'] * users_population['Population']) / 100

# %%
# Save to file and re-import
users_population.to_csv('users.csv', index=False)

# Usable dataframe
df_users = pd.read_csv('users.csv')

# %%
df_users[df_users['Country Code'] == 'USA'].tail()

# %%
df_users.info()

# %% [markdown]
# # Analisis and VIZ

# %%
# Create df_regions and df_income_group
df_regions = df_users.groupby(['Region', 'Year']).agg({'Users percentage':'mean', 'Users Total': 'sum'}).reset_index()
df_income_group = df_users.groupby(['IncomeGroup', 'Year']).agg({'Users percentage':'mean', 'Users Total': 'sum'}).reset_index()

# %%
# VIZ Variables
title = df_metadata_indicator['INDICATOR_NAME'][0]
note = df_metadata_indicator['SOURCE_NOTE'][0]
source = df_metadata_indicator['SOURCE_ORGANIZATION'][0]
source_link = 'https://data.worldbank.org/indicator/IT.NET.USER.ZS'

y_max = df_users['Users percentage'].max() + 10

# %%
source

# %% [markdown]
# ## Share of the population using the internet by country, historical progression | MAP

# %%
# Documentation of this VIZ "Using Built-in Country and State Geometries":
# https://plotly.com/python/choropleth-maps/
# https://plotly.github.io/plotly.py-docs/generated/plotly.express.choropleth.html
# https://plotly.com/python/map-configuration/
# https://plotly.com/python/reference/layout/annotations/
# https://plotly.com/python/builtin-colorscales/


fig = px.choropleth(df_users,
                    locations="Country Code",
                    color="Users percentage",
                    hover_name="Country Name", # column to add to hover information
                    hover_data=['Year','Users percentage', 'Region','IncomeGroup', 'Population'],
                    color_continuous_scale=px.colors.sequential.Mint,
                    animation_frame="Year",
                    animation_group="Country Name",
                    range_color=(0, 100),
                    )

fig.update_layout(
    title_text='Individuals using the Internet<br>% of population',


    # coloraxis_colorbar_x=-0.1, # Bar to the left
    # coloraxis_colorbar_tickprefix = '%',
    coloraxis_colorbar_title = '% of population',    
    # margin={"r":0,"t":10,"l":0,"b":0}, # Map margins
    # height=300 # Map height
    annotations = [dict(
        x=0.55,
        y=0.1,
        xref='paper',
        yref='paper',
        text='Source: <a href="https://data.worldbank.org/indicator/IT.NET.USER.ZS">\
            International Telecommunication Union (ITU)</a>',
        showarrow = False
    )]
)

fig.update_geos(showframe=False,
                showcoastlines=False,
                # coastlinecolor="RebeccaPurple",
                showland=True, 
                landcolor="LightGrey",
                projection_type='equirectangular',
                # lataxis_showgrid=True,
                # lonaxis_showgrid=True
)

fig.update_traces(marker_line_color='white',
                  marker_line_width=0.5
                  )

fig.show()

# %%
df_users.columns

# %% [markdown]
# ## Share of the population using the internet by country

# %%
# VIZ Variables
title = df_metadata_indicator['INDICATOR_NAME']
note = df_metadata_indicator['SOURCE_NOTE']
source = df_metadata_indicator['SOURCE_ORGANIZATION']

y_max = df_users['Users percentage'].max() + 10

# %%
# To-do : add a line representing the world progression over time in a different colour
# To-do : add year selector on dash
# To-do : Style VIZ

# VIZ Share of the population using the internet
# https://plotly.com/python/line-charts/

fig = px.line(df_users,
              x="Year",
              y="Users percentage",
              color='Country Name',
#              text=df_users['Year']
            )
fig.show()

# %% [markdown]
# ## Share of the population using the internet by Income Group

# %%
# VIZ Share of the population using the internet
# https://plotly.com/python/line-charts/

fig = px.line(df_income_group,
              x="Year",
              y="Users percentage",
              color='IncomeGroup',
#              text=df_users['Year']
            )
fig.show()



# %% [markdown]
# ## Share of the population using the internet by Region

# %%
fig = px.line(df_regions,
              x="Year",
              y="Users percentage",
              color='Region',
#              text=df_users['Year']
            )
fig.show()


# %% [markdown]
# ## Total number of people using the internet by region

# %%
fig = px.line(df_regions,
              x="Year",
              y="Users Total",
              color='Region',
#              text=df_users['Year']
            )
fig.show()

# %% [markdown]
# ## Top 10 countries with the highest internet use (by population share) in 2020?

# %%
# Top 10 countries with the highest internet use by population share in 2020

year_max = df_users['Year'].max()
df_top_10_2020 = df_users.query(f'Year == {year_max}')

df_top_10_2020 = df_top_10_2020.groupby(['Country Name', 'Country Code','Year' ])['Users percentage'].sum().to_frame().reset_index()
df_top_10_2020 = df_top_10_2020.sort_values(by=['Year', 'Users percentage'], ascending=False)[:10]
df_top_10_2020

# %%
# Documentation of this VIZ "Using Built-in Country and State Geometries":
# https://plotly.com/python/choropleth-maps/

fig = px.choropleth(df_top_10_2020,
                    locations="Country Code",
                    color="Users percentage",
                    hover_name="Country Name", # column to add to hover information
                    color_continuous_scale=px.colors.sequential.Plasma,
                    )

fig.update_geos(fitbounds="locations") # Automatic Zooming or Bounds Fitting

fig.update_layout(height=300,
                  margin={"r":0,"t":10,"l":0,"b":10})

fig.show()

# %% [markdown]
# ## Top 10 over time

# %%
# Top 10 countries with the highest internet use by population share over time

def top_10(my_df, col_year):
    years = my_df[col_year].unique()

    df_top_10 = pd.DataFrame(columns=['Country Name', 'Country Code',  'Year',  'Users percentage'])

    for i in years:
        ds = my_df.query(f'Year == {i}')
        ds = ds.groupby(['Country Name', 'Country Code','Year' ])['Users percentage'].sum().to_frame().reset_index()
        ds = ds.sort_values(by=['Users percentage'], ascending=False)[:10]
        df_top_10 = pd.concat([df_top_10, ds])
    return df_top_10



# %%
df_top_10 = top_10(df_users, 'Year')
df_top_10

# %%
fig = px.choropleth(df_top_10,
                    locations="Country Code",
                    color="Users percentage",
                    hover_name="Country Name", # column to add to hover information
                    color_continuous_scale=px.colors.sequential.Plasma,
                    animation_frame="Year",
                    animation_group="Country Name",
                    )
fig.show()


