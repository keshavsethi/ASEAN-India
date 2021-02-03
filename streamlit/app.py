import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import plot_confusion_matrix,plot_roc_curve,plot_precision_recall_curve
from sklearn.metrics import precision_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier


def main():
    #todo
    st.title("Binary Classification Web App")
    st.sidebar.title("Diabates or Not")
    st.markdown("Are you a diabates patient?")
    st.sidebar.markdown("Are you a diabates patient?")

    @st.cache(persist=True)
    def load_data():
        data = pd.read_csv("diabetes.csv")
        return data

    @st.cache(persist = True)
    def split(df):
        X = np.array(df.iloc[:,0:8])
        Y = np.array(df.iloc[:,8])
        xtrain, xtest, ytrain, ytest = train_test_split(X,Y,test_size=0.2, random_state=0)
        return xtrain, xtest, ytrain, ytest

    def plot_metrics(metrics_list):
        if "Confusion_matrix" in metrics_list:
            st.subheader("Confusion Matrix")
            plot_confusion_matrix(model,xtest,ytest,display_labels=class_name)
            st.pyplot()
        if "ROC" in metrics_list:
            st.subheader("ROC")
            plot_roc_curve(model,xtest,ytest)
            st.pyplot()
        if "Precision Recall Curve" in metrics_list:
            st.subheader("Precision Recall Curve")
            plot_precision_recall_curve(model,xtest,ytest)
            st.pyplot()
        
    
    data = load_data()
    xtrain, xtest, ytrain, ytest = split(data)
    class_name = ["Diabetic","NonDiabetic"]
    ch = st.sidebar.checkbox("Show Dataset")
    if(ch):
        st.subheader("Diabetes Data Set from Kaggles")
        st.write(data)
    classifier = st.sidebar.selectbox("Classifier",("Logistic Regression","Decision Tree","Neural Network"))

    if classifier == "Logistic Regression":
        st.sidebar.subheader("Parameters: ")
        iterations = st.sidebar.number_input("Iterations",100,1000,step=5,key='iterations')
        C = st.sidebar.number_input("Regularization Factor",0.01,1.0,step=0.01,key='C')
        solver = st.sidebar.radio("Solver",("newton-cg", "lbfgs", "liblinear", "sag", "saga"),key='solver')
        metrics = st.sidebar.multiselect("What metrics to plot?",("Confusion_matrix","ROC","Precision Recall Curve"))
        if st.sidebar.button("Classify"):
            model = LogisticRegression(max_iter=iterations,solver=solver,C=C)
            model.fit(xtrain,ytrain)
            ypred = model.predict(xtest)
            st.write("Model Accuracy: ",model.score(xtest,ytest))
            st.write("Model Precision: ", precision_score(ytest,ypred,labels=class_name))
            plot_metrics(metrics)

    if classifier == "Decision Tree":
        st.sidebar.subheader("Parameters: ")
        max_leaf_nodes = st.sidebar.number_input("Max Leaf Nodes",50,200,step=1,key='max_leaf_nodes')
        criterion = st.sidebar.radio("Criterion",("gini", "entropy"),key='criterion')
        max_features = st.sidebar.radio("Features",("auto", "sqrt", "log2"),key='max_features')
        metrics = st.sidebar.multiselect("What metrics to plot?",("Confusion_matrix","ROC","Precision Recall Curve"))
        if st.sidebar.button("Classify"):
            model = DecisionTreeClassifier(max_leaf_nodes=max_leaf_nodes,criterion=criterion,max_features=max_features)
            model.fit(xtrain,ytrain)
            ypred = model.predict(xtest)
            st.write("Model Accuracy: ",model.score(xtest,ytest))
            st.write("Model Precision: ", precision_score(ytest,ypred,labels=class_name))
            plot_metrics(metrics)

    if classifier == "Neural Network":
        st.sidebar.subheader("Parameters: ")
        activation = st.sidebar.radio("Activation",("identity", "logistic", "tanh", "relu"),key='activation')
        solver = st.sidebar.radio("Solver",("lbfgs", "sgd", "adam"),key='solver')
        alpha = st.sidebar.number_input("Regularization Factor",0.0001,0.1,step=0.0001,key='alpha')
        learning_rate = st.sidebar.radio("Learning Rate",("constant", "invscaling", "adaptive"),key='learning_rate')
        max_iter = st.sidebar.number_input("Iterations",200,1000,step=5,key='max_iter')
        metrics = st.sidebar.multiselect("What metrics to plot?",("Confusion_matrix","ROC","Precision Recall Curve"))
        if st.sidebar.button("Classify"):
            model = MLPClassifier(activation=activation,solver=solver, alpha=alpha,learning_rate=learning_rate,max_iter=max_iter,hidden_layer_sizes=(8,8,8))
            model.fit(xtrain,ytrain)
            ypred = model.predict(xtest)
            st.write("Model Accuracy: ",model.score(xtest,ytest))
            st.write("Model Precision: ", precision_score(ytest,ypred,labels=class_name))
            plot_metrics(metrics)
if __name__ == '__main__':
    main()