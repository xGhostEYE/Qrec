from ast import *
import ast
from anytree import Node, NodeMixin, RenderTree, node
from queue import Queue
import csv


# global variables
is_assignment_in_global = [False]
is_assignment_in_local = [False]
global_variables = []
local_variables = []

def extract_aroma_tree(file):

    
    class Position():
        def __init__(self, lineno, col_offset, end_lineno, end_col_offset):
            self.lineno = lineno
            self.col_offset = col_offset
            self.end_lineno = end_lineno
            self.end_col_offset = end_col_offset

        def __repr__(self):
            return " line: " + str(self.lineno) + " - endline: " + str(self.end_lineno) + " | col_offset: " + str(self.col_offset) + " - end_col_offset: " + str(self.end_col_offset)
            

    class MyAnyTreeNode(NodeMixin):  # Add Node feature
        def __init__(self, label, position, parent=None, children=None, true_label=None):
            super().__init__()
            self.label = label
            self.position = position
            self.parent = parent
            if(children):
                self.children = children
            self.true_label = true_label


        def __repr__(self):
            return node.util._repr(self)

    
    class MyVisitor (ast.NodeVisitor):
        def visit(self, node, parent_AnyTree_Node):
            """Visit a node."""
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            return visitor(node, parent_AnyTree_Node)

        def generic_visit(self, node, parent_AnyTree_Node):
            """Called if no explicit visitor function exists for a node."""
            for field, value in iter_fields(node):
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, AST):
                            return self.visit(item, parent_AnyTree_Node)
                elif isinstance(value, AST):
                    return self.visit(value, parent_AnyTree_Node)
        
        #Helper
        def check_empty_parameters(self, node):

            if (isinstance(node, ast.arguments)):
                if len(node.posonlyargs) > 0 or len(node.args) > 0 or node.vararg != None or len(node.kwonlyargs) > 0 or node.kwarg != None:
                    return False

            return True

        def check_is_module(self, node):
            # check if the node is a Module type
            if node.parent is None:
                return True
            else:
                return False
            
        # Root nodes
        
        def visit_Module(self, node, parent):
            
            Module_body_label = ""
            for i in range ( len(node.body)):
                Module_body_label = Module_body_label + "#"
            
            Module_AnyTreeNode = MyAnyTreeNode(Module_body_label, None, parent)
            
            for childNode in node.body:
                self.visit(childNode, Module_AnyTreeNode)
                local_variables.clear()
                
            return Module_AnyTreeNode
            
        
        def visit_Expression(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            
            Expression_AnyTreeNode = MyAnyTreeNode("#", position, parent)
            
            body = node.body
            
            self.visit(body, Expression_AnyTreeNode)
            
            return Expression_AnyTreeNode
        
        def visit_Interactive(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            
            Interactive_body_label = ""
            for i in range ( len(node.body)):
                Interactive_body_label = Interactive_body_label + "#"
            
            Interactive_AnyTreeNode = MyAnyTreeNode(Interactive_body_label, position, parent)
            
            for childNode in node.body:
                self.visit(childNode, Interactive_AnyTreeNode)
            
            if(len(node.assign) != 0):
                for childNode in node.assign:
                    self.visit(childNode, Interactive_AnyTreeNode)
            
            return Interactive_AnyTreeNode
        
        # Literals
        
        def visit_Constant(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            
            value = node.value
            
            Constant_AnyTreeNode = MyAnyTreeNode(value, position, parent)
            
            return Constant_AnyTreeNode
            
        def visit_FormattedValue(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "{#}"
            if node.format_spec is not None:
                label = "{#:#}"
            
            FormattedValue_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            
            value = node.value                
            self.visit(value, FormattedValue_AnyTreeNode)
            
            if node.format_spec is not None:
                self.visit(node.format_spec, FormattedValue_AnyTreeNode)
            
            return FormattedValue_AnyTreeNode
        
        def visit_JoinedStr(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            
            JoinedStr_AnyTreeNode = MyAnyTreeNode('f"#"', position, parent)
            values = node.values
            for i in range (len(values)):
                self.visit(values[i], JoinedStr_AnyTreeNode)
            
            return JoinedStr_AnyTreeNode
        
        def visit_List(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "[#]"
            List_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            number_of_nodes = len(node.elts)
            if number_of_nodes != 0:
                label = ""
                for i in range(number_of_nodes):
                    if label == "":
                        label = label + "#"
                    else:
                        label = label + ",#"
                List_AnyTreeNode_Children = MyAnyTreeNode(label, position, List_AnyTreeNode)
                values = node.elts
                for i in range(len(values)):
                    self.visit(values[i], List_AnyTreeNode_Children)
                return List_AnyTreeNode
            else:
                return List_AnyTreeNode
        
        def visit_Tuple(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "(#)"
            Tuple_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            number_of_nodes = len(node.elts)
            if number_of_nodes != 0:
                label = ""
                for i in range(number_of_nodes):
                    if label == "":
                        label = label + "#"
                    else:
                        label = label + ",#"
                Tuple_AnyTreeNode_Children = MyAnyTreeNode(label, position, Tuple_AnyTreeNode)
                values = node.elts
                for i in range(len(values)):
                    if self.check_is_module(parent.parent):
                        is_assignment_in_global[0] = True
                    self.visit(values[i], Tuple_AnyTreeNode_Children)
                return Tuple_AnyTreeNode
            else:
                return Tuple_AnyTreeNode
        
        def visit_Set(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "{#}"
            Set_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            number_of_nodes = len(node.elts)
            if number_of_nodes != 0:
                label = ""
                for i in range(number_of_nodes):
                    if label == "":
                        label = label + "#"
                    else:
                        label = label + ",#"
                Set_AnyTreeNode_Children = MyAnyTreeNode(label, position, Set_AnyTreeNode)
                values = node.elts
                for i in range(len(values)):
                    self.visit(values[i], Set_AnyTreeNode_Children)
                return Set_AnyTreeNode
            else:
                return Set_AnyTreeNode
        
        def visit_Dict(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            Dict_AnyTreeNode = MyAnyTreeNode("{#}", position, parent)
            number_of_nodes = len(node.values)
            
            if number_of_nodes != 0:
                label = ""
                for i in range(number_of_nodes):
                    if label == "":
                        label = label + "#"
                    else:
                        label = label + ",#"
                Dict_AnyTreeNode_Children = MyAnyTreeNode(label, position, Dict_AnyTreeNode)
                
                for i in range(number_of_nodes):
                    label = "#:#"
                    if node.keys[i] == None:
                        label = "**#"
                    Dict_AnyTreeNode_Children_Values = MyAnyTreeNode(label, position, Dict_AnyTreeNode_Children)
                    values = node.values
                    keys = node.keys
                    if keys[i] != None:
                        self.visit(keys[i], Dict_AnyTreeNode_Children_Values)
                    self.visit(values[i], Dict_AnyTreeNode_Children_Values)
            
            return Dict_AnyTreeNode
                
    
        # Variables
        
        def visit_Name(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            
            value = "#VAR"  
            if is_assignment_in_global[0] is True:
                if node.id not in global_variables:
                    global_variables.append(node.id)
                value = node.id
                is_assignment_in_global[0] = False
            
            elif is_assignment_in_local[0] is True: 
                if node.id not in local_variables:
                    local_variables.append(node.id)
                is_assignment_in_local[0] = False

            elif node.id in local_variables:
                value = "#VAR"
            elif node.id in global_variables:
                value = node.id
            
            if (value == "#VAR"):
                Name_AnyTreeNode = MyAnyTreeNode(value, position, parent, true_label=node.id)
            else:
                Name_AnyTreeNode = MyAnyTreeNode(value, position, parent)
            
            return Name_AnyTreeNode
            
        def visit_Del(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            
            Del_AnyTreeNode = MyAnyTreeNode("del#", position, parent)
            
            value = node.id                
            self.visit(value, Del_AnyTreeNode)
            
            return Del_AnyTreeNode
        
        def visit_Starred(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            Starred_AnyTreeNode = MyAnyTreeNode("*#", position, parent)
            self.visit(node.value, Starred_AnyTreeNode)
            
            # if len(node.elts) != 0:
            #     label = ""
            #     for i in range(len(node.elts)):
            #         if label == "":
            #             label = label + "#"
            #         else:
            #             label = label + ",#"
            #     Starred_AnyTreeNode_Children = MyAnyTreeNode(label, position, Starred_AnyTreeNode)
            #     values = node.elts
            #     for i in range(len(values)):
            #         self.visit(values[i], Starred_AnyTreeNode_Children)
            #     return Starred_AnyTreeNode
            # else:
            #     return Starred_AnyTreeNode
        
        # Expressions
        
        def visit_Expr(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            Expr_AnyTreeNode = MyAnyTreeNode("#", position, parent)
            value = node.value
            
            self.visit(value, Expr_AnyTreeNode)
            
            return Expr_AnyTreeNode
        def visit_UnaryOp(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)

            label = ""

            if (isinstance(node.op, ast.UAdd)):
                label = "+#"
            if (isinstance(node.op, ast.USub)):
                label = "-#"
            if (isinstance(node.op, ast.Not)):
                label = "not#"
            if (isinstance(node.op, ast.Invert)):
                label = "~#"
            UnaryOp_TreeNode = MyAnyTreeNode(label, position, parent)

            self.visit(node.operand, UnaryOp_TreeNode)
            return UnaryOp_TreeNode

        def visit_BinOp(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = ""
            
            if (isinstance(node.op, ast.Add)):
                label = "#+#"
            if (isinstance(node.op, ast.Sub)):
                label = "#-#"
            if (isinstance(node.op, ast.Mult)):
                label = "#*#"
            if (isinstance(node.op, ast.FloorDiv)):
                label = "#//#"
            if (isinstance(node.op, ast.Mod)):
                label = "#%#"
            if (isinstance(node.op, ast.Pow)):
                label = "#**#"

            Expr_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            
            left_value = node.left
            right_value = node.right
            
            self.visit(left_value, Expr_AnyTreeNode)
            self.visit(right_value, Expr_AnyTreeNode)
            
            return Expr_AnyTreeNode
        
        def visit_BoolOp(self, node, parent):
            
            #if @ is NOT in the parent label, that means this node is NOT a child node of a BoolOp node
            if not ("@" in parent.label):
                position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)

                operator = ""
                if (isinstance(node.op, ast.Or)):
                    operator = "or"
                else:
                    operator = "and"
                
                label = ""
                for i in range(len(node.values)):

                    #Use @ to denote the spot of the label where the next BoolOp should override
                    char = "#"
                    if (isinstance(node.values[i], ast.BoolOp)):
                        char = "@"

                    if (label == ""):
                        label = char 
                    else:
                        label =  label + operator + char
                BoolOp_AnyTreeNode = MyAnyTreeNode(label, position, parent)
                for value in node.values:                        
                    self.visit(value, BoolOp_AnyTreeNode)
                return BoolOp_AnyTreeNode
            
            #if @ is NOT in the parent label, that means this node is NOT a child node of a BoolOp node
            #This means this boolOp should modify the parent node instead of creating a new boolOp
            else:
                operator = ""
                if (isinstance(node.op, ast.Or)):
                    operator = "or"
                else:
                    operator = "and"
                
                index_of_alt = parent.label.index("@")
                parent_label = parent.label
                label = ""
                for i in range(len(node.values)):
                    #Use @ to denote the spot of the label where the next BoolOp should override
                    char = "#"
                    if (isinstance(node.values[i], ast.BoolOp)):
                        char = "@"
                    if (label == ""):
                        label = char 
                    else:
                        label =  label + operator + char
                
                if (index_of_alt < len(parent_label)-1):
                    parent_label = parent.label[:index_of_alt] + label + parent.label[index_of_alt+1:]
                else:
                    parent_label = parent.label[:index_of_alt] + label
                
                parent.label = parent_label

                for value in node.values:
                    self.visit(value, parent)
            
                return parent

        def visit_Compare(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            
            ops_values = node.ops
            comparators_values = node.comparators
            
            label = "#"
            for i in range(len(ops_values)):
                if isinstance(ops_values[i], ast.Eq):
                    label = label + "==#"
                if isinstance(ops_values[i], ast.NotEq):
                    label = label + "!=#"
                if isinstance(ops_values[i],ast.Lt):
                    label = label + "<#"
                if isinstance(ops_values[i], ast.LtE):
                    label = label + "<=#"
                if isinstance(ops_values[i], ast.Gt):
                    label = label + ">#"
                if isinstance(ops_values[i], ast.GtE):
                    label = label + ">=#"
                if isinstance(ops_values[i], ast.Is):
                    label = label + "is#"
                if isinstance(ops_values[i], ast.IsNot):
                    label = label + "is not#"
                if isinstance(ops_values[i], ast.In):
                    label = label + "in#"
                if isinstance(ops_values[i], ast.NotIn):
                    label = label + "not in#"

            Compare_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            self.visit(node.left, Compare_AnyTreeNode)
            
            for i in range(len(ops_values)):
                self.visit(comparators_values[i], Compare_AnyTreeNode)
        
            return Compare_AnyTreeNode
            
        def visit_Call(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            call_label = "#("

            if (len(node.args) > 0):
                call_label = call_label + "#"
            call_label = call_label + ")"
            Call_AnyTreeNode = MyAnyTreeNode(call_label, position, parent)
            
            name_position = Position(node.func.lineno, node.func.col_offset, node.func.end_lineno, node.func.end_col_offset)
            
            method_name = ""
            if (isinstance(node.func, ast.Name)):
                method_name = node.func.id
                MyAnyTreeNode(method_name, name_position, Call_AnyTreeNode)
            elif (isinstance(node.func, ast.Attribute)):
                self.visit(node.func, Call_AnyTreeNode )
                        
            labels = ""
            for i in range(len(node.args)):
                if labels == "":
                    labels = labels + "#"
                else:
                    labels = labels + ",#"

            for i in range(len(node.keywords)):
                if labels == "":
                    labels = labels + "#"
                else:
                    labels = labels + ",#"

            #If labels is not empty, that means there are args or keywords to visit
            if (labels != ""):            
                Parameter_node = MyAnyTreeNode(labels, position, Call_AnyTreeNode)
                for i in range(len(node.args)):
                    self.visit(node.args[i], Parameter_node)
                
                for i in range(len(node.keywords)):
                    self.visit(node.keywords[i], Parameter_node)              
            
            return Call_AnyTreeNode

        def visit_keyword(self, node, parent):
        # TODO: we may need to do this in the future, but there is no way to determine if there is a keyword
        # that has stars
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            
            if node.arg != None:
                label = "#=#"
                keyword_AnyTreeNode = MyAnyTreeNode(label, position, parent)
                keyword_AnyTreeNode_Children = MyAnyTreeNode("#VAR", position, keyword_AnyTreeNode, true_label=node.arg)
                self.visit(node.value, keyword_AnyTreeNode)
            else:
                self.visit(node.value, parent)       
                
            return keyword_AnyTreeNode
            
        def visit_IfExp(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "# if # else #"
            
            if node.orelse == None:
                label = "# if #"
                IfExp_AnyTreeNode = MyAnyTreeNode(label, position, parent)
                self.visit(node.body, IfExp_AnyTreeNode)
                self.visit(node.test, IfExp_AnyTreeNode)
                return IfExp_AnyTreeNode
            
            else:
                IfExp_AnyTreeNode = MyAnyTreeNode(label, position, parent)
                self.visit(node.body, IfExp_AnyTreeNode)
                self.visit(node.test, IfExp_AnyTreeNode)
                self.visit(node.orelse, IfExp_AnyTreeNode)
                return IfExp_AnyTreeNode
        
        def visit_Attribute(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            
            label = "#.#"
            Attribute_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            self.visit(node.value, Attribute_AnyTreeNode)
            Attribute_AnyTreeNode_Attribute = MyAnyTreeNode(node.attr, position, Attribute_AnyTreeNode)
            
            return Attribute_AnyTreeNode
        
        def visit_NamedExpr(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "#:=#"

            NamedExpr_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            self.visit(node.target, NamedExpr_AnyTreeNode)
            self.visit(node.value, NamedExpr_AnyTreeNode)
            
            return NamedExpr_AnyTreeNode
        
        #Subscripting
        
        def visit_Subscript(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "#[#]"
            Subscript_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            
            self.visit(node.value, Subscript_AnyTreeNode)
            self.visit(node.slice, Subscript_AnyTreeNode)         
                        
            return Subscript_AnyTreeNode

        def visit_Slice(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "#:#"
            
            if (node.step):
                label = label + ":#"

            Slice_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            
            self.visit(node.lower,Slice_AnyTreeNode)
            self.visit(node.upper,Slice_AnyTreeNode)
            if (node.step):
                self.visit(node.step, Slice_AnyTreeNode)

            return Slice_AnyTreeNode
        
        #Comprehensions
        
        def visit_ListComp(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "[#"
            for i in range(len(node.generators)):
                label= label+ "#"
            label = label + "]"
            ListComp_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            
            self.visit(node.elt, ListComp_AnyTreeNode)
            for comprehension in node.generators:
                self.visit(comprehension, ListComp_AnyTreeNode)
            
        def visit_SetComp(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "{#"
            for i in range(len(node.generators)):
                label= label+ "#"
            label = label + "}"  
            SetComp_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            
            self.visit(node.elt,SetComp_AnyTreeNode)
            for comprehension in node.generators:
                self.visit(comprehension, SetComp_AnyTreeNode)            
            
            return SetComp_AnyTreeNode
            
        def visit_GeneratorExp(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "(#"
            for i in range(len(node.generators)):
                label= label+ "#"
            label = label + ")" 
            GeneratorExp_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            
            self.visit(node.elt,GeneratorExp_AnyTreeNode)
            for comprehension in node.generators:
                self.visit(comprehension, GeneratorExp_AnyTreeNode)   
            return GeneratorExp_AnyTreeNode
        
        def visit_DictComp(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "{#"
            for i in range(len(node.generators)):
                label= label+ "#"
            label = label + "}"
            DictComp_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            
            DictComp_AnyTreeNode_key_value = MyAnyTreeNode("#:#", position, DictComp_AnyTreeNode)
            self.visit(node.key, DictComp_AnyTreeNode_key_value)
            self.visit(node.value, DictComp_AnyTreeNode_key_value)
            
            for comprehension in node.generators:
                self.visit(comprehension, DictComp_AnyTreeNode)   
     
            return DictComp_AnyTreeNode
        
        #TODO: check if this aligns with Aroma paper
        def visit_comprehension(self, node, parent):
            position = parent.position
            
            label = "##"
            comprehension_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            
            for_label = "for#"
            for_AnyTreeNode = MyAnyTreeNode(for_label, position, comprehension_AnyTreeNode)
            self.visit(node.target, for_AnyTreeNode)

            in_label = "in#"
            for i in range(len(node.ifs)):
                in_label = in_label + "#"

            in_AnyTreeNode = MyAnyTreeNode(in_label, position, comprehension_AnyTreeNode)

            self.visit(node.iter, in_AnyTreeNode)
            for if_statement in node.ifs:
                if_AnyTreenode = MyAnyTreeNode("if#", position, in_AnyTreeNode)
                self.visit(if_statement, if_AnyTreenode)

            return comprehension_AnyTreeNode

        #Statements
        
        def visit_Assign(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = ""
            for i in range(len(node.targets)):
                if label == "":
                    label = "#"
                else:
                    label = label + "=#"

            label = label + "=#"
            Assign_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            
            for target in node.targets:
                if self.check_is_module(parent):
                    is_assignment_in_global[0] = True
                else:
                    is_assignment_in_local[0] = True
                    
                self.visit(target, Assign_AnyTreeNode)
            self.visit(node.value, Assign_AnyTreeNode)
            
            return Assign_AnyTreeNode
            
            
        def visit_AnnAssign(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "#:#"
            if node.value != None:
                label = label + "=#"

            AnnAssign_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            
            if self.check_is_module(parent):
                is_assignment_in_global[0] = True
                
            self.visit(node.target, AnnAssign_AnyTreeNode)
            self.visit(node.annotation, AnnAssign_AnyTreeNode)

            if node.value != None:
                self.visit(node.value, AnnAssign_AnyTreeNode)
            
            return AnnAssign_AnyTreeNode
        
        def visit_AugAssign(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "#"            
            if isinstance(node.op, ast.Add):
                label += "+=#"
            elif isinstance(node.op, ast.Sub):
                label += "-=#"
            elif isinstance(node.op, ast.Mult):
                label += "*=#"
            elif isinstance(node.op, ast.MatMult):
                label += "@=#"
            elif isinstance(node.op, ast.Div):
                label += "/=#"
            elif isinstance(node.op, ast.FloorDiv):
                label += "//=#"
            elif isinstance(node.op, ast.Mod):
                label += "%=#"
            elif isinstance(node.op, ast.Pow):
                label += "**=#"
            elif isinstance(node.op, ast.BitAnd):
                label += "&=#"
            elif isinstance(node.op, ast.BitOr):
                label += "|=#"
            elif isinstance(node.op, ast.BitXor):
                label += "^=#"
            elif isinstance(node.op, ast.RShift):
                label += ">>=#"
            else:
                label += "<<=#"
                # walrus op is not here because it's already done in visit_NamedExpr()
            
            AugAssign_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            self.visit(node.target, AugAssign_AnyTreeNode)
            self.visit(node.value, AugAssign_AnyTreeNode)
            
            return AugAssign_AnyTreeNode
            
        def visit_Raise(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "raise"
            
            
            if node.exc != None:
                label = label + "#"
                if node.cause != None:
                    label = label + "from#"
                    
                Raise_AnyTreeNode = MyAnyTreeNode(label, position, parent)

                self.visit(node.exc, Raise_AnyTreeNode)
                if node.cause != None:
                    self.visit(node.cause, Raise_AnyTreeNode)

                return Raise_AnyTreeNode
            else:
                Raise_AnyTreeNode = MyAnyTreeNode(label, position, parent)
                return Raise_AnyTreeNode

        
        def visit_Assert(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            Assert_AnyTreeNode = MyAnyTreeNode("assert#,#", position, parent)
            self.visit(node.test, Assert_AnyTreeNode)
            self.visit(node.msg, Assert_AnyTreeNode)            
            
            return Assert_AnyTreeNode
        
        def visit_Delete(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "del"

            for i in range (len(node.targets)):
                if label == "":
                    label = "#"
                else:
                    label = label + ",#"
            
            Delete_AnyTreeNode = MyAnyTreeNode(label, position, parent)

            for target in node.targets:
                self.visit(target, Delete_AnyTreeNode)
           
            return Delete_AnyTreeNode            
            
        def visit_Pass(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            Pass_AnyTreeNode = MyAnyTreeNode("pass", position, parent)
            
            return Pass_AnyTreeNode
            
        def visit_TypeAlias(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            label = "type#"


            if len(node.type_params) != 0:
                label = label + "[#]"
            label = label + "=#"
            TypeAlias_AnyTreeNode = MyAnyTreeNode(label, position, parent)
            
            #Visit the name
            self.visit(node.name, TypeAlias_AnyTreeNode)
            
            #Visit the parameters
            parameter_label = ""
            for i in range(len(node.type_params)):
                if parameter_label == "":
                    parameter_label = parameter_label + "#"
                else:
                    label = label + ",#"        
            TypeAliasParameter_AnyTreeNode = MyAnyTreeNode(parameter_label, position, TypeAlias_AnyTreeNode)
            for parameter in node.type_params:
                self.visit(parameter, TypeAliasParameter_AnyTreeNode)
            
            #Visit value
            self.visit(node.value, TypeAlias_AnyTreeNode)

                  
            return TypeAlias_AnyTreeNode  
            
        
        #Control Flow
        def visit_If(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)                
            
            if_AnyTreeNode = MyAnyTreeNode("if##", position, parent)

            if_conditional_AnyTreeNode = MyAnyTreeNode("(#)", position, if_AnyTreeNode)

            #Traverse through the conditional statement
            conditional_node = node.test
            self.visit(conditional_node, if_conditional_AnyTreeNode)

            if_body_label = ":"
            for i in range ( len(node.body)):
                if_body_label = if_body_label + "#"

            if_body_AnyTreeNode = MyAnyTreeNode(if_body_label, position, if_AnyTreeNode)
            
            #Traverse through statements in the body
            for childNode in node.body:
                self.visit(childNode, if_body_AnyTreeNode)

            #Traverse through else statement if exists
            if (len(node.orelse) != 0):            
                else_AnyTreeNode = MyAnyTreeNode("else#", position, parent)

                else_body_label = ":"

                #TODO: since else node is stored in another node and not a node by itself, we would only have 1 # instead of 2 #s.
                for i in range ( len(node.orelse)):
                    else_body_label = else_body_label + "#"

                #Get lineno of else token
                else_lineno = node.body[-1].end_lineno + 1

                #TODO: end col offset might not be correct. Fix this later
                position = Position(else_lineno, node.col_offset, node.end_lineno, node.end_col_offset)
                else_body_AnyTreeNode = MyAnyTreeNode(else_body_label, position, else_AnyTreeNode)
                
                for childNode in node.orelse:
                    self.visit(childNode, else_body_AnyTreeNode)

            return if_AnyTreeNode

        def visit_For(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)                
            
            for_AnyTreeNode = MyAnyTreeNode("for##", position, parent)


            for_conditional_AnyTreeNode = MyAnyTreeNode("#in#", position, for_AnyTreeNode)

            self.visit(node.target, for_conditional_AnyTreeNode)
            self.visit(node.iter, for_conditional_AnyTreeNode)

            for_body_label = ":"
            for i in range ( len(node.body)):
                for_body_label = for_body_label + "#"

            for_body_AnyTreeNode = MyAnyTreeNode(for_body_label, position, for_AnyTreeNode)
            
            #Traverse through statements in the body
            for childNode in node.body:
                self.visit(childNode, for_body_AnyTreeNode)

            #Traverse through else statement if exists
            if (len(node.orelse) != 0):
                else_AnyTreeNode = MyAnyTreeNode("else#", position, parent)

                else_body_label = ":"

                #TODO: since else node is stored in another node and not a node by itself, we would only have 1 # instead of 2 #s.
                for i in range ( len(node.orelse)):
                    else_body_label = else_body_label + "#"

                #Get lineno of else token
                else_lineno = node.body[-1].end_lineno + 1

                #TODO: end col offset might not be correct. Fix this later
                position = Position(else_lineno, node.col_offset, node.end_lineno, node.end_col_offset)
                else_body_AnyTreeNode = MyAnyTreeNode(else_body_label, position, else_AnyTreeNode)
                
                for childNode in node.orelse:
                    self.visit(childNode, else_body_AnyTreeNode)

            return for_AnyTreeNode
        
        def visit_While(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)                
            
            while_AnyTreeNode = MyAnyTreeNode("while##", position, parent)


            while_conditional_AnyTreeNode = MyAnyTreeNode("(#)", position, while_AnyTreeNode)

            self.visit(node.test, while_conditional_AnyTreeNode)

            while_body_label = ":"
            for i in range ( len(node.body)):
                while_body_label = while_body_label + "#"

            while_body_AnyTreeNode = MyAnyTreeNode(while_body_label, position, while_AnyTreeNode)
            
            #Traverse through statements in the body
            for childNode in node.body:
                self.visit(childNode, while_body_AnyTreeNode)

            #Traverse through else statement if exists
            if (len(node.orelse) != 0):
                else_AnyTreeNode = MyAnyTreeNode("else#", position, parent)

                else_body_label = ":"

                #TODO: since else node is stored in another node and not a node by itself, we would only have 1 # instead of 2 #s.
                for i in range ( len(node.orelse)):
                    else_body_label = else_body_label + "#"

                #Get lineno of else token
                else_lineno = node.body[-1].end_lineno + 1

                #TODO: end col offset might not be correct. Fix this later
                position = Position(else_lineno, node.col_offset, node.end_lineno, node.end_col_offset)
                else_body_AnyTreeNode = MyAnyTreeNode(else_body_label, position, else_AnyTreeNode)
                
                for childNode in node.orelse:
                    self.visit(childNode, else_body_AnyTreeNode)

            return while_AnyTreeNode

        def visit_Break(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)                
            
            break_AnyTreeNode = MyAnyTreeNode("break", position, parent)

            return break_AnyTreeNode
        
        def visit_Continue(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)                
            
            continue_AnyTreeNode = MyAnyTreeNode("continue", position, parent)

            return continue_AnyTreeNode 
        
        def visit_Try(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)                
            
            try_AnyTreeNode = MyAnyTreeNode("try#", position, parent)

            try_body_label = ":"
            for i in range ( len(node.body)):
                try_body_label = try_body_label + "#"

            try_body_AnyTreeNode = MyAnyTreeNode(try_body_label, position, try_AnyTreeNode)
            
            #Traverse through statements in the body
            for childNode in node.body:
                self.visit(childNode, try_body_AnyTreeNode)

            if (len(node.handlers) != 0):
                
                for exception_handler in node.handlers:
                    self.visit(exception_handler, parent)
            
            if (len(node.orelse) != 0):
                else_AnyTreeNode = MyAnyTreeNode("else#", position, parent)
                
                else_body_label = ":"
                for i in range ( len(node.orelse)):
                    else_body_label = else_body_label + "#"

                #Get lineno of else token
                else_lineno = node.body[-1].end_lineno + 1
                #Get end lineno of else token
                else_end_lineno = node.orelse[-1].end_lineno
                
                position = Position(else_lineno, node.col_offset, else_end_lineno, node.end_col_offset)
                else_body_AnyTreeNode = MyAnyTreeNode(else_body_label, position, else_AnyTreeNode)

                for childNode in node.orelse:
                    self.visit(childNode, else_body_AnyTreeNode)

            if (len(node.finalbody) != 0):
                finally_AnyTreeNode = MyAnyTreeNode("finally#", position, parent)
                
                finally_body_label = ":"
                for i in range ( len(node.finalbody)):
                    finally_body_label = finally_body_label + "#"

                finally_lineno = node.orelse[-1].end_lineno + 1
  
                position = Position(finally_lineno, node.col_offset, node.end_lineno, node.end_col_offset)
                finally_body_AnyTreeNode = MyAnyTreeNode(finally_body_label, position, finally_AnyTreeNode)

                for childNode in node.finalbody:
                    self.visit(childNode, finally_body_AnyTreeNode)

            return try_AnyTreeNode

        def visit_TryStar(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)                
            
            try_AnyTreeNode = MyAnyTreeNode("try#", position, parent)

            try_body_label = ":"
            for i in range ( len(node.body)):
                try_body_label = try_body_label + "#"

            try_body_AnyTreeNode = MyAnyTreeNode(try_body_label, position, try_AnyTreeNode)
            
            #Traverse through statements in the body
            for childNode in node.body:
                self.visit(childNode, try_body_AnyTreeNode)

            if (len(node.handlers) != 0):
                
                for exception_handler in node.handlers:
                    self.visit(exception_handler, (parent, "star"))
            
            if (len(node.orelse) != 0):
                else_AnyTreeNode = MyAnyTreeNode("else#", position, parent)
                
                else_body_label = ":"
                for i in range ( len(node.orelse)):
                    else_body_label = else_body_label + "#"

                #Get lineno of else token
                else_lineno = node.body[-1].end_lineno + 1
                #Get end lineno of else token
                else_end_lineno = node.orelse[-1].end_lineno
                
                position = Position(else_lineno, node.col_offset, else_end_lineno, node.end_col_offset)
                else_body_AnyTreeNode = MyAnyTreeNode(else_body_label, position, else_AnyTreeNode)

                for childNode in node.orelse:
                    self.visit(childNode, else_body_AnyTreeNode)

            if (len(node.finalbody) != 0):
                finally_AnyTreeNode = MyAnyTreeNode("finally#", position, parent)
                
                finally_body_label = ":"
                for i in range ( len(node.finalbody)):
                    finally_body_label = finally_body_label + "#"

                finally_lineno = node.orelse[-1].end_lineno + 1
  
                position = Position(finally_lineno, node.col_offset, node.end_lineno, node.end_col_offset)
                finally_body_AnyTreeNode = MyAnyTreeNode(finally_body_label, position, finally_AnyTreeNode)

                for childNode in node.finalbody:
                    self.visit(childNode, finally_body_AnyTreeNode)

            return try_AnyTreeNode

        def visit_ExceptHandler(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)                
            
            if type(parent) is tuple and len(parent) == 2 and parent[1] == "star":
                except_AnyTreeNode = MyAnyTreeNode("exception*##", position, parent[0])
            else:
                except_AnyTreeNode = MyAnyTreeNode("exception##", position, parent)

            exception_conditional_AnyTreeNode = MyAnyTreeNode("(#)", position, except_AnyTreeNode)

            self.visit(node.type, exception_conditional_AnyTreeNode)
            
            exception_body_label = ":"
            for i in range ( len(node.body)):
                exception_body_label = exception_body_label + "#"

            try_body_AnyTreeNode = MyAnyTreeNode(exception_body_label, position, except_AnyTreeNode)
            for childNode in node.body:
                self.visit(childNode, try_body_AnyTreeNode)

            return except_AnyTreeNode
        
        def visit_With(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)                

            with_AnyTreeNode = MyAnyTreeNode("with##", position, parent)
            
            # Get the context manager part of a With statement
            with_context_label = ""
            for i in range (len(node.items)):
                if (with_context_label == ""):
                    with_context_label = with_context_label + "#"
                else:
                    with_context_label = with_context_label + ",#"

            with_context_managers = MyAnyTreeNode(with_context_label, position, with_AnyTreeNode )
            
            for withItem_node in node.items:
                self.visit(withItem_node, with_context_managers)
            
            # Get the body of the With statement
            body_label = ":"
            for i in range (len(node.body)):
                body_label = body_label + "#"
            
            with_body_AnyTree = MyAnyTreeNode(body_label, position, with_AnyTreeNode)
            
            for childNode in node.body:
                self.visit(childNode, with_body_AnyTree)

            return with_AnyTreeNode
        
        def visit_withitem(self, node, parent):
            position = parent.position                

            if (node.optional_vars):
                withItem_AnyTree = MyAnyTreeNode("#as#", position, parent)
            else:
                withItem_AnyTree = MyAnyTreeNode("#", position, parent)

            context_expr = node.context_expr
            self.visit(context_expr, withItem_AnyTree)

            optional_vars = node.optional_vars
            if (optional_vars):
                self.visit(optional_vars, withItem_AnyTree)

            return withItem_AnyTree

    # Pattern Matching
        def visit_Match( self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)    

            match_statement = MyAnyTreeNode("match##", position, parent)

            subject = MyAnyTreeNode("(#)", position, match_statement)
            self.visit(node.subject, subject)

            body_label = ":"
            for i in range (len(node.cases)):
                body_label = body_label + "#"
            body = MyAnyTreeNode(body_label, position, match_statement)
            for case in node.cases:
                self.visit(case, body)
            
            return match_statement
        
        def visit_match_case(self, node, parent):
            position = parent.position  

            #condition
            case_label = "case#"
            if (node.guard):
                case_label = case_label + "if#"
            case_statement = MyAnyTreeNode(case_label, position, parent)
            
            self.visit(node.pattern, case_statement)

            if (node.guard):
                self.visit(node.guard, case_statement)

            #body
            body_label = ":"
            for i in range (len(node.body)):
                body_label = body_label + "#"
            body = MyAnyTreeNode(body_label, position, case_statement)

            for case in node.body:
                self.visit(case, body)

        def visit_MatchValue(self, node, parent):
            
            return self.visit(node.value, parent)

        def visit_MatchSingleton(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)    

            return MyAnyTreeNode(str(node.value), position, parent)

        def visit_MatchSequence(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)    

            label = "["

            for i in range(len(node.patterns)):
                if label == "[":
                    label = label + "#"

                else:
                    label = label + ",#"

            label = label + "]"
            sequence_statement = MyAnyTreeNode(label,position, parent)

            for childNode in node.patterns:
                self.visit(childNode, sequence_statement)

            return sequence_statement


        def visit_MatchStar(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)    
            
            label = "*"
            if (node.name):
                label = label + node.name
            else:
                label = label + "_"

            return MyAnyTreeNode(label, position, parent)

        def visit_MatchMapping(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)    
           
            label = ""

            for i in range(len(node.keys)):
                if label == "":
                    label = label + "#"
                else:
                    label = label + ",#"

            if (node.rest):
                if label == "":
                    label = label + "#"
                else:
                    label = label + ",#"   
                
            match_mapping = MyAnyTreeNode(label, position, parent)
            
            for i in range(len(node.keys())):
                subtree_root = MyAnyTreeNode("#:#", position, match_mapping)

                self.visit(node.keys[i], subtree_root )
                self.visit(node.patterns[i], subtree_root)
            
            if (node.rest):
                MyAnyTreeNode("**"+node.rest, position, match_mapping)

            return match_mapping

        def visit_MatchClass(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)    
            label = "#(#)"

            parameter_label = ""
            for i in range(len(node.keys)):
                if label == "":
                    label = label + "#"
                else:
                    label = label + ",#"
                    
            matchclass_node = MyAnyTreeNode(label, position, parent)
            self.visit(node.cls, matchclass_node)

            parameter_node = MyAnyTreeNode(parameter_label, position, matchclass_node)
            for i in range(len(node.patterns)):
                self.visit(node.patterns[i], parameter_node)
            
            for i in range(len(node.kwd_attrs)):
                if (node.kwd_patterns[i]):
                    kw_pair_node = MyAnyTreeNode("#=#", position, parameter_node)
                    self.visit(node.kwd_attrs[i],kw_pair_node)
                    self.visit(node.kwd_patterns[i],kw_pair_node)
            
            return matchclass_node

        def visit_MatchAs(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)    
            label = ""
            if node.name:
                if node.pattern:
                    label = "#as#"
                else:
                    label = node.name
            else:
                label = "_"

            match_as_node = MyAnyTreeNode(label, position,parent)  

            if (label == "#as#"):
                self.visit(node.pattern, match_as_node)
                match_as_name_node = MyAnyTreeNode(str(node.name), position, match_as_node)
   
            return match_as_node
        
        def visit_MatchOr(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)    
            
            label = ""
            for i in range(len(node.patterns)):
                if label == "":
                    label = label + "#"
                else:
                    label = label + "|#"
            
            match_or_node = MyAnyTreeNode(label, position, parent)

            for childNode in node.patterns:
                self.visit(childNode, match_or_node)
            
            return match_or_node

    #Type parameters 
        def visit_TypeVar(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)  

            label = "[#:#]"

            typeVar_node = MyAnyTreeNode(label, position, parent)

            name_node = MyAnyTreeNode(str(node.name), position, typeVar_node) 

            self.visit(node.bound, typeVar_node)

            return typeVar_node 

        def visit_ParamSpec(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)  

            label = "[**#]"
            typeVar_node = MyAnyTreeNode(label, position, parent)

            name_node = MyAnyTreeNode(str(node.name), position, typeVar_node) 

            return typeVar_node
        
        def visit_TypeVarTuple(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)  

            label = "[*#]"
            typeVar_node = MyAnyTreeNode(label, position, parent)

            name_node = MyAnyTreeNode(str(node.name), position, typeVar_node) 

            return typeVar_node  
    #Function and class definitions
        def visit_FunctionDef(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)  
            label = "def##"

            def_func_node = MyAnyTreeNode(label, position, parent)
            
            #Declarative
            func_declaration = "#("

            isEmpty = self.check_empty_parameters(node.args)

            if (not isEmpty):
                func_declaration = func_declaration + "#" 
            func_declaration = func_declaration + ")" 

            if (node.returns):
                func_declaration = func_declaration + "->#"
            
            parameter_func_node = MyAnyTreeNode(func_declaration, position, def_func_node)  
            
            func_name_node = MyAnyTreeNode(node.name, position, parameter_func_node)
            if (not isEmpty):
                self.visit(node.args, parameter_func_node)

            if (node.returns):
                self.visit(node.returns, parameter_func_node)

            #Body
            body_label = ":"

            for i in range ( len(node.body)):
                body_label = body_label + "#"
            
            body_node = MyAnyTreeNode(body_label, position, def_func_node)

            for childNode in node.body:
                self.visit(childNode, body_node)
            
            return def_func_node
        
        def visit_Lambda(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)  
            label = "lambda##"

            def_func_node = MyAnyTreeNode(label, position, parent)
            
            #Declarative
            func_declaration = "("

            isEmpty = self.check_empty_parameters(node.args)

            if (not isEmpty):
                func_declaration = func_declaration + "#"
            func_declaration  = func_declaration + ")"
            
            parameter_func_node = MyAnyTreeNode(func_declaration, position, def_func_node)  
            
            if (not isEmpty):
                self.visit(node.args, parameter_func_node)

            #Body
            body_label = ":#"
            body_node = MyAnyTreeNode(body_label, position, def_func_node)
            self.visit(node.body, body_node)
            return def_func_node

        def visit_arguments(self, node, parent):
            position = parent.position

            args_label = ""
            for i in range(len(node.args)):
                if (args_label == ""):
                    args_label = args_label + "#"
                else:
                    args_label = args_label + ",#"
            if node.vararg is not None:
                if (args_label == ""):
                    args_label = args_label + "#"
                else:
                    args_label = args_label + ",#"
            for i in range(len(node.kwonlyargs)):
                if (args_label == ""):
                    args_label = args_label + "#"
                else:
                    args_label = args_label + ",#"
            if node.kwarg is not None:
                if (args_label == ""):
                    args_label = args_label + "#"
                else:
                    args_label = args_label + ",#"


            arguments_node = MyAnyTreeNode(args_label, position, parent)
            for i in range(0-len(node.args), 0):
                if i >= 0-len(node.defaults):
                    arg_label = "#=#"
                    arg_node = MyAnyTreeNode(arg_label, position, arguments_node)

                    self.visit(node.args[i],arg_node)
                    self.visit(node.defaults[i], arg_node)
                    
                else:
                    self.visit(node.args[i], arguments_node)
            if node.vararg is not None:
                star_arg_label = "*#"
                star_arg_node = MyAnyTreeNode(star_arg_label, position, arguments_node)
                self.visit(node.vararg, star_arg_node)

            for i in range(len(node.kwonlyargs)):
                if (node.kwonlyargs[i] and node.kw_defaults[i]):
                    arg_label = "#=#"
                    arg_node = MyAnyTreeNode(arg_label, position, arguments_node)

                    self.visit(node.kwonlyargs[i],arg_node)
                    self.visit(node.kw_defaults[i], arg_node)
                else:
                    self.visit(node.kwonlyargs[i],arguments_node)
            
            if node.kwarg is not None:
                double_star_arg_label = "**#"
                double_star_arg_node = MyAnyTreeNode(double_star_arg_label, position, arguments_node)
                self.visit(node.kwarg, double_star_arg_node)
            
            return arguments_node

        def visit_arg(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)  

            arg_node = None
            if (node.annotation):
                label = "#:#"
                arg_node = MyAnyTreeNode(label, position, parent)
                MyAnyTreeNode("#VAR", position, arg_node, true_label=node.arg)
                self.visit(node.annotation, arg_node)

            else:
                label = str(node.arg)
                if label == "":
                    return parent
                else:
                    arg_node = MyAnyTreeNode("#VAR", position, parent, true_label=node.arg)
        
            return arg_node

        def visit_Return(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)

            label = "return#"

            return_node = MyAnyTreeNode(label, position, parent)

            self.visit(node.value, return_node)

            return return_node
        

        def visit_Yield(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)

            label = "yield#"

            yield_node = MyAnyTreeNode(label, position, parent)

            self.visit(node.value, yield_node)

            return yield_node
    
        def visit_YieldFrom(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)

            label = "yieldfrom#"

            yield_node = MyAnyTreeNode(label, position, parent)

            self.visit(node.value, yield_node)

            return yield_node 

        def visit_Global(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)

            label = "global"

            for name in node.names:
                if label == "global":
                    label = label + "#"
                else:
                    label = label + ",#"
            
            global_node = MyAnyTreeNode(label, position, parent)

            for name in node.names:
                name_node = MyAnyTreeNode(str(name), position, global_node)
            
            return global_node

        def visit_Nonlocal(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)

            label = "nonlocal"

            for name in node.names:
                if label == "nonlocal":
                    label = label + "#"
                else:
                    label = label + ",#"
            
            global_node = MyAnyTreeNode(label, position, parent)

            for name in node.names:
                name_node = MyAnyTreeNode(str(name), position, global_node)
            
            return global_node
    
        def visit_ClassDef (self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)  
            label = "class##"

            def_class_node = MyAnyTreeNode(label, position, parent)
            
            #Declarative
            class_declaration = "#("

            if (len(node.bases) != 0 or len(node.keywords) != 0):
                class_declaration = class_declaration + "#"  

            class_declaration = class_declaration + ")"   
 
   
            class_func_node = MyAnyTreeNode(class_declaration, position, def_class_node)  
            
            class_name_node = MyAnyTreeNode(node.name, position, class_func_node)
            
            #AnyTree Node for parameters
            paremeters_label = ""
            for i in range(len(node.bases)):
                if (paremeters_label == ""):
                    paremeters_label = paremeters_label + "#"
                else:
                    paremeters_label = paremeters_label + ",#"

            for i in range(len(node.keywords)):
                if (paremeters_label == ""):
                    paremeters_label = paremeters_label + "#"
                else:
                    paremeters_label = paremeters_label + ",#"
            
            parameters_AnyTreeNode = MyAnyTreeNode(paremeters_label, position, class_func_node)
            
            for childNode in node.bases:
                self.visit(childNode, parameters_AnyTreeNode)
            for keyword in node.keywords:
                self.visit(keyword, parameters_AnyTreeNode)

            #Body
            body_label = ":"

            for i in range ( len(node.body)):
                body_label = body_label + "#"
            
            body_node = MyAnyTreeNode(body_label, position, def_class_node)

            for childNode in node.body:
                self.visit(childNode, body_node)
            
            return def_class_node

    #Async and await¶
        def visit_AsyncFunctionDef(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)  
            label = "async def##"

            def_func_node = MyAnyTreeNode(label, position, parent)
            
            #Declarative
            func_declaration = "#("

            isEmpty = self.check_empty_parameters(node.args)

            if (not isEmpty):
                func_declaration = func_declaration + "#" 
            func_declaration = func_declaration + ")" 

            if (node.returns):
                func_declaration = func_declaration + "->#"
            
            parameter_func_node = MyAnyTreeNode(func_declaration, position, def_func_node)  
            
            func_name_node = MyAnyTreeNode(node.name, position, parameter_func_node)
            if (not isEmpty):
                self.visit(node.args, parameter_func_node)

            if (node.returns):
                self.visit(node.returns, parameter_func_node)

            #Body
            body_label = ":"

            for i in range ( len(node.body)):
                body_label = body_label + "#"
            
            body_node = MyAnyTreeNode(body_label, position, def_func_node)

            for childNode in node.body:
                self.visit(childNode, body_node)
            
            return def_func_node

        def visit_Await(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)  

            label = "await#"

            await_node = MyAnyTreeNode(label, position, parent)

            self.visit(node.value, await_node)

            return await_node
            
        def visit_AsyncFor(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)                
            
            for_AnyTreeNode = MyAnyTreeNode("async-for##", position, parent)


            for_conditional_AnyTreeNode = MyAnyTreeNode("#in#", position, for_AnyTreeNode)

            self.visit(node.target, for_conditional_AnyTreeNode)
            self.visit(node.iter, for_conditional_AnyTreeNode)

            for_body_label = ":"
            for i in range ( len(node.body)):
                for_body_label = for_body_label + "#"

            for_body_AnyTreeNode = MyAnyTreeNode(for_body_label, position, for_AnyTreeNode)
            
            #Traverse through statements in the body
            for childNode in node.body:
                self.visit(childNode, for_body_AnyTreeNode)

            #Traverse through else statement if exists
            if (len(node.orelse) != 0):
                else_AnyTreeNode = MyAnyTreeNode("else#", position, parent)

                else_body_label = ":"

                #TODO: since else node is stored in another node and not a node by itself, we would only have 1 # instead of 2 #s.
                for i in range ( len(node.orelse)):
                    else_body_label = else_body_label + "#"

                #Get lineno of else token
                else_lineno = node.body[-1].end_lineno + 1

                #TODO: end col offset might not be correct. Fix this later
                position = Position(else_lineno, node.col_offset, node.end_lineno, node.end_col_offset)
                else_body_AnyTreeNode = MyAnyTreeNode(else_body_label, position, else_AnyTreeNode)
                
                for childNode in node.orelse:
                    self.visit(childNode, else_body_AnyTreeNode)

            return for_AnyTreeNode

        def visit_AsyncWith(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)                

            with_AnyTreeNode = MyAnyTreeNode("async-with##", position, parent)
            
            # Get the context manager part of a With statement
            with_context_label = ""
            for i in range (len(node.items)):
                if (with_context_label == ""):
                    with_context_label = with_context_label + "#"
                else:
                    with_context_label = with_context_label + ",#"

            with_context_managers = MyAnyTreeNode(with_context_label, position, with_AnyTreeNode )
            
            for withItem_node in node.items:
                self.visit(withItem_node, with_context_managers)
            
            # Get the body of the With statement
            body_label = ":"
            for i in range (len(node.body)):
                body_label = body_label + "#"
            
            with_body_AnyTree = MyAnyTreeNode(body_label, position, with_AnyTreeNode)
            
            for childNode in node.body:
                self.visit(childNode, with_body_AnyTree)

            return with_AnyTreeNode


    tree = ast.parse(file.read())
    visitor = MyVisitor()
    print(RenderTree(visitor.visit(tree, None)))
    aroma_tree = visitor.visit(tree, None)
    return aroma_tree


# the main function to get the features
def token_feature(leaf_node):

    return leaf_node.label
    
def parent_feature(leaf_node):
    
    def parent_feature(child, parent, parent_features, label):

        if len(parent_features) == 3:
            return 
        
        if (parent != None):
            position = get_child_position(child, parent)        
            parent_features.append( (label,position, parent.label) )
            return parent_feature(parent, parent.parent, parent_features, label)
        return parent_features
        
    parent_features = []
    parent_feature(leaf_node, leaf_node.parent, parent_features, leaf_node.label)
    return parent_features

def sibling_feature(leaf_node, leaf_nodes):
    index = leaf_nodes.index(leaf_node)
    sibling_features = []
    left_index = index - 1
    if (left_index >= 0):
        left_sibling = leaf_nodes[left_index]
        sibling_features.append( (left_sibling.label, leaf_node.label) )
    
    right_index = index + 1
    if (right_index < len(leaf_nodes)):
        right_sibling = leaf_nodes[right_index]
        sibling_features.append( (leaf_node.label, right_sibling.label))

    return sibling_features
def get_child_position(child, parent):
        
        position = 1
        if parent.children != None:
            for the_child in parent.children:
                if child == the_child:
                    return position
                position = position + 1

def variable_usage_feature(leaf_node, leaf_nodes):

    def get_context(node):
        parent = node.parent
        if (parent != None):
            position = get_child_position(node, parent)

            if parent.label != "#.#":
                return (position, parent.label)

            else:
                children = parent.leaves
                label = ""
                for child in children:
                    if child.label != "#VAR":
                        label = child.label
                        break

                return (position, label)
        return ("","")          
    variable_usage_features = []
    if leaf_node.label == "#VAR":
        index = leaf_nodes.index(leaf_node)
        label = leaf_node.true_label

        if (index -1 >= 0 ):
            for i in range(index - 1,0,-1):
                
                another_leaf_node = leaf_nodes[i]
                another_leaf_node_label = another_leaf_node.label if leaf_nodes[i].label != "#VAR" else leaf_nodes[i].true_label
                if another_leaf_node_label == label:
                    variable_usage_features.append( (get_context(another_leaf_node), get_context(leaf_node)) )
                    break
        
        if (index + 1 < len(leaf_nodes)):
            for i in range(index+1, len(leaf_nodes)):
                another_leaf_node = leaf_nodes[i]
                another_leaf_node_label = leaf_nodes[i].label if leaf_nodes[i].label != "#VAR" else leaf_nodes[i].true_label
                if another_leaf_node_label == label:
                    variable_usage_features.append( (get_context(leaf_node),get_context(another_leaf_node)) )
                    break
        
    return variable_usage_features

def extract_aroma_features(aromatree):
    leaf_nodes = aromatree.leaves
    aroma_dict = {}
    for leaf in leaf_nodes:
        
        token = token_feature(leaf)
        parent = parent_feature(leaf)
        sibling = sibling_feature(leaf, leaf_nodes)
        variable_usage = variable_usage_feature ( leaf, leaf_nodes )

        features = [token, parent, sibling, variable_usage]
        aroma_dict[leaf] = features
    
    for key,value in aroma_dict.items():
        print(key.label," : ", value)
    
    
    return aroma_dict

def create_csv_data_set(aroma_dict):
    data = [
        {'name': 'Nikhil', 'branch': 'COE', 'year': 2, 'cgpa': 9.0},
        {'name': 'Sanchit', 'branch': 'COE', 'year': 2, 'cgpa': 9.1},
        {'name': 'Aditya', 'branch': 'IT', 'year': 2, 'cgpa': 9.3},
        {'name': 'Sagar', 'branch': 'SE', 'year': 1, 'cgpa': 9.5},
        {'name': 'Prateek', 'branch': 'MCE', 'year': 3, 'cgpa': 7.8},
        {'name': 'Sahil', 'branch': 'EP', 'year': 2, 'cgpa': 9.1}
    ]
    with open('../data/aroma_dataset.csv', 'a', newline='') as csvfile:
        fieldnames = ['name', 'branch', 'year', 'cgpa']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)




    