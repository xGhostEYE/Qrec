from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.query import *
import csv


def index_data(csv_file_path, recreate_index):
    # index section
    # TODO finish the columns to extract after julian gets his answer from prof
    columns_to_extract = ["method_name", "path", ""] 
    if recreate_index:
        # title is the method call (object.method)
        # path will be the path to the file where the method calls are
        # the rest are the features we collected
        schema = Schema(title=TEXT(stored=True), path=TEXT(stored=True), token_feature=TEXT, parent_feature=TEXT, sibling_feature=TEXT, variable_feature=TEXT)
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
            method_name = row[column_indices[0]]                
            path = row[column_indices[1]]
            # TODO add the rest of the columns here as well as add them to writer.add_document
            writer.add_document(title=method_name, path=path, )
    writer.commit()
    
    
    return


def search_data():
    # searching section
    ix = open_dir(r"./Indexing")
    with ix.searcher as searcher:
        
    



# evalution section (determine which feature has the most impact on performance)
