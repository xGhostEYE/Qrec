from collections import defaultdict
import csv
import os.path as op
import os

from joblib import load
import numpy as np
import pandas as pd
import DataExtractor.FeatureCollector as fc
import DataExtractor.CandidateGenerator as cg
import DataEncoder.DataEncoder as de
import traceback

from Models.Randomforest import FitRandomForest, GetRandomForestModel 
from Evaluation import Evaluators as ev
from tqdm import tqdm

# from GetFiles import GetFilesInDirectory

def create_pyart_dataset(directory, csv_path):
    files = os.listdir(directory)
    directoryPath = []
        
    #clear csv file
    file = open(csv_path, "w+")
    # writing headers (field names)
    fields = ["file_path", "object", "api", "line_number", "is_true_api", "x1", "x2", "x3", "x4"]
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    file.close()
    
    stdlibs_calls = cg.get_calls_from_standard_libs()

    for file in files:
        #directory contains projects (folders). We collect the path of those projects
        file_path = os.path.join(directory, file)
        directoryPath.append(file_path)
    
    #For each projects in directory
    with tqdm(directoryPath, total = len(directoryPath)) as t:
        for path in t:
            t.set_description("Executing Project: %s. Current Progress:" %path)
            print("[LOGGING] Executing Project: " + path + " | project number/total projects : " + str(directoryPath.index(path) + 1)+ "/" + str(len(directoryPath)))
            elapsed = t.format_dict['elapsed']
            elapsed_str = t.format_interval(elapsed)            
            rate = t.format_dict["rate"]
            remaining = (t.total - t.n) / rate if rate and t.total else 0
            print("Elapsed: " + elapsed_str, "| Rate: " + str(rate), "| Remaining (seconds): " + str(remaining) + "\n")

            file_dict = {}

            #Stores frequency of tokens in EACH file    
            frequency_file_dict = {}
            #Stores frequency of tokens in ALL files    
            frequency_files_dict = {}

            #Stores occurence of tokens in EACH file    
            occurrence_file_dict = {}
            #Stores occurence of tokens in ALL files    
            occurrence_files_dict = {}

            try:
                # os.walk NEEDS a subdirectory in the directory that it's walking for it to work.
                # meaning that it needs 2 layers of folders to work
                for root, directories, files in os.walk(path, topdown=False):
                    for name in files:
                        file_path = (os.path.join(root, name))
                        
                        if file_path.endswith(".py") or file_path.endswith(".pyi"):
                            try: 
                                #Key: file_name
                                #Value: bag of tokens (a dictionary)
                                        #Key: line number
                                        #Value: list of tokens from left to right 
                                with open(file_path, encoding='utf-8') as file:
                                    frequency_dict = {}
                                    occurrence_dict = {}
                                    
                                    file_dict[file_path] = fc.extract_bag_of_tokens(file, frequency_dict, occurrence_dict)
                                    frequency_file_dict[file_path] = frequency_dict
                                    occurrence_file_dict[file_path] = occurrence_dict
                                
                            
                            except Exception as e:
                                print(f"Error processing file dictionary for '{file_path}': {e}")
                                traceback.print_exc()   

                list_all_file_path = list(file_dict.keys())

                for file_path in list_all_file_path:     
                    try:
                        with open(file_path, encoding='utf-8') as file:
                            method_dict = fc.extract_data(file)

                        with open(file_path, encoding='utf-8') as file:
                            default_calls = stdlibs_calls.copy()
                            default_calls.update(cg.get_calls_from_third_party_libs(file_path))
                            default_calls.update(cg.get_calls_from_scope(file_path))
                            candidate_dict = cg.CandidatesGenerator(file, file_path, method_dict, default_calls)
                        
                        #Format of data_dict:
                        # #Key = [object, api, line number, 0 if it is not true api and 1 otherwise]
                        # #Value = [x1,x2,x3,x4]
                        data_dict = de.DataEncoder(method_dict,candidate_dict, file_dict, list_all_file_path, file_path, frequency_files_dict, frequency_file_dict, occurrence_files_dict, occurrence_file_dict)
                        write_pyart_csv_data(data_dict, csv_path, file_path)
                    except Exception as e:
                        print(f"Error processing during data encoding stage for '{file_path}': {e}")
                        traceback.print_exc()
            except Exception as e:
                print(e)
                traceback.print_exc()

            print("\n")
            t.update(1)
            t.refresh()
    
        elapsed = t.format_dict['elapsed']
        elapsed_str = t.format_interval(elapsed)  
        print("Finished creating csv file with runtime: " + elapsed_str)


def write_pyart_csv_data(data_dict, csv_file_path, file_path):
    fields = ["file_path", "object", "api", "line_number", "is_true_api", "x1", "x2", "x3", "x4"]
    with open(csv_file_path, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        for key, value in data_dict.items():
            writer.writerow({"file_path": file_path, "object": key[0], "api": key[1], "line_number": key[2], "is_true_api": key[3], "x1": value[0], "x2": value[1], "x3": value[2], "x4": value[3]})

    
def SortTuples(tuples):
    # sorting function
    return sorted(tuples, key=lambda x: x[2][0, 1], reverse=True)

def get_labeled_data(csv_path):
    data = pd.read_csv(csv_path, header=None,  dtype=str)
    labels = data.loc[1:, 4:4]
    features = data.loc[1:, 5:]

    # for key,value in data_dict.items():
    #     labels.append(key[3])
    return (features, labels)

def get_detailed_labeling_data(csv_path):
    data = pd.read_csv(csv_path, header=None, dtype=str)

    labels = data.loc[1:, :4]
    features = data.loc[1:, 5:]

    # for key,value in data_dict.items():
    #     labels.append(key[3])
    return (features, labels)

def train(train_csv_file_path):
    labeled_data_tuple = get_labeled_data(train_csv_file_path)
    X =  labeled_data_tuple[0].astype(float)
    y = labeled_data_tuple[1].astype(float).values.ravel()
    FitRandomForest(X, y)  

def test(test_csv_file_path):
    grouped_dict = defaultdict(list)
    labeled_data_tuple = get_detailed_labeling_data(test_csv_file_path)

    list_features = labeled_data_tuple[0].astype(float)
    labels = labeled_data_tuple[1]

    model = GetRandomForestModel()
    # Group objects by their key values
    for index in tqdm(range(len(labels))):
        file_path, object_name, api_name, line_number, is_true_api = list(labels.iloc[index].values)
        reshaped_value = list_features.iloc[index].values.reshape(1, -1)
        grouped_dict[(file_path, object_name, line_number)].append((int(is_true_api), api_name, model.predict_proba(reshaped_value)))

    if grouped_dict == None:
        exit(1)

    print("Done prediction, sorting data...")
    sorted_data = {key: SortTuples(value) for key, value in grouped_dict.items()}
    print("Done sorting data")

    # get the index +1 of the sorted dictionary value list that has '1' as the first tuple value
    api_dict = {}

    for key, value in sorted_data.items():
        candidates = []
        correct_api = None
        for tuple in value:
            candidates.append(tuple[1])
            if tuple[0] == 1:
                correct_api = tuple[1]
                
        if (correct_api):
            api_dict[correct_api] = candidates

    first_recommendation_set_true_api = list(api_dict.keys())[0]
    first_recommendation_set = api_dict[first_recommendation_set_true_api]
    print("\ncorrect apis: ", list(api_dict.keys())[0])
    print("\ntop 10 recommended apis for: ",next(iter(sorted_data)),"\n",first_recommendation_set[:10])
    print("calculating mrr")
    k = [1,2,3,4,5,10]
    print("MRR: ", ev.calculate_mrr(api_dict))
    for i in k:
        print("Top K Accuracy ",i,": ", ev.calculate_top_k_accuracy(api_dict, i))
    # print("Precision Recall: ",ev.calculate_precision_recall(recommendation, correct_apis))

#Not in use any more. For reference.
def Run_file_prediction():
    # Initialize a defaultdict to store grouped objects
    grouped_dict = defaultdict(list)
    test_data_dict = {}
    file_dict = {}
    file_path = "../test/Test/Streamer.py"
    test_directory = "../test"
    model = load("./random_forest_model.joblib")

    print("test file exists: ",op.isfile(file_path), "\n")
    if (not op.isfile(file_path)):
        return None
    try:
        #Get file_dict
        files = os.listdir(test_directory)
        directoryPath = []
        for file in files:
            file_path = os.path.join(test_directory, file)
            directoryPath.append(file_path)
        
        for path in directoryPath:
            try:
                for root, directories, files in os.walk(path, topdown=False):
                    for name in files:
                        file_path = (os.path.join(root, name))
      
                        if file_path.endswith(".py") or file_path.endswith(".pyi"):
                            with open(file_path, encoding='utf-8') as file:
                                file_dict[file_path] = fc.extract_bag_of_tokens(file)
            except Exception as e:
                print("Encountered exception when getting a file dict: ", e)

        with open(file_path, encoding='utf-8') as file:
                    method_dict = fc.extract_data(file)

        with open(file_path, encoding='utf-8') as file:
            candidate_dict = cg.CandidatesGenerator(file, file_path, method_dict)
    
        #Format of data_dict:
        #Key = [object, api, line number, 0 if it is not true api and 1 otherwise]
        #Value = [x1,x2,x3,x4]
        test_data_dict.update(de.DataEncoder(method_dict,candidate_dict, file_dict, file_path))

        # Group objects by their key values
        for key, value in test_data_dict.items():
            object_name, api_name, line_number, is_true_api = key
            reshaped_value = np.array(value).reshape(1, -1)
            grouped_dict[(object_name, line_number)].append((is_true_api, api_name, model.predict_proba(reshaped_value)))
        return grouped_dict

    except Exception as e:
        traceback.print_exc()        
