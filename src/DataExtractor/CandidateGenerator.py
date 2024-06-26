import importlib
import os
import re
import sys
from pytype.tools import traces 
import textwrap
import ast
from pytype import config
from pytype.tools.annotate_ast import annotate_ast

# stdlib=['string','re','difflib','textwrap','unicodedata','stringprep','readline','rlcompleter',
# 'struct','codecs','datetime','calendar','collections','collections.abc','heapq','bisect',
# 'array','weakref','types','copy','pprint','reprlib','enum','numbers','math','cmath',
# 'decimal','fractions','random','statistics','itertools','functools','operator','pathlib',
# 'os.path','fileinput','stat','filecmp','tempfile','glob','fnmatch','linecache','shutil',
# 'pickle','copyreg','shelve','marshal','dbm','sqlite3','zlib','gzip','bz2','lzma','zipfile',
# 'tarfile','csv','configparser','netrc','xdrlib','plistlib','hashlib','hmac','secrets',
# 'os','io','time','argparse','getopt','logging','logging.config','logging.handlers',
# 'getpass','curses','curses.textpad','curses.ascii','curses.panel','platform','errno',
# 'ctypes','threading','multiprocessing','multiprocessing.shared_memory','concurrent',
# 'concurrent.futures','subprocess','sched','queue','_thread',
# 'contextvars','asyncio','socket','ssl','select','selectors','asyncore','asynchat','signal',
# 'mmap','email','json','mailcap','mailbox','mimetypes','base64','binascii',
# 'quopri','uu','html','html.parser','html.entities','xml','webbrowser','xml.etree.ElementTree',
# 'xml.dom','xml.dom.minidom','xml.dom.pulldom','xml.sax','xml.sax.handler','xml.sax.saxutils',
# 'xml.sax.xmlreader','xml.parsers.expat','cgi','cgitb','wsgiref','urllib','urllib.request',
# 'urllib.response','urllib.parse','urllib.error','urllib.robotparser','http','http.client',
# 'ftplib','poplib','imaplib','nntplib','smtplib','smtpd','telnetlib','uuid','socketserver',
# 'http.server','http.cookies','http.cookiejar','xmlrpc','xmlrpc.client','xmlrpc.server',
# 'ipaddress','audioop','aifc','sunau','wave','chunk','colorsys','imghdr','sndhdr','ossaudiodev',
# 'gettext','locale','turtle','cmd','shlex','tkinter','tkinter.ttk','tkinter.tix','tkinter.scrolledtext',
# 'typing','pydoc','doctest','unittest','unittest.mock','unittest.mock','test','test.support',
# 'test.support.script_helper','bdb','faulthandler','pdb','timeit','trace','tracemalloc','distutils',
# 'ensurepip','venv','zipapp','sys','sysconfig','builtins','__main__','warnings','dataclasses',
# 'contextlib','abc','atexit','traceback','__future__','gc','inspect','site','code','codeop','zipimport',
# 'pkgutil','modulefinder','runpy','importlib','ast','symtable','symbol','token','keyword',
# 'tokenize','tabnanny','pyclbr','py_compile','compileall','dis','pickletools','formatter','msilib',
# 'msvcrt','winreg','winsound','posix','pwd','spwd','grp','crypt','termios','tty','pty','fcntl','pipes',
# 'resource','nis','optparse','imp', 'tuple', 'list', 'dict']
stdlib = list(sys.stdlib_module_names)

#TODO - doc
#method_dict format: {(object, api, linenumber): [variables and methods in order of data flow]}                               
#A recommendation point is an API call
def CandidatesGenerator ( file, file_path, method_dict):

    #perform type inference
    #types_dict format: {target object: target object type}
    raw_file = file.read()

    types_dict = get_inferred_type_dynamic(raw_file)
    default_calls = get_calls_from_others(file_path)
    API_candidates_for_object = {} 
    for key in method_dict.keys():
        the_object = key[0]
        if the_object != None:
            type = None
            try:
                type = types_dict[the_object]
            except KeyError as e:
                pass
            #get list of calls in the type inference
            calls = get_calls(the_object,type)
            if ( len(calls) == 0):
                calls = default_calls
            line_number = key[2]
            API_candidates_key = (the_object, line_number )
            API_candidates_for_object[API_candidates_key] = calls
    
    #Check if we get the correct dict
    # for key,value in API_candidates_for_object.items():
    #     print(key, len(value))
                
    return API_candidates_for_object
        
        
def get_calls(object, type):
    calls = []
    if (type != None and type != "None" and type != "Any"):
        for call in get_calls_from_valid_type(object, type):
            if call.startswith('__') or re.match('[A-Z0-9_]+$',call) or call.strip()=='_':
                continue
            calls.append(call)
    return calls   
    
def get_calls_from_valid_type(object,the_type):
    calls = []
    if (the_type == 'module'):
        #object is a string. We need to convert it into a class object
        module = importlib.import_module(object)
        #if object is type "module" then we can just get the calls straight from the object
        return dir(module)
    try:
        #importlib.import_module returns a module of name "str" for type str.
        #We explicitly implement this case
        if (the_type != "str"):
            module = importlib.import_module(the_type)
        else:
            module = the_type
        calls = calls + dir(module)
    
    except Exception as error_1:
        print(error_1)
        print("Proceed to install potential missing modules")
        try:
            if '.' in the_type:
                rootmodule = the_type[: type.find('.')]
                os.system("pip3 install " + rootmodule)
            else:
                os.system("pip3 install " + the_type)
            #Usually the naming format of a type is capitalized. We need to do lowercase on them
            lower = the_type.lower()
            module = importlib.import_module(lower)
            calls = calls + dir(module)
        except Exception as error_2:
            print(error_2)
            print("Returning empty list of calls for type: " + the_type + " due to exception")
            calls = []
    return calls

#Return calls from:
#1. standard libraries, 
#2. imported third-party libraries
#3. all the callable methods declared in the current scope
def get_calls_from_others(file_path):
    refined_calls = []
    calls = get_calls_from_standard_libs() + get_calls_from_third_party_libs(file_path) + get_calls_from_scope(file_path)
    for call in calls:
        if call.startswith('__') or re.match('[A-Z0-9_]+$',call) or call.strip()=='_':
            continue
        refined_calls.append(call)
    return refined_calls

def get_calls_from_standard_libs():
    calls = []
    for lib in stdlib:
        
        try:
            module = importlib.import_module(lib)           
            calls = calls + dir(module)
        except Exception as e:
            try:
                module = eval(lib)           
                calls = calls + dir(module)
            #Continue to the extract the methods of the next module in the list if there is an exception.
            except Exception as e:
                continue

    return calls
         

def get_calls_from_third_party_libs(file_path):
    def get_imports(file_path):
        with open(file_path) as file:        
            tree = ast.parse(file.read())
        
        #format of modules = [ [from module, import module, alias], ...]
        imports = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                module = []
            elif isinstance(node, ast.ImportFrom):  
                module = node.module.split('.')
            else:
                continue

            for n in node.names:
                line_of_module_import = [module, n.name.split('.'), n.asname]
                imports.append(line_of_module_import)
        return imports
    
    calls = []
    imports = get_imports(file_path)

    for import_statement in imports:
        from_module = import_statement[0]
        import_module = import_statement[1]

        try:
            if len(from_module) != 0:
                os.system("pip3 install " + from_module[0])
            else:
                for module in import_module:
                    os.system("pip3 install " + module)
            for modules in import_module:
                moduleObject = importlib.import_module(modules)
                calls = calls + dir(moduleObject)
        except Exception as e:
            try:
                #There is a chance the calls are stored in the from-module, we will retrieve that
                if (len(from_module) != 0):
                    calls = calls + dir(from_module[0])
                else:
                    raise e
            except Exception as e:
                print("Encountered exception when getting third party library calls. Proceed to use whatever calls we have scraped from this task: ", e)
    return calls

def get_calls_from_scope(file_path):
    calls = []
    class Traverser(ast.NodeTransformer):

        def visit_FunctionDef(self, node):
            calls.append( node.name)

    with open(file_path) as file:      
        code  = file.read()
        node = ast.parse(code)
        Traverser().visit(node)

    return calls


#The implementation is inspired by get_type that is used in PyART. 
def get_inferred_type_static(rawfile,filePath):

	lindex=filePath.rfind('/')
	tmp=filePath[:lindex]+'/tmp.py'
     
	with open(tmp,'w+') as f:
		f.write(rawfile.read())

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
                 treeObjectDict[item[1]] = item[0]
        #  = {get_tree_node_key(nodetree): get_tree_node_key(nodetree)[1]
        #     for nodetree in ast.walk(tree)}
        
        object_and_type_dict = {}
        for key,value in treeObjectDict.items():
            id = value
            line = key
            
            methodDict_object = moduleDict.get((line, id))
            if methodDict_object is not None:
                object_and_type_dict[(line,id)] = methodDict_object
            else:
                object_and_type_dict[(line,id)] = "None"
        return object_and_type_dict

    def get_module_node_key(node):
        base = (node.lineno,)
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
	
    
    source = textwrap.dedent(source.lstrip('\n'))
    ast_factory = ast
    pytype_options = config.Options.create()
    module = annotate_ast.annotate_source(source, ast_factory, pytype_options)
    annotations_dict = get_annotations_dict(ast.parse(source), module)
    return annotations_dict

# with open(" /Volumes/Transcend/Julian-Transcend/GithubRepo/QrecProject/Test/passpdf.py", encoding='utf-8') as file:
      
#     print(CandidatesGenerator(file))
