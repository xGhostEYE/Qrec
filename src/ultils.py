from collections import defaultdict
import configparser
import csv
import json
import math
import os.path as op
import os

from joblib import load
import numpy as np
import pandas as pd
import DataExtractor.FeatureCollector as fc
import DataExtractor.AromaFeatureCollector as afc
import DataExtractor.CandidateGenerator as cg
import DataEncoder.DataEncoder as de
import Indexing.AromaIndexer as ai
import traceback
from timeit import default_timer as timer

from Models.Randomforest import FitRandomForest, GetRandomForestModel 
from Evaluation import Evaluators as ev
from matplotlib_venn import venn3 
from matplotlib import pyplot as plt 
from tqdm import tqdm

# from GetFiles import GetFilesInDirectory

# Create a ConfigParser object
config = configparser.ConfigParser()
 
# Read the configuration file
config.read('../config.ini')

def create_aroma_dataset_for_one_commit(commit, csv_path):
    #clear csv file
    file = open(csv_path, "w+")
    
    # writing headers (field names)
    fields = ["file_path", "position", "receiver", "method", "token_feature", "parent_feature", "sibling_feature", "variable_usage_feature"]
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    file.close()
                        
    try:
        json_file_name = config.get("User", "json_file_name")
        json_file_path = os.path.join(commit, json_file_name)
        
        #Iterate through each files in the project
        for root, directories, files in os.walk(commit, topdown=False):
            for name in files:
                file_path = (os.path.join(root, name))
                if file_path.endswith(".py") or file_path.endswith(".pyi"):
                    try: 
                        with open(file_path, encoding='utf-8') as file:

                            with open(json_file_path, encoding='utf-8') as json_file:
                                json_dict = json.load(json_file)

                                if file_path not in json_dict:
                                    print("The python file to be processed does not contain new changes. Continue to process next python file")
                                    continue
                            
                                changed_lines_dict = json_dict[file_path]
                                aroma_tree = afc.extract_aroma_tree(file)
                                method_calls_aroma_dict = afc.extract_aroma_features_for_method_calls(aroma_tree, changed_lines_dict)
                            write_method_calls_aroma_csv_data_set( csv_path, file_path, method_calls_aroma_dict)

                    except Exception as e:
                        print(f"Error processing file '{file_path}': {e}")
                        traceback.print_exc()
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc() 

def create_pyart_dataset_for_one_commit(commit, csv_path):
        
    #clear csv file
    file = open(csv_path, "w+")
    # writing headers (field names)
    fields = ["file_path", "object", "api", "line_number", "is_true_api", "x1", "x2", "x3", "x4"]
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    file.close()
    
    stdlibs_calls = cg.get_calls_from_standard_libs()
    
    #For each projects in directory
    print("[LOGGING] Processing Commit: " + commit)
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
        for root, directories, files in os.walk(commit, topdown=False):
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
                print("Processing file: " + file_path, "| Progress: " + str(list_all_file_path.index(file_path) + 1) + "/" + str(len(list_all_file_path)))
                with open(file_path, encoding='utf-8') as file:
                    json_file_name = config.get("User", "json_file_name")
                    json_file_path = os.path.join(root, json_file_name)
                    with open(json_file_path, encoding='utf-8') as json_file:
                        json_dict = json.load(json_file)

                        if file_path not in json_dict:
                            print("The python file to be processed does not contain new changes. Continue to process next python file")
                            continue
                        
                        changed_lines_dict = json_dict[file_path]
                        method_dict = fc.extract_data(file, changed_lines_dict)

                        #If no data flows are extracted, skip to process next file
                        if len(method_dict) == 0:
                            continue

                with open(file_path, encoding='utf-8') as file:
                    print("Generating candidates...")
                    default_calls = stdlibs_calls.copy()
                    default_calls.update(cg.get_calls_from_third_party_libs(file_path))
                    default_calls.update(cg.get_calls_from_scope(file_path))
                    candidate_dict = cg.CandidatesGenerator(file, file_path, method_dict, default_calls)
                
                #Format of data_dict:
                # #Key = [object, api, line number, 0 if it is not true api and 1 otherwise]
                # #Value = [x1,x2,x3,x4]
                print("Encoding data...")
                data_dict = de.DataEncoder(method_dict,candidate_dict, file_dict, list_all_file_path, file_path, frequency_files_dict, frequency_file_dict, occurrence_files_dict, occurrence_file_dict)
                write_pyart_csv_data(data_dict, csv_path, file_path)
            except Exception as e:
                print(f"Error processing during data encoding stage for '{file_path}': {e}")
                traceback.print_exc()
    except Exception as e:
        print(e)
        traceback.print_exc()

    print("\n")

def create_aroma_dataset(directory, csv_path):

        files = os.listdir(directory)
        directoryPath = []

        #clear csv file
        file = open(csv_path, "w+")
        
        # writing headers (field names)
        fields = ["file_path", "position", "receiver", "method", "token_feature", "parent_feature", "sibling_feature", "variable_usage_feature","variable_with_method_usage_feature"]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        file.close()
        
        for file in files:
            #directory contains projects (folders). We collect the path of those projects
            file_path = os.path.join(directory, file)
            directoryPath.append(file_path)


        #For each projects in directory
        with tqdm(directoryPath, total = len(directoryPath)) as t:
            for path in t:
                t.set_description("Processing Commit: %s. Current Progress:" %path)
                print("[LOGGING] Processing Commit: " + path + " | commit number/total commits : " + str(directoryPath.index(path) + 1)+ "/" + str(len(directoryPath)))
                elapsed = t.format_dict['elapsed']
                elapsed_str = t.format_interval(elapsed)            
                rate = t.format_dict["rate"]
                remaining = (t.total - t.n) / rate if rate and t.total else 0
                print("Elapsed: " + elapsed_str, "| Rate: " + str(rate), "| Remaining (seconds): " + str(remaining) + "\n")
                
                json_file_name = config.get("User", "json_file_name")
                json_file_path = os.path.join(path, json_file_name)
                          
                try:
                    #Iterate through each files in the project
                    for root, directories, files in os.walk(path, topdown=False):
                        for name in files:
                            file_path = (os.path.join(root, name))
                            if file_path.endswith(".py") or file_path.endswith(".pyi"):
                                try: 
                                    with open(file_path, encoding='utf-8') as file:

                                        with open(json_file_path, encoding='utf-8') as json_file:
                                            json_dict = json.load(json_file)

                                            if file_path not in json_dict:
                                                # print("The python file to be processed does not contain new changes. Continue to process next python file")
                                                continue
                                        
                                            changed_lines_dict = json_dict[file_path]
                                            aroma_tree = afc.extract_aroma_tree(file)
                                            method_calls_aroma_dict = afc.extract_aroma_features_for_method_calls(aroma_tree, changed_lines_dict)
                                        write_method_calls_aroma_csv_data_set( csv_path, file_path, method_calls_aroma_dict)

                                except Exception as e:
                                    print(f"Error processing file '{file_path}': {e}")
                                    traceback.print_exc()
                                    exit(1)   

                    
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    traceback.print_exc()
                    exit(1)   

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
            t.set_description("Processing Commit: %s. Current Commit:" %path)
            print("[LOGGING] Processing Commit: " + path + " | commit number/total commits : " + str(directoryPath.index(path) + 1)+ "/" + str(len(directoryPath)))
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
                                exit(1) 

                list_all_file_path = list(file_dict.keys())

                for file_path in list_all_file_path:     
                    try:
                        print("Processing file: " + file_path, "| Progress: " + str(list_all_file_path.index(file_path) + 1) + "/" + str(len(list_all_file_path)))
                        with open(file_path, encoding='utf-8') as file:
                            
                            json_file_name = config.get("User", "json_file_name")
                            json_file_path = os.path.join(root, json_file_name)
                            with open(json_file_path, encoding='utf-8') as json_file:
                                json_dict = json.load(json_file)

                                if file_path not in json_dict:
                                    print("The python file to be processed does not contain new changes. Continue to process next python file")
                                    continue
                                
                                changed_lines_dict = json_dict[file_path]
                                method_dict = fc.extract_data(file, changed_lines_dict)

                                #If no data flows are extracted, skip to process next file
                                if len(method_dict) == 0:
                                    continue

                        with open(file_path, encoding='utf-8') as file:
                            print("Generating candidates...")
                            default_calls = stdlibs_calls.copy()
                            default_calls.update(cg.get_calls_from_third_party_libs(file_path))
                            default_calls.update(cg.get_calls_from_scope(file_path))
                            candidate_dict = cg.CandidatesGenerator(file, file_path, method_dict, default_calls)
                        
                        #Format of data_dict:
                        # #Key = [object, api, line number, 0 if it is not true api and 1 otherwise]
                        # #Value = [x1,x2,x3,x4]
                        print("Encoding data...")
                        data_dict = de.DataEncoder(method_dict,candidate_dict, file_dict, list_all_file_path, file_path, frequency_files_dict, frequency_file_dict, occurrence_files_dict, occurrence_file_dict)
                        write_pyart_csv_data(data_dict, csv_path, file_path)
                    except Exception as e:
                        print(f"Error processing during data encoding stage for '{file_path}': {e}")
                        traceback.print_exc()
                        exit(1)
            except Exception as e:
                print(e)
                traceback.print_exc()
                exit(1)

            print("\n")
            t.update(1)
            t.refresh()
    
        elapsed = t.format_dict['elapsed']
        elapsed_str = t.format_interval(elapsed)  
        print("Finished creating csv file with runtime: " + elapsed_str)


def write_method_calls_aroma_csv_data_set(csv_file_path, file_path ,method_dict_aroma_dict):
    with open(csv_file_path, 'a') as csvfile:
        # creating a csv dict writer object
        fields = ["file_path", "position", "receiver","method", "token_feature", "parent_feature", "sibling_feature", "variable_usage_feature", "variable_with_method_usage_feature"]
        writer = csv.DictWriter(csvfile, fieldnames=fields)

        for key, value in method_dict_aroma_dict.items():
            receiver = key[0]
            position = str(receiver.position)
            receiver_label = receiver.label if receiver.label != "#VAR" else receiver.true_label
            
            method = key[1]
            method_label = method.label
            writer.writerow({"file_path": file_path, "position": position, "receiver": receiver_label, "method": method_label, "token_feature": value[0], "parent_feature": value[1], "sibling_feature": value[2], "variable_usage_feature": value[3], "variable_with_method_usage_feature": value[4]})



def write_pyart_csv_data(data_dict, csv_file_path, file_path):
    fields = ["file_path", "object", "api", "line_number", "is_true_api", "x1", "x2", "x3", "x4"]
    with open(csv_file_path, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        for key, value in data_dict.items():
            writer.writerow({"file_path": file_path, "object": key[0], "api": key[1], "line_number": key[2], "is_true_api": key[3], "x1": value[0], "x2": value[1], "x3": value[2], "x4": value[3]})

    
def SortTuples(tuples):
    # sorting function
    return sorted(tuples, key=lambda x: x[2], reverse=True)

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

def train_aroma(train_csv_file_path):
    ai.index_data(train_csv_file_path, True)

def train_pyart(train_csv_file_path):
    labeled_data_tuple = get_labeled_data(train_csv_file_path)
    X =  labeled_data_tuple[0].astype(float)
    y = labeled_data_tuple[1].astype(float).values.ravel()
    FitRandomForest(X, y)  

def test_aroma(test_csv_file_path, isEval=True):
    top_k = config.get("User", "top_k")

    return ai.search_data(test_csv_file_path, top_k, isEval=isEval)
    
def test_pyart(test_csv_file_path, isEval=True):
    start = timer()
    grouped_dict = defaultdict(list)
    labeled_data_tuple = get_detailed_labeling_data(test_csv_file_path)

    list_features = labeled_data_tuple[0].astype(float)
    labels = labeled_data_tuple[1]

    model = GetRandomForestModel()
    #Each probability is an array: [prob_for_0, prob_for_1]
    probabilities = model.predict_proba(list_features)
    
    # Group objects by their key values
    for index in tqdm(range(len(labels))):
        file_path, object_name, api_name, line_number, is_true_api = list(labels.iloc[index].values)
        grouped_dict[(file_path, object_name, line_number)].append((int(is_true_api), api_name, probabilities[index][1]))

    if grouped_dict == None:
        exit(1)

    print("Done prediction, sorting data...")
    sorted_data = {key: SortTuples(value) for key, value in grouped_dict.items()}
    print("Done sorting data")

    if (isEval):
        # get the index +1 of the sorted dictionary value list that has '1' as the first tuple value
        api_details_dict = {}
        for key, value in sorted_data.items():
            candidates = []
            correct_api = None
            for tuple in value:
                candidates.append(tuple[1])
                if tuple[0] == 1:
                    correct_api = tuple[1]   
            if (correct_api):
                string_key = ""
                for item in key:
                    string_key = string_key + str(item) + ":"
                string_key = string_key + str(correct_api)
                api_details_dict[string_key] = candidates

        first_recommendation_set_true_api = list(api_details_dict.keys())[0]
        first_recommendation_set = api_details_dict[first_recommendation_set_true_api]
        print("\ncorrect apis: ", list(api_details_dict.keys())[0])
        print("\ntop 10 recommended apis for: ",next(iter(sorted_data)),"\n",first_recommendation_set[:10])
        print("calculating mrr")
        print("MRR: ", ev.calculate_mrr(api_details_dict))
        k = [1,2,3,4,5,10]
        for i in k:
            print("Top K Accuracy ",i,": ", ev.calculate_top_k_accuracy(api_details_dict, i))
        # print("Precision Recall: ",ev.calculate_precision_recall(recommendation, correct_apis))
        end = timer()
        print(end - start, "(seconds)")
    else:
        api_details_dict = {}
        for key, value in sorted_data.items():
            candidates = []
            correct_api = None
            for tuple in value:
                candidates.append(tuple[1])
                if tuple[0] == 1:
                    correct_api = tuple[1]   
            if (correct_api):
                string_key = ""
                for item in key:
                    string_key = string_key + str(item) + ":"
                string_key = string_key + str(correct_api)
                api_details_dict[string_key] = candidates

        with open("../data/pyart_test_result.json", 'w', encoding='utf-8') as f:
            json.dump(api_details_dict, f, ensure_ascii=False)
        return api_details_dict
#TODO
def pyart_vs_aroma(test_pyart_csv_file_path, test_aroma_csv_file_path):
    #Pyart
    pyart_test_result_path = "../data/pyart_test_result.json"
    if (os.path.exists(pyart_test_result_path)):
        with open(pyart_test_result_path, encoding='utf-8') as json_file:
            pyart_dict = json.load(json_file)
    else:
        pyart_dict = test_pyart(test_pyart_csv_file_path, isEval=False)

    #Aroma
    aroma_test_result_path = "../data/aroma_test_result.json" 
    if (os.path.exists(aroma_test_result_path)):
        with open(aroma_test_result_path, encoding='utf-8') as json_file:
            aroma_dict = json.load(json_file)
    else:
        aroma_dict = test_aroma(test_aroma_csv_file_path, isEval=False)
    
    top_k_list = [1,10]
    top_k_dict = {}
    print("Total Aroma:", len(aroma_dict))
    print("Total Pyart:", len(pyart_dict))
    for k in top_k_list:    
        total = 0
        aroma_correct_only = 0
        pyart_correct_only = 0
        aroma_and_pyart_correct = 0
        aroma_and_pyart_incorrect = 0

    #     for key,value in pyart_dict.items():
    #         info = key.split(":")
    #         file_path = info[0]
    #         receiver = info[1]
    #         position = info[2]
    #         correct_method = info[3]

    #         if key in aroma_dict:
    #             pyart_candidates = value
    #             pyart_top_k_candidates = pyart_candidates[:k]

    #             aroma_candidates = aroma_dict[key]
    #             aroma_top_k_candidates = aroma_candidates[:k]

    #             if (correct_method in pyart_top_k_candidates and correct_method in aroma_top_k_candidates):
    #                 aroma_and_pyart_correct += 1

    #             elif(correct_method in pyart_top_k_candidates):
    #                 pyart_correct_only += 1
    #             elif(correct_method in aroma_top_k_candidates):
    #                 aroma_correct_only += 1
    #             else:
    #                 aroma_and_pyart_incorrect += 1
    #             total += 1
    #         else :
    #             print(file_path,receiver,position)
    #             continue
        for key,value in aroma_dict.items():
            info = key.split(":")
            file_path = info[0]
            receiver = info[1]
            position = info[2]
            correct_method = info[3]

            if key in pyart_dict:
                aroma_candidates = value
                aroma_top_k_candidates = aroma_candidates[:k]

                pyart_candidates = pyart_dict[key]
                pyart_top_k_candidates = pyart_candidates[:k]

                if (correct_method in pyart_top_k_candidates and correct_method in aroma_top_k_candidates):
                    aroma_and_pyart_correct += 1

                elif(correct_method in pyart_top_k_candidates):
                    pyart_correct_only += 1
                elif(correct_method in aroma_top_k_candidates):
                    aroma_correct_only += 1
                else:
                    aroma_and_pyart_incorrect += 1
                total += 1
            else :
                # print(file_path,receiver,position)
                continue

        top_k_dict[str(k)] = {"total": total, "aroma_correct_only": aroma_correct_only, "pyart_correct_only": pyart_correct_only, "aroma_and_pyart_correct": aroma_and_pyart_correct, "aroma_and_pyart_incorrect": aroma_and_pyart_incorrect}
    
    for k,value in top_k_dict.items():
        Aroma = set([value["aroma_correct_only"], value["aroma_and_pyart_correct"]])
        Pyart = set([value["pyart_correct_only"], value["aroma_and_pyart_correct"]])
        Total = set([value["total"]])
        v = venn3([Aroma,Pyart,Total], ('Aroma', 'Pyart', 'Total'))

        v.get_label_by_id('100').set_text('\n'.join(map(str,Aroma-Pyart)))
        v.get_label_by_id('110').set_text('\n'.join(map(str,Aroma&Pyart)))
        v.get_label_by_id('010').set_text('\n'.join(map(str,Pyart-Aroma)))
        v.get_label_by_id('001').set_text('\n'.join(map(str,Total)))
        v.get_patch_by_id('001').set_color('white')
        plt.axis('on')
        plt.title("Results for top k:" + str(k))
        plt.show()

    with open("../data/comparison_" + str(top_k_list) + ".json", 'w', encoding='utf-8') as f:
            json.dump(top_k_dict, f, ensure_ascii=False)



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
