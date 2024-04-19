def calculate_top_k_accuracy(recommendations, correct_apis, k):
    """
    Calculate the Top-k accuracy for the given recommendations.
    
    :param recommendations: A list of lists, where each sublist contains ordered API recommendations.
    :param correct_apis: A list of the correct APIs corresponding to each set of recommendations.
    :param k: The number of top recommendations to consider for accuracy calculation.
    :return: The Top-k accuracy as a percentage.
    """
    correct_count = 0
    for rec, correct_api in zip(recommendations, correct_apis):
        if correct_api in rec[:k]:
            correct_count += 1
    return (correct_count / len(correct_apis)) * 100

def calculate_mrr(recommendations, correct_apis):
    """
    Calculate the Mean Reciprocal Rank (MRR) for the given recommendations.
    
    :param recommendations: A list of lists, where each sublist contains ordered API recommendations.
    :param correct_apis: A list of the correct APIs corresponding to each set of recommendations.
    :return: The MRR of the recommendations.
    """
    mrr = 0
    for rec, correct_api in zip(recommendations, correct_apis):
        try:
            rank = rec.index(correct_api) + 1
            mrr += 1/rank
        except ValueError:
            # correct API not in recommendations
            pass
    return mrr / len(correct_apis)

def calculate_precision_recall(correct_apis, recommended_apis):
    true_positives = len(set(correct_apis) & set(recommended_apis))
    false_positives = len(set(recommended_apis) - set(correct_apis))
    false_negatives = len(set(correct_apis) - set(recommended_apis))
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    return precision, recall
