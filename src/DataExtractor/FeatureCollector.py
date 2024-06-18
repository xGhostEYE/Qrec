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
        
        # print("key: ",key, "\nvalue: ",value)
        
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
    exception_star_nodes = []
    vararg_arg_nodes = []
    kwarg_arg_nodes = []

    
    list_args_in_arg=[]

    class MyVisitor (ast.NodeVisitor):        
        #Try-Catch
        def visit_Try(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["try"]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_TryStar(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["try"]

            for exception_node in node.handlers:
                exception_star_nodes.append(exception_node)

            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_ExceptHandler(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            
            new_tokens = ["except"]
            if node in exception_star_nodes:
                new_tokens = ['except*']

            if(list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens

            super().generic_visit(node)

        #Keyword 
        def visit_keyword(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = [node.arg]
            if (list_of_tokens):
                if (node in list_of_tokens):
                    index = list_of_tokens.index(node)
                    list_of_tokens[index] = node.arg
                else:
                    list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        #If exp
        def visit_IfExp(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            
            new_tokens = [node.body, "if", node.test, "else", node.orelse]

            if (list_of_tokens):
                if (node in list_of_tokens):
                    index = list_of_tokens.index(node)
                    list_of_tokens[index] = node.arg
                else:
                    list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        #Attribute
        def visit_Attribute(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            
            new_nodes = [node.value, node.attr]

            if (list_of_tokens):
                if (node in list_of_tokens):
                    index = list_of_tokens.index(node)
                    bag_of_tokens[node.lineno] = list_of_tokens[0:index] + new_nodes + list_of_tokens[index+1:]
                else:
                    list_of_tokens.extend(new_nodes)
            else:
                bag_of_tokens[node.lineno] = new_nodes
            super().generic_visit(node)

        # Function 

        # def visit_FunctionType(self,node): - TODO, test with more cases for FunctionType
        #     junk_nodes_lineno.append(node.lineno)
        #     super().generic_visit(node)

        def visit_Lambda(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None

            new_tokens = ["lambda"]

            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens

            super().generic_visit(node)
            list_args_in_arg.clear()

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

        def visit_AsyncFunctionDef(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None

            #Collecting junk tokens:
            for token_node in node.decorator_list:
                junk_tokens.append(token_node)
            
            #Collecting useful tokens:
            new_tokens = ["async" , "def", node.name]

            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)
            list_args_in_arg.clear()
        
        def visit_Await(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None

            #Collecting junk tokens:
            for token_node in node.decorator_list:
                junk_tokens.append(token_node)
            
            #Collecting useful tokens:
            new_tokens = ["await"]

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

            #Get regular args
            #Going backward in forloop because according to docs:
            #If there are fewer defaults, they correspond to the last n arguments.
            for i in range (-1, 0-len(node.args)-1, -1):
                if (-i <= len(node.defaults)):
                    new_nodes.insert(0,node.defaults[i])
                new_nodes.insert(0,node.args[i])
            
            #Get var arg
            vararg = node.vararg
            if (vararg):
                vararg_arg_nodes.append(vararg)
                new_nodes.append(vararg)

            #Get keyword-only arg
            for i in range (0, len(node.kwonlyargs)):
                new_nodes.append(node.kwonlyargs[i])
                if (node.kw_defaults[i] != None):
                    new_nodes.append(node.kw_defaults[i])

            #Get keyword arg            
            kwarg = node.kwarg
            if (kwarg):
                kwarg_arg_nodes.append(kwarg)
                new_nodes.append(kwarg)


            if (list_of_tokens):
                list_of_tokens.extend(new_nodes)
            else:
                bag_of_tokens[line_of_function] = new_nodes
            super().generic_visit(node)
        
        def visit_Return(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["return"]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_Yield(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["yield"]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_YieldFrom(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["yield" ,"from"]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
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

        #Control-flow
        def visit_Continue(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["continue"]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_Break(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["break"]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_If(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["if"]
            
            if (list_of_tokens):
                if (list_of_tokens[-1] == "else"):
                    list_of_tokens[-1] = "elif"
                else:
                    list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens

            #Getting the else token in for-loop statement if it exists
            if (node.orelse):
                end_of_body_lineno = 0
                for the_node in node.body:
                    end_of_body_lineno = the_node.end_lineno

                else_lineno = end_of_body_lineno + 1

                list_of_tokens = bag_of_tokens[else_lineno] if else_lineno in bag_of_tokens else None
                new_tokens = ["else"]
                if (list_of_tokens):
                    list_of_tokens.extend(new_tokens)
                else:
                    bag_of_tokens[else_lineno] = new_tokens
            super().generic_visit(node)

        def visit_With(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["with"]

            for node_WITH in node.items:
                new_tokens.append(node_WITH)

            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_AsyncWith(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["async with"]

            for node_WITH in node.items:
                new_tokens.append(node_WITH)

            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)


        def visit_withitem(self, node):
            last_key = list(bag_of_tokens.keys())[-1]
            list_of_tokens = bag_of_tokens[last_key] if last_key in bag_of_tokens else None
                       
            if(list_of_tokens and node in list_of_tokens):
                index = list_of_tokens.index(node)
                context_expr = node.context_expr
                optional_vars = node.optional_vars
                        
                if optional_vars:
                    list_of_tokens[index] = optional_vars
                    list_of_tokens.insert(index, context_expr)
                else:
                    list_of_tokens[index] = context_expr

            super().generic_visit(node)
        
        def visit_While(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["while"]
            
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens

            #Getting the else token in for-loop statement if it exists
            if (node.orelse):
                end_of_body_lineno = 0
                for the_node in node.body:
                    end_of_body_lineno = the_node.end_lineno

                else_lineno = end_of_body_lineno + 1

                list_of_tokens = bag_of_tokens[else_lineno] if else_lineno in bag_of_tokens else None
                new_tokens = ["else"]
                if (list_of_tokens):
                    list_of_tokens.extend(new_tokens)
                else:
                    bag_of_tokens[else_lineno] = new_tokens
            super().generic_visit(node)

        def visit_For(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["for", node.target, "in", node.iter]
            
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens

            #Getting the else token in for-loop statement if it exists
            if (node.orelse):
                end_of_body_lineno = 0
                for the_node in node.body:
                    end_of_body_lineno = the_node.end_lineno

                else_lineno = end_of_body_lineno + 1

                list_of_tokens = bag_of_tokens[else_lineno] if else_lineno in bag_of_tokens else None
                new_tokens = ["else"]
                if (list_of_tokens):
                    list_of_tokens.extend(new_tokens)
                else:
                    bag_of_tokens[else_lineno] = new_tokens
            super().generic_visit(node)
        
        def visit_AsyncFor(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["async","for", node.target, "in", node.iter]
            
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens

            #Getting the else token in for-loop statement if it exists
            if (node.orelse):
                end_of_body_lineno = 0
                for the_node in node.body:
                    end_of_body_lineno = the_node.end_lineno

                else_lineno = end_of_body_lineno + 1

                list_of_tokens = bag_of_tokens[else_lineno] if else_lineno in bag_of_tokens else None
                new_tokens = ["else"]
                if (list_of_tokens):
                    list_of_tokens.extend(new_tokens)
                else:
                    bag_of_tokens[else_lineno] = new_tokens

            super().generic_visit(node)
        #Call statement
        def visit_Call(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None

            new_nodes = [node.func]

            #Get regular args

            new_nodes.extend(node.args) 
            new_nodes.extend(node.keywords)
            
            if (list_of_tokens):
                if node in list_of_tokens:
                    index = list_of_tokens.index(node)
                    bag_of_tokens[node.lineno] = list_of_tokens[0:index] + new_nodes +list_of_tokens[index+1:]
                else:
                    list_of_tokens.extend(new_nodes)
            else:
                bag_of_tokens[node.lineno] = new_nodes
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
            if ( (node not in junk_tokens)):  
                # or not node.lineno in junk_nodes_lineno):
                
                if (list_of_tokens):
                    if list_of_tokens[-1] == "*":
                        list_of_tokens[-1] = list_of_tokens[-1] + node.id
                    else:
                        if (node in list_of_tokens):
                            index = list_of_tokens.index(node)
                            list_of_tokens[index] = node.id
                        
                        else:
                            list_of_tokens.extend(new_tokens)
                else:
                    bag_of_tokens[node.lineno] = new_tokens

            super().generic_visit(node)

        def visit_Starred(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ['*']
            if (list_of_tokens):
                if (node in list_of_tokens):
                    index = list_of_tokens.index(node)
                    list_of_tokens[index] = "*"
                else:
                    list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)
        
        def visit_Constant(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            
            name = node.value
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

        def visit_Global(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["global"]
            for name in node.names:
                new_tokens.append(name)

            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_Nonlocal(self, node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["nonlocal"]
            for name in node.names:
                new_tokens.append(name)

            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        #Statement-type
        def visit_Raise(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["raise", node.exc, "from", node.cause]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_Del(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["del"]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_Raise(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["raise", node.exc, "from", node.cause]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_Assert(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["assert", node.test, "from", node.msg]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_Pass(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
            new_tokens = ["pass"]
            if (list_of_tokens):
                list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        #Expression 
        def visit_BoolOp(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None

            boolean_operation = "or" if isinstance(node.op, ast.Or) else "and"
            new_tokens = []
            for value in node.values:
                if (len(new_tokens) != 0):
                    new_tokens.append(boolean_operation)
                new_tokens.append(value)
                
                
            if (list_of_tokens):
                if (node in list_of_tokens):
                    index = list_of_tokens.index(node)
                    bag_of_tokens[node.lineno] = list_of_tokens[0:index] + new_tokens + list_of_tokens[index+1:]
                else:
                    list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_UnaryOp(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None

            new_tokens = ["not",node.operand]

            if (list_of_tokens):
                if (node in list_of_tokens):
                    index = list_of_tokens.index(node)
                    bag_of_tokens[node.lineno] = list_of_tokens[0:index] + new_tokens + list_of_tokens[index+1:]
                else:
                    list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)
        
        #Literals
        def visit_Dict(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None

            new_tokens = []
            for i in range (len(node.keys)):

                if (node.keys[i]):
                    new_tokens.append(node.keys[i])

                new_tokens.append(node.values[i])
                
            if (list_of_tokens):
                if (node in list_of_tokens):
                    index = list_of_tokens.index(node)
                    bag_of_tokens[node.lineno] = list_of_tokens[0:index] + new_tokens + list_of_tokens[index+1:]
                else:
                    list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_Set(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None

            new_tokens = []
            for the_node in node.elts:
                new_tokens.append(the_node)
                
            if (list_of_tokens):
                if (node in list_of_tokens):
                    index = list_of_tokens.index(node)
                    bag_of_tokens[node.lineno] = list_of_tokens[0:index] + new_tokens + list_of_tokens[index+1:]
                else:
                    list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_Tuple(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None

            new_tokens = []
            for the_node in node.elts:
                new_tokens.append(the_node)
                
            if (list_of_tokens):
                if (node in list_of_tokens):
                    index = list_of_tokens.index(node)
                    bag_of_tokens[node.lineno] = list_of_tokens[0:index] + new_tokens + list_of_tokens[index+1:]
                else:
                    list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        def visit_List(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None

            new_tokens = []
            for the_node in node.elts:
                new_tokens.append(the_node)
                
            if (list_of_tokens):
                if (node in list_of_tokens):
                    index = list_of_tokens.index(node)
                    bag_of_tokens[node.lineno] = list_of_tokens[0:index] + new_tokens + list_of_tokens[index+1:]
                else:
                    list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens
            super().generic_visit(node)

        #Subscripting
        def visit_Subscript(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None

            new_tokens = [node.value, node.slice]

                
            if (list_of_tokens):
                if (node in list_of_tokens):
                    index = list_of_tokens.index(node)
                    bag_of_tokens[node.lineno] = list_of_tokens[0:index] + new_tokens + list_of_tokens[index+1:]
                else:
                    list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens

            super().generic_visit(node)

        def visit_Slice(self,node):
            list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None

            new_tokens = [node.lower, node.upper]

                
            if (list_of_tokens):
                if (node in list_of_tokens):
                    index = list_of_tokens.index(node)
                    bag_of_tokens[node.lineno] = list_of_tokens[0:index] + new_tokens + list_of_tokens[index+1:]
                else:
                    list_of_tokens.extend(new_tokens)
            else:
                bag_of_tokens[node.lineno] = new_tokens

            super().generic_visit(node)
        

        #generic visit to catch token types that have not been implemented
        #TODO - ast.ListComp(); ast.SetComp(); ast.DictComp(); 
        #TODO - ast.GeneratorExp(); ast.FormattedValue(); ast.JoinedStr(); Match
        def generic_visit(self, node):
            
            try: 
                list_of_tokens = bag_of_tokens[node.lineno] if node.lineno in bag_of_tokens else None
                
                #Remove node that has not been implemented in visitor pattern to avoid error
                if list_of_tokens and node in list_of_tokens:
                    index = list_of_tokens.index(node)
                    del list_of_tokens[index]
            except AttributeError:
                pass
                
            super().generic_visit(node)
        
    tree = ast.parse(file.read())
    visitor = MyVisitor()
    visitor.visit(tree)
    return bag_of_tokens
    
    
    
    



