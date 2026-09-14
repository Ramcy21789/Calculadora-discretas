import re
import itertools

class LogicParser:
    def __init__(self):
        self.operators = ['∧', '∨', '→', '↔']
        self.unary = ['¬']
        self.precedence = {'↔': 1, '→': 2, '∨': 3, '∧': 4, '¬': 5}
        self.variables = []

    def is_logic_expression(self, expression):
        for op in self.operators + self.unary:
            if op in expression:
                return True
        return False

    def get_variables(self, expression):
        vars_found = set(re.findall(r'[a-zA-Z]', expression))
        # Exclude common non-variable characters if needed, but for logic we keep all letters
        if 'v' in vars_found and 'v' not in expression.replace('v', ''):
            pass
        return sorted(list(vars_found))

    def tokenize(self, expression):
        tokens = []
        i = 0
        while i < len(expression):
            char = expression[i]
            if char in self.operators or char in self.unary or char in '()':
                tokens.append(char)
            elif char.isalpha():
                tokens.append(char)
            i += 1
        return tokens

    def shunting_yard(self, tokens):
        output = []
        ops = []
        for token in tokens:
            if token.isalpha():
                output.append(token)
            elif token in self.unary:
                ops.append(token)
            elif token in self.operators:
                while ops and ops[-1] != '(' and self.precedence.get(ops[-1], 0) >= self.precedence.get(token, 0):
                    output.append(ops.pop())
                ops.append(token)
            elif token == '(':
                ops.append(token)
            elif token == ')':
                while ops and ops[-1] != '(':
                    output.append(ops.pop())
                if ops:
                    ops.pop() # pop '('
        while ops:
            output.append(ops.pop())
        return output

    def evaluate_rpn(self, rpn, context):
        stack = []
        try:
            for token in rpn:
                if token.isalpha():
                    stack.append(context.get(token, False))
                elif token == '¬':
                    val = stack.pop()
                    stack.append(not val)
                elif token in self.operators:
                    right = stack.pop()
                    left = stack.pop()
                    if token == '∧':
                        stack.append(left and right)
                    elif token == '∨':
                        stack.append(left or right)
                    elif token == '→':
                        stack.append((not left) or right)
                    elif token == '↔':
                        stack.append(left == right)
            return stack[0] if stack else False
        except IndexError:
            return False

    def solve(self, expression):
        steps = []
        steps.append(f"Paso 1: Analizando expresión lógica: {expression}")
        
        self.variables = self.get_variables(expression)
        steps.append(f"Paso 2: Variables identificadas: {', '.join(self.variables)}")
        
        if not self.variables:
            steps.append("Paso 3: No se encontraron variables proposicionales válidas.")
            return steps

        tokens = self.tokenize(expression)
        rpn = self.shunting_yard(tokens)
        steps.append(f"Paso 3: Notación Polaca Inversa (RPN): {' '.join(rpn)}")
        
        num_vars = len(self.variables)
        combinations = list(itertools.product([True, False], repeat=num_vars))
        
        steps.append(f"Paso 4: Construyendo tabla de verdad ({len(combinations)} combinaciones).")
        
        # Generar tabla de verdad
        header = " | ".join(self.variables) + " | Resultado"
        steps.append("-" * len(header))
        steps.append(header)
        steps.append("-" * len(header))
        
        for combo in combinations:
            ctx = dict(zip(self.variables, combo))
            res = self.evaluate_rpn(rpn, ctx)
            row_str = " | ".join(['V' if c else 'F' for c in combo]) + f" | {'V' if res else 'F'}"
            steps.append(row_str)
            
        steps.append("-" * len(header))
        steps.append("Paso 5: Evaluación completada con motor AST.")
        
        return steps
