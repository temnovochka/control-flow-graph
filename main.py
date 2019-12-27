import ast

from cfg import FunctionCFGBuilder
from parent_transformer import ParentTransformer
from visual import visualize_graph


class FunLevelCFGVisualiser(ast.NodeVisitor):

    def visit_FunctionDef(self, node):
        cfg_root = FunctionCFGBuilder().visit_FunctionDef(node, None)
        visualize_graph(cfg_root, name=node.name)


def main():
    file_name = 'test_file.py'
    source = open(file_name).read()
    root_ast = ast.parse(source, file_name)
    root_ast = ParentTransformer().visit(root_ast)
    FunLevelCFGVisualiser().visit(root_ast)


if __name__ == '__main__':
    main()
