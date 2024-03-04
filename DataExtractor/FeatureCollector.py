import astor
import ast
import itertools

def FeatureCollector(file):
    # TODO feature collector work to get the weights goes here
    tree = ast.parse(file.read())
    
    #replace pass with the feature when done
    pass

    

#Function to analyze code
def extract_function_calls(node, parent_class=None):
    """
    Extract function calls and their line numbers, including the context leading up to those calls.
    """
    function_calls = {}

    #helper function to process function/method calls
    def process_call(call_node):
        func_name = "complex_call"
        call_object = None
        call_args = []
        
        if isinstance(call_node.func, ast.Attribute):
            func_name = call_node.func.attr
            call_object = ast.unparse(call_node.func.value)  # The object the method is called on
        elif isinstance(call_node.func, ast.Name):
            func_name = call_node.func.id  # For direct function calls
        
        # get arguments in a readable format
        call_args = [ast.unparse(arg) for arg in call_node.args]
        
        if call_object:
            call_repr = call_args + [func_name, call_object]
        else:
            call_repr = call_args + [func_name]

        # Use the call node's lineno for accurate line numbers
        lineno = call_node.lineno
        function_calls.setdefault((func_name, lineno), []).append(call_repr)


    for node in ast.walk(node):
        if isinstance(node, ast.FunctionDef):
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    process_call(child)

        elif isinstance(node, ast.ClassDef):
            class_name = node.name
            for child in ast.walk(node):
                if isinstance(child, ast.FunctionDef) or isinstance(child, ast.Call):
                    extract_function_calls(child, class_name)

        elif isinstance(node, ast.Call):
            process_call(node)
    
    # remove duplicate lists
    for key, value in function_calls.items():
        unique_tuples = set(tuple(x) for x in value)
        unique_lists = [list(x) for x in unique_tuples]
        if len(unique_lists) == 1:
            function_calls[key] = unique_lists[0]
        else:
            function_calls[key] = unique_lists
        
    return function_calls