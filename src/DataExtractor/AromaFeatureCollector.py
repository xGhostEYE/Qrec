from ast import *
import ast
from anytree import Node, RenderTree
from queue import Queue

def extract_aroma_tree(file):
    queue = Queue()
    root = Node()


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
                            self.visit(item, parent_AnyTree_Node)
                elif isinstance(value, AST):
                    self.visit(value, parent_AnyTree_Node)

        #Control Flow
        def visit_If(self, node, parent):                
            if parent:
                if_node = AnyNode(id)
            self.generic_visit(node, if_node)




    tree = ast.parse(file.read())
    visitor = MyVisitor()
    visitor.visit(tree, None)