from graphviz import Digraph

from node import *


def _indexate_nodes(root: CFGNode):
    node_index = {'id': 0}

    def _visit(node: CFGNode):
        if node is None:
            return
        if node.index is not None:
            return
        node.index = node_index['id']
        node_index['id'] += 1
        for predecessor in node.predecessors:
            _visit(predecessor)

    _visit(root)


def _collect_nodes(root: CFGNode, predicate):
    return [node for node in CFGNode.flatten(root) if predicate(node)]


def _render_nodes_and_edges(graph, root: CFGNode):
    visited_nodes = set()
    drawed_edges = set()
    labels = {}
    _branch_labels(root, labels)
    _cycle_labels(root, labels)

    def _visit(node, successor, label=None):
        if node is None:
            return
        key = node, successor
        if key in visited_nodes:
            return
        visited_nodes.add(key)

        # hide Join nodes
        if isinstance(node, CFGJoin):
            for predecessor in node.predecessors:
                if predecessor is None:
                    continue
                key = predecessor.id(), node.id()
                _visit(predecessor, successor, label=labels.get(key))
            return

        graph.node(node.id(), str(node))
        edge = node.id(), successor.id()

        label = labels.get(edge) or label
        if isinstance(node, CFGCallNode):
            graph.edge(*edge, style='dashed')
        else:
            graph.edge(*edge, label=label)

        drawed_edges.add(edge)

        for predecessor in node.predecessors:
            _visit(predecessor, node)

    for predecessor in root.predecessors:
        _visit(predecessor, root)


def _branch_labels(root: CFGNode, labels):
    ifs = _collect_nodes(root, lambda it: isinstance(it, CFGIf))
    for cfg_if in ifs:
        if cfg_if.then_branch:
            labels[cfg_if.id(), cfg_if.then_branch.id()] = 'TRUE'
        if cfg_if.else_branch:
            labels[cfg_if.id(), cfg_if.else_branch.id()] = 'FALSE'
    return labels


def _cycle_labels(root: CFGNode, labels):
    cycles = _collect_nodes(root, lambda it: isinstance(it, (CFGFor, CFGWhile)))
    for cycle in cycles:
        if cycle.body:
            labels[cycle.id(), cycle.body.id()] = 'BODY'
        if cycle.exit:
            labels[cycle.id(), cycle.exit.id()] = 'EXIT'
    return labels


def visualize_graph(root: CFGNode, name=None):
    _indexate_nodes(root)
    graph = Digraph(name)
    _render_nodes_and_edges(graph, root)
    graph.render(format='png', view=True, cleanup=True)
