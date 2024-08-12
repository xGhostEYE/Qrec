import astor
import ast
import os
import DataExtractor.FeatureCollector as fc
import DataExtractor.CandidateGenerator as cg
import DataEncoder.DataEncoder as de
# from GetFiles import GetFilesInDirectory

def analyze_directory(directory):
    files = os.listdir(directory)
    # files = GetFilesInDirectory()
    directoryPath = []
    undefined_projects = []
    data_dict = {}
    file_dict = {}
    token_count_dict = {}
    for file in files:
        file_path = os.path.join(directory, file)
        directoryPath.append(file_path)
    
    for path in directoryPath:
        
        try:
            internal_folder = path.split('/')[-1]
            unparser_def = []
            # os.walk NEEDS a subdirectory in the directory that it's walking for it to work.
            # meaning that it needs 2 layers of folders to work

            for root, directories, files in os.walk(path, topdown=False):
                for name in files:
                    file_path = (os.path.join(root, name))
                    
                    if file_path.endswith(".py") or file_path.endswith(".pyi"):
                        
                        #Key: file_name
                        #Value: bag of tokens (a dictionary)
                            #Key: line number
                            #Value: list of tokens from left to right 
                        with open(file_path, encoding='utf-8') as file:
                            file_dict[file_path] = fc.extract_bag_of_tokens(file)

            for root, directories, files in os.walk(path, topdown=False):
                print("executing project: ", root)
                for name in files:
                    
                    file_path = (os.path.join(root, name))
                    file_name = file_path
                    
                    if file_name.endswith(".py") or file_name.endswith(".pyi"):

                        try:
                            with open(file_path, encoding='utf-8') as file:
                                method_dict = fc.extract_data(file)

                            with open(file_path, encoding='utf-8') as file:
                                candidate_dict = cg.CandidatesGenerator(file, file_path, method_dict)
                            
                            #Format of data_dict:
                            # #Key = [object, api, line number, 0 if it is not true api and 1 otherwise]
                            # #Value = [x1,x2,x3,x4]
                            data_dict.update(de.DataEncoder(method_dict,candidate_dict, file_dict, file_path, token_count_dict))
                            

                        except Exception as e:
                            print(e)
                            unparser_def.append(file_name)
                                                                
        except Exception as e:
            print(e)
            print(e.__traceback__.tb_lineno)
            undefined_projects.append(internal_folder)
    return data_dict
    
        
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
