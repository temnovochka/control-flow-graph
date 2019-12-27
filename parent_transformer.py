from ast import *


class ParentTransformer:

    def visit(self, node, parent=None):
        setattr(node, 'parent', parent)
        for field, value in iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        self.visit(item, node)
            elif isinstance(value, AST):
                self.visit(value, node)
        return node
