#!/usr/bin/env python
# coding: utf-8

# In[244]:


import pandas as pd
import numpy as np
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
# import plotly.plotly as py
import matplotlib.pyplot as plt
from matplotlib import pyplot
import plotly.graph_objs as go
init_notebook_mode(connected=True)


# In[245]:


time_series_df=pd.read_csv('../Data/main/Maritius_AOI_20200701_0731_full.csv')


# In[246]:


time_series_df.head()


# In[247]:


time_series_df.sort_values(by=['timestamp'], inplace=True)


# In[248]:


time_series_df.head()


# In[249]:


print(time_series_df.loc[time_series_df['timestamp'] == '2020-07'])


# In[250]:


time_sorted_df = time_series_df.sort_values(by=['timestamp'], inplace=True)


# In[251]:


time_series_df.head()


# In[252]:


time_series_df.head()


# In[253]:


time_series_df


# In[254]:


time_series_df.info()


# In[255]:


time_series_df['timestamp'] = pd.to_datetime(time_series_df['timestamp'], infer_datetime_format=True)


# In[256]:


time_series_df.info()


# In[257]:


time_series_df.head()


# In[ ]:





# In[258]:


plt.plot( time_series_df['timestamp'], time_series_df['speed'])


# In[259]:


time_series_df.drop(["call_sign", "flag" ,"draught" , "ship_and_cargo_type",  "length", "width","eta" , "destination",  "status", "maneuver",  "accuracy" ,"collection_type" ,'mmsi_label'], axis=1, inplace=True)


# In[260]:


time_series_df.info()


# In[261]:


time_series_df.head()


# In[262]:


time_series_df.drop(['created_at','imo', 'name'], axis=1, inplace=True)


# In[263]:


time_series_df.head()


# In[264]:


time_series_df = time_series_df[time_series_df['speed'].notna()]


# In[265]:


time_series_df.head()


# In[266]:


time_series_df.info()


# In[267]:


plt.plot( time_series_df['timestamp'], time_series_df['speed'])


# In[268]:


plt.plot( time_series_df['timestamp'], time_series_df['speed'])
plt.gcf().autofmt_xdate()
plt.show()


# In[269]:


time_series_df = time_series_df.reset_index(drop=True)


# In[270]:


time_series_df.head()


# In[271]:


len(time_series_df[(time_series_df['heading']==0)])


# In[272]:


plt.plot( time_series_df['timestamp'], time_series_df['heading'])
plt.gcf().autofmt_xdate()
plt.show()


# In[273]:


plt.plot( time_series_df['timestamp'], time_series_df['course'])
plt.gcf().autofmt_xdate()
plt.show()


# In[274]:


print(time_series_df.loc[[18000]])


# In[275]:


time_series_df.head()


# In[276]:


time_series_df.info()


# In[277]:


time_series_df.info()
time_series_df.drop(time_series_df[time_series_df['speed'] == 0].index, inplace = True) 


# In[278]:


time_series_df.mmsi.unique() 


# In[279]:


mv_value = 372711000
param = 'course'


# In[280]:


len(time_series_df[time_series_df["mmsi"]==mv_value])


# In[281]:


len(time_series_df[time_series_df["speed"]==0])


# In[282]:


mv_data = time_series_df[time_series_df['mmsi']==mv_value]


# In[283]:


mv_data.head()


# In[284]:


plt.plot( mv_data['timestamp'], mv_data['speed'])
plt.gcf().autofmt_xdate()
plt.show()


# In[285]:


plt.plot( mv_data['timestamp'], mv_data['course'])
plt.gcf().autofmt_xdate()
plt.show()


# In[286]:


# mv_data.reset_index(inplace=True) 
mv_data = mv_data.drop(['mmsi','msg_type','latitude', 'longitude'], axis=1)
mv_data.head()


# In[287]:


mv_data = mv_data[mv_data['speed'].notna()]
mv_data.info()


# In[288]:


mv_data.head()


# In[289]:


import warnings
mv_data = mv_data.set_index(['timestamp'])
mv_data.index = pd.to_datetime(mv_data.index, unit='s')

names=mv_data.columns
# Resample the entire dataset by daily average
rollmean = mv_data.resample(rule='D').mean()
rollstd = mv_data.resample(rule='D').std()
# Plot time series for each sensor with its mean and standard deviation
for name in names:
    _ = plt.figure(figsize=(18,3))
    _ = plt.plot(mv_data[name], color='blue', label='Original')
    _ = plt.plot(rollmean[name], color='red', label='Rolling Mean')
    _ = plt.plot(rollstd[name], color='black', label='Rolling Std' )
    _ = plt.legend(loc='best')
    _ = plt.title(name)
    plt.show()


# In[290]:


from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
df2 = mv_data
names=df2.columns
x = mv_data[names]
scaler = StandardScaler()
pca = PCA()
pipeline = make_pipeline(scaler, pca)
pipeline.fit(x)


# In[291]:


features = range(pca.n_components_)
_ = plt.figure(figsize=(15, 5))
_ = plt.bar(features, pca.explained_variance_)
_ = plt.xlabel('PCA feature')
_ = plt.ylabel('Variance')
_ = plt.xticks(features)
_ = plt.title("Importance of the Principal Components based on inertia")
plt.show()


# In[292]:


pca = PCA(n_components=2)
principalComponents = pca.fit_transform(x)
principalDf = pd.DataFrame(data = principalComponents, columns = ['pc1', 'pc2'])


# In[293]:


mv_data['pc1']=pd.Series(principalDf['pc1'].values, index=mv_data.index)
mv_data['pc2']=pd.Series(principalDf['pc2'].values, index=mv_data.index)


# In[294]:


from statsmodels.tsa.stattools import adfuller
# Run Augmented Dickey Fuller Test
result = adfuller(principalDf['pc1'])
# Print p-value
print(result[1])


# In[295]:


# Compute change in daily mean 
pca1 = principalDf['pc1'].pct_change()
# Compute autocorrelation
autocorrelation = pca1.dropna().autocorr()
print('Autocorrelation is: ', autocorrelation)


# In[296]:


from statsmodels.graphics.tsaplots import plot_acf
plot_acf(pca1.dropna(), lags=20, alpha=0.05)


# In[297]:


# Compute change in daily mean 
pca2 = principalDf['pc2'].pct_change()
# Compute autocorrelation
autocorrelation = pca2.autocorr()
print('Autocorrelation is: ', autocorrelation)


# In[298]:



from statsmodels.graphics.tsaplots import plot_acf
plot_acf(pca2.dropna(), lags=20, alpha=0.05)


# In[299]:



# outlier_lower = Q1 - (1.5*IQR)
# outlier_upper = Q3 + (1.5*IQR)
# Calculate outlier bounds for pc1
q1_pc1, q3_pc1 = mv_data['pc1'].quantile([0.25, 0.75])
iqr_pc1 = q3_pc1 - q1_pc1
lower_pc1 = q1_pc1 - (1.5*iqr_pc1)
upper_pc1 = q3_pc1 + (1.5*iqr_pc1)
# Calculate outlier bounds for pc2
q1_pc2, q3_pc2 = mv_data['pc2'].quantile([0.25, 0.75])
iqr_pc2 = q3_pc2 - q1_pc2
lower_pc2 = q1_pc2 - (1.5*iqr_pc2)
upper_pc2 = q3_pc2 + (1.5*iqr_pc2)


# In[300]:


lower_pc1, upper_pc1


# In[301]:


lower_pc2, upper_pc2


# In[302]:


mv_data['anomaly_pc1'] = ((mv_data['pc1']>upper_pc1) | (mv_data['pc1']<lower_pc1)).astype('int')
mv_data['anomaly_pc2'] = ((mv_data['pc2']>upper_pc2) | (mv_data['pc2']<lower_pc2)).astype('int')


# In[303]:


mv_data['anomaly_pc1'].value_counts()


# In[304]:


mv_data['anomaly_pc2'].value_counts()


# In[305]:


outliers_pc1 = mv_data.loc[(mv_data['pc1']>upper_pc1) | (mv_data['pc1']<lower_pc1), 'pc1']
outliers_pc2 = mv_data.loc[(mv_data['pc2']>upper_pc2) | (mv_data['pc2']<lower_pc2), 'pc2']


# In[306]:


len(outliers_pc1)/len(mv_data)


# In[307]:


len(outliers_pc2)/len(mv_data)


# In[308]:


mv_data.head()


# In[309]:


a = mv_data[mv_data['anomaly_pc1'] == 1] #anomaly
b = mv_data[mv_data['anomaly_pc2'] == 1] #anomaly
plt.figure(figsize=(18,6))
plt.plot(mv_data[param], color='blue', label='Normal')
plt.plot(a[param], linestyle='none', marker='X', color='red', markersize=12, label='Anomaly1')
plt.plot(b[param], linestyle='none', marker='X', color='green', markersize=12, label='Anomaly2')
plt.xlabel('Date and Time')
plt.ylabel(param)
plt.title(param +' Anomalies')
plt.legend(loc='best')
plt.show();


# In[310]:


b.info()


# In[311]:


from sklearn.cluster import KMeans
# I will start k-means clustering with k=2 as I already know that there are 3 classes of "NORMAL" vs 
# "NOT NORMAL" which are combination of BROKEN" and"RECOVERING"
kmeans = KMeans(n_clusters=2, random_state=42)
kmeans.fit(principalDf.values)
labels = kmeans.predict(principalDf.values)
unique_elements, counts_elements = np.unique(labels, return_counts=True)
clusters = np.asarray((unique_elements, counts_elements))


# In[312]:


plt.figure(figsize = (9, 7))
plt.bar(clusters[0], clusters[1], tick_label=clusters[0])
plt.xlabel('Clusters')
plt.ylabel('Number of points')
plt.title('Number of points in each cluster')
plt.show()


# In[313]:


plt.figure(figsize=(9,7))
plt.scatter(principalDf['pc1'], principalDf['pc2'], c=labels)
plt.xlabel('pc1')
plt.ylabel('pc2')
plt.title('K-means of clustering')
plt.show()


# In[314]:


def getDistanceByPoint(data, model):
    """ Function that calculates the distance between a point and centroid of a cluster, 
            returns the distances in pandas series"""
    distance = []
    for i in range(0,len(data)):
        Xa = np.array(data.loc[i])
        Xb = model.cluster_centers_[model.labels_[i]-1]
        distance.append(np.linalg.norm(Xa-Xb))
    return pd.Series(distance, index=data.index)


# In[315]:


outliers_fraction = 0.13
# get the distance between each point and its nearest centroid. The biggest distances are considered as anomaly
distance = getDistanceByPoint(principalDf, kmeans)
# number of observations that equate to the 13% of the entire data set
number_of_outliers = int(outliers_fraction*len(distance))
# Take the minimum of the largest 13% of the distances as the threshold
threshold = distance.nlargest(number_of_outliers).min()
# anomaly1 contain the anomaly result of the above method Cluster (0:normal, 1:anomaly) 
principalDf['anomaly1'] = (distance >= threshold).astype(int)


# In[316]:


principalDf.head()


# In[317]:


principalDf['anomaly1'].value_counts()


# In[ ]:





# In[318]:


mv_data['anomaly1'] = pd.Series(principalDf['anomaly1'].values, index=mv_data.index)
a = mv_data[mv_data['anomaly1'] == 1] #anomaly
plt.figure(figsize=(18,6))
plt.plot(mv_data[param], color='blue', label='Normal')
plt.plot(a[param], linestyle='none', marker='X', color='red', markersize=12, label='Anomaly')
plt.xlabel('Date and Time')
plt.ylabel(param)
plt.title('Anomalies')
plt.legend(loc='best')
plt.show();


# In[319]:


# Import IsolationForest
from sklearn.ensemble import IsolationForest
# Assume that 13% of the entire data set are anomalies 
outliers_fraction = 0.13
model =  IsolationForest(contamination=outliers_fraction)
model.fit(principalDf.values) 
principalDf['anomaly2'] = pd.Series(model.predict(principalDf.values))


# In[320]:


# visualization
mv_data['anomaly2'] = pd.Series(principalDf['anomaly2'].values, index=mv_data.index)
a = mv_data.loc[mv_data['anomaly2'] == -1] #anomaly
plt.figure(figsize=(18,6))
plt.plot(mv_data[param], color='blue', label='Normal')
plt.plot(mv_data[param], linestyle='none', marker='X', color='red', markersize=12, label='Anomaly')
plt.xlabel('Date and Time')
plt.ylabel(param +'Reading')
plt.title('Anomalies')
plt.legend(loc='best')
plt.show();


# In[321]:


mv_data['anomaly2'].value_counts()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




