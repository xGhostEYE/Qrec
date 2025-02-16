import pandas as pd
import joblib,os,sys
import time
from sklearn.ensemble import RandomForestClassifier
import configparser

config = configparser.ConfigParser()
config.read('../config.ini')
model_path = config.get("User", "model_path")

def FitRandomForest(data_file_path, label_file_path):
    start=time.time()
    data=pd.read_csv(data_file_path)
    label=pd.read_csv(label_file_path)
    lines=len(data)
    trainnum=lines
    train_data=data[:trainnum]
    train_label=label[:trainnum]
    labels=train_label.values.ravel()
    clf=RandomForestClassifier()
    clf.fit(train_data,labels)
    result=clf.score(train_data,labels)
    joblib.dump(clf,model_path)
    print(result)
    #sys.exit()
    end=time.time()
    print(end-start, "seconds")

