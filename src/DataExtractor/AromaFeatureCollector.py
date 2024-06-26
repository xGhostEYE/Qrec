from ast import *
import ast
from anytree import Node, NodeMixin, RenderTree
from queue import Queue

def extract_aroma_tree(file):
    queue = Queue()
    root = Node()

    class Position():
        def __init(self, lineno, col_offset, end_lineno, end_col_offset):
            self.lineno = lineno
            self.col_offset = col_offset
            self.end_lineno = end_lineno
            self.end_col_offset = end_col_offset

    class MyAnyTreeNode(NodeMixin):  # Add Node feature
         def __init__(self, label, position, parent=None, children=None):
            super().__init__()
            self.label = label
            self.position = position
            self.parent = parent
            if children:
                self.children = children

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