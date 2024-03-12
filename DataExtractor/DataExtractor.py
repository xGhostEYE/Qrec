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
        method_name = None
        if isinstance(call_node.func, ast.Attribute):
            func_name = call_node.func.attr
            method_name = call_node.func.value.id
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
        data_flows.setdefault((method_name, func_name, lineno), []).append(call_repr)
        
    
    # def transform_dictionary_entries(d):
    #     transformed = {}
    #     for key, value in d.items():
    #         if all(len(item) == 1 for item in value):
    #             joined_str = ''.join(value)
    #             for char in ['.', '(', ')', ',']:
    #                 joined_str = joined_str.replace(char, ' ')
    #             words = list(filter(None, joined_str.split(' ')))
    #             transformed[key] = words
    #         else:
    #             transformed[key] = value
    #     return transformed

    for node in ast.walk(node):

        # if isinstance(node, ast.For):
        #     # Process for loop
        #     iter_source = ast.unparse(node.iter)
        #     loop_var = ast.unparse(node.target)
        #     # Ensure iterable is a list
        #     iter_list = [iter_source] if isinstance(iter_source, str) else list(iter_source)
        #     data_flows.setdefault((loop_var, node.lineno), []).extend(iter_list)

        # elif isinstance(node, ast.Assign):
        #     # Process assignment
        #     target = ast.unparse(node.targets[0])
        #     value = ast.unparse(node.value)

        #     # Ensure value is a list
        #     value_list = [value] if isinstance(value, str) else list(value)
        #     data_flows.setdefault((target, node.lineno), []).extend(value_list)

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

def extract_data(filedirectory):
    with open(filedirectory, 'r') as file:
        tree = ast.parse(file.read())
    dataflows = extract_data_flows(tree)
    for key, value in dataflows.items():
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
    
    return dataflows