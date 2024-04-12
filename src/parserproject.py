import ultils as ult
import os.path as op
from joblib import dump, load
from Models.Randomforest import RunRandomForest
import numpy as np
import DataExtractor.FeatureCollector as fc
import DataExtractor.CandidateGenerator as cg
import DataEncoder.DataEncoder as de
from collections import defaultdict
import traceback 
# from Evaluation import Evaluators

directory = r"../test/Project1"
model = None
data_dict = {}
predictions = []
probabilities = []
probabilities_result_correct = []

def RunPrediction():
    model = load('./random_forest_model.joblib')
    file_path = "../test/coloredTiles.py"
    print("test file exists: ",op.isfile(file_path), "\n")
    try:
        with open(file_path, encoding='utf-8') as file:
            method_dict = fc.extract_data(file)
        with open(file_path, encoding='utf-8') as file:
            candidate_dict = cg.CandidatesGenerator(file, file_path, method_dict)
            print(candidate_dict)
        #Format of data_dict:
        #Key = [object, api, line number, 0 if it is not true api and 1 otherwise]
        #Value = [x1,x2,x3,x4]
        data_dict.update(de.DataEncoder(method_dict,candidate_dict))
        print("test")
        print("data_doct len ",len(data_dict))
        # Initialize a defaultdict to store grouped objects
        grouped_dict = defaultdict(list)

        # Group objects by their key values
        for key, value in data_dict.items():
            object_name, api_name, line_number, is_api = key
            grouped_dict[(object_name, line_number)].append((api_name, value))

        # Convert defaultdict back to a regular dictionary if needed
        grouped_dict = dict(grouped_dict)
        print("grouped_dict", grouped_dict)
        
        for key,value in grouped_dict.items():
            probabilities.append((key, model.predict_proba(value)))
        # probabilities = np.argsort(probabilities, axis=1)[:, ::-1]

    except Exception as e:
        traceback.print_exc() 
        

    
# check if we already have a model
# if we don't then train a new one
# if we do then train the already generated model
RunPrediction()
print(probabilities)

# if op.isfile("./random_forest_model.joblib"):
#     model = load('./random_forest_model.joblib')
# else:
#     data_dict = data_dict.update(ult.analyze_directory(directory))
#     labels = []
#     for key,value in data_dict.items():
#         labels.append(key[3])

#     RunRandomForest(list(data_dict.values()), labels)
#     model = load('./random_forest_model.joblib')


# RunPrediction()
# for i in range(len(probabilities)):
#     probabilities_result_correct.append(probabilities[i][1])
# Evaluators.calculate_mrr()






