import pandas as pd, numpy as np
from sklearn.model_selection import train_test_split
import torch
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

df = pd.read_csv('data.csv');

# get all the data except the label (y)
X = df.drop('',axis=1)
# get the label
y = df['heart disease']

X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7, random_state=42)
X_train.shape, X_test.shape

rf = RandomForestClassifier(random_state=42, n_jobs=-1)
# find the best hyper parameters
params = {
    'max_depth': [2,3,5,10,20],
    'min_samples_leaf': [5,10,20,50,100,200],
    'n_estimators': [10,25,30,50,100,200]
}

# Instantiate the grid search model
grid_search = GridSearchCV(estimator=rf,
                           param_grid=params,
                           cv = 4,
                           n_jobs=-1, verbose=1, scoring="accuracy")

grid_search.fit(X_train, y_train)
# apply the best hyper parameters
classifier_rf = grid_search.best_estimator_
# print the score 
classifier_rf.oob_score_

