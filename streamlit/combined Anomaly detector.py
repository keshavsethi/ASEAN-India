
# data
time_series_df=pd.read_csv('../Data/main/Maritius_AOI_20200701_0731_full.csv')
time_series_df.sort_values(by=['timestamp'], inplace=True)
time_sorted_df = time_series_df.sort_values(by=['timestamp'], inplace=True)
time_series_df['timestamp'] = pd.to_datetime(time_series_df['timestamp'])


# cleaning and indexing
time_series_df.drop(["call_sign", "flag" ,"draught" , "ship_and_cargo_type",  "length", "width","eta" , "destination",  "status", "maneuver",  "accuracy" ,"collection_type" ,'mmsi_label'], axis=1, inplace=True)
time_series_df.drop(['created_at','imo', 'name'], axis=1, inplace=True)
time_series_df = time_series_df[time_series_df['speed'].notna()]
time_series_df = time_series_df.reset_index(drop=True)
time_series_df.drop(time_series_df[time_series_df['speed'] == 0].index, inplace = True) 


# list mmsi
time_series_df.mmsi.unique() 

# paramameters -> speed, course, rot, heading
mv_value = 477269900
param = 'speed'
fraction = 0.05

# Data after parameters and everything
len(time_series_df[time_series_df["mmsi"]==mv_value])
mv_data = time_series_df[time_series_df['mmsi']==mv_value]


# param ploting after selecting vessel 
plt.plot( mv_data['timestamp'], mv_data['speed'])
plt.gcf().autofmt_xdate()
plt.show()

plt.plot( mv_data['timestamp'], mv_data['course'])
plt.gcf().autofmt_xdate()
plt.show()

plt.plot( mv_data['timestamp'], mv_data['rot'])
plt.gcf().autofmt_xdate()
plt.show()

plt.plot( mv_data['timestamp'], mv_data['heading'])
plt.gcf().autofmt_xdate()
plt.show()

# data cleaning again
mv_data = mv_data.drop(['mmsi','msg_type','latitude', 'longitude'], axis=1)
mv_data = mv_data[mv_data['speed'].notna()]
mv_data = mv_data.set_index(['timestamp'])
mv_data.index = pd.to_datetime(mv_data.index, unit='s')
names=mv_data.columns
rollmean = mv_data.resample(rule='D').mean()
rollstd = mv_data.resample(rule='D').std()


# Method 1 (checkpoint)
df2 = mv_data
names=df2.columns
x = mv_data[names]
scaler = StandardScaler()
pca = PCA()
pipeline = make_pipeline(scaler, pca)
pipeline.fit(x)


# PCA feature graph (Not done)
features = range(pca.n_components_)
plt.figure(figsize=(15, 5))
plt.bar(features, pca.explained_variance_)
plt.xlabel('PCA feature')
plt.ylabel('Variance')
plt.xticks(features)
plt.title("Importance of the Principal Components based on inertia")
plt.show()


pca = PCA(n_components=2)
principalComponents = pca.fit_transform(x)
principalDf = pd.DataFrame(data = principalComponents, columns = ['pc1', 'pc2'])
mv_data['pc1']=pd.Series(principalDf['pc1'].values, index=mv_data.index)
mv_data['pc2']=pd.Series(principalDf['pc2'].values, index=mv_data.index)

# p value and pc1 and pc2 autocorrelation
result = adfuller(principalDf['pc1'])
print(result[1])
pca1 = principalDf['pc1'].pct_change()
autocorrelation = pca1.dropna().autocorr()
print('Autocorrelation is: ', autocorrelation)
plot_acf(pca1.dropna(), lags=20, alpha=0.05)
pca2 = principalDf['pc2'].pct_change()
autocorrelation = pca2.autocorr()
print('Autocorrelation is: ', autocorrelation)
plot_acf(pca2.dropna(), lags=20, alpha=0.05)

# model calculations method 1
q1_pc1, q3_pc1 = mv_data['pc1'].quantile([0.25, 0.75])
iqr_pc1 = q3_pc1 - q1_pc1
lower_pc1 = q1_pc1 - (1.5*iqr_pc1)
upper_pc1 = q3_pc1 + (1.5*iqr_pc1)
q1_pc2, q3_pc2 = mv_data['pc2'].quantile([0.25, 0.75])
iqr_pc2 = q3_pc2 - q1_pc2
lower_pc2 = q1_pc2 - (1.5*iqr_pc2)
upper_pc2 = q3_pc2 + (1.5*iqr_pc2)
mv_data['anomaly_pc1'] = ((mv_data['pc1']>upper_pc1) | (mv_data['pc1']<lower_pc1)).astype('int')
mv_data['anomaly_pc2'] = ((mv_data['pc2']>upper_pc2) | (mv_data['pc2']<lower_pc2)).astype('int')
total_anomaly = mv_data['anomaly_pc1'].value_counts() + mv_data['anomaly_pc2'].value_counts()
outliers_pc1 = mv_data.loc[(mv_data['pc1']>upper_pc1) | (mv_data['pc1']<lower_pc1), 'pc1']
outliers_pc2 = mv_data.loc[(mv_data['pc2']>upper_pc2) | (mv_data['pc2']<lower_pc2), 'pc2']
len(outliers_pc1)/len(mv_data)
len(outliers_pc2)/len(mv_data)

# ploting anomaly method 1
a = mv_data[mv_data['anomaly_pc1'] == 1] #anomaly
b = mv_data[mv_data['anomaly_pc2'] == 1] #anomaly
plt.figure(figsize=(18,6))
plt.plot(mv_data[param], color='blue', label='Normal')
plt.plot(a[param], linestyle='none', marker='X', color='red', markersize=12, label='Anomaly1')
plt.plot(b[param], linestyle='none', marker='X', color='green', markersize=12, label='Anomaly2')
plt.xlabel('Date and Time')
plt.ylabel(param)
plt.title(param +' Anomalies with MMSI: ' mv_value)
plt.legend(loc='best')
plt.show();
data1 = a
data2 = b


#  Method 2 K means (checkpoint)
kmeans = KMeans(n_clusters=2, random_state=42)
kmeans.fit(principalDf.values)
labels = kmeans.predict(principalDf.values)
unique_elements, counts_elements = np.unique(labels, return_counts=True)
clusters = np.asarray((unique_elements, counts_elements))

# no of points in each clusters
plt.figure(figsize = (9, 7))
plt.bar(clusters[0], clusters[1], tick_label=clusters[0])
plt.xlabel('Clusters')
plt.ylabel('Number of points')
plt.title('Number of points in each cluster')
plt.show()

# cluster graph
plt.figure(figsize=(9,7))
plt.scatter(principalDf['pc1'], principalDf['pc2'], c=labels)
plt.xlabel('pc1')
plt.ylabel('pc2')
plt.title('K-means of clustering')
plt.show()

# function to be used
def getDistanceByPoint(data, model):
    distance = []
    for i in range(0,len(data)):
        Xa = np.array(data.loc[i])
        Xb = model.cluster_centers_[model.labels_[i]-1]
        distance.append(np.linalg.norm(Xa-Xb))
    return pd.Series(distance, index=data.index)

# method 2 calulations
outliers_fraction = fraction
distance = getDistanceByPoint(principalDf, kmeans)
number_of_outliers = int(outliers_fraction*len(distance))
threshold = distance.nlargest(number_of_outliers).min() 
principalDf['anomaly1'] = (distance >= threshold).astype(int)

# Anomaly count
principalDf['anomaly1'].value_counts()

# K means anomaly plots
mv_data['anomaly1'] = pd.Series(principalDf['anomaly1'].values, index=mv_data.index)
a = mv_data[mv_data['anomaly1'] == 1] #anomaly
plt.figure(figsize=(18,6))
plt.plot(mv_data[param], color='blue', label='Normal')
plt.plot(a[param], linestyle='none', marker='X', color='red', markersize=12, label='Anomaly')
plt.xlabel('Date and Time')
plt.ylabel(param)
plt.title(param +' Anomalies with MMSI: ' mv_value)
plt.legend(loc='best')
plt.show();
data3 = a


# IsolationForest method 3 (checkpoint)
outliers_fraction = fraction
model =  IsolationForest(contamination=outliers_fraction)
model.fit(principalDf.values) 
principalDf['anomaly2'] = pd.Series(model.predict(principalDf.values))

# visualization
mv_data['anomaly2'] = pd.Series(principalDf['anomaly2'].values, index=mv_data.index)
a = mv_data.loc[mv_data['anomaly2'] == -1] #anomaly
plt.figure(figsize=(18,6))
plt.plot(mv_data[param], color='blue', label='Normal')
plt.plot(a[param], linestyle='none', marker='X', color='red', markersize=12, label='Anomaly')
plt.xlabel('Date and Time')
plt.ylabel(param +'Reading')
plt.title(param +' Anomalies with MMSI: ' mv_value)
plt.legend(loc='best')
plt.show();
data4 = a

# anomaly count method 3 
mv_data['anomaly2'].value_counts()


# Method 4 
def intersection(lst1, lst2,lst3,lst4): 
    lst5 = [value for value in lst2 if value in lst1]
    lst6 = [value for value in lst3 if value in lst5]
    lst7 = [value for value in lst4 if value in lst6]
    return lst7
 
time_common = intersection(data1.index.unique() , data2.index.unique() , data3.index.unique() , data4.index.unique() )
time_df = pd.DataFrame(columns = mv_data.columns, index = time_common) 
for time in time_common:
    time_df.loc[time] = mv_data.loc[time]

# visualization
plt.figure(figsize=(18,6))
plt.plot(mv_data[param], color='blue', label='Normal')
plt.plot(time_df[param], linestyle='none', marker='X', color='red', markersize=12, label='Anomaly')
plt.xlabel('Date and Time')
plt.ylabel(param +'Reading')
plt.title('Anomalies')
plt.legend(loc='best')
plt.show();

