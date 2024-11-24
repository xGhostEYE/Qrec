
import os
import re
import configparser
from collections import OrderedDict
import kenlm
import ultils as ult

def DataEncoder(method_dict, candidate_dict, file_dict, list_all_file_path, filepath, frequency_files_dict, frequency_file_dict, occurrence_files_dict, occurrence_file_dict):

    data_dict = {}
    set_of_S = OrderedDict()

    bag_of_tokens = file_dict[filepath]
    
    set_of_S_line_num =  list(bag_of_tokens.keys())
    current_index = 0

    len_list_all_file_path = len(list_all_file_path)
    current_file_index = list_all_file_path.index(filepath)

    print("Encoding data for file: " + filepath, "| Progress: " + str(current_file_index + 1) + "/" + str(len_list_all_file_path))
    method_count = 0
    list_keys = [key for key in method_dict.keys() if key[0] != None]
    total = len(list_keys)
    try:
        #method_dict is not sorted. 
        #We sort it by the line number (key[2]) so we can add new tokens in to set of S each line at a time from top to bottom
        ordered_method_dict = dict(sorted(method_dict.items(), key=lambda t: t[0][2])) #t is the item, t[0] = key and t[1] = value
        for key, value in ordered_method_dict.items():
            the_object = key[0]
            if the_object != None:
                true_api = key[1]
                line_number = key[2]
                
                tokens = []
                for index in range(current_index ,len(set_of_S_line_num)):
                    current_line_number = set_of_S_line_num[index]
                    tokens = bag_of_tokens[current_line_number]
                    if (current_line_number < line_number):
                        valid_tokens = valid_string_token_list(tokens)
                        populate_set_of_S(set_of_S, valid_tokens)
                        continue

                    if (current_line_number >= line_number):
                        if (true_api in tokens):
                            valid_tokens = valid_string_token_list(tokens[0: tokens.index(true_api)])
                            populate_set_of_S(set_of_S, valid_tokens)
                            current_index = index
                        else:
                            valid_tokens = valid_string_token_list(tokens)
                            populate_set_of_S(set_of_S, valid_tokens)
                            current_index = index
                        break
        
                candidates = candidate_dict[(the_object,line_number,true_api)]
                candidates.add(true_api)
                method_count += 1
                print("Extracting features for the candidates of method call: " + the_object + "." + true_api, "| Progress: " + str(method_count) + "/" + str(total) + " (methods to be processed)")            
                x1_dict = get_x1(candidates, value,true_api)
                for candidate in candidates:
                    isTrue = 0
                    if (candidate == true_api):
                        isTrue = 1         
                    x1 = x1_dict[candidate]
                    x2 = get_x2(candidate, value, true_api)
                    x3 = get_x3(file_dict, filepath, the_object, candidate, frequency_files_dict, frequency_file_dict)
                    x4 = get_x4(file_dict, filepath, candidate, set_of_S,occurrence_files_dict, occurrence_file_dict)
                    x = [x1,x2,x3,x4]

                    data_dict[ (the_object, candidate, line_number, isTrue, true_api)] = x
                print("Finished extracting features for the candidates of method call: " + the_object + "." + true_api)            
                print(len(candidates))
                try:
                    if true_api in tokens:
                        continue_index = tokens.index(true_api)
                        valid_tokens = valid_string_token_list(tokens[continue_index: ])
                        populate_set_of_S(set_of_S, valid_tokens)
                
                except Exception as e:
                    print("Enountered error when appending missing tokens (that was left out during the current encoding process) into the set of S")
                    print("Proceed to not appending the left-out tokens")
                    ult.write_error_log(e, filepath)
    except Exception as e:
        ult.write_error_log(e, filepath)
                
    return data_dict


def populate_set_of_S(set_of_S, tokens):
    if len(tokens) == 0:
        return
    for token in tokens:
        set_of_S[token] = None
def valid_string_token_list(tokens):
    try:
        valid_token_list = []
        for token in tokens:
            if (isinstance(token,str)):
                valid_token_list.append(token)
            elif (isinstance(token, list)):
                token_list = token
                for each_token in token_list:
                    if (isinstance(each_token,str)):
                        valid_token_list.append(each_token)

        return valid_token_list
    except:
        print("Encountered error when retrieving bag of tokens for a code line. Returning empty list of that code line ")
        return []
def get_x1(candidates, dataflow, true_api):
    ngram_scores = {}
    model = kenlm.Model("../../Qrec/trainfile.arpa")
    for candidate in candidates:
        input = ""
        for data in dataflow:
            token = data
            if token == true_api:
                token = candidate
            if not input or input.split(" ")[-1] == "\n":
                input = input + token
            else:
                input = input + " " + token

        #Format of each result [set(first, second, third)] in full_scores: 
            #first = log prob 
            #second = ngram length
            #third = true if word is OOV (out of vocabulary). false otherwise       
        total_logprob = 0
        for result in list(model.full_scores(input)):
            if result[2] == False:
                total_logprob = total_logprob + result[0]
        ngram_scores[candidate]=total_logprob

    return ngram_scores  
          

def get_x2(candidate, dataflow, true_api):
    sum = 0
    true_api_idx = dataflow.index(true_api)
    for data in dataflow:
        if (data != true_api):
            data_idx = dataflow.index(data)
            d = abs(true_api_idx - data_idx)
            sum = sum + sim(candidate, data, d)

    if (len(dataflow) -1 == 0):
        return 0
    return float(sum/ (len(dataflow) -1))

def sim(candidate, data, d):
    #Longest common sub-sequence: https://www.geeksforgeeks.org/longest-common-subsequence-dp-4/
    def lcs(X, Y, m, n):
        # Declaring the array for storing the dp values
        L = [[None]*(n+1) for i in range(m+1)]
    
        # Following steps build L[m+1][n+1] in bottom up fashion
        # Note: L[i][j] contains length of LCS of X[0..i-1]
        # and Y[0..j-1]
        for i in range(m+1):
            for j in range(n+1):
                if i == 0 or j == 0:
                    L[i][j] = 0
                elif X[i-1] == Y[j-1]:
                    L[i][j] = L[i-1][j-1]+1
                else:
                    L[i][j] = max(L[i-1][j], L[i][j-1])
    
        # L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1]
        return L[m][n]
    
    return (2 * lcs(candidate,data, len(candidate), len(data)))/ (d* (len(candidate) + len(data))) 
        


def get_x3(file_dict, file_path, the_object, candidate, frequency_files_dict, frequency_file_dict):

    return get_x3_confidence(file_dict, file_path, the_object, candidate, frequency_files_dict, frequency_file_dict)

def get_x3_confidence(file_dict, file_path, the_object, candidate, frequency_files_dict, frequency_file_dict):
    n_x_api = get_n_x3_api(file_dict, file_path, the_object, candidate, frequency_files_dict, frequency_file_dict)
    
    if n_x_api == 0:
        return 0
    
    n_x = get_n_x3(file_dict, file_path, the_object, frequency_files_dict, frequency_file_dict )

    if n_x == 0:
        return 0

    return n_x_api/n_x

def get_current_file_tokens_frequency(token, candidate, frequency_current_file_dict):
    try:
        count = frequency_current_file_dict[(token,candidate)]
        return count
    except KeyError as e:
        return 0
      
def get_n_x3_api(file_dict, file_path, object, candidate, frequency_files_dict, frequency_file_dict):
    try:
        count = frequency_files_dict[(object,candidate)]
        frequency_current_file_dict = frequency_file_dict[file_path]
        count_current_file = frequency_current_file_dict[(object,candidate)]
        return count - count_current_file
    
    except KeyError as e:
        total_count = 0
        count_current_file = 0
        for key, value in file_dict.items():
            frequency_current_file_dict = frequency_file_dict[key]
            count = get_current_file_tokens_frequency(object, candidate, frequency_current_file_dict)
            total_count = total_count + count
            if (key == file_path):
                count_current_file = count


        frequency_files_dict[(object, candidate)] = total_count

        return total_count - count_current_file


def get_n_x3(file_dict, file_path, object, frequency_files_dict, frequency_file_dict):
    

    try:
        count = frequency_files_dict[(object, None)]
        frequency_current_file_dict = frequency_file_dict[file_path]
        count_current_file = frequency_current_file_dict[(object, None)]
        
        return count - count_current_file
    
    except KeyError as e:
    
        total_count = 0
        count_current_file = 0
        for key, value in file_dict.items():
            frequency_current_file_dict = frequency_file_dict[key]
            count = get_current_file_tokens_frequency(object, None, frequency_current_file_dict)
            total_count = total_count + count
            if (key == file_path):
                count_current_file = count


        frequency_files_dict[(object, None)] = total_count

        return total_count - count_current_file


def get_x4(file_dict, file_path, candidate, set_of_S, occurrence_files_dict, occurrence_file_dict):
    try:
        total_confidence = 0
        total_token = len(set_of_S)
        if total_token == 0:
            return 0
        
        list_of_S = list(set_of_S.keys())
        for i in range(total_token):
            token = list_of_S[i]
            confidence = get_x4_confidence(file_dict, file_path, token, candidate, occurrence_files_dict, occurrence_file_dict)
            distance = total_token - i
            if distance == 0:
                continue
            total_confidence = total_confidence + confidence/distance
            


        # for i in range(len(set_of_S)):
        #     for j in range(len(set_of_S[i])):
        #         total_token+=1
        #         confidence = get_x4_confidence(file_dict, file_path, set_of_S[i][j], candidate, occurrence_files_dict, occurrence_file_dict)
        #         distance = get_distance(i, set_of_S, j, len(set_of_S[i]))
        #         if distance == 0:
        #             continue
        #         total_confidence = total_confidence + confidence/distance
        
        return (1/total_token) * total_confidence
    except Exception as e:
        ult.write_error_log(e, file_path)
        return 0

def get_x4_confidence(file_dict, file_path, token, candidate, occurrence_files_dict, occurrence_file_dict):
    nx_api = get_n_x4_api(file_dict, file_path, token, candidate, occurrence_files_dict, occurrence_file_dict)

    if nx_api == 0:
        return 0
    
    nx = get_n_x4(file_dict, file_path, token, occurrence_files_dict, occurrence_file_dict)

    if nx == 0:
        return 0
        
    return nx_api/nx

def get_current_file_token_occurrence(token, occurrence_current_file_dict):
    try:
        isExist = occurrence_current_file_dict[(token, None)]
        return True
    except KeyError as e:
        return False
    
def get_n_x4_api(file_dict, file_path, token, candidate, occurrence_files_dict, occurrence_file_dict):
    #Assume we have stored this value for every file. We need to exclude the current file
    try:        
        count = occurrence_files_dict[(token, candidate)]
        
        occurrence_current_file_dict = occurrence_file_dict[file_path]
        found_token = get_current_file_token_occurrence(token, occurrence_current_file_dict)
        found_candidate = get_current_file_token_occurrence(candidate, occurrence_current_file_dict)

        #exclude the current file
        if found_token and found_candidate:
            return count - 1
        
        return count      

    except KeyError as e:    
        #If we have NOT stored this value for all files dictionary, we need to do so.
        
        total_count = 0

        #value of the current file
        count_current_file = 0

        for key, value in file_dict.items():
            occurrence_current_file_dict = occurrence_file_dict[key]
            found_token = get_current_file_token_occurrence(token, occurrence_current_file_dict)
            found_candidate = get_current_file_token_occurrence(candidate, occurrence_current_file_dict)
                    
            if found_token and found_candidate:
                total_count += 1
                
                if (key == file_path):
                    count_current_file = 1
        
        occurrence_files_dict[(token, candidate)] = total_count

        return total_count - count_current_file
        
    

def get_n_x4(file_dict, file_path, token, occurrence_files_dict, occurrence_file_dict):
    try:
        count = occurrence_files_dict[(token, None)]
        occurrence_current_file_dict = occurrence_file_dict[file_path]
        found_token = get_current_file_token_occurrence(token, occurrence_current_file_dict)

        #exclude the current file
        if found_token:
            return count - 1
        return count      

    except KeyError as e:
        total_count = 0
        count_current_file = 0
        for key, value in file_dict.items():
            occurrence_current_file_dict = occurrence_file_dict[key]
            found_token = get_current_file_token_occurrence(token, occurrence_current_file_dict = occurrence_file_dict[file_path])
            if found_token:
                total_count += 1
                if (key == file_path):
                    count_current_file = 1
                 

        occurrence_files_dict[(token, None)] = total_count

        return total_count - count_current_file


#TODO: check how PyArt defines "distance between tokens"
def get_distance(index_of_sublist, set_S, index_in_sublist, len_sublist):
    distance_to_end_of_sublist = len_sublist - index_in_sublist

    try:
        start_index = index_of_sublist + 1
        for i in range(start_index, len(set_S)):
            distance_to_end_of_sublist = distance_to_end_of_sublist + len(set_S[i])
        
    except Exception as e:    
        pass

    return distance_to_end_of_sublist

                
