import token_tree
import re


#nodeTypes = ('print', 'var_init', 'input')
#chain_root_values = ('then', 'else', 'child')


reserved_keywords = ['if', 'then', 'else', 'end', 'print']
reserved_compare_words = ['>', '<', '=', '<=', '>=']
reserved_arithmetic_operations = {
    '+': (lambda a, b : a + b),
    '-': (lambda a, b : a - b),
    '*': (lambda a, b : a * b),
    '/': (lambda a, b : a / b)
}

priorities = {'+': 1, '-': 1, '*': 2, '/': 2}

roman_numbers = {'I': 1, 'IV': 4, 'V': 5, 'IX': 9, 'X': 10}

def create_arith_expression(tokens):
    out = []
    stack = []
    for t in tokens:
        if t in reserved_arithmetic_operations.keys():
            if t == '+' or t == '-':
                if len(stack) < 1:
                    stack.append(t)
                else:
                    out.append(stack.pop())
                    stack.append(t)
            else:
                if (len(stack) < 1) or (('*' not in stack) and ('/' not in stack)):
                    stack.append(t)
                else:
                    while len(stack) > 0:
                        out.append(stack.pop())
                    stack.append(t)
        else:
            var = create_var(t)
            out.append(var)
    while len(stack) > 0:
        out.append(stack.pop())
    out = token_tree.ArithmeticExpression(out)
    return out


def checkIdentifier(token):
    if re.fullmatch(r'[a-zA-Z]+\w*', token): #variable name that start with letter
        return token
    else:
        return None

def checkRomanNumber(token):
    pattern = r'X{,3}((IX)?|VI{,3}|IV|I{,3})'
    if re.fullmatch(pattern, token):
        c_IX = len(re.findall(r'IX', token))
        token = re.sub(r'IX', '', token)
        c_IV = len(re.findall(r'IV', token))
        token = re.sub(r'IV', '', token)
        c_X = len(re.findall(r'X', token))
        c_V = len(re.findall(r'V', token))
        c_I = len(re.findall(r'I', token))
        num = 10 * c_X + 9 * c_IX + 5 * c_V + 4 * c_IV + 1 * c_I
        return num
    else:
        return None

def create_var(token):
    num = checkRomanNumber(token)
    if num is None:
        name = checkIdentifier(token)
        if name is None:
            raise Exception("Incorrect identifier of num")
        else:
            return token_tree.Variable('var', name)
    else:
        return token_tree.Variable('num', num)

def build_tree(tokens):
    if len(tokens) < 1:
        return token_tree.TokenTree()
    x = 0
    tree = token_tree.TokenTree()
    while x < len(tokens):
        if tokens[x] == 'if':
            then_index = x
            comp_operator_index = x
            while tokens[then_index] != 'then':
                if tokens[then_index] in reserved_compare_words:
                    comp_operator_index = then_index
                then_index += 1
            if comp_operator_index <= x + 1 or comp_operator_index >= then_index - 1:
                raise Exception("Incorrect compare statement for ", tokens[x])
            first_expression = create_arith_expression(tokens[x + 1 : comp_operator_index])
            second_expression = create_arith_expression(tokens[comp_operator_index + 1 : then_index])
            op = tokens[comp_operator_index]

            if op not in reserved_compare_words:
                raise Exception("Incorrect compare operator")
            compareExp = token_tree.CompareExpression(first_expression, second_expression, op)
            tree.add_conditional_node(compareExp)
            x = then_index + 1
        elif tokens[x] == 'print':
            coma_index = x
            while tokens[coma_index] != ';':
                coma_index += 1
            expression = create_arith_expression(tokens[x + 1 : coma_index])

            tree.add_expression_node('print', expression)
            x = coma_index + 1
        elif tokens[x] == 'input':
            var_name = checkIdentifier(tokens[x + 1])

            if var_name is None:
                raise Exception("Incorrect input statement")
            var = create_var(var_name)
            if tokens[x + 2] != ';':
                raise Exception("Missing ; token")
            tree.add_expression_node('input', var)
            x = x + 3
        elif tokens[x] == 'else':
            tree.activate_else()
            print('Activated else chain for Node', tree.current_node.to_string())
            x = x + 1
        elif tokens[x] == 'end':
            if tokens[x + 1] != ';':
                raise Exception("Missing ; token")
            tree.activate_end()
            print('Activated end statement for Node', tree.current_node.to_string())
            x = x + 2
        elif checkIdentifier(tokens[x]) is not None:  # check if statement is a var init statement
            var = create_var(tokens[x])
            if tokens[x + 1] != '=':
                raise Exception(" = statement expected")
            coma_index = x + 1
            while tokens[coma_index] != ';':
                coma_index += 1

            init_expression = create_arith_expression(tokens[x + 2 : coma_index])

            tree.add_expression_node('var_init', (var, init_expression))
            x = coma_index + 1
        else:
            print('Token', tokens[x], 'is not identified for x', x)
            raise Exception("Token ", tokens[x], 'is not identified')

    return tree

