
import os
import re


def DataEncoder(method_dict, candidate_dict):

    data_dict = {}
    print("Encoding data...")
    for key, value in method_dict.items():
        
        the_object = key[0]
        if the_object != None:
            true_api = key[1]
            line_number = key[2]

            candidates = candidate_dict[(the_object,line_number)]

            if not (true_api in candidates):
                candidates.append(true_api)
            
            x1_dict = get_x1(candidates, value,true_api)
            for candidate in candidates:
                isTrue = 0
                if (candidate == true_api):
                    isTrue = 1

                x1 = x1_dict[candidate]
                x2 = get_x2(candidate, value, true_api)
                x3 = get_x3(the_object, candidate, line_number, method_dict)
                x4 = get_x4(method_dict, line_number, the_object, candidate)
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

    with open('test.txt','w+') as f:
        f.write(s)
    os.system('/home/melvin/runshit/Qrec/utils/Linux/srilm-1.7.3/lm/bin/i686-m64/ngram  -ppl test.txt  -order 4 -lm /home/melvin/runshit/Qrec/trainfile.lm -debug 2 > /home/melvin/runshit/Qrec/Ngram-output/output.ppl')

    with open('/home/melvin/runshit/Qrec/Ngram-output/output.ppl',encoding='ISO-8859-1') as f: 
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
    os.system('rm /home/melvin/runshit/Qrec/Ngram-output/output.ppl')
    return ngram_scores  
          

def get_x2(candidate, dataflow, true_api):
    sum = 0
    true_api_idx = dataflow.index(true_api)
    for data in dataflow:
        if (data != true_api):
            data_idx = dataflow.index(data)
            d = abs(true_api_idx - data_idx)
            sum = sum + sim(candidate, data, d)
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
        


def get_x3(the_object, candidate, line_number, method_dict):
    return get_confidence(the_object, candidate, line_number, method_dict)

def get_confidence(the_object, candidate, line_number, method_dict):
    n_x = get_n_x(the_object, line_number, method_dict)
    n_x_api = get_n_x_api(the_object, candidate, line_number, method_dict)
    if n_x == 0:
        return 0
    else:
        return n_x_api/n_x
def get_n_x(the_object, line_num, method_dict):
    count = 0
    for key in method_dict.keys():
        object_in_dict = key[0]
        line_num_in_dict = key[2]
        if (the_object == object_in_dict and line_num > line_num_in_dict):
            count += 1

    return count
def get_n_x_api(the_object, candidate, line_num, method_dict):
    count = 0
    for key in method_dict.keys():
        object_in_dict = key[0]
        api_in_dict = key[1]
        line_num_in_dict = key[2]
        if (the_object == object_in_dict and candidate == api_in_dict and line_num > line_num_in_dict ):
            count += 1
        
    return count

def get_x4(method_dict, line_number, object_name, candidate):

    token_dict = {}
    total_tokens_count = 0
    for key, val in method_dict.items():
       object_in_dict = key[0]
       api_in_dict = key[1]
       line_num_in_dict = key[2]
       if object_in_dict == object_name and line_number == line_num_in_dict:
           break
       if line_num_in_dict <= line_number:
           token_dict[line_num_in_dict] =  val
           total_tokens_count = total_tokens_count + len(val)
    
    sum = 0
    for line_number, tokens in token_dict.items():
        for token in tokens:
            confidence = get_confidence(token, candidate, line_number, method_dict )
            distance = get_distance(token_dict, token, line_number)
            sum = sum + (confidence/distance)

    # print(sum/total_tokens_count)
    return sum/total_tokens_count

def get_distance(token_dict, token, token_line_number):
    dist = 0
    found = False
    for key, value in token_dict.items():
        if found:
            dist = dist + found 
        if key == token_line_number:
            token_index = value.index(token)
            token_dist = len(value) - token_index 
            dist = dist + token_dist
            found = True
        else:
            continue
    return dist

                
