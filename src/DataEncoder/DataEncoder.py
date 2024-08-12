
import os
import re
import configparser

def DataEncoder(method_dict, candidate_dict, file_dict, filepath, token_dict):

    data_dict = {}
    set_of_S = []
    bag_of_tokens = file_dict[filepath]
    set_of_S_cursor_value =  list(bag_of_tokens.keys())
    current_cursor = 0

    print("Encoding data...")
    for key, value in method_dict.items():
        
        the_object = key[0]
        if the_object != None:
            true_api = key[1]
            line_number = key[2]
            
            for cursor in range(current_cursor ,len(set_of_S_cursor_value)):
                current_line_number = set_of_S_cursor_value[cursor]
                tokens = bag_of_tokens[current_line_number]
                if (current_line_number < line_number):
                    set_of_S.append(tokens)
                    continue
                
                elif (current_line_number == line_number and true_api in tokens):
                    set_of_S.append(tokens[0: tokens.index(true_api)])
                    current_cursor = cursor + 1    
                    break
            
            candidates = candidate_dict[(the_object,line_number)]

            if not (true_api in candidates):
                candidates.append(true_api)
            
            # x1_dict = get_x1(candidates, value,true_api)
            print("Extracting features for the candidates")
            for candidate in candidates:
                isTrue = 0
                if (candidate == true_api):
                    isTrue = 1
                
                x1 = 0 
                x2 = get_x2(candidate, value, true_api)
                x3 = get_x3(the_object, candidate, line_number, method_dict, file_dict, filepath)
                x4 = get_x4(file_dict, filepath, candidate, token_dict, set_of_S,)
                x = [x1,x2,x3,x4]

                data_dict[ (the_object, candidate, line_number, isTrue)] = x
    return data_dict        
def get_x1(candidates, dataflow, true_api):
    s = ""
    ngram_scores = {}
    for candidate in candidates:
        for data in dataflow:
            token = data
            if token == true_api:
                token = candidate
            if not s or s.split(" ")[-1] == "\n":
                s = s + token
            else:
                s = s + " " + token
        s = s + " \n"

    with open('../../Qrec/Ngram-output/ngram_input.txt','w+') as f:
        f.write(s)
	
    config = configparser.ConfigParser()
	
    #Change to absolute path if encounter errors
    config.read('../config.ini')
    system = config.get("User", "system")

    if (system.upper() == "LINUX"):
        os.system('../../Qrec/utils/Linux/srilm-1.7.3/lm/bin/i686-m64/ngram  -ppl ../../Qrec/Ngram-output/ngram_input.txt -order 4 -lm ../../Qrec/trainfile.lm -debug 2 > ../../Qrec/Ngram-output/output.ppl')  
    elif (system.upper() == "MACOS"):
        os.system('../../Qrec/utils/MacOs/srilm-1.7.3/lm/bin/macosx/ngram  -ppl ../../Qrec/Ngram-output/ngram_input.txt -order 4 -lm ../../Qrec/trainfile.lm -debug 2 > ../../Qrec/Ngram-output/output.ppl')
    else:
       raise Exception("Error due to unspecified or incorrect value for [User]'s system ") 
	
    with open('../../Qrec/Ngram-output/output.ppl',encoding='ISO-8859-1') as f: 
         lines=f.readlines()
	
    for candidate in candidates:
            flag=0
            for i in range(0,len(lines)):
                kname=lines[i].strip().split(' ')		
                for item in kname:
                    if item==candidate:
                        flag=1
                        break
                if flag==1:
                    #print(lines[i])
                    j=i+1
                    while 'logprob=' not in lines[j]:
                        j=j+1
                    score=re.findall('logprob=\s[0-9\-\.]+',lines[j])
                    ngram_scores[candidate]=float(score[0][9:])
                    break
            if flag==0:
                ngram_scores[candidate]=0.0
    os.system('rm ../../Qrec/Ngram-output/output.ppl')
    os.system('rm ../../Qrec/Ngram-output/ngram_input.txt')
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
        


def get_x3(the_object, candidate, line_number, method_dict, file_dict, file_path):
    bag_of_tokens = file_dict[file_path]
            
    return get_x3_confidence(the_object, candidate, line_number, method_dict, bag_of_tokens)

def get_x3_confidence(the_object, candidate, line_number, method_dict, bag_of_tokens):
    n_x = get_n_x3(the_object, line_number, bag_of_tokens)
    n_x_api = get_n_x3_api(the_object, candidate, line_number, method_dict)

    if n_x == 0:
        return 0
    else:
        return n_x_api/n_x
    
def get_n_x3(the_object, line_num, bag_of_tokens):
    count = 0

    for line in bag_of_tokens:
        if line < line_num:
            count = count + 1 if the_object in bag_of_tokens[line] else count
    return count

def get_n_x3_api(the_object, candidate, line_num, method_dict):
    count = 0
    for key in method_dict.keys():
        object_in_dict = key[0]
        api_in_dict = key[1]
        line_num_in_dict = key[2]
        if (the_object == object_in_dict and candidate == api_in_dict and line_num > line_num_in_dict ):
            count += 1
    return count

def get_x4(file_dict, file_path, candidate, tokens_dict, set_of_S):

    
    
    total_confidence = 0

    for i in range(len(set_of_S)):
        for j in range(len(set_of_S[i])):
            confidence = get_x4_confidence(file_dict, file_path, set_of_S[i][j], candidate, tokens_dict)
            distance = get_distance(i, set_of_S, j, len(set_of_S[i]))
        
            if distance == 0:
                continue

            total_confidence = total_confidence + confidence/distance

    return (1/len(set_of_S)) * total_confidence

def get_x4_confidence(file_dict, file_path, token, candidate, tokens_dict):
    nx_api = get_n_x4_api(file_dict, file_path, token, candidate, tokens_dict)
    
    if nx_api == 0:
        return 0
    
    nx = get_n_x4(file_dict, file_path, token, tokens_dict)

    if nx == 0:
        return 0
        
    return nx_api/nx

def get_n_x4(file_dict, file_path, token, tokens_dict):
    count = 0
    try:
        return tokens_dict[(token, None)]
    except KeyError as e:
        pass

    for key, value in file_dict.items():
        
        if key != file_path:    
            for tokens in value.values():
                if token in tokens:
                    count = count + 1
                    break
    tokens_dict[(token, None)] = count
    return count

def get_n_x4_api(file_dict, file_path, token, candidate, tokens_dict):
    count = 0

    try:
        return tokens_dict[(token, candidate)]
    except KeyError as e:
        pass

    for key, value in file_dict.items():
        found_token = False
        found_candidate = False
        if key != file_path:    
            for tokens in value.values():
                if not found_token and token in tokens:
                    found_token = True
                    
                if not found_candidate and candidate in tokens:
                    found_candidate = True

                if found_token and found_candidate:
                    count += 1
                    break
    tokens_dict[(token, candidate)] = count
    return count
def get_distance(index_of_sublist, set_S, index_in_sublist, len_sublist):
    distance_to_end_of_sublist = len_sublist - index_in_sublist - 1

    try:
        start_index = index_of_sublist + 1
        for i in range(start_index, len(set_S)):
            distance_to_end_of_sublist = distance_to_end_of_sublist + len(set_S[i])
        
    except Exception as e:
        pass
    
    return distance_to_end_of_sublist

                
