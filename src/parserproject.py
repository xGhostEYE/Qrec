import argparse
import ultils as ult
import os.path as op
import os
from joblib import dump, load
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
    parser.add_argument('-a', '--all', action='store_true', help="A flag to request everything (except for --commit and --outputfile). This flag has the highest priority")    
    parser.add_argument('-r', '--run', action='store_true', help="A flag to request running training and testing only for the default train and test dataset")    
    
    parser.add_argument('-p', '--commit', help="A flag to specify the commit to be extracted. Run with --outputfile flag to specify the output file")  
    parser.add_argument('-f', '--outputfile', help="A flag to specify the csv file name for the extracted dataset. Run with --commit flag to specify the commit to be extracted")  

    parser.add_argument('-n', '--csv_train', action='store_true', help="A flag to request creating training dataset (in csv)")    
    parser.add_argument('-t', '--csv_test', action='store_true', help="A flag to request creating testing dataset (in csv)")    
    parser.add_argument('-d', '--scrape_train', action='store_true', help="A flag to request scrapping commits for train data ")    
    parser.add_argument('-c', '--scrape_test', action='store_true', help="A flag to request srapping commits for test data")    
    parser.add_argument('-i', '--train', action='store_true', help="A flag to request running training")    
    parser.add_argument('-o', '--test', action='store_true', help="A flag to request running testing")    
    parser.add_argument('-j', '--compare', action='store_true', help="A flag to compare the accuracy between pyart and aroma")    

    args = parser.parse_args()

    is_csv_train = args.csv_train
    is_csv_test = args.csv_test
    is_scrape_train = args.scrape_train
    is_scrape_test = args.scrape_test
    is_train = args.train
    is_test = args.test
    is_compare = args.compare
    commit = args.commit
    output_file = args.outputfile
    
    if (args.run):
        is_csv_train = False
        is_csv_test = False
        is_scrape_train = False
        is_scrape_test = False
        is_train = True
        is_test = True
        commit = None
        output_file = None

    if (args.all):
        is_csv_train = True
        is_csv_test = True
        is_scrape_train = True
        is_scrape_test = True
        is_train = True
        is_test = True
        commit = None
        output_file = None

    if (config.get("User", "type").upper() == "PYART"):
        create_data_set = ult.create_pyart_dataset
        train_csv_file_path = config.get("User", "training_data_pyart_csv_path")
        test_csv_file_path = config.get("User", "testing_data_pyart_csv_path")
        train = ult.train_pyart
        test = ult.test_pyart
        create_data_set_for_one_commit = ult.create_pyart_dataset_for_one_commit
    elif (config.get("User", "type").upper() == "AROMA"):
        create_data_set = ult.create_aroma_dataset
        train_csv_file_path = config.get("User", "training_data_aroma_csv_path")
        test_csv_file_path = config.get("User", "testing_data_aroma_csv_path")
        train = ult.train_aroma
        test = ult.test_aroma
        create_data_set_for_one_commit = ult.create_aroma_dataset_for_one_commit

    else:
        print("Error: type of run is not defined in the config file")
        exit(1)
        
    if (commit is not None and output_file is not None):
            create_data_set_for_one_commit(commit, "../data/" + output_file)
            exit(0)

    train_dr = config.get("User", "train_dir")
    test_dir = config.get("User", "test_dir")
        

    if (is_scrape_train):
        isContinue =  input("The training data is very large, make sure to allocate enough disk space. Please type 'Yes' or 'Y' to continue ") 
        if (isContinue.upper() == "YES" or isContinue.upper() == "Y"):
            print("Scraping train data...")

            url = config.get("User","url")
            dr.Git_Train_RepoScrapper(url)
        else:
            print("Canceling commits data scrapping")

    if (is_scrape_test):
        isContinue =  input("The testing data is very large, make sure to allocate enough disk space. Please type 'Yes' or 'Y' to continue ") 
        if (isContinue.upper() == "YES" or isContinue.upper() == "Y"):
            print("Scraping test data...")
   
            url = config.get("User","url")
            dr.Git_Test_RepoScrapper(url)
        
        else:
            print("Canceling commits data scrapping")

    if (is_csv_train):
        print("Creating train dataset...")
        create_data_set(train_dr, train_csv_file_path)
    
    if (is_csv_test):
        print("Creating test dataset...")
        create_data_set(test_dir, test_csv_file_path)

    if (is_train):
        print("Training...")
        train(train_csv_file_path)
    

    if (is_test):
        print("Testing...")
        test(test_csv_file_path)

    if (is_compare):
        print("Comparing...")
        test_pyart_csv_file_path = config.get("User", "testing_data_pyart_csv_path")
        test_aroma_csv_file_path = config.get("User", "testing_data_aroma_csv_path")
        ult.pyart_vs_aroma(test_pyart_csv_file_path,test_aroma_csv_file_path)

        