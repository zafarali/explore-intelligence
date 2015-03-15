
# coding: utf-8

# # Plot.ly Challenge
# I was given a challenge by plot.ly to make a creative graph. Here is the walk through of what I created.
# 
# ## Inspiration
# In the midst of March Break, I find myself stuck in Montreal and I wonder at what age do Canadian travel. When would I travel? 
# 
# ## Methodology
# I found two data disjoint sets from Statistics Canada for the years [1980 to 1996](http://www5.statcan.gc.ca/cansim/pick-choisir?lang=eng&id=04260008&p2=33) and [2006 to 2010](http://www5.statcan.gc.ca/cansim/pick-choisir?lang=eng&id=04260014&p2=33) and cleaned them for joining. I wanted to look at Age ranges and the trend over the years. 
# 
# ## Questions
# 1. At what age do Canadians Travel the most?
# 2. How has the trend changed over the years and the decades?
# 
# *Answers at the end*
# 

# We first import all the necessary [plot.ly](http://plot.ly) packages. *(note that I've already saved my username and API key, you must do this too)*

# In[246]:

# Here we import all our plotting requirements
import plotly
print 'plot.ly version:', plotly.__version__

pltly = plotly.plotly

import plotly.tools as pltls
from plotly.graph_objs import *


# In[378]:

import pandas as pd #import pandas
import numpy as np #import numpy


# We now proceed to import our first data set which contains data for the years 2006 to 2010. The `CHAR` column contains different characteristics and the `Value` column contains the corresponding column. We are interested in the characteristic 'Age group'.
# 
# 

# In[380]:

# import the data
data = pd.read_csv('travel_data_canada.csv')

# convert values to floats
data['Value'] = data['Value'].convert_objects(convert_numeric=True)


# The data set also contains information regarding the different provices of Canada, however, we only want the Canada-wide statistics,

# In[381]:

# we want canada wide stats
data = data[data.GEO=='Canada']

data.head()


# Now for the data cleaning *(Note the use of *`r'*'`* is REGEX and is important for pattern matching)*:

# In[382]:

# we now select age group data only
data = data[data['CHAR'].str.contains(r'Age group,')]

# remove the 'Age group' text before our categories
data['CHAR'] = data['CHAR'].str[11:]

#rename the column to be reflective of what it shows and for consistency with later data set
data.rename(columns={'CHAR':'AGE'}, inplace=True)


# select overnight data only
pattern = r'Overnight'
data = data[data['DURATION'].str.contains(pattern)]

#delete unnecessary columns
del data['Vector']
del data['Coordinate']
del data['DURATION']
del data['GEO']
data.head()


# Now we deal with the older data from 1980 to 1996:

# In[251]:

olddata = pd.read_csv('travel_data_canada_old.csv')

#change the value to numeric values
olddata['Value'] = olddata['Value'].convert_objects(convert_numeric=True)

#select only overnight data for consistency
olddata = olddata[olddata['DURATION']=='Overnight']


# select specific age groups only.
olddata = olddata[(olddata['AGE'].str.contains(r'All ages') == False)]
olddata = olddata[olddata['AGE'].str.contains(r'Under') == False]

#data cleaning
olddata['AGE'] = olddata['AGE'].str[:-10]

olddata['AGE'] = olddata['AGE'].str.replace('years of age and over', 'years and over')
del olddata['Vector']
del olddata['Coordinate']
del olddata['UOM']
del olddata['GEO']
del olddata['DURATION']
olddata.head()


# The old data contains '15-19 years' instead of '18-19 years', for simplicity, I just changed the prior to the latter.

# In[252]:

#merging the two data frames
alldata = pd.concat([data, olddata])

#some data cleaning
alldata['AGE'] = alldata['AGE'].str.replace('15', '18')
alldata['AGE'] = alldata['AGE'].str.replace(r'[ ]*-[ ]*', ' to ')
alldata.head()


# Now we need to decide what kind of graph we need. I'm thinking of something like the following:
# 
# Y-axis : number of people
# 
# X-axis : age groups

# In[364]:

# now lets prepare our data for plotting

years = sorted(list(set(list(alldata['Ref_Date'].values.astype(int)))))
stringify = np.vectorize(lambda x: str(x))

plotdata = {}
for year in years:
    thisYearData = alldata[alldata['Ref_Date'] == year]
    plotdata[str(year)] = {}
    plotdata[str(year)]['x'] = stringify(thisYearData['AGE'].values).tolist()
    plotdata[str(year)]['y'] = thisYearData['Value'].values.tolist()



# So far we have enough data to plot year lines. However, I also want to compare decade averages...

# In[374]:

# get our categories
decades = [1990, 2000, 2011]
ageCategories = sorted(list(set(alldata['AGE'].values.tolist())))


#preparation of our summary data
summaryData = {}
for decade in decades:
    thisSummary = alldata[alldata['Ref_Date'].isin(range(decade-10,decade))].groupby('AGE').mean()
    summaryData[str(decade)] = {}
    summaryData[str(decade)]['x'] = ageCategories
    summaryData[str(decade)]['y'] = thisSummary['Value'].values.tolist()



# We now have all the plotting data we need seperated as follows:
# 
# ```
# year: {
#     x: age,
#     y: value
# }
# ```
# we can iterate over these list and turn it into plot.ly `Scatter` objects.
# 
# I normalize the data using the following formula (with some adjustments for coloring):

# In[390]:

get_ipython().run_cell_magic(u'latex', u'', u'N(x_i) = \\frac{x_i - min(x)}{max(x)-min(x)}')


# In[385]:

#set up the traces
# we will use our base rgba(20, 72, 119, N) where N=year/max(years)

traces = []
maxYear = float(max(years))
minYear = float(min(years))

normalize = lambda year, maxYear = (maxYear+25), minYear = minYear : (year - minYear)/(maxYear - minYear)

for year, yearData in plotdata.items():
    alphaChannel = normalize(float(year))
    color = 'rgba(20, 72, 119, %f)' % (alphaChannel if alphaChannel != 0 else 0.10)
    thisTrace = Scatter(
        x = yearData['x'],
        y = yearData['y'],
        name = str(year),
        marker = Marker(
                color = color
        ),
        line = Line(
                shape = 'spline'
        )
    )
    traces = traces + [thisTrace]
    
#now for the decade summaries:

for decade, decadeData in summaryData.items():
    alphaChannel = normalize(float(decade), max(decades), min(decades))
    color = 'rgba(215, 40, 40, %f)' % (alphaChannel if alphaChannel > 0.2 else (0.4 - alphaChannel))
    thisTrace = Scatter(
        x = decadeData['x'],
        y = decadeData['y'],
        name = '%ss average'% (str(int(decade)-10 if decade != '2011' else 2000)),
        marker = Marker(
            color = color
        ),
    line = Line(
            shape = 'spline'
        )
    )
    traces = traces + [thisTrace]
        
    
# set up the data
pltlyData = Data(traces)

#set up the layout
layout = Layout(
    title = 'At what age do Canadians travel?',
    xaxis = XAxis(
        title ='Age group'
    ),
    yaxis = YAxis(
        title = 'Number of Canadians'
    ),
    legend = Legend(
        traceorder = 'reversed'
    )
#     barmode = 'group',
#     bargap = 0.15,
#     bargroupgap = 0.1
)

fig = Figure(data = pltlyData, layout = layout)


# In[386]:

pltly.iplot(fig, filename='canadians-travel-by-age')


# Ligher colors represent older data while darker colors represent more recent data (blues). You can click the blue lines on the legend to get rid of them and just see average trends (red).
# 
# ## Conclusions
# 1. It seems that people travel for longer periods of their lives more recent decades. In 1980s, most people traveled between 26 and 44 years. While in the 2010s, most people traveled between 25 and 64 years.
# 2. Peak travel is in the age group of 25 to 34 years.
# 3. The time to travel in my life is still a few years away!
# 
# ### Pitfalls
# We cannot conclude that more people travel in the 2000s due to increases in population sizes.

# Thanks for reading!
# You can see more of my stuff on my [website](http://zafarali.me) or you can check out my [plot.ly](http://plot.ly/~iamzaf)





