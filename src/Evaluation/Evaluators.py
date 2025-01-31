def calculate_top_k_accuracy(api_dict, k):
    """
    Calculate the Top-k accuracy for the given recommendations.
    
    :param api_dict: a dictionary represents true api and candidates for every recommendation points in the project 
                                   key = true api of the recommendation point, 
                                   value = the candidates for the recommendation point
    :param k: The number of top recommendations to consider for accuracy calculation.
    :return: The Top-k accuracy as a percentage.
    """
    correct_count = 0
    for key, value in api_dict.items():
        info = key.split(":")
        file_path = info[0]
        receiver = info[1]
        correct_method = info[2]
        position = info[3]
        if correct_method in value[:k]:
            correct_count += 1

    return (correct_count / len(api_dict)) * 100

def calculate_mrr(api_dict):
    """
    Calculate MRR for the test projects

    :param api_dict: a dictionary represents true api and candidates for every recommendation points in the project 
                                   key = true api of the recommendation point, 
                                   value = the candidates for the recommendation point
    :return the mrr for the test projects
    """
    total_rr = 0
    for key, value in api_dict.items():
        info = key.split(":")
        file_path = info[0]
        receiver = info[1]
        correct_method = info[2]
        position = info[3]
        try:
            index = value.index(correct_method)
            rank = index + 1
            total_rr = total_rr + 1/rank
        except ValueError:
            # correct API not in recommendations
            pass
    return total_rr / len(api_dict)

def calculate_precision_recall(correct_apis, recommended_apis):
    true_positives = len(set(correct_apis) & set(recommended_apis))
    false_positives = len(set(recommended_apis) - set(correct_apis))
    false_negatives = len(set(correct_apis) - set(recommended_apis))
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    return precision, recall
