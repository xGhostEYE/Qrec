
def DataEncoder(method_dict, candidate_dict):

    data_dict = {}
    print("Encoding data...")
    for key, value in method_dict.items():
        
        the_object = key[0]
        if the_object != None:
            true_api = key[1]
            line_number = key[2]

            candidates = candidate_dict[(the_object,line_number)]
            candidates = candidates[:2]
            for candidate in candidates:
                x2 = get_x2(candidate, value, true_api)
                x3 = get_x3(the_object, candidate, line_number, method_dict)
                x4 = get_x4(method_dict, line_number, the_object)
                # print (the_object + "." + candidate, x2,x3)
                #vectorize this
                #x = a vector. TODO
                x = 0
                data_dict[ (the_object, candidate, line_number)] = x


    
        
        
def get_x2(candidate, dataflow, true_api):
    sum = 0
    true_api_idx = dataflow.index(true_api)
    for data in dataflow:
        if (data != true_api):
            data_idx = dataflow.index(data)
            d = abs(true_api_idx - data_idx)
            sum = sum + sim(candidate, data, d)
    return sum/ (len(dataflow) -1)

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
    THElist = []
    for key, val in method_dict.items():
       if key == object_name and line_number == key[2]:
           continue
       else:
           THElist.append(val)
    print(THElist)


