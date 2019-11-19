import line_separator
import tree_builder
import sys
from token_tree import TreeExecutor


if(len(sys.argv) != 2):
    print('You must enter filename')
else:
    tokens = line_separator.getTokensFromFile(sys.argv[1])
    print(tokens)
    tree = tree_builder.build_tree(tokens)
    executor = TreeExecutor()
    executor.executeTree(tree)

