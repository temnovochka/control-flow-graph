from node import *


class FunctionCFGBuilder:
    known_entries = {}
    known_exits = {}

    def visit(self, node, predecessor: CFGNode) -> CFGNode:
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.visit_generic_node)
        return visitor(node, predecessor)

    def visit_generic_node(self, node, predecessor):
        calls = self.collect_call_expressions(node)
        cfg_node = CFGSimpleNode(node, predecessor)
        self.known_entries[node] = cfg_node
        self.known_exits[node] = cfg_node
        if not calls:
            return cfg_node
        call_cfg_nodes = [CFGCallNode(it) for it in calls]
        cfg_node.predecessors += call_cfg_nodes
        return cfg_node

    def visit_If(self, node, predecessor):
        entrypoint = CFGIf(node, predecessor)
        self.known_entries[node] = entrypoint
        exitpoint = CFGJoin()
        self.known_exits[node] = exitpoint
        body = self.visit_node_list(node.body, entrypoint)
        orelse = self.visit_node_list(node.orelse, entrypoint)
        exitpoint.predecessors.append(body)
        exitpoint.predecessors.append(orelse)
        if node.body:
            entrypoint.then_branch = self.known_entries[node.body[0]]
        if node.orelse:
            entrypoint.else_branch = self.known_entries[node.orelse[0]]
        return exitpoint

    def visit_FunctionDef(self, node, predecessor):
        entrypoint = FunctionEntryNode(node, [predecessor])
        return_node = CFGReturnNode(node)
        self.known_entries[node] = entrypoint
        self.known_exits[node] = return_node
        self.visit_node_list(node.body, entrypoint)
        return return_node

    def visit_Return(self, node, predecessor):
        value = self.visit(node.value, predecessor)
        function = self.find_first_parent(node, lambda it: isinstance(it, ast.FunctionDef))
        cfg_node = CFGSimpleNode(node, value)
        self.known_exits[function].predecessors.append(cfg_node)
        self.known_exits[node] = cfg_node
        self.known_entries[node] = self.known_entries[node.value]

    def visit_For(self, node, predecessor):
        """
        for <node.target> in <node.iter>:
            <node.body>
        else:
            <node.orelse>
        """

        iterable = self.visit(node.iter, predecessor)

        entrypoint = CFGFor(node, iterable)
        self.known_entries[node] = entrypoint
        exitpoint = CFGJoin(entrypoint)
        self.known_exits[node] = exitpoint

        body = self.visit_node_list(node.body, entrypoint)
        entrypoint.predecessors.append(body)
        if node.body:
            entrypoint.body = self.known_entries[node.body[0]]
        entrypoint.exit = exitpoint
        return exitpoint

    def visit_While(self, node, predecessor):
        """
        while <node.test>:
            <node.body>
        else:
            <node.orelse>
        """

        entrypoint = CFGWhile(node, predecessor)
        self.known_entries[node] = entrypoint
        exitpoint = CFGJoin(entrypoint)
        self.known_exits[node] = exitpoint

        body = self.visit_node_list(node.body, entrypoint)
        entrypoint.predecessors.append(body)

        if node.body:
            entrypoint.body = self.known_entries[node.body[0]]
        entrypoint.exit = exitpoint

        return exitpoint

    def visit_Continue(self, node, predecessor):
        cfg_node = CFGContinueNode(node)
        cfg_node.predecessors.append(predecessor)
        nearest_cycle = self.find_first_parent(node, lambda it: isinstance(it, (ast.While, ast.For)))
        cycle_cfg_node = self.known_entries[nearest_cycle]
        cycle_cfg_node.predecessors.append(cfg_node)
        self.known_entries[node] = cfg_node
        self.known_exits[node] = cfg_node

    def visit_Break(self, node, predecessor):
        cfg_node = CFGBreakNode(node)
        cfg_node.predecessors.append(predecessor)
        nearest_cycle = self.find_first_parent(node, lambda it: isinstance(it, (ast.While, ast.For)))
        cycle_cfg_node = self.known_exits[nearest_cycle]
        cycle_cfg_node.predecessors.append(cfg_node)
        self.known_entries[node] = cfg_node
        self.known_exits[node] = cfg_node

    def visit_node_list(self, nodes, predecessor):
        result = predecessor
        for node in nodes:
            result = self.visit(node, result)
        return result

    def collect_call_expressions(self, node):
        if isinstance(node, ast.Call):
            return [node]

        result = []
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        result += self.collect_call_expressions(item)
            elif isinstance(value, ast.AST):
                result += self.collect_call_expressions(value)
        return result

    def find_first_parent(self, node, predicate):
        if node is None:
            raise Exception('Parent expected')
        if predicate(node):
            return node
        return self.find_first_parent(node.parent, predicate)
