# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from functions import event_probability 

# %%
# Load csv 
df_train = pd.read_csv('train.csv')
df_test = pd.read_csv('test.csv')

# Create new column (Survived) in raw test data with a value of 0 on each row
df_test['Survived'] = 0

# %%
# Show the given row and columns in the datasets
shape_train = df_train.shape
shape_test = df_test.shape
print('Train dataset shape: ')
print(shape_train)
print('Test dataset shape: ')
print(shape_test)

# %%
# Show all info of the datasets
df_train.info()
df_test.info()

# %%
display(df_train)
# display(df_test)

# %%
# Show total of people onboard
total = df_train['PassengerId'].count() # 891

# %%
# Show total number of male and female onboard of the ship
df_train['Sex'].value_counts()

# %%
# Show null values per column
df_train.isnull().sum()

# %%
sex = df_train.groupby('Sex')

male_pass = sex.get_group('male')
female_pass = sex.get_group('female')

# %%
# Gives the age thats most common amongst men onboard
male_pass.Age.mode()


# %%
# Fill NaN values in the Age column
df_train['Age'].fillna(df_train['Age'].mean(), inplace=True)

# %%
# Create bins to fit an age range to every passenger
bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]

# Cut age into age groups so you can view it better
df_train['Agerange'] = pd.cut(df_train.Age, bins,include_lowest = True)
df_test['Agerange'] = pd.cut(df_test.Age, bins,include_lowest = True)


# %%
# Check most common age range among male passengers that survived in the first class
male_surv_first_class = df_train[(df_train.Sex == 'male') & (df_train.Pclass == 1) & (df_train.Survived == 1)]
print(male_surv_first_class.Agerange.mode())
# display(male_surv_first_class)

# Check most common age range among female passengers that survived in the first class
female_surv_first_class = df_train[(df_train.Sex == 'female') & (df_train.Pclass == 1) & (df_train.Survived == 1)]
print(female_surv_first_class.Agerange.mode())
# display(male_surv_first_class)

# %%
# Check most common age range among male passengers that survived in the second class
male_surv_second_class = df_train[(df_train.Sex == 'male') & (df_train.Pclass == 2) & (df_train.Survived == 1)]
print(male_surv_second_class.Agerange.mode())
# display(male_surv_second_class)

# Check most common age range among female passengers that survived in the second class
female_surv_second_class = df_train[(df_train.Sex == 'female') & (df_train.Pclass == 2) & (df_train.Survived == 1)]
print(female_surv_second_class.Agerange.mode())
# display(male_surv_second_class)

# %%
# Check most common age range among male passengers that survived in the third class
male_surv_third_class = df_train[(df_train.Sex == 'male') & (df_train.Pclass == 3) & (df_train.Survived == 1)]
print(male_surv_third_class.Agerange.mode())
# display(male_surv_third_class)

# Check most common age range among female passengers that survived in the third class
female_surv_third_class = df_train[(df_train.Sex == 'female') & (df_train.Pclass == 3) & (df_train.Survived == 1)]
print(female_surv_third_class.Agerange.mode())
display(female_surv_third_class)

# %%
# Shows how many male passengers did not survive
not_surv_male_pass = male_pass[(male_pass['Survived'] == 0)]
count_not_surv_male_pass = not_surv_male_pass.PassengerId.count() # 468


# %%
# Shows how many male passengers did survive
surv_male_pass = male_pass[(male_pass['Survived'] == 1)]
count_surv_male_pass = surv_male_pass.PassengerId.count() # 109

# %%
# Group male passengers by survived or not to plot the results
male_pass_graph = male_pass.groupby('Survived').Survived.count()


# %%
# Gives the age thats most common amongst women onboard
female_pass.Age.mean()

# %%
# Shows how many female passengers did not survive
not_surv_female_pass = female_pass[(female_pass['Survived'] == 0)]
count_not_surv_female_pass = not_surv_female_pass.PassengerId.count() # 81

# %%
# Shows how many female passengers did survive
surv_female_pass = female_pass[(female_pass['Survived'] == 1)]
count_surv_female_pass = surv_female_pass.PassengerId.count() # 233


# %%
# Group female passengers by survived or not to plot the results
female_pass_graph = female_pass.groupby('Survived').Survived.count()

# %%
# Total of people who survived
total_surv = df_train[(df_train['Survived'] == 1)]
total_not_surv = df_train[(df_train['Survived'] == 0)]

# %%
# Group survivers by sex
groupby_sex_surv = total_surv.groupby('Sex').Survived.count()
groupby_sex_not_surv = total_not_surv.groupby('Sex').Survived.count()

# %%
# Graphing surviving and non surviving females
fig, ax = plt.subplots(1, 2, figsize=(8,8))

ax[0].pie(male_pass_graph.values, labels=['Died', 'Survived'], autopct='%.2f%%')
ax[0].set_title('Male passengers that died')
ax[1].pie(female_pass_graph.values, labels=['Died', 'Survived'], autopct='%.2f%%')
ax[1].set_title('Female passengers that died')
ax[0].legend()
ax[1].legend()
plt.show()

# %%
# Probability for surviving as a female
prob_surv_female = event_probability(count_surv_female_pass, total)
print('Probability for surviving as a female: ' + str(prob_surv_female) + '%')

# Probability for not surviving as a female
prob_not_surv_female = event_probability(count_not_surv_female_pass, total)
print('Probability for not surviving as a female: ' + str(prob_not_surv_female) + '%')


# %%
# Probability for surviving as a male
prob_surv_male = event_probability(count_surv_male_pass, total)
print('Probability for surviving as a male: ' + str(prob_surv_male) + '%')

# Probability for not surviving as male
prob_not_surv_male = event_probability(count_not_surv_male_pass, total)
print('Probability for not surviving as male: ' + str(prob_not_surv_male) + '%')

# %%
plt.figure(figsize=(6,4))
plt.hist(df_train.Pclass)
plt.xticks(range(1,4,1))
plt.yticks(range(100,550,50))
plt.xlabel('Travel class', fontsize=15)
plt.ylabel('Number of passengers', fontsize=15)
plt.show()

# %%
# Group passengers by class
classes = df_train.groupby('Pclass')

# Get every class seperate from eachother to plot 
first = classes.get_group(1)
second = classes.get_group(2)
third = classes.get_group(3)

# %%
# Plot survived per class
fig, ax = plt.subplots(1,3, figsize=(20,4))
xlabels = ['Died', 'Survived']

ax[0].hist(first.Survived)
ax[0].set_title("First class passangers",fontsize = 20)
ax[0].set_ylabel("Total numbers of passangers",fontsize = 20)
ax[0].set_xticklabels(xlabels)
ax[0].set_xticks(range(0,2,1))

ax[1].hist(second.Survived)
ax[1].set_title("Second Class Passangers",fontsize = 20)
ax[1].set_ylabel("Total Numbers Of passangers",fontsize = 20)
ax[1].set_xticklabels(xlabels)
ax[1].set_xticks(range(0,2,1))

ax[2].hist(third.Survived)
ax[2].set_title("Third Class Passangers",fontsize = 20)
ax[2].set_ylabel("Total Number Of Passangers",fontsize = 20)
ax[2].set_xticklabels(xlabels)
ax[2].set_xticks(range(0,2,1))

plt.show()

# %%
# Group female passengers by class. This way we can plot them into histograms to see survival rate
female_pass_class = female_pass.groupby('Pclass')

female_first = female_pass_class.get_group(1)
female_second = female_pass_class.get_group(2)
female_third = female_pass_class.get_group(3)

# Group male passengers by class. This way we can plot them into histograms to see survival rate
male_pass_class = male_pass.groupby('Pclass')

male_first = male_pass_class.get_group(1)
male_second = male_pass_class.get_group(2)
male_third = male_pass_class.get_group(3)

# %%
# Histogram of female passengers per class, this way we can conclude that most female passengers survived in the first and second class
fig, ax = plt.subplots(1,3, figsize=(20,5))

ax[0].hist(female_first.Survived)
ax[0].set_title("First class female passangers",fontsize = 20)
ax[0].set_ylabel("Total number of female passangers",fontsize = 15)
ax[0].set_xticklabels(xlabels)
ax[0].set_xticks(range(0,2,1))

ax[1].hist(female_second.Survived)
ax[1].set_title("Second class female passangers",fontsize = 20)
ax[1].set_ylabel("Total number of female passangers",fontsize = 15)
ax[1].set_xticklabels(xlabels)
ax[1].set_xticks(range(0,2,1))

ax[2].hist(female_third.Survived)
ax[2].set_title("Third class female passangers",fontsize = 20)
ax[2].set_ylabel("Total number of female passangers",fontsize = 15)
ax[2].set_xticklabels(xlabels)
ax[2].set_xticks(range(0,2,1))

plt.show()

# %%
# Histogram of male passengers per class, most male passengers died in every class
fig, ax = plt.subplots(1,3, figsize=(20,5))

ax[0].hist(male_first.Survived)
ax[0].set_title("First class male passangers",fontsize = 20)
ax[0].set_ylabel("Total number of male passangers",fontsize = 15)
ax[0].set_xticklabels(xlabels)
ax[0].set_xticks(range(0,2,1))

ax[1].hist(male_second.Survived)
ax[1].set_title("Second class male passangers",fontsize = 20)
ax[1].set_ylabel("Total number of male passangers",fontsize = 15)
ax[1].set_xticklabels(xlabels)
ax[1].set_xticks(range(0,2,1))

ax[2].hist(male_third.Survived)
ax[2].set_title("Third class male passangers",fontsize = 20)
ax[2].set_ylabel("Total number of male passangers",fontsize = 15)
ax[2].set_xticklabels(xlabels)
ax[2].set_xticks(range(0,2,1))

plt.show()

# %%
#Create title feature from name
df_train['Title'] = df_train.Name.str.split(', ').str[1]
df_train['Title'] = df_train.Title.str.split('. ').str[0]

df_test['Title'] = df_test.Name.str.split(', ').str[1]
df_test['Title'] = df_test.Title.str.split('. ').str[0]

# %%
# Create bins to fit an fare range to every passenger
bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200]
bin_labels_fare = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90-99', '100-149', '150+']

# Cut age into age groups so you can view it better
df_train['Farerange'] = pd.cut(df_train.Fare, bins, labels = bin_labels_fare,include_lowest = True)
df_test['Farerange'] = pd.cut(df_test.Fare, bins, labels = bin_labels_fare,include_lowest = True)

# %%
# Check the most common fare range among surving male passengers in first class
male_surv_first_class = df_train[(df_train.Sex == 'male') & (df_train.Pclass == 1) & (df_train.Survived == 1)]
print(male_surv_first_class.Farerange.mode())
# display(male_surv_first_class)

# Check the most common fare range among surving female passengers in first class
female_surv_first_class = df_train[(df_train.Sex == 'female') & (df_train.Pclass == 1) & (df_train.Survived == 1)]
print(female_surv_first_class.Farerange.mode())
# display(male_surv_first_class)

# %%
# Check the most common fare range among surving male passengers in second class
male_surv_second_class = df_train[(df_train.Sex == 'male') & (df_train.Pclass == 2) & (df_train.Survived == 1)]
print(male_surv_second_class.Farerange.mode())
# display(male_surv_second_class)

# Check the most common fare range among surving female passengers in second class
female_surv_second_class = df_train[(df_train.Sex == 'female') & (df_train.Pclass == 2) & (df_train.Survived == 1)]
print(female_surv_second_class.Farerange.mode())
# display(male_surv_second_class)

# %%
# Check the most common fare range among surving male passengers in third class
male_surv_third_class = df_train[(df_train.Sex == 'male') & (df_train.Pclass == 3) & (df_train.Survived == 1)]
print(male_surv_third_class.Farerange.mode())
# display(male_surv_third_class)

# Check the most common fare range among surving female passengers in third class
female_surv_third_class = df_train[(df_train.Sex == 'female') & (df_train.Pclass == 3) & (df_train.Survived == 1)]
print(female_surv_third_class.Farerange.mode())
# display(male_surv_third_class)

# %%
df_train['Comp'] = df_train['SibSp'] + df_train['Parch']
df_test['Comp'] = df_test['SibSp'] + df_test['Parch']

# %%
df_surv= df_train.loc[(df_train['Pclass'] == 1) & (df_train['Sex'] == 'female')]
df_not_surv = df_train.loc[(df_train['Pclass'] == 2) & (df_train['Sex'] == 'male')  & (df_train['Survived'] == 0)]

fig, ax = plt.subplots()

sns.histplot(data=df_surv, x='Age', hue='Survived')
plt.show()




# %% [markdown]
# Hier onder wordt de test data aangepast en in een csv file opgeslagen om het resultaat te kunnen inleveren op Kaggle

# %%
# Male in first class
df_test[(df_test['Sex'] == 'male') & (df_test['Pclass'] == 1) & (df_test['Comp'] == 3)]
df_test.loc[(df_test['Sex'] == 'male') & (df_test['Pclass'] == 1) & (df_test['Age'] > 79) , 'Survived'] = 1

# Male in second class
df_test.loc[(df_test['Sex'] == 'male') & (df_test['Pclass'] == 2) & (df_test['Age'] < 10), 'Survived'] = 1

# Male in third class
df_test.loc[(df_test['Sex'] == 'male') & (df_test['Pclass'] == 3) & (df_test['Fare'] > 50) & (df_test['Fare'] < 60), 'Survived'] = 1

# Female in first class
df_test.loc[(df_test['Sex'] == 'female') & (df_test['Pclass'] == 1), 'Survived'] = 1
df_test.loc[(df_test['Sex'] == 'female') & (df_test['Pclass'] == 1) & (df_test['Age'] < 9), 'Survived'] = 0

# Female in second class
df_test.loc[(df_test['Sex'] == 'female') & (df_test['Pclass'] == 2), 'Survived'] = 1

# Female in third class
df_test[(df_test['Sex'] == 'female') & (df_test['Pclass'] == 3) & (df_test['Comp'] == 3)]

# Everyone that payed more than 500 survives
df_test.loc[(df_test['Fare'] > 500), 'Survived'] = 1




# %%
# Create new dataframe that only contains de PassengerId and Survived columns
data = df_test[['PassengerId', 'Survived']]

# Display the new dataframe
display(data)

# Create a csv file of the dataframe called result
# data.to_csv('result.csv', index=False)


