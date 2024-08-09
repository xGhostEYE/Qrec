import csv
import os
import traceback 
import DataExtractor.AromaFeatureCollector as afc
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split

#Please add the training projects inside test/. 
test_directory = "../test/"
train_directory = "../train"

def extract_and_append_dataset():
    try:
        # Validate directory existence
        if not os.path.isdir(train_directory):
            print(f"Error: Directory '{train_directory}' does not exist.")
            return None
        elif not os.path.isdir(test_directory):
            print(f"Error: Directory '{test_directory}' does not exist.")
            return None
        
        #clear csv file
        f = open("../data/aroma_dataset.csv", "w+")
        f.close()
        # Iterate through all Python files in the train directory to extract dataset
        for root, directories, files in os.walk(train_directory, topdown=False):
            for filename in files:
                if filename.endswith(".py") or filename.endswith(".pyi"):
                    file_path = os.path.join(root, filename)

                    try: 
                        with open(file_path, encoding='utf-8') as file:
                                aroma_tree = afc.extract_aroma_tree(file)
                                aroma_dict = afc.extract_aroma_features_for_method_calls(aroma_tree)
                                afc.write_csv_data_set(file_path, aroma_dict)

                    except Exception as e:
                        print(f"Error processing file '{file_path}': {e}")
                        traceback.print_exc()

        # Iterate through all Python files in the test directory to extract dataset
        for root, directories, files in os.walk(test_directory, topdown=False):
            for filename in files:
                if filename.endswith(".py") or filename.endswith(".pyi"):
                    file_path = os.path.join(root, filename)

                    try: 
                        with open(file_path, encoding='utf-8') as file:
                                aroma_tree = afc.extract_aroma_tree(file)
                                aroma_dict = afc.extract_aroma_features_for_method_calls(aroma_tree)
                                afc.write_csv_data_set(file_path ,aroma_dict)

                    except Exception as e:
                        print(f"Error processing file '{file_path}': {e}")
                        traceback.print_exc()

        # split the data into training and testing
        df = pd.read_csv("../data/aroma_dataset.csv")
        sampled_training_df, sampled_test_df = train_test_split(df, test_size = 0.2, random_state = 200)
        sampled_training_df.to_csv("../data/training_data_aroma.csv", index = False, header = True)
        sampled_test_df.to_csv("../data/testing_data_aroma.csv", index = False, header = True)
        
                
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--dataset', action='store_true', help="A flag to request creating dataset (in csv)")    
    
    args = parser.parse_args()
    if (args.dataset):
        extract_and_append_dataset()