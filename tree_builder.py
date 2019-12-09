import token_tree
import re


#nodeTypes = ('print', 'var_init', 'input')
#chain_root_values = ('then', 'else', 'child')


reserved_keywords = ['if', 'then', 'else', 'end', 'print']
reserved_compare_words = ['>', '<', '==', '<=', '>=']
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
        if t not in reserved_arithmetic_operations.keys():
            if checkIdentifier(t) is None:
                if checkRomanNumber(t) is None:
                    return None

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
    if checkRomanNumber(token) is not None:
        return None

    if re.fullmatch(r'[a-zA-Z]+[a-zA-Z_]*', token): #variable name that start with letter
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
            return None
        else:
            return token_tree.Variable('var', name)
    else:
        return token_tree.Variable('num', num)

def handleIfError(x,statement, tokens, message):
    print("ERROR!!!!__________", message, " Statement: ", statement, " x:", x, " token: ", tokens[x])
    while (x < len(tokens)):
        if tokens[x] == "end":
            if x + 2 < len(tokens):
                if tokens[x + 2] == 'else':
                    x = x + 2
            else:
                return x + 1;
        x = x + 1

    print("Program finished could not process further.")

def handleError(x,statement, tokens, message):
    print("ERROR!!!!__________", message, " Statement: ", statement, " x:", x, " token: ", tokens[x])
    while(x < len(tokens)):
        if tokens[x] == ';':
            return x + 1
        x = x + 1

    print("Program finished could not process further.")
    return x


def build_tree(tokens):
    if len(tokens) < 1:
        return token_tree.TokenTree()
    x = 0
    statement = 0
    tree = token_tree.TokenTree()
    while x < len(tokens):
        if tokens[x] == 'if':
            then_index = x
            comp_operator_index = x
            if x + 4 < len(tokens):
                while tokens[then_index] != 'then':

                    if tokens[then_index] in reserved_compare_words:
                        comp_operator_index = then_index

                    then_index += 1

                    if then_index >= len(tokens):
                        break

                if then_index >= len(tokens):
                    handleIfError(x, statement, tokens, "Could not find THEN token")
                    continue

                if comp_operator_index <= x + 1 or comp_operator_index >= then_index - 1:
                    x = handleIfError(x, statement, tokens, "Could not find compare operator")
                    continue
                first_expression = create_arith_expression(tokens[x + 1: comp_operator_index])
                second_expression = create_arith_expression(tokens[comp_operator_index + 1: then_index])
                if first_expression is None or second_expression is None:
                    x = handleIfError(x, statement, tokens, "Could not process arith expressions.")
                    continue
                op = tokens[comp_operator_index]

                if op not in reserved_compare_words:
                    x = handleIfError(x, statement, tokens, "Could not find compare operator")
                    continue
                compareExp = token_tree.CompareExpression(first_expression, second_expression, op)
                if compareExp is None:
                    x = handleIfError(x, statement, tokens, "Could not process compare expression")
                    continue
                tree.add_conditional_node(compareExp)
                x = then_index + 1
                statement = statement + 1
            else:
                x = handleIfError(x, statement, tokens, "IF expression not enough operands")
                continue

        elif tokens[x] == 'print':
            if x + 2 >= len(tokens):
                x = handleError(x, statement, tokens, "Not enough operands for Print Token")
                continue
            coma_index = x
            while tokens[coma_index] != ';':

                coma_index += 1
                if coma_index >= len(tokens):
                    break

            if coma_index >= len(tokens):
                x = handleError(x, statement, tokens, "Could not find ; Token")
                continue



            expression = create_arith_expression(tokens[x + 1 : coma_index])
            if expression  is None:
                x = handleError(x, statement, tokens, "Could not create expression")
                continue
            tree.add_expression_node('print', expression)
            x = coma_index + 1
            statement = statement + 1
        elif tokens[x] == 'input':
            if x + 2 >= len(tokens):
                x = handleError(x, statement, tokens, "Not enough operands for Input token")
                continue
            var_name = checkIdentifier(tokens[x + 1])

            if var_name is None:
                x = handleError(x, statement, tokens, "Left value should be a variable name")
                continue
            var = create_var(var_name)
            if tokens[x + 2] != ';':
                x = handleError(x, statement, tokens, "Could not find ; token")
                continue
            tree.add_expression_node('input', var)
            x = x + 3
            statement = statement + 1
        elif tokens[x] == 'else':
            tree.activate_else()
            print('Activated else chain for Node', tree.current_node.to_string())
            x = x + 1
            statement = statement + 1
        elif tokens[x] == 'end':
            if tokens[x + 1] != ';':
                x = handleError(x, statement, tokens, "Could not find ; token")
                continue
            tree.activate_end()
            print('Activated end statement for Node', tree.current_node.to_string())
            x = x + 2
            statement = statement + 1
        elif checkIdentifier(tokens[x]) is not None:  # check if statement is a var init statement
            var = create_var(tokens[x])
            if x + 3 >= len(tokens):
                x = handleError(x, statement, tokens, "Not enough operands for Init token")
                continue
            if tokens[x + 1] != '=':
                x = handleError(x, statement, tokens, "= Token expected")
                continue
            coma_index = x + 1
            while coma_index < len(tokens) and tokens[coma_index] != ';':
                coma_index += 1

            if coma_index >= len(tokens):
                x = handleError(x, statement, tokens, "Could not find ; token")
                continue

            init_expression = create_arith_expression(tokens[x + 2 : coma_index])

            if init_expression is None:
                x = handleError(x, statement, tokens, "Could not create arith expression")
                continue

            tree.add_expression_node('var_init', (var, init_expression))
            x = coma_index + 1
            statement = statement + 1
        elif tokens[x] == ';':
            x = x + 1
        else:
            x = handleError(x, statement, tokens, "Could not process token " + tokens[x])

    return tree

