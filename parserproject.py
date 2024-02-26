import ast
import os
    
directory = r"/Volumes/Transcend/Julian-Transcend/GithubRepo/QrecProject/Test"
files = os.listdir(directory)
directoryPath = []
undefined_projects = []

for file in files:
    file_path = os.path.join(directory, file)
    # print(file_path)
    directoryPath.append(file_path)
    
for path in directoryPath:
    try:
        # print(type(path))
        internal_folder = path.split('/')[-1]
        unparser_def = []

        class Traverser(ast.NodeTransformer):
            #Implementation goes here
            # def visit_ClassDef(self, node):
            #     pass

            # def visit_FunctionDef(self, node):
            #     pass

            # def visit_for(self, node):
            #     pass
                
            # def vist_try(self, node):
            #     pass
            # pass
            def visit_Call(self, node):
                print("Print line number")
                print(node.lineno)

                self.generic_visit(node)


           
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
        undefined_projects.append(internal_folder)
