import ast
from abc import ABC
from typing import List

import astor


class CFGNode(ABC):
    predecessors: List['CFGNode']

    def __init__(self, node, predecessors):
        self.ast_node = node
        self.predecessors = predecessors
        self.index = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self.ast_node and self.ast_node.__class__.__name__}'

    def id(self):
        return str(self.index)

    @staticmethod
    def flatten(root):
        visited_nodes = set()
        result = []

        def _visit(node):
            if node is None:
                return
            if node in visited_nodes:
                return
            visited_nodes.add(node)
            result.append(node)

            for predecessor in node.predecessors:
                _visit(predecessor)

        for predecessor in root.predecessors:
            _visit(predecessor)
        return result


class FunctionEntryNode(CFGNode):
    def __str__(self):
        return f'Entrypoint: {self.ast_node.name}'


class CFGSimpleNode(CFGNode):
    def __init__(self, node: ast.AST, predecessor: CFGNode):
        super(CFGSimpleNode, self).__init__(node, [predecessor])

    def __str__(self):
        return astor.to_source(self.ast_node)


class CFGJoin(CFGNode):
    def __init__(self, *predecessors):
        super(CFGJoin, self).__init__(None, list(predecessors))

    def __str__(self):
        return f'Join'


class CFGIf(CFGSimpleNode):
    then_branch = None
    else_branch = None

    def __str__(self):
        return 'IF ' + astor.to_source(self.ast_node.test)


class CFGFor(CFGSimpleNode):
    body = None
    exit = None

    def __str__(self):
        return 'For ' + astor.to_source(self.ast_node.target) + ' in ' + astor.to_source(self.ast_node.iter)


class CFGWhile(CFGSimpleNode):
    body = None
    exit = None

    def __str__(self):
        return 'While ' + astor.to_source(self.ast_node.test)


class CFGControlNode(CFGNode):
    control_type = None

    def __init__(self, node: ast.AST):
        super(CFGControlNode, self).__init__(node, [])

    def __str__(self):
        return f'{self.control_type}'


class CFGReturnNode(CFGControlNode):
    control_type = 'Return'


class CFGBreakNode(CFGControlNode):
    control_type = 'Break'


class CFGContinueNode(CFGControlNode):
    control_type = 'Continue'


class CFGCallNode(CFGNode):
    def __init__(self, node: ast.Call):
        super(CFGCallNode, self).__init__(node, [])

    def __str__(self):
        return f'Call {self.ast_node.func.id}'
