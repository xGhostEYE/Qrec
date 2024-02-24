import ast
import os
with open ("C:\\Users\\melvi\\Documents\\Coding\\USASK\\470\\parsetestfile.py", 'r') as file:
    for line in file:
        print(file.readline())

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

directory = r"C:\Users\melvi\Documents\Coding\USASK\470"
files = os.listdir(directory)
directoryPath = []

for file in files:
    file_path = os.path.join(directory, file)
    # print(file_path)
    directoryPath.append(file_path)
    
for path in directoryPath:
    try:

        # print(type(path))
        internal_folder = path.split('\\')[-1]
        class Traverser(ast.NodeTransformer):
            #Implementation goes here
            def visit_ClassDef(self, node):
                pass

            def visit_FunctionDef(self, node):
                pass

            def visit_for(self, node):
                pass
                
            def vist_try(self, node):
                pass
            pass
           
        from tqdm import tqdm

        dic_list = []

        for root, directories, files in tqdm(os.walk(path, topdown=False)):

            for name in files:
                file_path = (os.path.join(root, name))
                file_name = file_path

                if file_name.endswith(".py") or file_name.endswith(".pyi"):

                    try:
                        with open(file_path, encoding='utf-8') as f:
                            parentDict = {}
                            code = f.read()
                            node = ast.parse(code)

                            Traverser().visit(node)

                        dic_list.append([parentDict, file_name])


                    except Exception as e:
                        print(e.__traceback__.tb_lineno)
                        print(e.__traceback__)
                        unparser_def.append(file_name)
                    
                       
        break

    except Exception as e:
        print(e)
        print(e.__traceback__.tb_lineno)
        undefined_porjects.append(internal_folder)
        undefined_porjects_df = pd.DataFrame(undefined_porjects)
