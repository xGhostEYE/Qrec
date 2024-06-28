from ast import *
import ast
from anytree import Node, NodeMixin, RenderTree, node
from queue import Queue


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
        def __init__(self, label, position, parent=None, children=None):
            super().__init__()
            self.label = label
            self.position = position
            self.parent = parent
            if children:
                self.children = children

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
        # Root nodes
        def visit_Module(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            
            Module_body_label = ""
            for i in range ( len(node.body)):
                Module_body_label = Module_body_label + "#"
            
            Module_AnyTreeNode = MyAnyTreeNode(Module_body_label, position, parent)
            
            for childNode in node.body:
                self.visit(childNode, Module_AnyTreeNode)
                
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
            
            Constant_AnyTreeNode = MyAnyTreeNode("#", position, parent)
            
            body = node.body
            
            self.visit(body, Constant_AnyTreeNode)
            
            return Constant_AnyTreeNode
            
        def visit_FormattedValue(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)
            
            
            
            
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
                for_body_label = for_body_label + "#"

            while_body_AnyTreeNode = MyAnyTreeNode(for_body_label, position, while_body_label)
            
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

            if parent and len(parent) == 2 and parent[1] == "star":
                except_AnyTreeNode = MyAnyTreeNode("exception*##", position, parent)
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
                if (with_context_managers == ""):
                    with_context_label = with_context_label + "#"
                else:
                    with_context_label = with_context_label + ",#"

            with_context_managers = MyAnyTreeNode(with_context_label, position, with_AnyTreeNode )
            
            for withItem_node in node.items:
                self.visit(withItem_node, with_context_managers)
            
            # Get the body of the With statement
            body_label = ""
            for i in range (len(node.body)):
                body_label = body_label + "#"
            
            with_body_AnyTree = MyAnyTreeNode(body_label, position, with_AnyTreeNode)
            
            for childNode in node.body:
                self.visit(childNode, with_body_AnyTree)

            return with_AnyTreeNode
        
        def visit_withitem(self, node, parent):
            position = Position(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)                

            if (optional_vars):
                withItem_AnyTree = MyAnyTreeNode("#as#", position, parent)
            else:
                withItem_AnyTree = MyAnyTreeNode("#", position, parent)

            context_expr = node.context_expr
            self.visit(context_expr, withItem_AnyTree)

            optional_vars = node.optional_vars
            if (optional_vars):
                self.visit(optional_vars, withItem_AnyTree)

            return withItem_AnyTree



            

    tree = ast.parse(file.read())
    visitor = MyVisitor()
    print(RenderTree(visitor.visit(tree, None)))
    