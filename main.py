import line_separator
import tree_builder
from token_tree import TreeExecutor

tokens = line_separator.getTokensFromFile('my_program.txt')
print(tokens)
tree = tree_builder.build_tree(tokens)
executor = TreeExecutor()
executor.executeTree(tree)
