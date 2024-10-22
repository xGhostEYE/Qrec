import configparser
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser import QueryParser
from whoosh.analysis import *
import csv
from Evaluation import Evaluators as ev


# Create a ConfigParser object
config = configparser.ConfigParser()
 
# Read the configuration file
config.read('../config.ini')

def index_data(csv_file_path, recreate_index):
    # index section
    columns_to_extract = ["file_path", "position", "receiver", "method", "token_feature", "parent_feature", "sibling_feature", "variable_usage_feature", "variable_with_method_usage_feature"] 
    
    if recreate_index:
        # title is the method call (object.method)
        # path will be the path to the file where the method calls are
        # the rest are the features we collected

        # expression = r'[\w\'#(),[\]=\s]+'
        expression = r'.+'
        myanalyzer = analysis.RegexTokenizer(expression=expression)

        schema = Schema(file_path=TEXT(stored=True,analyzer=myanalyzer), position=TEXT(stored=True,analyzer=myanalyzer) ,reciever=TEXT(stored=True,analyzer=myanalyzer), method=TEXT(stored=True,analyzer=myanalyzer), token_feature=TEXT(analyzer=myanalyzer), parent_feature=TEXT(analyzer=myanalyzer), sibling_feature=TEXT(analyzer=myanalyzer), variable_usage_feature=TEXT(analyzer=myanalyzer), variable_with_method_usage_feature=TEXT(analyzer=myanalyzer))
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


def search_data(test_csv_file_path, top_k = None):

    # searching section

    with open(test_csv_file_path, 'r') as csv_file:
        ix = open_dir(r"./Indexing")

        with ix.searcher() as searcher:
            data_reader = csv.reader(csv_file)
            
            
            header = next(data_reader)
            columns_to_extract = ["file_path", "position", "receiver", "method", "token_feature", "parent_feature", "sibling_feature", "variable_usage_feature", "variable_with_method_usage_feature"] 
            column_indices = [header.index(col) for col in columns_to_extract]
            
            #Key: (true method)
            #Value: list of recommendations (sorted)
            recommendation_dict = {}
            for row in data_reader:
                
                file_path = row[column_indices[0]]
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

                list_feature_queries = [token_feature_query,parent_feature_query,sibling_feature_query,variable_usage_feature_query,variable_with_method_usage_feature_query]
                
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
                #             method_result_list = [0,0,0,0]
                #             method_result_list[index] = 1
                #             search_result_dict[method_call] = method_result_list    
                
                # w1 = float(config.get("User", "w1"))
                # w2 = float(config.get("User", "w2"))
                # w3 = float(config.get("User", "w3"))
                # w4 = float(config.get("User", "w4"))
                # def sort(item):
                #     return w1*item[1][0] + w2*item[1][1] + w3*item[1][2] + w4*item[1][3]                
                # sorted_search_result_dict = dict(sorted(search_result_dict.items(), key=sort, reverse=True))
                # recommendation_dict[method] = list(sorted_search_result_dict.keys())

                #Ranking system version 2
                search_result_list = []
                for index in range(len(list_feature_queries)):
                    feature_query = list_feature_queries[index]

                    #Top K results for each feature-search
                    results = searcher.search(feature_query, limit = top_k)

                    for matched_document in results:
                        method_call = matched_document['method']
                        search_result_list.insert((method_call,matched_document))
                
                w1 = float(config.get("User", "w1"))
                w2 = float(config.get("User", "w2"))
                w3 = float(config.get("User", "w3"))
                w4 = float(config.get("User", "w4"))
                w5 = float(config.get("User", "w4"))
                
                def sort(result):
                    matched_document = result[1]
                    matched_document_token_feature = matched_document['token_feature']
                    matched_document_parent_feature =  matched_document['parent_feature']
                    matched_document_sibling_feature =  matched_document['sibling_feature']
                    matched_document_variable_usage_feature =  matched_document['variable_usage_feature']
                    matched_document_variable_with_method_usage_feature =  matched_document['variable_with_method_usage_feature']

                    s1 = 0
                    if (matched_document_token_feature == token_feature):
                        s1 = s1 * w1
                    
                    s2 = 0
                    if (matched_document_parent_feature == parent_feature):
                        s2 = s2 * w2

                    s3 = 0
                    if (matched_document_sibling_feature == sibling_feature):
                        s3 = s3 * w3

                    s4 = 0
                    if (matched_document_variable_usage_feature == variable_usage_feature):
                        s4 = s4 * w4

                    s5 = 0
                    if (matched_document_variable_with_method_usage_feature == variable_with_method_usage_feature):
                        s5 = s5 * w5

                    return s1+s2+s3+s4+s5
                    

                search_result_list.sort(key=sort)
                sorted_result = {}
                for result in search_result_list:
                    sorted_result.add(result)
                
                recommendation_dict[method] = list(sorted_result)

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
    