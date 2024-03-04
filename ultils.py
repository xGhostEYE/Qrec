import astor
import ast
import itertools
#Function to analyze code
def extract_data_flows(node):
    """
    Extract function calls and their line numbers, including the context leading up to those calls.
    """
    data_flows = {}

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
        
        # get arguments in a readable format
        call_args = [ast.unparse(arg) for arg in call_node.args]
        
        if call_object:
            call_repr = call_args + [func_name, call_object]
        else:
            call_repr = call_args + [func_name]

        lineno = call_node.lineno
        data_flows.setdefault((func_name, lineno), []).append(call_repr)
    
    def transform_dictionary_entries(d):
        transformed = {}
        for key, value in d.items():
            if all(len(item) == 1 for item in value):
                joined_str = ''.join(value)
                for char in ['.', '(', ')', ',']:
                    joined_str = joined_str.replace(char, ' ')
                words = list(filter(None, joined_str.split(' ')))
                transformed[key] = words
            else:
                transformed[key] = value
        return transformed

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
    
    # Remove duplicate lists
    for key, value in data_flows.items():
        unique_tuples = set(tuple(x) for x in value)
        unique_lists = [list(x) for x in unique_tuples]
        data_flows[key] = unique_lists[0] if len(unique_lists) == 1 else unique_lists

    return transform_dictionary_entries(data_flows)

def parse_functions_and_classes(filedirectory):
    with open(filedirectory, 'r') as file:
        tree = ast.parse(file.read())
    
    return extract_data_flows(tree)


def node_analyzer(node):
    arg_value = []

    for i in node:

        if isinstance(i, ast.Name):
            arg_value.append(i.id)
        elif isinstance(i, ast.Constant):
            arg_value.append(i.value)
        elif isinstance(i, ast.BinOp):

            if hasattr(i, 'left'):
                if hasattr(i.left, 'id'):
                    arg_value.append(i.left.id)

        elif isinstance(i, ast.BinOp):
            for ix in i.values:
                arg_value.append(node_analyzer([ix]))
        elif isinstance(i, ast.Attribute):

            xc = []
            calls = []

            def attr_collector(node):
                # print(astor.dump_tree(node))

                if hasattr(node, 'attr'):
                    calls.append(node.attr)
                    attr_collector(node.value)
                elif hasattr(node, 'id'):
                    calls.append(node.id)
                    # print(calls)
                return calls

            arg_value.append(attr_collector(i))
        elif isinstance(i, ast.GeneratorExp):

            if hasattr(i, 'elt'):
                if hasattr(i.elt, 'id'):
                    arg_value.append(i.elt.id)
                else:
                    arg_value.append(astor.dump_tree(i.elt))


        elif isinstance(i, ast.Subscript):
            arg_value.append(node_analyzer([i.value]))
        elif isinstance(i, ast.Dict):
            arg_value.append([node_analyzer(i.keys), node_analyzer(i.values)])

        elif isinstance(i, ast.IfExp):
            arg_value.append("IfExp")
        elif isinstance(i, ast.Compare):
            # print(astor.dump_tree(i.left))
            arg_value.append(node_analyzer([i.left]))

        elif isinstance(i, ast.Tuple):

            if hasattr(i, 'elts'):
                for ix in i.elts:
                    arg_value.append(node_analyzer([ix]))

        elif isinstance(i, ast.Call):
            # print(astor.dump_tree(gen_e.func))
            xc = []
            calls = []

            def attr_collector(node):
                # print(astor.dump_tree(node))

                if hasattr(node, 'attr'):
                    calls.append(node.attr)
                    attr_collector(node.value)
                elif hasattr(node, 'id'):
                    calls.append(node.id)
                    # print(calls)
                return calls

            # print("sss",attr_collector(i.func))
            arg_in = []
            for ip in i.args:
                # print(ip)
                arg_in.append(node_analyzer([ip]))
            # print()
            arg_value.append([attr_collector(i.func), arg_in])
        elif isinstance(i, ast.UnaryOp):
            arg_value.append(node_analyzer([i.operand]))
        elif isinstance(i, ast.List):
            if hasattr(i, 'elts'):
                elts_val = []
                for ii in i.elts:
                    if hasattr(ii, 'id'):
                        arg_value.append(node_analyzer([ii.id]))
                    elif hasattr(ii, 'value'):
                        arg_value.append(node_analyzer([ii.value]))
        elif isinstance(i, ast.keyword):
            arg_value.append([i.arg, node_analyzer([i.value])])
        elif isinstance(i, ast.Starred):

            arg_value.append(node_analyzer([i.value]))
        elif isinstance(i, ast.ListComp):
            if hasattr(i, 'elt'):
                if hasattr(i.elt, 'id'):
                    node_val = i.elt.id
                    arg_value.append(node_val)

            xc = []
            calls = []

            def attr_collector(node):
                # print(astor.dump_tree(node))

                if hasattr(node, 'attr'):
                    calls.append(node.attr)
                    attr_collector(node.value)
                elif hasattr(node, 'id'):
                    calls.append(node.id)
                    # print(calls)
                return calls

            arg_value.append(attr_collector(i))

        else:
            arg_value.append(i)
    return arg_value

def node_analyzer_variable(i):
    arg_value = []

    if isinstance(i, ast.Name):
        arg_value.append(i.id)
    elif isinstance(i, ast.Constant):
        arg_value.append(i.value)
    elif isinstance(i, ast.BinOp):

        if hasattr(i, 'left'):
            if hasattr(i.left, 'id'):
                arg_value.append(i.left.id)

    elif isinstance(i, ast.BinOp):
        for ix in i.values:
            arg_value.append(node_analyzer([ix]))
    elif isinstance(i, ast.Attribute):

        xc = []
        calls = []

        def attr_collector(node):
            # print(astor.dump_tree(node))

            if hasattr(node, 'attr'):
                calls.append(node.attr)
                attr_collector(node.value)
            elif hasattr(node, 'id'):
                calls.append(node.id)
                # print(calls)
            return calls

        arg_value.append(attr_collector(i))
    elif isinstance(i, ast.GeneratorExp):

        if hasattr(i, 'elt'):
            if hasattr(i.elt, 'id'):
                arg_value.append(i.elt.id)
            else:
                arg_value.append(astor.dump_tree(i.elt))


    elif isinstance(i, ast.Subscript):
        arg_value.append(node_analyzer([i.value]))
    elif isinstance(i, ast.Dict):
        arg_value.append([node_analyzer(i.keys), node_analyzer(i.values)])

    elif isinstance(i, ast.IfExp):
        arg_value.append("IfExp")
    elif isinstance(i, ast.Compare):
        # print(astor.dump_tree(i.left))
        arg_value.append(node_analyzer([i.left]))

    elif isinstance(i, ast.Tuple):

        if hasattr(i, 'elts'):
            for ix in i.elts:
                arg_value.append(node_analyzer([ix]))




    elif isinstance(i, ast.Call):
        # print(astor.dump_tree(gen_e.func))
        xc = []
        calls = []

        def attr_collector(node):
            # print(astor.dump_tree(node))

            if hasattr(node, 'attr'):
                calls.append(node.attr)
                attr_collector(node.value)
            elif hasattr(node, 'id'):
                calls.append(node.id)
                # print(calls)
            return calls

        # print("sss",attr_collector(i.func))
        arg_in = []
        for ip in i.args:
            # print(ip)
            arg_in.append(node_analyzer([ip]))
        # print()
        arg_value.append([attr_collector(i.func), arg_in])
    elif isinstance(i, ast.UnaryOp):
        arg_value.append(node_analyzer([i.operand]))
    elif isinstance(i, ast.List):
        if hasattr(i, 'elts'):
            elts_val = []
            for ii in i.elts:
                if hasattr(ii, 'id'):
                    arg_value.append(node_analyzer([ii.id]))
                elif hasattr(ii, 'value'):
                    arg_value.append(node_analyzer([ii.value]))

    elif isinstance(i, ast.keyword):
        arg_value.append([i.arg, node_analyzer([i.value])])
    elif isinstance(i, ast.Starred):

        arg_value.append(node_analyzer([i.value]))
    elif isinstance(i, ast.ListComp):
        if hasattr(i, 'elt'):
            if hasattr(i.elt, 'id'):
                node_val = i.elt.id
                arg_value.append(node_val)

        xc = []
        calls = []

        def attr_collector(node):
            # print(astor.dump_tree(node))

            if hasattr(node, 'attr'):
                calls.append(node.attr)
                attr_collector(node.value)
            elif hasattr(node, 'id'):
                calls.append(node.id)
                # print(calls)
            return calls

        arg_value.append(attr_collector(i))

    else:
        arg_value.append(i)

    return arg_value

def check_ast(node):
    match node:
        case ast.ClassDef():
            return "ClassDef"
        case ast.Module():
            return "Module"
        case ast.Interactive():
            return "Interactive"
        case ast.Expression():
            return "Expression"
        case ast.FunctionType():
            return "FunctionType"
        case ast.FunctionDef():
            return "FunctionDef"
        case ast.AsyncFunctionDef():
            return "AsyncFunctionDef"
        case ast.ExceptHandler():
            return "ExceptHandler"
        case ast.Return():
            return "Return"
        case ast.Delete():
            return "Delete"
        case ast.Assign():
            return "Assign"
        case ast.AugAssign():
            return "AugAssign"
        case ast.AnnAssign():
            return "AnnAssign"
        case ast.For():
            return "For"
        case ast.AsyncFor():
            return "AsyncFor"
        case ast.While():
            return "While"
        case ast.If():
            return "If"
        case ast.With():
            return "With"
        case ast.AsyncWith():
            return "AsyncWith"
        case ast.Raise(): 
            return "Raise"
        case ast.Try():
            return "Try"
        case ast.Assert():
            return "Assert"
        case ast.Import():
            return "Import"
        case ast.ImportFrom():
            return "ImportFrom"
        case ast.Global():
            return "Global"
        case ast.Nonlocal():
            return "Nonlocal"
        case ast.Expr():
            return "Expr"
        case ast.Pass():
            return "Pass" 
        case ast.Break():
            return "Break"
        case ast.Continue():
            return "Continue"
        case ast.BoolOp():
            return "BoolOp"
        case ast.NamedExpr():
            return "NamedExpr"
        case ast.BinOp():
            return "BinOp"
        case ast.UnaryOp():
            return "UnaryOp"
        case ast.Lambda():
            return "Lambda"
        case ast.IfExp():
            return "IfExp"
        case ast.Dict():
            return "Dict"
        case ast.Set():
            return "Set"
        case ast.ListComp():
            return "ListComp"
        case ast.SetComp():
            return "SetComp"
        case ast.DictComp():
            return "DictComp"
        case ast.GeneratorExp():
            return "GeneratorExp"
        case ast.Await():
            return "Await"
        case ast.Yield():
            return "Yield"
        case ast.YieldFrom():
            return "YieldFrom"
        case ast.Compare():
            return "Compare"
        case ast.Call():
            return "Call"
        case ast.FormattedValue():
            return "FormattedValue"
        case ast.JoinedStr():
            return "JoinedStr"
        case ast.Constant():
            return "Constant"
        case ast.Attribute():
            return "Attribute"
        case ast.Subscript():
            return "Subscript"
        case ast.Starred():
            return "Starred"
        case ast.Name():
            return "Name"
        case ast.List():
            return "List"
        case ast.Tuple():
            return "Tuple"
        case ast.Slice():
            return "Slice"