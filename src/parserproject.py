import argparse
import ultils as ult
import os.path as op
import os
from joblib import dump, load
from Models.Randomforest import RunRandomForest, FitRandomForest, GetRandomForestModel
import numpy as np
import DataExtractor.FeatureCollector as fc
import DataExtractor.CandidateGenerator as cg
import DataEncoder.DataEncoder as de
from collections import defaultdict
import traceback 
from Evaluation import Evaluators as ev
import configparser
from GitScrapper import Driller as dr

# Create a ConfigParser object
config = configparser.ConfigParser()
 
# Read the configuration file
config.read('../config.ini')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--all', action='store_true', help="A flag to request everything. This flag has the highest priority")    
    parser.add_argument('-r', '--run', action='store_true', help="A flag to request running training and testing only")    

    parser.add_argument('-n', '--csv_train', action='store_true', help="A flag to request creating training dataset (in csv)")    
    parser.add_argument('-t', '--csv_test', action='store_true', help="A flag to request creating testing dataset (in csv)")    
    parser.add_argument('-p', '--scrape_train', action='store_true', help="A flag to request scrapping projects for train data ")    
    parser.add_argument('-c', '--scrape_test', action='store_true', help="A flag to request srapping projects for test data")    
    parser.add_argument('-i', '--train', action='store_true', help="A flag to request running training")    
    parser.add_argument('-o', '--test', action='store_true', help="A flag to request running testing")    

    args = parser.parse_args()

    is_csv_train = args.csv_train
    is_csv_test = args.csv_test
    is_scrape_train = args.scrape_train
    is_scrape_test = args.scrape_test
    is_train = args.train
    is_test = args.test

    if (args.run):
        is_train = True
        is_test = True

    if (args.all):
        is_csv_train = True
        is_csv_test = True
        is_scrape_train = True
        is_scrape_test = True
        is_train = True
        is_test = True

    
    train_dr = config.get("User", "train_dir")
    test_dir = config.get("User", "test_dir")

    train_csv_file_path = config.get("User", "training_data_pyart_csv_path")
    test_csv_file_path = config.get("User", "testing_data_pyart_csv_path")

    if (is_scrape_train):
        isContinue =  input("The training data is very large, make sure to allocate enough disk space. Please type 'Yes' or 'Y' to continue ") 
        if (isContinue.upper() == "YES" or isContinue.upper() == "Y"):
    
            url = config.get("User","url")
            dr.Git_Train_RepoScrapper(url)
        else:
            print("Canceling projects data scrapping")
    
    if (is_scrape_test):
        isContinue =  input("The testing data is very large, make sure to allocate enough disk space. Please type 'Yes' or 'Y' to continue ") 
        if (isContinue.upper() == "YES" or isContinue.upper() == "Y"):   
            url = config.get("User","url")
            dr.Git_Test_RepoScrapper(url)
        
        else:
            print("Canceling projects data scrapping")
    
    if (is_csv_train):
        ult.create_pyart_dataset(train_dr, train_csv_file_path)
    
    if (is_csv_test):
        ult.create_pyart_dataset(test_dir, test_csv_file_path)
    
    if (is_train):
        ult.train(train_csv_file_path)
    
    if (is_test):
        ult.test(test_csv_file_path)
        