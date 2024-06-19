import ultils as ult
import os.path as op
import os
from joblib import dump, load
from Models.Randomforest import RunRandomForest
import numpy as np
import DataExtractor.FeatureCollector as fc
import DataExtractor.CandidateGenerator as cg
import DataEncoder.DataEncoder as de
from collections import defaultdict
import traceback 
from Evaluation import Evaluators as ev
from GitScrapper import Driller as dr
import sys

#Please add the training projects inside training/. 
train_directory = r"../training/"

#Please add the training projects inside test/. 
test_directory = r"../test"
model = None
predictions = []
probabilities_result_correct = []


#TODO - Make this run with all the projects
def Run_Project_Prediction():
    # Initialize a defaultdict to store grouped objects
    grouped_dict = defaultdict(list)
    test_data_dict = {}
    file_dict = {}

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
                
                for root, directories, files in os.walk(path, topdown=False):
                    for name in files:
                        file_path = (os.path.join(root, name))
      
                        if file_path.endswith(".py") or file_path.endswith(".pyi"):
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

            except Exception as e:
                print("Encountered exception when getting a file dict: ", e)

    
    except Exception as e:
        traceback.print_exc()

def Run_file_Prediction():
    # Initialize a defaultdict to store grouped objects
    grouped_dict = defaultdict(list)
    test_data_dict = {}
    file_dict = {}
    file_path = "../test/Test/Streamer.py"

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
        
def SortTuples(tuples):
    # sorting function
    return sorted(tuples, key=lambda x: x[2][0, 1], reverse=True)

def GetTrainingData():
    data_dict = {}
    data_dict.update(ult.analyze_directory(train_directory))
    labels = []
    for key,value in data_dict.items():
        labels.append(key[3])
    return (list(data_dict.values()), labels)
  
# check if we already have a model
# if we don't then train a new one
# if we do then train the already generated model

print("checking if model exists")
if op.isfile("./random_forest_model.joblib"):
    print("model exists, checking if retrain is requested")
    model = load('./random_forest_model.joblib')
    if (not len(sys.argv) == 1):
        if (sys.argv[1] == "retrain"):
            print("retrain model requested, gathering training data")
            data = GetTrainingData()
            print("aquired training data with size: ", len(data[0]))
            X =  data[0]
            y = data[1]
            model.partial_fit(X, y)
            dump(model, './random_forest_model.joblib')
            print("retrain training data aquired")
    else:
        print("retrain model not reqested")
else:
    print("no model detected, training a new one")

    #Please uncomment these lines to start scrapping projects for training. NOTE: The training data is very large, make sure to allocate enough disk space.
    # urls = ["https://github.com/allenai/allennlp", "https://github.com/wention/BeautifulSoup4", "https://github.com/Cornices/cornice"]
    # # for repo in urls:
    # dr.GitRepoScrapper(urls[0])

    print("gathering training data for new model")
    data = GetTrainingData()
    print("aquired training data with size: ", len(data[0]))
    X =  data[0]
    y = data[1]
    print("running random forest model")
    RunRandomForest(X, y)
    print("done running random forest model")
    model = load('./random_forest_model.joblib')



print("running prediction")
grouped_dict = RunPrediction()

if grouped_dict == None:
    exit(1)

print("done prediction, sorting data")
sorted_data = {key: SortTuples(value) for key, value in grouped_dict.items()}
print("done sorting data")

# get the index +1 of the sorted dictionary value list that has '1' as the first tuple value
recommendation = []
correct_apis = []
for key, value in sorted_data.items():
    temp_list = []
    for tuple in value:
        temp_list.append(tuple[1])
        if tuple[0] == 1:
            correct_apis.append(tuple[1])
    recommendation.append(temp_list)
print("\ncorrect apis: ", correct_apis[0])
print("\ntop 10 recommended apis for: ",next(iter(sorted_data)),"\n",recommendation[0][:10])
print("calculating mrr")
k = [1,2,3,4,5,10]
print("MRR: ", ev.calculate_mrr(recommendation, correct_apis))
for i in k:
    print("Top K Accuracy ",i,": ", ev.calculate_top_k_accuracy(recommendation, correct_apis, i))
# print("Precision Recall: ",ev.calculate_precision_recall(recommendation, correct_apis))