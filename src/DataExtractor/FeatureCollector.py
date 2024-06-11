import ast
import sys
def extract_data_flows(node):
    """
    Extract function calls and their line numbers, including the context leading up to those calls.
    """
    data_flows = {}
    assign_name = ""
    assign_lines = []

    def process_call(call_node):
        func_name = None
        call_object = None
        call_args = []
        method_name = None
        if isinstance(call_node.func, ast.Attribute):
            func_name = call_node.func.attr
            if isinstance(call_node.func.value, ast.Name):
                method_name = call_node.func.value.id
                call_object = method_name
            elif isinstance(call_node.func.value, ast.Subscript):
                call_object = ast.unparse(call_node.func.value)  # correctly parse the Subscript object
                # Avoid accessing .id on Subscript; handle it separately or leave method_name as None if not applicable
            else:
                call_object = ast.unparse(call_node.func.value)  # handle other types like Member or Call etc.
        elif isinstance(call_node.func, ast.Name):
            func_name = call_node.func.id

        call_args = [ast.unparse(arg) for arg in call_node.args]
        if call_object:
            call_repr = call_args + [func_name, call_object]
        else:
            call_repr = call_args + [func_name]
        
        lineno = call_node.lineno
        data_flows.setdefault((method_name, func_name, lineno), []).append(call_repr)
        


        # extract identifiers from an assignment target.
    def get_identifiers_from_target(target):
        if isinstance(target, ast.Name):
            return [target.id]
        elif isinstance(target, (ast.Tuple, ast.List)):
            identifiers = []
            for element in target.elts:
                identifiers.extend(get_identifiers_from_target(element))
            return identifiers
        return []

    for node in ast.walk(node):
        if isinstance(node, ast.Call):
            process_call(node)

        elif isinstance(node, ast.Assign):
            # Process assignment
            assign_name = ast.unparse(node.targets[0])
            assign_line = node.lineno
            assign_lines.append((assign_name, assign_line))

        elif isinstance(node, ast.For):
            # Handle complex 'for' targets
            targets = get_identifiers_from_target(node.target)
            assign_line = node.lineno
            for target in targets:
                assign_lines.append((target, assign_line))

    for node in ast.walk(node):

        if isinstance(node, ast.Call):
            process_call(node)
        
        elif isinstance(node, ast.Assign):
            # process assignment
            assign_name = ast.unparse(node.targets[0])
            assign_line = node.lineno
            assign_lines.append((assign_name, assign_line))
        elif isinstance(node, ast.For):
            # extract identifiers from the target of the 'for' loop
            targets = get_identifiers_from_target(node.target)
            assign_line = node.lineno
            for target in targets:
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

def extract_data(rawfile):
    """
    dictionary format:
        key:[method name, function name, line number]
            - method name would be foo in this case (foo.bar())
            - method name would be bar in the above example
            - line number for the line the code is at
        value:[follows the data flow]
        
        
    
    """
    tree = ast.parse(rawfile.read())
    dataflows = extract_data_flows(tree)
    for key, value in dataflows.items():
        
        print("key: ",key, "\nvalue: ",value)
        
        #TODO: check for comments and skip them!!!!
        new_values = []
        for words in value:
            if isinstance(words, list):
                for word in words:
                    new_values.append(word)
            else:
                new_values.append(words)
        value = new_values
                    
        value.reverse()
        new_words = []
        more_words = []
        for words in value:
            if words.count('\'') == 2 and words.count('\"') == 0:
                new_words.append(words)
                continue
            new_words.extend(words.split('.'))
        for words in new_words:
            more_words.extend(words.split('('))

        new_words.clear()
        for words in more_words:
            new_words.extend(words.split(','))
        for words in new_words:
            if ')' in words:
                words.replace(')', "")
        dataflows[key] = new_words
    sys.exit()
    return dataflows

