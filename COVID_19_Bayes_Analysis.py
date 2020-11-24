import json 
import requests
import pandas as pd
from datetime import datetime
import plotly
import plotly.express as px
from plotly.offline import plot
import plotly.graph_objs as go

# Bayes Theorem 
def bayes(sensitivity = 0 , specificity = 0, prevalence = 0, situation = "+/+"):
    if situation == "+/+":
        return (sensitivity * prevalence) / ( (sensitivity * prevalence) + ((1 - specificity) * (1- prevalence)))
    
    elif situation == '-/-':
        return (specificity * (1- prevalence)) / ( (specificity * (1- prevalence))  + ((1- sensitivity) * prevalence))

# Box Plot with Plotly
def table_plot(head = [], data = [], data_format = [], title = ''):
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(head),
                    fill_color = 'LightSteelBlue',
                    line_color='SlateGray',
                    align='center'),
        cells=dict(values=data,
                   fill=dict(color=['PowderBlue', 'aliceblue']),
                   format = data_format,
                   line_color='LightSteelBlue',
                   align='center')),    
    ])
    fig.update_layout(title_text = title,  title_x=0.5, width=800, height=880)
    plot(fig)


# Importing COVID-19 cases for the world and their populations 
df_world = pd.read_csv('https://opendata.ecdc.europa.eu/covid19/casedistribution/csv')

# Setting the date variable to index
df_world['dateRep'] = pd.to_datetime(df_world['dateRep'], format = '%d/%m/%Y')  
df_world.set_index('dateRep', inplace = True)
df_world.index = pd.DatetimeIndex(df_world.index)

# Renaming adn dropping the columns 
df_world.drop(['geoId', 'countryterritoryCode','Cumulative_number_for_14_days_of_COVID-19_cases_per_100000'],axis = 1 ,inplace = True)
df_world.columns = ['day', 'month', 'year', 'new_case', 'new_death', 'country','population_2019', 'continent']
df_world.dropna(inplace = True)
df_world.loc[df_world['country'] == 'United_States_of_America', 'country'] = 'United States'


# PCR test sensitivity and specificity
sensitivity_pcr = 0.70
specificity_pcr = 0.95

# Creating DataFrame for bayes theorem results
df_world_bayes = {'date_today' :[], 'country' : [], 'total_cases': [], 'total_death': [] , 'population' : [], 'prevalence': [], 'prob_+/+' :[], 'prob_-/-': []}
df_world_bayes = pd.DataFrame(df_world_bayes)
date_today = datetime.now()
countries = list(df_world['country'].unique())          # this variable created to find all countries and will be used to calculate bayes result for each country

idx = 0
for country in countries:
    df_world_bayes.loc[idx, 'date_today'] = date_today
    df_world_bayes.loc[idx,'country'] = country
    df_world_bayes.loc[idx, 'total_cases'] = df_world[df_world['country'] == country]['new_case'].sum()
    df_world_bayes.loc[idx, 'total_death'] = df_world[df_world['country'] == country]['new_death'].sum()
    df_world_bayes.loc[idx, 'population'] = df_world[df_world['country'] == country]['population_2019'].iloc[0]
    df_world_bayes.loc[idx, 'prevalence'] = df_world_bayes.loc[idx,'total_cases'] / df_world_bayes.loc[idx, 'population']
    df_world_bayes.loc[idx, 'prob_+/+'] = bayes(sensitivity = 0.70, specificity = 0.95, prevalence = df_world_bayes.loc[idx, 'prevalence'], situation = '+/+')
    df_world_bayes.loc[idx, 'prob_-/-'] = bayes(sensitivity = 0.70, specificity = 0.95, prevalence = df_world_bayes.loc[idx, 'prevalence'], situation = '-/-') 
    idx +=1
    
# Top 10 countrties that has most cases in the world
top_10_prevalence = df_world_bayes.sort_values(by = 'prevalence',ascending = False).head(10)
# Top 10 countries that has highest prevalence of Covid-19
top_10_cases = df_world_bayes.sort_values(by = 'total_cases', ascending = False).head(10)

# Prevalence Tables
table_plot(head = ['Countries','Prevalence of Covid-19',  'Population'], data= [top_10_cases['country'], top_10_cases['prevalence'],top_10_cases['population']],data_format = [None, '.2%', ',.d'],title = 'Probability of Having Covid-19 by Country (Highest Cases)')
table_plot(head = ['Countries','Prevalence of Covid-19',  'Population'], data= [top_10_prevalence['country'], top_10_prevalence['prevalence'],top_10_prevalence['population']],data_format = [None, '.2%', ',.d'],title = 'Probability of Having Covid-19 by Country (Highest Prevalence)')

# Bayes Tables
table_plot(head = ['Countries','Prevalence of Covid-19','Probability of +/+',   'Population'], data= [top_10_cases['country'], top_10_cases['prevalence'], top_10_cases['prob_+/+'],top_10_cases['population']],data_format = [None, '.2%', '.2%',',.d'],title = 'Probability of Having Covid-19 if Being Tested Positive by Country (Highest Cases)')
table_plot(head = ['Countries','Prevalence of Covid-19', 'Probability of +/+',  'Population'], data= [top_10_prevalence['country'], top_10_prevalence['prevalence'], top_10_prevalence['prob_+/+'],top_10_prevalence['population']],data_format = [None, '.2%', '.2%',',.d'],title = 'Probability of Having Covid-19 if Tested Positive in the World (Highest Prevalence)')

# 
df_world_bayes['prevalence'] = df_world_bayes['prevalence'] * 100

# World Map for showing its prevalence
fig = px.choropleth(df_world_bayes,
              locations = 'country',
              color='prevalence', 
              color_continuous_scale=plotly.colors.diverging.RdYlGn[::-1],
              locationmode='country names',
              scope="world",
              range_color=(0.5, 3.5),
              height=600
             )
fig.update_layout(
    title={
        'text': "Prevalence of Covid-19 by Country",
        'y':0.85,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
plot(fig)

# Importing COVID-19 cases for the US states and their populations 
#df_us = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
df_us = pd.read_csv('https://data.cdc.gov/api/views/9mfq-cb36/rows.csv?accessType=DOWNLOAD')
df_us_population = pd.read_csv('http://www2.census.gov/programs-surveys/popest/datasets/2010-2019/national/totals/nst-est2019-alldata.csv')
us_abbreviation = dict(json.loads(requests.get('https://gist.githubusercontent.com/mshafrir/2646763/raw/8b0dbb93521f5d6889502305335104218454c2bf/states_hash.json').text))
df_abbreviation = pd.DataFrame(us_abbreviation, index = [0]).T.reset_index()
df_abbreviation.columns = ["abbreviation", 'state']

# Mergin the abbreviation of states
df_us = pd.merge(df_us, df_abbreviation, left_on = 'state', right_on = 'abbreviation', how = 'left')
# Dropping unneccesary columns and renaming them
df_us.drop(['conf_cases', 'prob_cases', 'pnew_case', 'conf_death', 'prob_death','pnew_death', 'created_at','consent_cases', 'consent_deaths', 'abbreviation'], axis = 1, inplace= True  )
df_us.columns = ['date', 'abbreviation', 'total_cases', 'new_case', 'total_death', 'new_death', 'state']

# Adding the populations column for states
df_us = pd.merge(df_us.sort_values('state'), df_us_population.loc[:,['NAME', 'POPESTIMATE2019']], left_on = 'state', right_on = 'NAME', how = 'left')
df_us.drop('NAME', axis= 1, inplace =True)
df_us.rename(columns = {'POPESTIMATE2019': 'population'}, inplace = True)

 # In COVID-19 dataset includes NY State and NY City cases seperately. Hence, the populations has been filled for New York City and calculated all cases in NY State
df_us.loc[df_us['abbreviation'] == 'NYC', 'state']= 'New York City'
df_us.loc[df_us['abbreviation'] == 'NYC', 'population'] = 8550971   # New York City population
df_us_nyc_total_cases = df_us.loc[df_us['abbreviation'] == 'NY', 'new_case'].reset_index()['new_case'] + df_us.loc[df_us['abbreviation'] == 'NYC', 'new_case'].reset_index()['new_case']
df_us.loc[df_us['abbreviation'] == 'NY', 'new_case'] = list(df_us_nyc_total_cases)
df_us.loc[df_us['abbreviation'] == 'DC', 'population'] = 5322000    # DC population
   
# You can see the total cases in New Yory State including NYC 
df_us[(df_us['abbreviation'] == 'NYC') | (df_us['abbreviation'] == 'NY' )]['new_case'].sum()
df_us[(df_us['abbreviation'] == 'NYC') | (df_us['abbreviation'] == 'NY' )]['population']
    
# The COVID-19 case dataset includes the islands where is belongs to the US. I am dropping them
df_us[df_us['population'].isnull()]['abbreviation'].value_counts()
df_us.dropna(inplace = True)

# PCR test sensitivity and Specificity
sensitivity_pcr = 0.70
specificity_pcr = 0.95

# List for all states. It will used to calculate states bayes results
states = list(df_us['state'].unique()) 

# Creating Dataframe for US bayes calculation
df_us_bayes = {'date_today' :[],'abbreviation': [], 'state' : [], 'total_cases': [], 'total_death': [] , 'population' : [], 'prevalence': [], 'prob_+/+' :[], 'prob_-/-': []}
df_us_bayes = pd.DataFrame(df_us_bayes)
date_today = datetime.now()

idx = 0
for state in states:
    df_us_bayes.loc[idx, 'date_today'] = date_today
    df_us_bayes.loc[idx,'abbreviation'] = df_us[df_us['state'] == state]['abbreviation'].iloc[0]
    df_us_bayes.loc[idx,'state'] = state
    df_us_bayes.loc[idx, 'total_cases'] = df_us[df_us['state'] == state]['new_case'].sum()
    df_us_bayes.loc[idx, 'total_death'] = df_us[df_us['state'] == state]['new_death'].sum()
    df_us_bayes.loc[idx, 'population'] = df_us[df_us['state'] == state]['population'].iloc[0]
    df_us_bayes.loc[idx, 'prevalence'] = df_us_bayes.loc[idx,'total_cases'] / df_us_bayes.loc[idx, 'population']
    df_us_bayes.loc[idx, 'prob_+/+'] = bayes(sensitivity = 0.70, specificity = 0.95, prevalence = df_us_bayes.loc[idx, 'prevalence'], situation = '+/+')
    df_us_bayes.loc[idx, 'prob_-/-'] = bayes(sensitivity = 0.70, specificity = 0.95, prevalence = df_us_bayes.loc[idx, 'prevalence'], situation = '-/-') 
    idx +=1

# Top 10 states that has most cases
top_10_us_total_cases = df_us_bayes.sort_values(by = 'total_cases', ascending = False).head(10)
# Top 10 states that has highest prevelance of Covid-19
top_10_us_total_prevalence = df_us_bayes.sort_values(by = 'prevalence' ,ascending = False).head(10)

# Prevalence Table
table_plot(head = ['States','Prevalence of Covid-19',  'Population'], data= [top_10_us_total_cases['state'], top_10_us_total_cases['prevalence'],top_10_us_total_cases['population']],data_format = [None, '.2%', ',.d'],title = 'Probability of Having Covid-19 by States (Highest Cases)')
table_plot(head = ['States','Prevalence of Covid-19',  'Population'], data= [top_10_us_total_prevalence['state'], top_10_us_total_prevalence['prevalence'],top_10_us_total_prevalence['population']],data_format = [None, '.2%', ',.d'],title = 'Probability of Having Covid-19 by States (Highest Prevalence)')

# Bayes Tables
table_plot(head = ['States','Prevalence of Covid-19', 'Probability of +/+',  'Population'], data= [top_10_us_total_cases['state'], top_10_us_total_cases['prevalence'], top_10_us_total_cases['prob_+/+'],top_10_us_total_cases['population']],data_format = [None, '.2%', '.2%',',.d'],title = 'Probability of Having Covid-19 if Being Tested Positive by States (Highest Cases)')
table_plot(head = ['States','Prevalence of Covid-19','Probability of +/+',   'Population'], data= [top_10_us_total_prevalence['state'], top_10_us_total_prevalence['prevalence'], top_10_us_total_prevalence['prob_+/+'],top_10_us_total_prevalence['population']],data_format = [None, '.2%', '.2%',',.d'],title = 'Probability of Having Covid-19 if Tested Positive (Highest Prevalence)')

# US Prevalence Map
fig = px.choropleth(df_us_bayes,
                   # geojson=counties,
              locations = 'abbreviation',
              color='prevalence', 
              color_continuous_scale=plotly.colors.diverging.RdYlGn[::-1],
              locationmode='USA-states',
              scope="usa",
              range_color=(0.015, 0.055),

              height=600
             )

fig.update_layout(
    title={
        'text': "Prevalence of Covid-19 by States",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
plot(fig)
