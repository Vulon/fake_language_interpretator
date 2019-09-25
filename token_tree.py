



nodeTypes = ('print', 'var_init', 'input', 'return')
chain_root_values = ('then', 'else', 'child')

class ArithmeticExpression(object):

    def __init__(self, polish_statement):
        self.storage = polish_statement

    def getValue(self, stack):
        from tree_builder import reserved_arithmetic_operations
        temp_store = []
        for v in self.storage:
            if v in reserved_arithmetic_operations.keys():
                a = temp_store.pop()
                a = a.getValue(stack)
                b = temp_store.pop()
                b = b.getValue(stack)
                value = reserved_arithmetic_operations[v](b, a)
                var = Variable('num', value)
                temp_store.append(var)
            else:
                temp_store.append(v)
        var = temp_store.pop()
        return var.getValue(stack)

    def to_string(self):
        from tree_builder import reserved_arithmetic_operations
        string = ''
        for v in self.storage:
            if v in reserved_arithmetic_operations.keys():
                string += v + ' '
            else:
                string += str(v.data) + ' '
        return string

class Variable(object):
    #data types: var, num
    # if type == var, then data is a name of a variable
    # if type == num then data is a number
    def __init__(self, var_type, data):
        self.var_type = var_type
        self.data = data

    def __str__(self):
        return self.to_string()

    def setData(self, data):
        self.data = data

    def to_string(self):
        string = str(self.data)
        return string

    def getValue(self, stack):
        if self.var_type.__eq__('var'):
            return stack[self.data]
        else:
            return self.data



class CompareExpression:
    def __init__(self, first_expression, second_expression, compare_operator):
        self.first_expression = first_expression
        self.second_expression = second_expression
        self.compare_operator = compare_operator

    def to_string(self):
        return self.first_expression.to_string() + " " + self.compare_operator + " " + self.second_expression.to_string()

    def executeCompare(self, stack, verbose=True):
        a = self.first_expression.getValue(stack)
        b = self.second_expression.getValue(stack)
        if verbose:
            print("Comparing: ", self.to_string(), 'a, b:', a, b)
        if self.compare_operator == '<':
            return a < b
        elif self.compare_operator == '<=':
            return a <= b
        elif self.compare_operator == '==':
            return a == b
        elif self.compare_operator == '>':
            return a > b
        elif self.compare_operator == '>=':
            return a >= b

class ExpressionNode(object):
    def getType(self):
        return self.node_type


    def __init__(self, parent, node_type, value=None):
        self.parent = parent
        self.node_type = node_type
        self.value = value
        self.child = None
        if node_type not in nodeTypes:
            raise Exception("Incorrect type")

    def add_node(self, child):
        self.child = child

    def to_string(self):
        string = self.node_type + ' '
        if self.node_type == 'print':
            string += self.value.to_string()
        elif self.node_type == 'var_init':
            string += self.value[0].data + '=' + self.value[1].to_string()
        elif self.node_type == 'input':
            string += str(self.value.to_string())
        return string


    def executeExpression(self, stack, verbose=True):
        if self.node_type == 'print':
            if verbose:
                print("Printing ", self.value.getValue(stack))
            print(self.value.getValue(stack))
        elif self.node_type == 'var_init':

            left_exp = self.value[0]
            right_exp = self.value[1]
            if verbose:
                print("Initializing ", left_exp.to_string(), '=', right_exp.getValue(stack))
            stack[left_exp.data] = right_exp.getValue(stack)
        elif self.node_type == 'input':
            from tree_builder import checkRomanNumber
            print('Please enter roman number: ')
            num = checkRomanNumber(input())
            if num is None:
                num = 0
            if verbose:
                print("inputed ", num, 'to', self.value.data)
            stack[self.value.data] = num


class ConditionalNode(object):
    def getType(self):
        return 'if'

    def __init__(self, parent, value):
        self.parent = parent
        self.value = value
        #value should be CompareExpression !!!
        self.then_chain = None
        self.else_chain = None
        self.node_type = 'if'
        self.child = None
        self.chain_root = 'then'

    def to_string(self):
        string = "Compare node: " + self.value.to_string()
        return string



    def activate_root(self, root):
        if root not in chain_root_values:
            raise Exception("Incorrect root type")
        else:
            self.chain_root = root

    def add_node(self, child):
        if self.chain_root.__eq__('then'):
            self.then_chain = child
        elif self.chain_root.__eq__('else'):
            self.else_chain = child
        elif self.chain_root.__eq__('child'):
            self.child = child
        else:
            raise Exception(self.chain_root, 'does not match correct types')

class TokenTree(object):
    def __init__(self):
        self.head = None
        self.current_node = None
        self.isFinished = False

    def finish_building(self, node='head'):
        self.isFinished = True
        if node is None:
            return
        if node == 'head':
            node = self.head
            self.finish_building(node)
        else:
            if node.getType() == 'if':
                node.chain_root = 'unseen'
                self.finish_building(node.then_chain)
                self.finish_building(node.else_chain)
            self.finish_building(node.child)


    def add_expression_node(self, node_type, value):
        if self.isFinished:
            return
        # for print value = variable
        # for var_init value = (variable, variable)
        # for input value = variable
        # for return value = none
        if self.head is None:
            self.head = ExpressionNode(None, node_type, value)
            self.current_node = self.head
        else:
            new_node = ExpressionNode(self.current_node, node_type, value)
            string = "Added Expression, parent: " + self.current_node.to_string() + ' <- child - ' + new_node.to_string()
            if self.current_node.getType() == 'if':
                string += ' root ' + self.current_node.chain_root
            print(string)
            self.current_node.add_node(new_node)
            self.current_node = new_node

    def findTopConditionalNode(self, node):
        string = 'search for node ' + node.to_string()
        node = node.parent
        while node is not None:
            if node.getType() == 'if':
                break
            node = node.parent

        if node is None:
            print(string, 'not found')
            return None
        else:
            print(string, 'found', node.to_string())
            return node

    def add_conditional_node(self, value):  #value should be CompareExpression that takes 2 expressions and operation
        if self.isFinished:
            return
        if self.head is None:
            self.head = ConditionalNode(None, value)
            self.current_node = self.head
        else:
            new_node = ConditionalNode(self.current_node, value)
            string = "Added Conditional, parent: " + self.current_node.to_string() + ' <- child - ' + new_node.to_string()
            if self.current_node.getType() == 'if':
                string += ' root ' + self.current_node.chain_root
            print(string)
            self.current_node.add_node(new_node)
            self.current_node = new_node

    def activate_else(self):
        if self.head is None:
            raise Exception("Tree head is empty")
        node = self.current_node
        node.child = ExpressionNode(node, 'return', None)
        while node is not None and not node.getType().__eq__('if'):
            node = node.parent
        if node is None:
            raise Exception("If node not found")
        node.activate_root('else')
        self.current_node = node

    def activate_end(self):
        if self.head is None:
            raise Exception("Tree head is empty")
        node = self.current_node
        self.current_node.child = ExpressionNode(node, 'return', None)
        node = node.parent
        while node is not None and not node.getType().__eq__('if'):
            node = node.parent
        if node is None:
            raise Exception("If node not found")
        node.activate_root('child')
        self.current_node = node

class TreeExecutor(object):

    def executeTree(self, tree, verbose=True):  #verbose False to disable debug printing
        stack = {}
        node = tree.head
        print("Started executing tree")
        tree.finish_building()
        while node is not None:

            if node.getType() == 'input':
                node.executeExpression(stack, verbose)
                node = node.child
            elif node.getType() == 'var_init':
                node.executeExpression(stack, verbose)
                node = node.child
            elif node.getType() == 'print':
                node.executeExpression(stack, verbose)
                node = node.child
            elif node.getType() == 'return':
                if verbose:
                    print("returning")
                node = tree.findTopConditionalNode(node)
            elif node.getType() == 'if':
                if node.chain_root == 'unseen':
                    compareExpr = node.value
                    res = compareExpr.executeCompare(stack, verbose)
                    if res:
                        if verbose:
                            print("went to then root")
                        node.chain_root = 'then'
                        node = node.then_chain
                    else:
                        if node.else_chain is None:
                            if verbose:
                                print('went to child root')
                            node.chain_root = 'child'
                            node = node.child
                        else:
                            if verbose:
                                print('went to else root')
                            node.chain_root = 'else'
                            node = node.else_chain
                elif node.chain_root == 'then':

                    if node.child is None:
                        if verbose:
                            print("This node was visited, no child root found, went upwards")
                        node = tree.findTopConditionalNode(node)
                    else:
                        if verbose:
                            print("This node was visited, went to child root")
                        node.chain_root = 'child'
                        node = node.child
                elif node.chain_root == 'child':
                    if verbose:
                        print("This node was visited, went upwards")
                    node = tree.findTopConditionalNode(node)

        print("Program finished")













