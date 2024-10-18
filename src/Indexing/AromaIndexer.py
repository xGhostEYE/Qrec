from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser import QueryParser

import csv
from Evaluation import Evaluators as ev



def index_data(csv_file_path, recreate_index):
    # index section
    columns_to_extract = ["file_path", "position", "receiver", "method", "token_feature", "parent_feature", "sibling_feature", "variable_usage_feature"] 
    
    if recreate_index:
        # title is the method call (object.method)
        # path will be the path to the file where the method calls are
        # the rest are the features we collected
        schema = Schema(file_path=TEXT(stored=True), position=TEXT(stored=True) ,reciever=TEXT(stored=True), method=TEXT(stored=True), token_feature=TEXT, parent_feature=TEXT, sibling_feature=TEXT, variable_usage_feature=TEXT)
        ix = create_in(r"./Indexing", schema)
                
    ix = open_dir(r"./Indexing")
    writer = ix.writer()
    
    with open(csv_file_path, 'r') as csv_file:
        data_reader = csv.reader(csv_file)
        # read the header row to get the column indices
        header = next(data_reader)
        # find the columns we want
        column_indices = [header.index(col) for col in columns_to_extract]

        for row in data_reader:
            file_path = row[column_indices[0]]
            position = row[column_indices[1]]              
            reciever = row[column_indices[2]]
            method = row[column_indices[3]]
            token_feature = row[column_indices[4]]
            parent_feature = row[column_indices[5]]
            sibling_feature = row[column_indices[6]]
            variable_usage_feature = row[column_indices[7]]
            writer.add_document(file_path=file_path, position = position ,reciever=reciever, method = method, token_feature = token_feature, parent_feature = parent_feature, sibling_feature = sibling_feature, variable_usage_feature = variable_usage_feature)
    writer.commit()


def search_data(test_csv_file_path, top_k = None):

    # searching section

    with open(test_csv_file_path, 'r') as csv_file:
        ix = open_dir(r"./Indexing")

        with ix.searcher() as searcher:
            data_reader = csv.reader(csv_file)
            
            
            header = next(data_reader)
            columns_to_extract = ["file_path", "position", "receiver", "method", "token_feature", "parent_feature", "sibling_feature", "variable_usage_feature"] 
            column_indices = [header.index(col) for col in columns_to_extract]
            
            #Key: (true method)
            #Value: list of recommendations (sorted)
            recommendation_dict = {}
            for row in data_reader:
                
                file_path = row[column_indices[0]]
                receiver = row[column_indices[2]]
                method = row[column_indices[3]]

                token_feature = row[column_indices[4]]
                parent_feature = row[column_indices[5]]
                sibling_feature = row[column_indices[6]]
                variable_usage_feature = row[column_indices[7]]

                
                # feature_query = Or([Term("token_feature", token_feature), Term("parent_feature", parent_feature), Term("sibling_feature", sibling_feature), Term("variable_usage_feature", variable_usage_feature)])
                # recomemnded_methods_call = searcher.query(feature_query, limit=top_k)
                
                token_feature_query = QueryParser("token_feature", token_feature).parse(token_feature)
                parent_feature_query = QueryParser("parent_feature", token_feature).parse(parent_feature)
                sibling_feature_query = QueryParser("sibling_feature", token_feature).parse(sibling_feature)
                variable_usage_feature_query = QueryParser("variable_usage_feature", token_feature).parse(variable_usage_feature)

                list_feature_queries = [token_feature_query,parent_feature_query,sibling_feature_query,variable_usage_feature_query]
                
                search_result_dict = {}
                for index in range(len(list_feature_queries)):
                    feature_query = list_feature_queries[index]

                    #Top K results for each feature-search
                    results = searcher.search(feature_query, limit = top_k)

                    #Saving the occurance of a method_call for a feature-search
                    for matched_document in results:
                        method_call = matched_document['method']
                        if method_call in search_result_dict:
                            method_result_list = search_result_dict[method_call]
                            method_result_list[index] = method_result_list[index] + 1
                        else:
                            method_result_list = [0,0,0,0]
                            method_result_list[index] = 1
                            search_result_dict[method_call] = method_result_list

                w1 = 0.25
                w2 = 0.25
                w3 = 0.25
                w4 = 0.25

                def sort(item):
                    return w1*item[1][0] + w2*item[1][1] + w3*item[1][2] + w4*item[1][3]                
                sorted_search_result_dict = dict(sorted(search_result_dict.items(), key=sort, reverse=True))
                recommendation_dict[method] = list(sorted_search_result_dict.keys())
            evaluate_result(recommendation_dict)
                
    # search each of the features using top k as the limit, and use the pyart similarity score in the paper which gives a number
    # repeat for all the other features and then i get 4 scores in total
    # calculate the average



# evalution section (determine which feature has the most impact on performance)
def evaluate_result(api_dict):
    first_recommendation_set_true_api = list(api_dict.keys())[0]
    first_recommendation_set = api_dict[first_recommendation_set_true_api]
    print("\ncorrect apis: ", list(api_dict.keys())[0])
    print("\ntop 10 recommended apis for: ",first_recommendation_set_true_api,"\n",first_recommendation_set[:10])
    print("calculating mrr")
    
    k = [1,2,3,4,5,10]
    print("MRR: ", ev.calculate_mrr(api_dict))
    for i in k:
        print("Top K Accuracy ",i,": ", ev.calculate_top_k_accuracy(api_dict, i))
    