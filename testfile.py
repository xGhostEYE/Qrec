from DataExtractor import FeatureCollector
filename = "./parsetestfile.py"
function_calls_info = FeatureCollector.extract_data(filename)
for key, val in function_calls_info.items():
    print(key,": ", val)
print("\n")
data = FeatureCollector.x3_extractor(function_calls_info)
for i in data:
    print(i)