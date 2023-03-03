# %%
import requests
import json
import pandas as pd
import numpy as np
import plotly.express as px
import kaggle

# %% [markdown]
# Import dataset via kaggle api

# %%
api = kaggle.api
api.get_config_value('username')

# Below paste the of the code to download the dataset from Kaggle

# import main dataset
!kaggle datasets download -d equilibriumm/sleep-efficiency
!unzip sleep-efficiency.zip

# import sleep study pilot dataset
# !kaggle datasets download -d mlomuscio/sleepstudypilot
# !unzip sleepstudypilot.zip

# import sleep study US dataset
# !kaggle datasets download -d thedevastator/how-much-sleep-do-americans-really-get
# !unzip how-much-sleep-do-americans-really-get.zip

# %% [markdown]
# Data analysis

# %%
df = pd.read_csv('Sleep_Efficiency.csv')

df.head()

# %%
df.shape

# %%
df.info()

# %%
df.rename(columns = {'Wakeup time':'Wakeup_time', 'Sleep duration':'Sleep_duration ',"Sleep efficiency":"Sleep_efficiency",
                     "REM sleep percentage":"REM_sleep_percentage","Deep sleep percentage":"Deep_sleep_percentage",
                     "Light sleep percentage":"Light_sleep_percentage","Caffeine consumption":"Caffeine_consumption",
                     "Alcohol consumption":"Alcohol_consumption","Smoking status":"Smoking_status","Exercise frequency":"Exercise_frequency"}, inplace = True)

# %%
df.info()

# %%
# Check for missing values
df.isnull().sum()

# %% [markdown]
# Fill in all missing values with the average of that column

# %%
avg_awake = df['Awakenings'].mean()
round(avg_awake, 0)

df['Awakenings'].fillna(round(avg_awake, 0), inplace = True)

# %%
# fill in null values in Caffeine_consumption with the mean of Caffeine_consumption
avg_caffeine = df['Caffeine_consumption'].mean()
round(avg_caffeine, 0)

df['Caffeine_consumption'].fillna(round(avg_caffeine, 0), inplace = True)

# %%
# fill in null values in Alcohol_consumption with the mean of Alcohol_consumption
avg_alc = df['Alcohol_consumption'].mean()
round(avg_alc, 0)

df['Alcohol_consumption'].fillna(round(avg_alc, 0), inplace = True)

# %%
# fill in null values in Exercise_frequency with the mean of Exercise_frequency
avg_exercise = df['Exercise_frequency'].mean()
round(avg_exercise, 0)

df['Exercise_frequency'].fillna(round(avg_exercise, 0), inplace = True)

# %% [markdown]
# LET'S START PLOTTING
# 
# Below there is a pie chart plotted to show the ratio between male and female participants.

# %%
fig = px.pie(df, values='ID', names='Gender')
fig.update_layout(title='Ratio of male and female', legend_title='Gender')
fig.show()

# %%
fig = px.box(df, x='Age', color_discrete_sequence=['green'], labels={'Age':'Age (years)'})
fig.update_layout(title='Age distribution')
fig.show()

# %%
fig = px.scatter(df, x='Age', color='Age', color_continuous_scale='jet', size='Age', hover_data=['Age'])
fig.update_layout(title='Age distribution')
fig.show()

# %% [markdown]
# Below you see a histogram that shows the ages of the people in the dataset, categorized by gender. This shows the ratio between male and female participants of every age.

# %%
fig = px.histogram(df, x='Age', color='Gender', barmode='overlay', labels={'Age':'Age (years)'})
fig.update_layout(title='Male and Females age distribution')
fig.show()

# %% [markdown]
# Below an extra visual to display the age distribution and the gender distribution

# %%
fig = px.scatter(df, x='Age', color='Gender', color_continuous_scale='jet', size='Age', hover_data=['Age'])
fig.update_layout(title='Age distribution')
fig.show()

# %% [markdown]
# Below is a histogram that displays the smoking status of the paricipants sorted on age

# %%
fig = px.histogram(df, x='Age', color='Smoking_status', barmode='overlay', labels={'Age':'Age (years)'})
fig.update_layout(title='Smoking status distribution', legend_title='Smoking status')
fig.show()

# %%



