import os
import re
import sys
from pytype.tools import traces 
import textwrap
import ast
from pytype import config
from pytype.tools.annotate_ast import annotate_ast

                                
def CandidatesGenerator ( file, methodsDict ):

    
    for key,value in methodsDict:
        
        #get the object
        objectOfTargetAPI = getObject(key,value)

        #perform type inference
        type_dict = get_inferred_type_dynamic(file)
        print (type_dict)
        
        #get list of calls in the type inference


def getObject(key,value):
    pass


#The implementation is inspired by get_type that is used in PyART. 
def get_inferred_type_static(source,filePath):

	lindex=filePath.rfind('/')
	tmp=filePath[:lindex]+'/tmp.py'

	with open(tmp,'w+') as f:
		f.write(source.read())

	try:
		os.system('pytype '+tmp+' > log.txt')
	except Exception:
		sys.exit()
	with open('log.txt') as f:
		lines=f.readlines()
	vtype='None'
	for line in lines:
		if '[reveal-type]' in line:
			tp=line.split(':')[1]
			vtype=re.sub('\[reveal\-type\]','',tp)
			break

	return vtype

#Getting the type dynamically for experiment purpose
def get_inferred_type_dynamic(source):

    def get_annotations_dict(tree, module):
        moduleDict = {get_module_node_key(node): node.resolved_annotation
            for node in ast.walk(module)
            if hasattr(node, 'resolved_type')}
        
        treeObjectDict={}
        for nodetree in ast.walk(tree):
            item = get_tree_node_key(nodetree)
            if item is not None:
                 treeObjectDict[item[0]] = item[1]
        #  = {get_tree_node_key(nodetree): get_tree_node_key(nodetree)[1]
        #     for nodetree in ast.walk(tree)}
        
        object_and_type_dict = {}
        for key,value in moduleDict.items():           
            line = key[0]
            id = key[2]
            treeObjectValue = treeObjectDict.get(id)
            if treeObjectValue is not None:
                if treeObjectValue == line:
                    object_and_type_dict[id] = value
       
        print(object_and_type_dict)            
        return object_and_type_dict

    def get_module_node_key(node):
        base = (node.lineno, node.__class__.__name__)
        if isinstance(node, ast.Name):
            return base + (node.id,)
        if isinstance(node, ast.Attribute):

            return base + (node.attr,)
        elif isinstance(node, ast.FunctionDef):
            return base + (node.name,)
        else:
            return base
        
    def get_tree_node_key(node):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            return (ast.unparse(node.func.value), node.lineno)
	
    
    source = source.read()   
    source = textwrap.dedent(source.lstrip('\n'))
    ast_factory = ast
    pytype_options = config.Options.create()
    module = annotate_ast.annotate_source(source, ast_factory, pytype_options)
    annotations_dict = get_annotations_dict(ast.parse(source), module)
    print(annotations_dict)
    return module

# with open(" /Volumes/Transcend/Julian-Transcend/GithubRepo/QrecProject/Test/passpdf.py", encoding='utf-8') as file:
      
#     print(CandidatesGenerator(file))
