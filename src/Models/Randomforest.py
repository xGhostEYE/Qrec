import configparser
import pandas as pd, numpy as np
from joblib import dump, load
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

# Create a ConfigParser object
config = configparser.ConfigParser()
 
# Read the configuration file
config.read('../config.ini')
model_path = config.get("User", "model_path")

def RunRandomForestWithGridSearchCV(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, random_state=42)
    
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
    

def FitRandomForestWithGridSearchCV(X, y):
    X_train = X
    y_train = y
    # X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, random_state=42)
    
    rf = RandomForestClassifier(random_state=42, n_jobs=-1)
    # find the best hyper parameters
    params = {
        'max_depth': [2,3,5,10,20],
        'min_samples_leaf': [5,10,20,50,100,200],
        'n_estimators': [10,25,30,50,100,200]
    }

    # Instantiate the grid search model
    grid_search = GridSearchCV(
                            estimator=rf,
                            param_grid=params,
                            cv = 4,
                            n_jobs=-1, verbose=1, scoring="accuracy")

    grid_search.fit(X_train, y_train)
    # apply the best hyper parameters
    classifier_rf = grid_search.best_estimator_
    dump(classifier_rf, model_path)

def FitRandomForest(X, y):
    X_train = X
    y_train = y
    # X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, random_state=42)
    
    rf = RandomForestClassifier(n_jobs=-1)
    rf.fit(X_train, y_train)
    dump(rf, model_path)

    
def TestRandomForest(X, y):    
    X_test = X
    y_test = y

    model = load(model_path)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)

def GetRandomForestModel():
    model = load(model_path)
    return model
    