import configparser
import json
import random
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser import QueryParser
from whoosh.analysis import *
import csv
from Evaluation import Evaluators as ev
from strsimpy.longest_common_subsequence import LongestCommonSubsequence
from strsimpy.cosine import Cosine
from strsimpy.ngram import NGram
from timeit import default_timer as timer

# Create a ConfigParser object
config = configparser.ConfigParser()
 
# Read the configuration file
config.read('../config.ini')

def index_data(csv_file_path, recreate_index):
    columns_to_extract = ["file_path", "position", "receiver", "method", "token_feature", "parent_feature", "sibling_feature", "variable_usage_feature", "variable_with_method_usage_feature"] 
    
    if recreate_index:
        # title is the method call (object.method)
        # path will be the path to the file where the method calls are
        # the rest are the features we collected

        # expression = r'[\w\'#(),[\]=\s]+'
        expression = r'.+'
        myanalyzer = analysis.RegexTokenizer(expression=expression)

        schema = Schema(file_path=TEXT(stored=True,analyzer=myanalyzer), position=TEXT(stored=True,analyzer=myanalyzer) ,reciever=TEXT(stored=True,analyzer=myanalyzer), method=TEXT(stored=True,analyzer=myanalyzer), token_feature=TEXT(stored=True,analyzer=myanalyzer), parent_feature=TEXT(stored=True,analyzer=myanalyzer), sibling_feature=TEXT(stored=True,analyzer=myanalyzer), variable_usage_feature=TEXT(stored=True,analyzer=myanalyzer), variable_with_method_usage_feature=TEXT(stored=True,analyzer=myanalyzer))
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
            token_feature = row[column_indices[4]].replace("[","").replace("]","").replace(" ","").replace("),",") ")
            parent_feature = row[column_indices[5]].replace("[","").replace("]","").replace(" ","").replace("),",") ")
            sibling_feature = row[column_indices[6]].replace("[","").replace("]","").replace(" ","").replace("),",") ")
            variable_usage_feature = row[column_indices[7]].replace("[","").replace("]","").replace(" ","").replace("),",") ")
            variable_with_method_usage_feature = row[column_indices[8]].replace("[","").replace("]","").replace(" ","").replace("),",") ")
            writer.add_document(file_path=u'%s'%file_path, position = u'%s'%position ,reciever=u'%s'%reciever, method = u'%s'%method, token_feature = u'%s'%token_feature, parent_feature = u'%s'%parent_feature, sibling_feature = u'%s'%sibling_feature, variable_usage_feature = u'%s'%variable_usage_feature,
                                variable_with_method_usage_feature=u'%s'%variable_with_method_usage_feature)
    writer.commit()


def search_data(test_csv_file_path, top_k = None, isJsonExtracted = False, isEval = True):
    f = open("../data/results_topk_" + str(top_k) + ".json", 'w', encoding='utf-8')
    f.close()    
    
    start = timer()
    with open(test_csv_file_path, 'r') as csv_file:
        ix = open_dir(r"./Indexing")

        with ix.searcher() as searcher:
            data_reader = csv.reader(csv_file)
            
            
            header = next(data_reader)
            columns_to_extract = ["file_path", "position", "receiver", "method", "token_feature", "parent_feature", "sibling_feature", "variable_usage_feature", "variable_with_method_usage_feature"] 
            column_indices = [header.index(col) for col in columns_to_extract]
            
            #Key: (path:lineno:method)
            #Value: list of recommendations (sorted)
            recommendation_dict = {}
            details_recommendation_dict = {}

            for row in data_reader:
                
                file_path = row[column_indices[0]]
                position = row[column_indices[1]]
                receiver = row[column_indices[2]]
                method = row[column_indices[3]]

                token_feature = row[column_indices[4]].replace("[","").replace("]","").replace(" ","").replace("),",") ")
                parent_feature = row[column_indices[5]].replace("[","").replace("]","").replace(" ","").replace("),",") ")
                sibling_feature = row[column_indices[6]].replace("[","").replace("]","").replace(" ","").replace("),",") ")
                variable_usage_feature = row[column_indices[7]].replace("[","").replace("]","").replace(" ","").replace("),",") ")
                variable_with_method_usage_feature = row[column_indices[8]].replace("[","").replace("]","").replace(" ","").replace("),",") ")
                
                # Using QueryParser. A popular practice but could not land any hit, need more investigation
                # token_feature_query = QueryParser("token_feature", ix.schema).parse(u'%s'%token_feature)
                # parent_feature_query = QueryParser("parent_feature", ix.schema).parse(u'%s'%parent_feature)
                # sibling_feature_query = QueryParser("sibling_feature", ix.schema).parse(u'%s'%sibling_feature)
                # variable_usage_feature_query = QueryParser("variable_usage_feature", ix.schema).parse(u'%s'%variable_usage_feature)

                token_feature_query = Term("token_feature", u'%s'%token_feature)
                parent_feature_query = Term("parent_feature",u'%s'%parent_feature)
                sibling_feature_query = Term("sibling_feature", u'%s'%sibling_feature)
                variable_usage_feature_query = Term("variable_usage_feature", u'%s'%variable_usage_feature)
                variable_with_method_usage_feature_query = Term("variable_with_method_usage_feature", u'%s'%variable_with_method_usage_feature)

                list_feature = [token_feature,parent_feature,sibling_feature,variable_usage_feature,variable_with_method_usage_feature]
                list_feature_queries = [token_feature_query,parent_feature_query,sibling_feature_query,variable_usage_feature_query,variable_with_method_usage_feature_query]
                
                #Ranking system version 3
                results_dict = {}
                results_features_dict = {}

                w1 = float(config.get("User", "w1"))
                w2 = float(config.get("User", "w2"))
                w3 = float(config.get("User", "w3"))
                w4 = float(config.get("User", "w4"))
                w5 = float(config.get("User", "w5"))
                weights_list = [w1,w2,w3,w4,w5]
                fields = ["token_feature","parent_feature","sibling_feature","variable_usage_feature","variable_with_method_usage_feature"]

                def similarity_score(result_feature, query_feature):
                    #LCS
                    # lcs = LongestCommonSubsequence()
                    # lcs_result = lcs.distance(result_feature, query_feature)

                    #NGram - 4 Gram
                    # fourgram = NGram(4)
                    # fourgram_result = fourgram.distance(result_feature, query_feature)

                    #Cosine
                    cosine = Cosine(2)
                    cosine_result = cosine.similarity(result_feature, query_feature)

                    #TODO: custom sim. Number of similar term/ total number of terms
                    #custom_sim_result = custom_sim_result(result,list_feature[index])
                    return cosine_result

                def rank(result):
                    return result[1][0]


                for index in range(len(list_feature_queries)):
                    feature_query = list_feature_queries[index]

                    #Top K results for each feature-search
                    if top_k == "UNLIMITED":
                        top_k_value = None
                    else:
                        top_k_value = int(top_k)

                    results = searcher.search(feature_query, limit = top_k_value)

                    for matched_document in results:
                        if str(matched_document.fields()) not in results_features_dict:
                            results_features_dict[str(matched_document.fields())] = matched_document


                for string_matched_document, matched_document in results_features_dict.items():
                    method_call = matched_document['method']
                    list_score = [0,0,0,0,0]
                    sum = 0 
                    for index in range(len(fields)):
                        sim_score = similarity_score(matched_document[fields[index]],list_feature[index])
                        sum = sum + weights_list[index] * sim_score
                        list_score[index] = sim_score

                    if method_call not in results_dict:
                        results_dict[method_call] = (sum,list_score)
                    else:

                        current_sum = results_dict[method_call][0]
                        if current_sum < sum:
                            results_dict[method_call] = (sum,list_score)

                sorted_results_dict = dict(sorted(results_dict.items(), key=rank, reverse=True))            
                if (isEval):
                    position_category = position.replace(" ","").split("|")
                    position_line = position_category[0].split("-")
                    position_starting = position_line[0].replace("line:","")       
                    recommendation_dict[( ""+file_path+":"+receiver+":"+position_starting+":"+method)] = list(sorted_results_dict.keys())

                    # recommendation_dict[method] = list(sorted_results_dict.keys())
                    #Uncomment to extract the dict as json for researching purpose
                    # if (isJsonExtracted):
                    #     result_json_dict = {}
                    #     result_json_dict[method] = sorted_results_dict
                    #     with open("../data/results_topk_" + str(top_k) + ".json", 'a', encoding='utf-8') as f:
                    #         json.dump(result_json_dict, f, ensure_ascii=False)
                else:
                    position_category = position.replace(" ","").split("|")
                    position_line = position_category[0].split("-")
                    position_starting = position_line[0].replace("line:","")       
                    details_recommendation_dict[( ""+file_path+":"+receiver+":"+position_starting+":"+method)] = list(sorted_results_dict.keys())

            if (isEval):
                evaluate_result(recommendation_dict)
                end = timer()
                print(end - start, "(seconds)")   
            else:
                with open("../data/aroma_test_result.json", 'w', encoding='utf-8') as f:
                    json.dump(details_recommendation_dict, f, ensure_ascii=False)
                return details_recommendation_dict
                  

#Evalution section (determine which feature has the most impact on performance)
def evaluate_result(api_dict):
    index = random.randint(0, len((api_dict.keys())))
    first_recommendation_set_true_api = list(api_dict.keys())[index]
    first_recommendation_set = api_dict[first_recommendation_set_true_api]
    print("\ncorrect apis: ", list(api_dict.keys())[index])
    print("\ntop 10 recommended apis for: ",first_recommendation_set_true_api,"\n",first_recommendation_set[:10])
    print("calculating mrr")
    
    k = [1,2,3,4,5,10]
    print("MRR: ", ev.calculate_mrr(api_dict))
    for i in k:
        print("Top K Accuracy ",i,": ", ev.calculate_top_k_accuracy(api_dict, i))


#ARCHIVED:
#Ranking system version 1
# search_result_dict = {}
# for index in range(len(list_feature_queries)):
#     feature_query = list_feature_queries[index]

#     #Top K results for each feature-search
#     results = searcher.search(feature_query, limit = top_k)

#     #Saving the occurance of a method_call for a feature-search
#     for matched_document in results:
#         method_call = matched_document['method']
#         if method_call in search_result_dict:
#             method_result_list = search_result_dict[method_call]
#             method_result_list[index] = method_result_list[index] + 1
#         else:
#             method_result_list = [0,0,0,0,0]
#             method_result_list[index] = 1
#             search_result_dict[method_call] = method_result_list    

# w1 = float(config.get("User", "w1"))
# w2 = float(config.get("User", "w2"))
# w3 = float(config.get("User", "w3"))
# w4 = float(config.get("User", "w4"))
# w5 = float(config.get("User", "w5"))
# def sort(item):
#     return w1*item[1][0] + w2*item[1][1] + w3*item[1][2] + w4*item[1][3] + w5*item[1][4]               
# sorted_search_result_dict = dict(sorted(search_result_dict.items(), key=sort, reverse=True))
# recommendation_dict[method] = list(sorted_search_result_dict.keys())

#Ranking system version 2
# grouped_search_result_list = {}
# found_results = set()

# w1 = float(config.get("User", "w1"))
# w2 = float(config.get("User", "w2"))
# w3 = float(config.get("User", "w3"))
# w4 = float(config.get("User", "w4"))
# w5 = float(config.get("User", "w5"))
# weights_list = [w1,w2,w3,w4,w5]
# fields = ["token_feature","parent_feature","sibling_feature","variable_usage_feature","variable_with_method_usage_feature"]

# def similarity_score(result_feature, query_feature):
#     #LCS
#     # lcs = LongestCommonSubsequence()
#     # lcs_result = lcs.distance(result_feature, query_feature)

#     #NGram - 4 Gram
#     # fourgram = NGram(4)
#     # fourgram_result = fourgram.distance(result_feature, query_feature)

#     #Cosine
#     cosine = Cosine(2)
#     cosine_result = cosine.similarity(result_feature, query_feature)

#     #TODO: custom sim. Number of similar term/ total number of terms
#     #custom_sim_result = custom_sim_result(result,list_feature[index])
#     return cosine_result

# def rank(result):
#     sum = 0
#     for index in range(len(fields)):
#         if result in grouped_search_result_list[fields[index]]:
#             sum = sum + weights_list[index] * grouped_search_result_list[fields[index]][result]
#     return sum

# for index in range(len(list_feature_queries)):
#     feature_query = list_feature_queries[index]

#     #Top K results for each feature-search
#     if top_k == "UNLIMITED":
#         top_k_value = None
#     else:
#         top_k_value = int(top_k)
#     results = searcher.search(feature_query, limit = top_k_value)
#     search_result_dict = {}
#     for matched_document in results:
#         method_call = matched_document['method']
#         found_results.add(method_call)
#         sim_score = similarity_score(matched_document[fields[index]],list_feature[index])
    
#         if method_call not in search_result_dict:
#             search_result_dict[method_call] = sim_score
#         else:
#             current_sim_score = search_result_dict[method_call]
#             if current_sim_score < sim_score:
#                 search_result_dict[method_call] = sim_score
#     grouped_search_result_list[fields[index]] = search_result_dict
            
# sorted_found_results = sorted(found_results, key=rank, reverse=True)
# recommendation_dict[method] = sorted_found_results

# method_json_dict = {}
# result_json_dict = {}
# for result in sorted_found_results:
#     result_json_dict[result] = rank(result)
# method_json_dict[method] = result_json_dict

# with open("../data/results_topk_" + str(top_k) + ".json", 'a', encoding='utf-8') as f:
#     json.dump(method_json_dict, f, ensure_ascii=False)


#Ranking system version 3
# results_dict = []
# results_set = set()

# w1 = float(config.get("User", "w1"))
# w2 = float(config.get("User", "w2"))
# w3 = float(config.get("User", "w3"))
# w4 = float(config.get("User", "w4"))
# w5 = float(config.get("User", "w5"))
# weights_list = [w1,w2,w3,w4,w5]
# fields = ["token_feature","parent_feature","sibling_feature","variable_usage_feature","variable_with_method_usage_feature"]

# def similarity_score(result_feature, query_feature):
#     #LCS
#     # lcs = LongestCommonSubsequence()
#     # lcs_result = lcs.distance(result_feature, query_feature)

#     #NGram - 4 Gram
#     # fourgram = NGram(4)
#     # fourgram_result = fourgram.distance(result_feature, query_feature)

#     #Cosine
#     cosine = Cosine(2)
#     cosine_result = cosine.similarity(result_feature, query_feature)

#     #TODO: custom sim. Number of similar term/ total number of terms
#     #custom_sim_result = custom_sim_result(result,list_feature[index])
#     return cosine_result

# def rank(result):
#     return result[0]


# for index in range(len(list_feature_queries)):
#     feature_query = list_feature_queries[index]

#     #Top K results for each feature-search
#     if top_k == "UNLIMITED":
#         top_k_value = None
#     else:
#         top_k_value = int(top_k)

#     results = searcher.search(feature_query, limit = top_k_value)

#     for matched_document in results:
#         results_set.add(matched_document)

# for matched_document in results_set:
#     method_call = matched_document['method']
#     list_score = list(range(len(fields)))
#     sum = 0 
#     for index in range(len(fields)):
#         sim_score = similarity_score(matched_document[fields[index]],list_feature[index])
#         sum = sum + weights_list[index] * sim_score
#         list_score[index] = sim_score

#     if method_call not in results_dict:
#         results_dict[method_call] = (sum,list_score)
#     else:
#         current_sum = results_dict[method_call][0]
#         if current_sum < sum:
#             results_dict[method_call] = (sum,list_score)


# sorted_results_dict = dict(sorted(results_dict.items(), key=rank, reverse=True))            
# recommendation_dict[method] = list(sorted_results_dict.keys())

# result_json_dict = {}
# result_json_dict[method] = sorted_results_dict

# with open("../data/results_topk_" + str(top_k) + ".json", 'a', encoding='utf-8') as f:
#     json.dump(result_json_dict, f, ensure_ascii=False)