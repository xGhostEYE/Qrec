import pandas as pd, numpy as np
from joblib import dump, load
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
import torch
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV


def RunRandomForest(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7, random_state=42)
    
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

    dump(classifier_rf, './random_forest_model.joblib')
    y_pred = classifier_rf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)