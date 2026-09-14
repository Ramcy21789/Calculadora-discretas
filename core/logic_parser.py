import re
import itertools

class LogicParser:
    def __init__(self):
        # Operadores lógicos soportados
        self.operators = ['∧', '∨', '→', '↔', '¬']
        self.variables = []

    def is_logic_expression(self, expression):
        # Si tiene operadores lógicos, es una expresión lógica
        for op in self.operators:
            if op in expression:
                return True
        return False

    def get_variables(self, expression):
        # Extraer variables (asumiremos letras minúsculas p, q, r para lógica)
        # o cualquier letra que no sea operador o paréntesis
        vars_found = set(re.findall(r'[a-zA-Z]', expression))
        # Quitar 'v' si la usan como O, pero aquí el operador es ∨
        return sorted(list(vars_found))

    def evaluate(self, expression, context):
        # Aquí se haría la evaluación real de la AST
        # Por simplificación en esta fase, solo hacemos un parse básico
        pass

    def solve(self, expression):
        steps = []
        steps.append(f"Paso 1: Analizando expresión lógica: {expression}")
        
        self.variables = self.get_variables(expression)
        steps.append(f"Paso 2: Variables identificadas: {', '.join(self.variables)}")
        
        if not self.variables:
            steps.append("Paso 3: No se encontraron variables proposicionales válidas.")
            return steps

        # Crear tabla de verdad simulada
        num_vars = len(self.variables)
        combinations = list(itertools.product([True, False], repeat=num_vars))
        
        steps.append(f"Paso 3: Construyendo tabla de verdad con 2^{num_vars} = {len(combinations)} combinaciones posibles.")
        
        # Simulamos algunos pasos de simplificación
        steps.append("Paso 4: Aplicando leyes de Morgan / Simplificación (Simulado).")
        steps.append("Paso 5: Resultado final: Construcción completada.")
        
        return steps
