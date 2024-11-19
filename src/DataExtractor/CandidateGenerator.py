import importlib
import os
import re
import subprocess
import sys
from pytype.tools import traces 
import textwrap
import ast
from pytype import config
import builtins
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
pytype_error_classes = ['import-error','annotation-type-mismatch','assert-type','attribute-error',
                        'bad-concrete-type','bad-function-defaults','bad-return-type','bad-slots','bad-unpacking',
                        'bad-yield-annotation','base-class-error','container-type-mismatch','dataclass-error','duplicate-keyword-argument',
                        'final-error','ignored-abstractmethod','ignored-metaclass','ignored-type-comment','incomplete-match','invalid-annotation',
                        'invalid-directive','invalid-function-definition','invalid-function-type-comment','invalid-namedtuple-arg','invalid-signature-mutation',
                        'invalid-super-call','invalid-typevar','late-directive','match-error','missing-parameter','module-attr','mro-error',
                        'name-error','not-callable','not-indexable','not-instantiable','not-supported-yet','not-writable','override-error',
                        'paramspec-error','pyi-error','python-compiler-error','recursion-error','redundant-function-type-comment','redundant-match',
                        'reveal-type','signature-mismatch','typed-dict-error','unbound-type-param','unsupported-operands','wrong-arg-count',
                        'wrong-arg-types','wrong-keyword-args']

#TODO - doc
#method_dict format: {(object, api, linenumber): [variables and methods in order of data flow]}                               
#A recommendation point is an API call
def CandidatesGenerator ( file, file_path, method_dict, default_calls):

    #perform type inference
    #types_dict format: {target object: target object type}
    raw_file = file.read()
    types_dict = {}
    try:
        types_dict = get_inferred_type_dynamic(raw_file)
    except:
        pass
    API_candidates_for_object = {} 
    for key in method_dict.keys():
        the_object = key[0]
        true_method = key[1]
        line_number = key[2]
        if the_object != None:
            type = None
            try:
                type = types_dict[(line_number,the_object)]
            except KeyError as e:
                pass
            #get list of calls in the type inference
            calls = get_calls(the_object,type, file_path)
            if ( len(calls) == 0):
                calls = default_calls
            API_candidates_key = (the_object, line_number,  true_method)
            API_candidates_for_object[API_candidates_key] = calls
    
    #Check if we get the correct dict
    # for key,value in API_candidates_for_object.items():
    #     print(key, len(value))
                
    return API_candidates_for_object
        
        
def get_calls(object, type, file_path):
    calls = set()
    if (type != None and type != "None" and type != "Any"):
        for call in get_calls_from_valid_type(object, type,file_path):
            if call.startswith('__') or re.match('[A-Z0-9_]+$',call) or call.strip()=='_':
                continue
            calls.add(call)
    return calls   
    
def get_calls_from_valid_type(object,the_type, file_path):
    calls = set()
    if (the_type == 'module'):
        try:
            #object is a string. We need to convert it into a class object
            module = importlib.import_module(object)
            #if object is type "module" then we can just get the calls straight from the object
            return dir(module)
        except:
            imported_module = get_imports_as(file_path, object)
            if imported_module != None:
                try:
                    module = importlib.import_module(imported_module)
                    return dir(module)
                except:
                    return calls
            return calls
    try:
        types = ["int", "float", "str", "list", "tuple", "dict", "set", "bool", "complex"]
        matching_type = [type for type in types if the_type.find(type) == 0]
        if (len(matching_type) != 0):
            calls.update(set(dir(getattr(builtins, matching_type[0]))))
        else:
            module = importlib.import_module(the_type)        
            calls.update(set(dir(module)))
    
    except Exception as error_1:
        print(error_1)
        print("Proceed to install potential missing modules for type: ", the_type)
        package = the_type.split(".")
        try:
            result = subprocess.run(['pip3', 'install', package[0]], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
            if (result != 0):
                subprocess.run(['pip3', 'install', package[0].lower()], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
            #Usually the naming format of a type is capitalized. We need to do lowercase on them
            lower = the_type.lower()
            module = importlib.import_module(lower)
            calls.update(dir(module))
        except subprocess.CalledProcessError as error_1:
            print("Encountered error when installing third party library name: " + package[0] + ". This library is used to provide type: " + the_type + " .Error: ", error_1)
            print("Returning empty list of calls for type: " + the_type + " due to exception")
            calls = set()

        except Exception as error_2:
            print(error_2)
            print("Returning empty list of calls for type: " + the_type + " due to exception")
            calls = set()
    return calls

#Return calls from:
#1. standard libraries, 
#2. imported third-party libraries
#3. all the callable methods declared in the current scope
def get_calls_from_others(file_path):
    refined_calls = []
    calls = set()
    calls.update(get_calls_from_standard_libs(),get_calls_from_third_party_libs(file_path),get_calls_from_scope(file_path))
    for call in calls:
        if call.startswith('__') or re.match('[A-Z0-9_]+$',call) or call.strip()=='_':
            continue
        refined_calls.append(call)
    return refined_calls

def get_calls_from_others_excluding_current_scope(file_path):
    refined_calls = []
    calls = set()
    calls.update(get_calls_from_standard_libs(),get_calls_from_third_party_libs(file_path))
    for call in calls:
        if call.startswith('__') or re.match('[A-Z0-9_]+$',call) or call.strip()=='_':
            continue
        refined_calls.append(call)
    return refined_calls

def get_calls_from_standard_libs():
    calls = set()
    for lib in stdlib:
        try:
            module = importlib.import_module(lib)           
            calls.update(set(dir(module)))
        except Exception as e:
            try:
                module = eval(lib)           
                calls.update(set(dir(module)))
            #Continue to the extract the methods of the next module in the list if there is an exception.
            except Exception as e:
                continue

    return calls
         
def get_imports_as(file_path, alias):
    with open(file_path) as file:        
        tree = ast.parse(file.read())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.alias):
            if node.asname == alias:
                return node.name

    return None
def get_calls_from_third_party_libs(file_path):
    def get_imports(file_path):
        with open(file_path) as file:        
            tree = ast.parse(file.read())
        
        #Format of imports: 
        #imports = [ [from keyword, import keyword: list] ]
        imports = {}
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                list_import_statement_in_a_line = set()
                for n in node.names:
                    list_import_statement_in_a_line.add(n.name)
                
                try:
                    sub_list = imports[None]
                    sub_list.update(list_import_statement_in_a_line)
                except KeyError as e:
                    imports[None] = list_import_statement_in_a_line

            elif isinstance(node, ast.ImportFrom):  
                key = (node.module)

                list_import_statement_in_a_line = set()
                for n in node.names:
                    list_import_statement_in_a_line.add(n.name)

                try:
                    sub_list = imports[key]
                    sub_list.update(list_import_statement_in_a_line)
                except KeyError as e:
                    
                    imports[key] = list_import_statement_in_a_line

            else:
                continue

        return imports
    
    calls = set()
    imports = get_imports(file_path)

    #Get calls from the module in 'from' keyword
    for from_module, import_modules in imports.items():
        if from_module != None:
            package = from_module.split(".")
            #1. install module in 'from' keyword
            try:
                status = subprocess.run(['pip3', 'install', package[0]], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL, check=True)
                if (status.returncode != 0):
                    print("Status code of library installation was " +  status.returncode + " (zero means sucess). This happens during the installation of library name: " + from_module[0] + ". This library is used in the 'from' keyword")
            except Exception as e:
                    print("Encountered error when installing third party library name: " + package[0] + ". This library is used in the 'from' keyword. Error: ", e)
            
            #2. Extract methods from the installed module
            try: 
                moduleObject = importlib.import_module(from_module)
                calls.update(set(dir(moduleObject)))

            except Exception as e:
                #If failed, attempt to get calls from the main package. 
                #For example, instead of extracting methods in 'camera.Camera', we extract methods in 'camera' (excluding the sub packages after dot)
                try:
                    moduleObject = importlib.import_module(package[0])
                    calls.update(set(dir(moduleObject)))

                except Exception as e:
                    print("Encountered exception when getting calls from library name: " + package[0] + ". Proceed to use whatever calls we have scraped from this task. Error:", e)
                
        #Get calls from the module in 'import' keyword
        if len(import_modules) > 0:

            #1. install module in import keyword
            for import_module in import_modules:
                package = import_module.split(".")

                try:
                        status = subprocess.run(['pip3', 'install', package[0]], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL, check=True)
                        if (status.returncode != 0):
                            print("Status code of library installation was " + status.returncode + " (zero means sucess). This happens during the installation of library name: " + from_module[0] + ". This library is used in the 'import' keyword")
                except Exception as e:
                        print("Encountered error when installing third party library name: " + package[0] + ". This library is used in the 'from' keyword. Error:", e)
                
                #2. Extract methods from the installed module
                try:
                    moduleObject = importlib.import_module(import_module)
                    calls.update(set(dir(moduleObject)))

                except Exception as e:
                    try:
                        #Try to get calls from the package. 
                        #For example, instead of extracting methods in camera.Camera, we extract methods in camera (excluding the sub packages after dot)
                        moduleObject = importlib.import_module(package[0])
                        calls.update(set(dir(moduleObject)))

                    except Exception as e:
                        print("Encountered exception when getting calls from library name: " + package[0] + ". Proceed to use whatever calls we have scraped from this task. Error:", e)


    return calls

def get_calls_from_scope(file_path):
    calls = set()
    class Traverser(ast.NodeTransformer):

        def visit_FunctionDef(self, node):
            calls.add(node.name)

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
        
        moduleDict = {}
        if module != None:
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
    pytype_options.ignore_missing_imports = True
    pytype_options.disable = pytype_error_classes
    try:
        module = annotate_ast.annotate_source(source, ast_factory, pytype_options)
    except:
        module = None
    annotations_dict = get_annotations_dict(ast.parse(source), module)
    return annotations_dict

# with open(" /Volumes/Transcend/Julian-Transcend/GithubRepo/QrecProject/Test/passpdf.py", encoding='utf-8') as file:
      
#     print(CandidatesGenerator(file))
