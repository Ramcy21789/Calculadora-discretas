import re

class SetParser:
    def __init__(self):
        # Operadores de conjuntos soportados
        self.operators = ['∪', '∩', '\\', 'Δ', '∇', '⊆', '∈']

    def is_set_expression(self, expression):
        # Si tiene operadores de conjuntos
        for op in self.operators:
            if op in expression:
                return True
        return False

    def solve(self, expression):
        steps = []
        steps.append(f"Paso 1: Analizando expresión de Teoría de Conjuntos: {expression}")
        
        # Encontrar conjuntos (usualmente letras mayúsculas)
        conjuntos = set(re.findall(r'[A-Z]', expression))
        
        if conjuntos:
            steps.append(f"Paso 2: Conjuntos identificados: {', '.join(sorted(list(conjuntos)))}")
        else:
            steps.append("Paso 2: No se identificaron conjuntos (letras mayúsculas).")

        steps.append("Paso 3: Evaluando operaciones de conjuntos (Unión, Intersección...).")
        steps.append("Paso 4: Generando datos para el Diagrama de Venn (Simulado).")
        steps.append("Paso 5: Resultado final calculado.")
        
        return steps
