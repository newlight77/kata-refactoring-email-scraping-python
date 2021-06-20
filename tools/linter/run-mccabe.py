import ast
import sys
import configparser
import mccabe
from utils import collect_sources


configParser = configparser.RawConfigParser()
configFilePath = r'setup.cfg'
configParser.read(configFilePath)


def ignore(path):
    ignores = configParser.get('mccabe', 'ignores')
    if path in ignores:
        return True
    return False

def process(py_source, max_complexity):
    code = open(py_source, "r").read()
    tree = compile(code, py_source, "exec", ast.PyCF_ONLY_AST)
    visitor = mccabe.PathGraphingAstVisitor()
    visitor.preorder(tree, visitor)
    for graph in visitor.graphs.values():
        if graph.complexity() > max_complexity:
            return "{}:{}:{} {} {}".format(py_source, graph.lineno, graph.column, graph.entity, graph.complexity())


def main():
    max_complexity = int(configParser.get('mccabe', 'max-complexity'))
    paths = configParser.get('mccabe', 'paths').split(",")
    ok = True
    for py_source in collect_sources(dirs=paths, extensions=".py", ignore_func=ignore):
        error = process(py_source, max_complexity)
        if error:
            ok = False
            print(error)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
