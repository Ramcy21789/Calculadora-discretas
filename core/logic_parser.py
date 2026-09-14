import re
import itertools

class ASTNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def __str__(self):
        if not self.left and not self.right:
            return self.value
        elif self.value == '¬':
            # don't put parenthesis around simple variables for negation
            if not self.left.left and not self.left.right:
                return f"¬{self.left}"
            return f"¬({self.left})"
        else:
            return f"({self.left} {self.value} {self.right})"

class LogicParser:
    def __init__(self):
        self.operators = ['∧', '∨', '→', '↔', '⊕']
        self.unary = ['¬']
        self.precedence = {'↔': 1, '→': 2, '⊕': 3, '∨': 4, '∧': 5, '¬': 6}
        self.variables = []

    def is_logic_expression(self, expression):
        for op in self.operators + self.unary:
            if op in expression:
                return True
        return False

    def get_variables(self, expression):
        vars_found = set(re.findall(r'[a-zA-Z]', expression))
        if 'v' in vars_found and 'v' not in expression.replace('v', ''):
            pass
        # Remove true/false literal constants if we eventually add them (V, F)
        if 'V' in vars_found: vars_found.remove('V')
        if 'F' in vars_found: vars_found.remove('F')
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

    def build_ast(self, rpn):
        stack = []
        try:
            for token in rpn:
                if token.isalpha():
                    stack.append(ASTNode(token))
                elif token == '¬':
                    node = ASTNode(token, left=stack.pop())
                    stack.append(node)
                elif token in self.operators:
                    right = stack.pop()
                    left = stack.pop()
                    node = ASTNode(token, left=left, right=right)
                    stack.append(node)
            return stack[0] if stack else None
        except IndexError:
            return None

    def simplify_step(self, node):
        """Intenta aplicar una regla lógica al nodo actual (de abajo hacia arriba).
           Devuelve (nuevo_nodo, nombre_de_regla_aplicada) o (nodo, None) si no hay cambios.
        """
        if not node:
            return None, None
            
        # Simplificar hijos primero
        if node.left:
            new_left, rule = self.simplify_step(node.left)
            if rule:
                node.left = new_left
                return node, rule
        if node.right:
            new_right, rule = self.simplify_step(node.right)
            if rule:
                node.right = new_right
                return node, rule

        # Reglas en el nodo actual
        val = node.value

        # Doble negación: ¬(¬p) => p
        if val == '¬' and node.left and node.left.value == '¬':
            return node.left.left, "Doble Negación (¬¬p ≡ p)"

        # Leyes de De Morgan
        if val == '¬' and node.left and node.left.value in ['∧', '∨']:
            inner_op = node.left.value
            new_op = '∨' if inner_op == '∧' else '∧'
            new_node = ASTNode(new_op, 
                               left=ASTNode('¬', left=node.left.left), 
                               right=ASTNode('¬', left=node.left.right))
            return new_node, "Leyes de De Morgan (¬(p " + inner_op + " q) ≡ ¬p " + new_op + " ¬q)"

        # Implicación: p → q => ¬p ∨ q
        if val == '→':
            new_node = ASTNode('∨', left=ASTNode('¬', left=node.left), right=node.right)
            return new_node, "Definición de Implicación (p → q ≡ ¬p ∨ q)"

        # Idempotencia
        if val in ['∧', '∨']:
            if str(node.left) == str(node.right):
                return node.left, f"Idempotencia (p {val} p ≡ p)"

        # Modus Ponens detect (simplified pattern matching): (p ∧ (p → q)) => q or similar equivalents
        # Since we just convert p -> q to ¬p ∨ q, we might match distributive instead:
        # p ∧ (¬p ∨ q) => (p ∧ ¬p) ∨ (p ∧ q) => F ∨ (p ∧ q) => p ∧ q. 
        # But let's look for explicit Modus Ponens in raw form before implication converts it if possible? 
        # Actually, bottom-up simplifies → first. Let's match (p ∧ (¬p ∨ q)) -> (p ∧ q) as "Reducción (Silogismo Disyuntivo)"
        if val == '∧':
            l_str = str(node.left)
            r_str = str(node.right)
            if node.right.value == '∨':
                if node.right.left.value == '¬' and str(node.right.left.left) == l_str:
                    return ASTNode('∧', left=node.left, right=node.right.right), "Silogismo Disyuntivo / Modus Ponens"
            if node.left.value == '∨':
                if node.left.left.value == '¬' and str(node.left.left.left) == r_str:
                    return ASTNode('∧', left=node.left.right, right=node.right), "Silogismo Disyuntivo / Modus Ponens"

        # Identidad / Dominación (simplificado)
        # Asumiendo 'V' es Verdadero y 'F' es Falso (literales)
        if val == '∧':
            if str(node.left) == 'F' or str(node.right) == 'F':
                return ASTNode('F'), "Dominación (p ∧ F ≡ F)"
            if str(node.left) == 'V': return node.right, "Identidad (V ∧ p ≡ p)"
            if str(node.right) == 'V': return node.left, "Identidad (p ∧ V ≡ p)"
            # Complemento: p ∧ ¬p = F
            if node.right.value == '¬' and str(node.left) == str(node.right.left): return ASTNode('F'), "Complemento (p ∧ ¬p ≡ F)"
            if node.left.value == '¬' and str(node.right) == str(node.left.left): return ASTNode('F'), "Complemento (¬p ∧ p ≡ F)"

        if val == '∨':
            if str(node.left) == 'V' or str(node.right) == 'V':
                return ASTNode('V'), "Dominación (p ∨ V ≡ V)"
            if str(node.left) == 'F': return node.right, "Identidad (F ∨ p ≡ p)"
            if str(node.right) == 'F': return node.left, "Identidad (p ∨ F ≡ p)"
            # Complemento: p ∨ ¬p = V
            if node.right.value == '¬' and str(node.left) == str(node.right.left): return ASTNode('V'), "Tercer Excluido (p ∨ ¬p ≡ V)"
            if node.left.value == '¬' and str(node.right) == str(node.left.left): return ASTNode('V'), "Tercer Excluido (¬p ∨ p ≡ V)"

        return node, None

    def evaluate_rpn_table(self, rpn, context):
        """Evalúa un RPN para una asignación específica de variables (Tabla de Verdad)"""
        stack = []
        try:
            for token in rpn:
                if token.isalpha():
                    # Check for literal true/false
                    if token == 'V': stack.append(True)
                    elif token == 'F': stack.append(False)
                    else: stack.append(context.get(token, False))
                elif token == '¬':
                    val = stack.pop()
                    stack.append(not val)
                elif token in self.operators:
                    right = stack.pop()
                    left = stack.pop()
                    if token == '∧': stack.append(left and right)
                    elif token == '∨': stack.append(left or right)
                    elif token == '→': stack.append((not left) or right)
                    elif token == '↔': stack.append(left == right)
                    elif token == '⊕': stack.append(left != right)
            return stack[0] if stack else False
        except IndexError:
            return False

    def solve(self, expression):
        steps = []
        steps.append(f"📌 Expresión original: {expression}")
        
        self.variables = self.get_variables(expression)
        
        tokens = self.tokenize(expression)
        rpn = self.shunting_yard(tokens)
        ast = self.build_ast(rpn)

        if not ast:
            steps.append("❌ Error: Expresión mal formada.")
            return steps

        # --- FASE 1: DESARROLLO SIMBÓLICO PASO A PASO ---
        steps.append("─────────────────────────────────")
        steps.append("🧠 Simplificación Paso a Paso (Leyes de Inferencia):")
        
        max_steps = 15
        current_step = 1
        current_ast = ast
        steps.append(f"   Inicio: {str(current_ast)}")
        
        while current_step <= max_steps:
            # We copy the AST string to detect changes, 
            # though our simplify_step modifies in place, we can just track the rule returned
            import copy
            ast_copy = copy.deepcopy(current_ast) # basic deepcopy for our simple tree
            
            new_ast, rule = self.simplify_step(current_ast)
            if rule:
                steps.append(f"   Paso {current_step}: Aplicando {rule}")
                steps.append(f"          = {str(new_ast)}")
                current_ast = new_ast
                current_step += 1
            else:
                break
        
        if current_step == 1:
            steps.append("   (La expresión ya está en su forma más simple o requiere reglas complejas)")
        else:
            steps.append(f"   Resultado simplificado: {str(current_ast)}")
        
        # --- FASE 2: TABLA DE VERDAD ---
        steps.append("─────────────────────────────────")
        if not self.variables:
            steps.append("✅ No hay variables proposicionales para construir una tabla de verdad (solo literales).")
            # Evaluate literal
            res = self.evaluate_rpn_table(rpn, {})
            steps.append(f"   Resultado final: {'Verdadero (V)' if res else 'Falso (F)'}")
            return steps

        num_vars = len(self.variables)
        combinations = list(itertools.product([True, False], repeat=num_vars))
        
        steps.append(f"📊 Tabla de Verdad ({len(combinations)} combinaciones):")
        
        header = " | ".join(self.variables) + " | Resultado"
        steps.append("-" * len(header))
        steps.append(header)
        steps.append("-" * len(header))
        
        tautologia = True
        contradiccion = True

        for combo in combinations:
            ctx = dict(zip(self.variables, combo))
            res = self.evaluate_rpn_table(rpn, ctx)
            
            if res: contradiccion = False
            else: tautologia = False

            row_str = " | ".join(['V' if c else 'F' for c in combo]) + f" | {'V' if res else 'F'}"
            steps.append(row_str)
            
        steps.append("-" * len(header))
        
        if tautologia:
            steps.append("✅ Conclusión: La expresión es una TAUTOLOGÍA (Siempre Verdadera).")
        elif contradiccion:
            steps.append("❌ Conclusión: La expresión es una CONTRADICCIÓN (Siempre Falsa).")
        else:
            steps.append("⚠️ Conclusión: La expresión es una CONTINGENCIA (Depende de las variables).")
            
        return steps

# monkey patch deepcopy for ASTNode
def ast_deepcopy(node):
    if not node: return None
    return ASTNode(node.value, ast_deepcopy(node.left), ast_deepcopy(node.right))
import copy
copy.deepcopy = lambda obj: ast_deepcopy(obj) if isinstance(obj, ASTNode) else copy._deepcopy(obj) 
# wait, better to just implement it as a method on ASTNode
ASTNode.__deepcopy__ = lambda self, memo: ASTNode(self.value, copy.deepcopy(self.left, memo), copy.deepcopy(self.right, memo))
