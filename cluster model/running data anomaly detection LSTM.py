#!/usr/bin/env python
# coding: utf-8

# In[18]:


get_ipython().system('pip install plotly==2.7.0')
import pandas as pd
import numpy as np
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.plotly as py
import matplotlib.pyplot as plt
from matplotlib import pyplot
import plotly.graph_objs as go
init_notebook_mode(connected=True)


# In[19]:


time_series_df=pd.read_csv('../Data/main/Maritius_AOI_20200701_0731_full.csv')


# In[20]:


time_series_df.head()


# In[21]:


time_series_df.sort_values(by=['timestamp'], inplace=True)


# In[22]:


time_series_df.head()


# In[23]:


print(time_series_df.loc[time_series_df['timestamp'] == '2020-07'])


# In[24]:


time_sorted_df = time_series_df.sort_values(by=['timestamp'], inplace=True)


# In[27]:


time_series_df.head()


# In[28]:


time_series_df.head()


# In[29]:


time_series_df


# In[30]:


time_series_df.info()


# In[31]:


time_series_df['timestamp'] = pd.to_datetime(time_series_df['timestamp'], infer_datetime_format=True)


# In[32]:


time_series_df.info()


# In[33]:


time_series_df.head()


# In[34]:


time_series_df.set_index('timestamp')[['speed', 'course','heading', 'rot']].plot(subplots=True)


# In[35]:


plt.plot( time_series_df['timestamp'], time_series_df['speed'])


# In[36]:


time_series_df.drop(["call_sign", "flag" ,"draught" , "ship_and_cargo_type",  "length", "width","eta" , "destination",  "status", "maneuver",  "accuracy" ,"collection_type" ,'mmsi_label'], axis=1, inplace=True)


# In[37]:


time_series_df.info()


# In[38]:


time_series_df.head()


# In[39]:


time_series_df.drop(['created_at','imo', 'name'], axis=1, inplace=True)


# In[40]:


time_series_df.head()


# In[41]:


time_series_df = time_series_df[time_series_df['speed'].notna()]


# In[42]:


time_series_df.head()


# In[43]:


time_series_df.info()


# In[44]:


plt.plot( time_series_df['timestamp'], time_series_df['speed'])


# In[45]:


plt.plot( time_series_df['timestamp'], time_series_df['speed'])
plt.gcf().autofmt_xdate()
plt.show()


# In[47]:


time_series_df = time_series_df.reset_index(drop=True)


# In[48]:


time_series_df.head()


# In[54]:


len(time_series_df[(time_series_df['heading']==0)])


# In[55]:


plt.plot( time_series_df['timestamp'], time_series_df['heading'])
plt.gcf().autofmt_xdate()
plt.show()


# In[56]:


plt.plot( time_series_df['timestamp'], time_series_df['course'])
plt.gcf().autofmt_xdate()
plt.show()


# In[83]:


import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler


np.random.seed(1)
tf.random.set_seed(1)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, RepeatVector, TimeDistributed


# In[112]:


print(time_series_df.loc[[15000]])


# In[114]:


train, test = time_series_df.loc[time_series_df['timestamp'] <= '2020-07-19 13:33:26+00:00'], time_series_df.loc[time_series_df['timestamp'] > '2020-07-19 13:33:26+00:00']


# In[115]:


train.shape, test.shape


# In[116]:


scaler = StandardScaler()
scaler = scaler.fit(train[['speed']])


# In[118]:


train['speed'] = scaler.transform(train[['speed']])
test['speed'] = scaler.transform(test[['speed']])


# In[119]:


TIME_STEPS=30 
# last 30 items together

def create_sequences(X, y, time_steps=TIME_STEPS):
    Xs, ys = [], []
    for i in range(len(X)-time_steps):
        Xs.append(X.iloc[i:(i+time_steps)].values)
        ys.append(y.iloc[i+time_steps])
    
    return np.array(Xs), np.array(ys)


# In[120]:


X_train, y_train = create_sequences(train[['speed']], train['speed'])
X_test, y_test = create_sequences(test[['speed']], test['speed'])


# In[121]:


print(f'Training shape: {X_train.shape}')
print(f'Testing shape: {X_test.shape}')


# In[ ]:


# Building the model


# In[ ]:




