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

            

    tree = ast.parse(file.read())
    visitor = MyVisitor()
    print(RenderTree(visitor.visit(tree, None)))
    