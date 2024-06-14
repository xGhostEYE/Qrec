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
        data_flows.setdefault((method_name, func_name, lineno), []).extend(call_repr)
        


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

    # for node in ast.walk(node):

    #     if isinstance(node, ast.Call):
    #         process_call(node)
        
    #     elif isinstance(node, ast.Assign):
    #         # process assignment
    #         assign_name = ast.unparse(node.targets[0])
    #         assign_line = node.lineno
    #         assign_lines.append((assign_name, assign_line))
    #     elif isinstance(node, ast.For):
    #         # extract identifiers from the target of the 'for' loop
    #         targets = get_identifiers_from_target(node.target)
    #         assign_line = node.lineno
    #         for target in targets:
    #             assign_lines.append((target, assign_line))

    # clean the dictionary
    for key, value in data_flows.items():
        # # remove duplicates
        # unique_tuples = set(tuple(x) for x in value)
        # unique_lists = [list(x) for x in unique_tuples]
        # data_flows[key] = unique_lists[0] if len(unique_lists) == 1 else unique_lists
        # add variable names to the end of values
        for token, line_number in assign_lines:
            if key[2] == line_number:
                data_flows[key].append(token)
    
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

def extract_bag_of_tokens(file):
    """
    dictionary format:
        key: line number
        value:[list of tokens from left to right]  
    """
    bag_of_tokens = {}
    junk_tokens = []
    junk_nodes_lineno = []
    vararg_arg_nodes = []
    kwarg_arg_nodes = []
    
    list_args_in_arg=[]

    class MyVisitor (ast.NodeVisitor):
        #Keyword 
        def visit_keyword(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = [node.arg]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        # Function - TODO, test with more cases for FunctionType

        # def visit_FunctionType(self,node):
        #     junk_nodes_lineno.append(node.lineno)
        #     super().generic_visit(node)

        def visit_FunctionDef(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None

            #Collecting junk tokens:
            for token_node in node.decorator_list:
                junk_tokens.append(token_node)
            
            #Collecting useful tokens:
            new_tokens = ["def", node.name]

            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)
            list_args_in_arg.clear()

        def visit_arg(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            
            name = node.arg
            if node in vararg_arg_nodes:
                name = "*"+node.arg
            elif node in kwarg_arg_nodes:
                name = "**"+node.arg if node in kwarg_arg_nodes else node.arg
            
            new_tokens = [name]
            if(list_of_tokens):
                if (node in list_of_tokens):
                        index = list_of_tokens.index(node)
                        list_of_tokens[index] = name
                else:
                    list_of_tokens.extend(new_tokens)

            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)
        
        def visit_arguments(self, node):
            line_of_function = list(bag_of_tokens)[-1]
            list_of_tokens = bag_of_tokens[line_of_function] if line_of_function in bag_of_tokens else None
            new_nodes = []

            # stop = 0-len(node.args) if len(node.args) != 0 else -1
            for i in range (-1, 0-len(node.args)-1, -1):
                if (-i <= len(node.defaults)):
                    new_nodes.insert(0,node.defaults[i])
                new_nodes.insert(0,node.args[i])
                
            vararg = node.vararg
            if (vararg):
                vararg_arg_nodes.append(vararg)
            
            kwarg = node.kwarg
            if (kwarg):
                kwarg_arg_nodes.append(kwarg)


            if (list_of_tokens):
                list_of_tokens.extend(new_nodes)
            else:
                bag_of_tokens[line_of_function] = new_nodes
            super().generic_visit(node)

        #Class 
        def visit_ClassDef(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None

            #Collecting junk tokens:
            for token_node in node.decorator_list:
                junk_tokens.append(token_node)
            
            #Collecting useful tokens:
            new_tokens = ["Class", node.name]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)
        
        #Import statement
        def visit_ImportFrom(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["from", node.module, "import"]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_Import(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["import"]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)
        
        def visit_alias(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = [node.name]
            if (node.asname):
                new_tokens.extend(["as", node.asname])
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        #Variable
        def visit_Name(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = [node.id]

            #Check if junk
            if ( (node not in junk_tokens)  
                or not node.lineno in junk_nodes_lineno):
                
                if (list_of_tokens):
                    if list_of_tokens[-1] == "*":
                        list_of_tokens[-1] = list_of_tokens[-1] + node.id
                    else:
                        list_of_tokens.extend(new_tokens)
                else:
                    bag_of_tokens[node.lineno] = new_tokens

            super().generic_visit(node)

        def visit_Starred(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ['*']
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)
            
            
        def generic_visit(self, node):
            # print(node)
            super().generic_visit(node)

    tree = ast.parse(file.read())
    visitor = MyVisitor()
    visitor.visit(tree)
    print(bag_of_tokens)
