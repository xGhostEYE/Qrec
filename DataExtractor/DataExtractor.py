import ast

#Function to analyze code
def extract_data_flows(node):
    """
    Extract function calls and their line numbers, including the context leading up to those calls.
    """
    data_flows = {}
    assign_name = ""
    assign_lines = []
    #helper function to process function/method calls
    def process_call(call_node):
        func_name = None
        call_object = None
        call_args = []
        
        if isinstance(call_node.func, ast.Attribute):
            func_name = call_node.func.attr
            call_object = ast.unparse(call_node.func.value)
        elif isinstance(call_node.func, ast.Name):
            func_name = call_node.func.id
        elif isinstance(node, ast.Call):
            process_call(node)
        
        # get arguments in a readable format
        call_args = [ast.unparse(arg) for arg in call_node.args]
        
        if call_object:
            call_repr = call_args + [func_name, call_object]
        else:
            call_repr = call_args + [func_name]

        lineno = call_node.lineno
        data_flows.setdefault((func_name, lineno), []).append(call_repr)
        

    for node in ast.walk(node):
        if isinstance(node, ast.Call):
            process_call(node)
        
        elif isinstance(node, ast.Assign):
            # Process assignment
            assign_name = ast.unparse(node.targets[0])
            assign_line = node.lineno
            assign_lines.append((assign_name, assign_line))
        elif isinstance(node, ast.For):
            # Word between 'for' and 'in'
            target = node.target.id
            assign_line = node.lineno
            assign_lines.append((target, assign_line))
    # clean the dictionary
    for key, value in data_flows.items():
        # remove duplicates
        unique_tuples = set(tuple(x) for x in value)
        unique_lists = [list(x) for x in unique_tuples]
        data_flows[key] = unique_lists[0] if len(unique_lists) == 1 else unique_lists
        # add variable names to the end of values
        for word, number in assign_lines:
            if key[1] == number:
                data_flows[key].append(word)

    assign_lines.clear()
    return data_flows

def parse_functions_and_classes(filedirectory):
    with open(filedirectory, 'r') as file:
        tree = ast.parse(file.read())
    
    return extract_data_flows(tree)