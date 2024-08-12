from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.query import *
import csv


def index_data(csv_file_path, recreate_index):
    # index section
    columns_to_extract = ["file_path", "position", "reciever", "method", "token_feature", "parent_feature", "sibling_feature", "variable_usage_feature"] 
    if recreate_index:
        # title is the method call (object.method)
        # path will be the path to the file where the method calls are
        # the rest are the features we collected
        schema = Schema(file_path=TEXT(stored=True), position=TEXT(stored=True) ,reciever=TEXT(stored=True), method=TEXT(stored=True), token_feature=TEXT, parent_feature=TEXT, sibling_feature=TEXT, variable_feature=TEXT)
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
    
    
    return


def search_data():
    # searching section
    ix = open_dir(r"./Indexing")
    searcher = ix.searcher()
    with ix.searcher as searcher:
        feature_query = Or([Term("token_feature", u"apple"), Term("parent_feature", "bear"), Term("sibling_feature", ""), Term("variable_usage_feature", "")])
    



# evalution section (determine which feature has the most impact on performance)
