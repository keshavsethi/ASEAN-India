import pandas as pd
import numpy as np
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import matplotlib.pyplot as plt
from matplotlib import pyplot
import plotly.graph_objs as go
import streamlit as st
import warnings
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import streamlit as st
from bokeh.plotting import figure

def main():
    st.set_page_config(
    page_title="Oil Spill Dashboard",
    page_icon=":ship:",
    layout="centered",
    initial_sidebar_state="expanded",
    )



    def load_raw_data(x):
        # data
        time_series_df=pd.read_csv(x)
        time_series_df.sort_values(by=['timestamp'], inplace=True, kind = "mergesort")
        time_sorted_df = time_series_df.sort_values(by=['timestamp'], inplace=True)
        time_series_df['timestamp'] = pd.to_datetime(time_series_df['timestamp'])
        return time_series_df

    def load_data(x):
        time_series_df = load_raw_data(x)
        # cleaning and indexing
        time_series_df.drop(["call_sign", "flag" ,"draught" , "ship_and_cargo_type",  "length", "width","eta" , "destination",  "status", "maneuver",  "accuracy" ,"collection_type" ,'mmsi_label'], axis=1, inplace=True)
        time_series_df.drop(['created_at','imo', 'name'], axis=1, inplace=True)
        time_series_df = time_series_df[time_series_df['speed'].notna()]
        time_series_df = time_series_df.reset_index(drop=True)
        time_series_df.drop(time_series_df[time_series_df['speed'] == 0].index, inplace = True)
        return time_series_df

    st.title("Oil spill prediction Dashboard :rocket:")
    st.sidebar.title("Enter Parameters :paperclip:")
    st.sidebar.markdown("Powered by AIS Data set")
    load_csv_data = st.sidebar.checkbox("Upload Csv")

    if(load_csv_data):
        uploaded_file = st.file_uploader("Choose Csv file")
    else:
        uploaded_file = None
    if uploaded_file is not None:
        uploaded_file.seek(0)
        time_series_df1 = load_raw_data(uploaded_file)
        time_series_df = load_data(uploaded_file)
    else:
        time_series_df1 = load_raw_data('../Data/main/Maritius_AOI_20200701_0731_full.csv')
        time_series_df = load_data('../Data/main/Maritius_AOI_20200701_0731_full.csv')

    raw = st.sidebar.checkbox("Show Raw Dataset")
    not_raw = st.sidebar.checkbox("Show cleaned Dataset")
    if(raw):
        st.subheader("AIS Dataset (Raw)")
        st.dataframe(time_series_df1[:500].style.highlight_max(axis=0))
    if(not_raw):
        st.subheader("AIS Dataset (Cleaned)")
        st.dataframe(time_series_df[:500].style.highlight_max(axis=0))

    vessels = time_series_df.mmsi.unique()
    st.markdown("Anomaly detection with time series data of: ",len(vessels))
    classifier = st.sidebar.selectbox("Classifier",("Select one model","Code", "Benchmark model(IQR)","K-Means clustering","Isolation Forest", "All of the above(Best)"))


    mv_value = st.sidebar.selectbox("Select vessel", vessels)
    st.write("Selected Vessel: ", mv_value)
    param = st.sidebar.radio("Vessel Parameter",("speed", "course", "heading", "rot"),key='param')
    mv_data = time_series_df[time_series_df['mmsi']==mv_value]


    if st.button("Plot all basic graphs"):
        p = figure(
            title='Speed Vs Time',
            x_axis_label='Timestamp',
            y_axis_label='Speed')
            
        p.line(mv_data['timestamp'], mv_data['speed'], legend='Speed Trend', line_width=2)
        st.bokeh_chart(p, use_container_width=True)
            
        q = figure(
            title='Course Vs Time',
            x_axis_label='Timestamp',
            y_axis_label='Course')
        q.line(mv_data['timestamp'], mv_data['course'], legend='Course Trend', line_width=2)
        st.bokeh_chart(q, use_container_width=True)
            
        r = figure(
            title='Heading Vs Time',
            x_axis_label='Timestamp',
            y_axis_label='Heading')
        r.line(mv_data['timestamp'], mv_data['heading'], legend='Heading Trend', line_width=2)
        st.bokeh_chart(r, use_container_width=True)
            
        s = figure(
            title='Rot Vs Time',
            x_axis_label='Timestamp',
            y_axis_label='Rot')
        s.line(mv_data['timestamp'], mv_data['rot'], legend='Rot Trend', line_width=2)
        st.bokeh_chart(s, use_container_width=True)
    map_df = mv_data[time_series_df['latitude'].notna()]
    map_df = map_df[time_series_df['longitude'].notna()]
    if st.button("Plot Map"):
        map_df.filter(['latitude', 'longitude'])
        st.map(map_df)

    mv_data = mv_data.drop(['mmsi','msg_type','latitude', 'longitude'], axis=1)
    mv_data = mv_data[mv_data['speed'].notna()]
    mv_data = mv_data.set_index(['timestamp'])
    mv_data.index = pd.to_datetime(mv_data.index, unit='s')
    names=mv_data.columns
    rollmean = mv_data.resample(rule='D').mean()
    rollstd = mv_data.resample(rule='D').std()

    if classifier == "Benchmark model: Interquartile Range (IQR)":
        
        df2 = mv_data
        names=df2.columns
        x = mv_data[names]
        scaler = StandardScaler()
        pca = PCA()
        pipeline = make_pipeline(scaler, pca)
        pipeline.fit(x)

        features = range(pca.n_components_)

        pca = PCA(n_components=2)
        principalComponents = pca.fit_transform(x)
        principalDf = pd.DataFrame(data = principalComponents, columns = ['pc1', 'pc2'])
        mv_data['pc1']=pd.Series(principalDf['pc1'].values, index=mv_data.index)
        mv_data['pc2']=pd.Series(principalDf['pc2'].values, index=mv_data.index)

        result = adfuller(principalDf['pc1'])
        st.write("p value", result[1])
        pca1 = principalDf['pc1'].pct_change()
        autocorrelation = pca1.dropna().autocorr()
        st.write('Autocorrelation(pc1) is: ', autocorrelation)
        plot_acf(pca1.dropna(), lags=20, alpha=0.05)
        pca2 = principalDf['pc2'].pct_change()
        autocorrelation = pca2.autocorr()
        st.write('Autocorrelation(pc2) is: ', autocorrelation)
        plot_acf(pca2.dropna(), lags=20, alpha=0.05)
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
        st.write("Outlier Propotion(pc1): ", len(outliers_pc1)/len(mv_data))
        st.write("Outlier Propotion(pc2): ", len(outliers_pc2)/len(mv_data))

        a = mv_data[mv_data['anomaly_pc1'] == 1] #anomaly
        b = mv_data[mv_data['anomaly_pc2'] == 1] #anomaly
        fig = plt.figure()
        plt.plot(mv_data[param], color='blue', label='Normal')
        plt.plot(a[param], linestyle='none', marker='X', color='red', markersize=12, label='Anomaly1')
        plt.plot(b[param], linestyle='none', marker='X', color='green', markersize=12, label='Anomaly2')
        plt.xlabel('Date and Time')
        plt.ylabel(param)
        plt.title('Anomalies with given MMSI')
        plt.legend(loc='best')
        plt.show()
        plt.gcf().autofmt_xdate()
        st.pyplot(fig)
        data1 = a
        data2 = b


    if classifier == "K-Means clustering":
        df2 = mv_data
        names=df2.columns
        x = mv_data[names]
        scaler = StandardScaler()
        pca = PCA()
        pipeline = make_pipeline(scaler, pca)
        pipeline.fit(x)

        features = range(pca.n_components_)

        pca = PCA(n_components=2)
        principalComponents = pca.fit_transform(x)
        principalDf = pd.DataFrame(data = principalComponents, columns = ['pc1', 'pc2'])
        mv_data['pc1']=pd.Series(principalDf['pc1'].values, index=mv_data.index)
        mv_data['pc2']=pd.Series(principalDf['pc2'].values, index=mv_data.index)
        fraction = st.number_input("Fraction",0.00,1.00,step=0.01,key='fraction')
        kmeans = KMeans(n_clusters=2, random_state=42)
        kmeans.fit(principalDf.values)
        labels = kmeans.predict(principalDf.values)
        unique_elements, counts_elements = np.unique(labels, return_counts=True)
        clusters = np.asarray((unique_elements, counts_elements))

        # no of points in each clusters
        fig = plt.figure()
        plt.bar(clusters[0], clusters[1], tick_label=clusters[0])
        plt.xlabel('Clusters')
        plt.ylabel('Number of points')
        plt.title('Number of points in each cluster')
        st.pyplot(fig)

        # cluster graph
        fig = plt.figure()
        plt.scatter(principalDf['pc1'], principalDf['pc2'], c=labels)
        plt.xlabel('pc1')
        plt.ylabel('pc2')
        plt.title('K-means of clustering')
        st.pyplot(fig)

        # distance function to be used
        def getDistanceByPoint(data, model):
            distance = []
            for i in range(0,len(data)):
                Xa = np.array(data.loc[i])
                Xb = model.cluster_centers_[model.labels_[i]-1]
                distance.append(np.linalg.norm(Xa-Xb))
            return pd.Series(distance, index=data.index)

        outliers_fraction = fraction
        distance = getDistanceByPoint(principalDf, kmeans)
        number_of_outliers = int(outliers_fraction*len(distance))
        threshold = distance.nlargest(number_of_outliers).min() 
        principalDf['anomaly1'] = (distance >= threshold).astype(int)

        st.write("Anomaly Count by Kmeans", principalDf['anomaly1'].value_counts())

        mv_data['anomaly1'] = pd.Series(principalDf['anomaly1'].values, index=mv_data.index)
        a = mv_data[mv_data['anomaly1'] == 1] #anomaly
        fig = plt.figure(figsize=(18,6))
        plt.plot(mv_data[param], color='blue', label='Normal')
        plt.plot(a[param], linestyle='none', marker='X', color='red', markersize=12, label='Anomaly')
        plt.xlabel('Date and Time')
        plt.ylabel(param)
        plt.title('Anomalies with given MMSI')
        plt.legend(loc='best')
        plt.gcf().autofmt_xdate()
        st.pyplot(fig)
        data3 = a

    if classifier == "Isolation Forest":
        df2 = mv_data
        names=df2.columns
        x = mv_data[names]
        scaler = StandardScaler()
        pca = PCA()
        pipeline = make_pipeline(scaler, pca)
        pipeline.fit(x)

        features = range(pca.n_components_)

        pca = PCA(n_components=2)
        principalComponents = pca.fit_transform(x)
        principalDf = pd.DataFrame(data = principalComponents, columns = ['pc1', 'pc2'])
        mv_data['pc1']=pd.Series(principalDf['pc1'].values, index=mv_data.index)
        mv_data['pc2']=pd.Series(principalDf['pc2'].values, index=mv_data.index)
        fraction = st.number_input("Fraction",0.00,1.00,step=0.01,key='fraction')
        kmeans = KMeans(n_clusters=2, random_state=42)
        kmeans.fit(principalDf.values)
        labels = kmeans.predict(principalDf.values)
        unique_elements, counts_elements = np.unique(labels, return_counts=True)
        clusters = np.asarray((unique_elements, counts_elements))

        # IsolationForest method 3 (checkpoint)
        outliers_fraction = fraction
        model =  IsolationForest(contamination=outliers_fraction)
        model.fit(principalDf.values) 
        principalDf['anomaly2'] = pd.Series(model.predict(principalDf.values))

        # visualization
        mv_data['anomaly2'] = pd.Series(principalDf['anomaly2'].values, index=mv_data.index)
        a = mv_data.loc[mv_data['anomaly2'] == -1] #anomaly
        # anomaly count method 3 
        st.write("Anomaly count isolated forest: ", mv_data['anomaly2'].value_counts())
        fig = plt.figure()
        plt.plot(mv_data[param], color='blue', label='Normal')
        plt.plot(a[param], linestyle='none', marker='X', color='red', markersize=12, label='Anomaly')
        plt.xlabel('Date and Time')
        plt.ylabel('Reading')
        plt.title('Anomalies with given MMSI')
        plt.legend(loc='best')
        plt.gcf().autofmt_xdate()
        st.pyplot(fig)
        data4 = a



    if classifier == "All of the above(Best)":

        df2 = mv_data
        names=df2.columns
        x = mv_data[names]
        scaler = StandardScaler()
        pca = PCA()
        pipeline = make_pipeline(scaler, pca)
        pipeline.fit(x)
        features = range(pca.n_components_)
        pca = PCA(n_components=2)
        principalComponents = pca.fit_transform(x)
        principalDf = pd.DataFrame(data = principalComponents, columns = ['pc1', 'pc2'])
        mv_data['pc1']=pd.Series(principalDf['pc1'].values, index=mv_data.index)
        mv_data['pc2']=pd.Series(principalDf['pc2'].values, index=mv_data.index)
        result = adfuller(principalDf['pc1'])
        st.write("p value", result[1])
        pca1 = principalDf['pc1'].pct_change()
        autocorrelation = pca1.dropna().autocorr()
        st.write('Autocorrelation(pc1) is: ', autocorrelation)
        pca2 = principalDf['pc2'].pct_change()
        autocorrelation = pca2.autocorr()
        st.write('Autocorrelation(pc2) is: ', autocorrelation)
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
        st.write("Outlier Propotion(pc1): ", len(outliers_pc1)/len(mv_data))
        st.write("Outlier Propotion(pc2): ", len(outliers_pc2)/len(mv_data))
        a = mv_data[mv_data['anomaly_pc1'] == 1] #anomaly
        b = mv_data[mv_data['anomaly_pc2'] == 1] #anomaly
        data1 = a
        data2 = b

        fraction = st.number_input("Fraction",0.00,1.00,step=0.01,key='fraction')
        kmeans = KMeans(n_clusters=2, random_state=42)
        kmeans.fit(principalDf.values)
        labels = kmeans.predict(principalDf.values)
        unique_elements, counts_elements = np.unique(labels, return_counts=True)
        clusters = np.asarray((unique_elements, counts_elements))

        # distance function to be used
        def getDistanceByPoint(data, model):
            distance = []
            for i in range(0,len(data)):
                Xa = np.array(data.loc[i])
                Xb = model.cluster_centers_[model.labels_[i]-1]
                distance.append(np.linalg.norm(Xa-Xb))
            return pd.Series(distance, index=data.index)

        outliers_fraction = fraction
        distance = getDistanceByPoint(principalDf, kmeans)
        number_of_outliers = int(outliers_fraction*len(distance))
        threshold = distance.nlargest(number_of_outliers).min() 
        principalDf['anomaly1'] = (distance >= threshold).astype(int)

        st.write("Anomaly Count by Kmeans", principalDf['anomaly1'].value_counts())

        mv_data['anomaly1'] = pd.Series(principalDf['anomaly1'].values, index=mv_data.index)
        a = mv_data[mv_data['anomaly1'] == 1] #anomaly
        data3 = a 
        outliers_fraction = fraction
        model =  IsolationForest(contamination=outliers_fraction)
        model.fit(principalDf.values) 
        principalDf['anomaly2'] = pd.Series(model.predict(principalDf.values))

        # visualization
        mv_data['anomaly2'] = pd.Series(principalDf['anomaly2'].values, index=mv_data.index)
        a = mv_data.loc[mv_data['anomaly2'] == -1] #anomaly
        # anomaly count method 3 
        st.write("Anomaly count isolated forest: ", mv_data['anomaly2'].value_counts())
        data4 = a

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
        fig = plt.figure()
        plt.plot(mv_data[param], color='blue', label='Normal')
        plt.plot(time_df[param], linestyle='none', marker='X', color='red', markersize=12, label='Anomaly')
        plt.xlabel('Date and Time')
        plt.ylabel('Reading')
        plt.title('Anomalies')
        plt.legend(loc='best')
        plt.gcf().autofmt_xdate()
        st.pyplot(fig)
        st.dataframe(time_df)


    code = ''' 
	# data
	time_series_df=pd.read_csv('../Data/main/Maritius_AOI_20200701_0731_full.csv')
	time_series_df.sort_values(by=['timestamp'], inplace=True)
	time_sorted_df = time_series_df.sort_values(by=['timestamp'], inplace=True)
	time_series_df['timestamp'] = pd.to_datetime(time_series_df['timestamp'])


	# cleaning and indexing
	time_series_df.drop(["call_sign", "flag" ,"draught" , "ship_and_cargo_type",
       "length", "width","eta" , "destination",  "status", "maneuver",  "accuracy" ,
       "collection_type" ,'mmsi_label'], axis=1, inplace=True)
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
'''
    if classifier == "Code":
        st.code(code, language='python')
    st.balloons()
if __name__ == '__main__':
    main()






