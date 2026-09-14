import re

# Conjuntos universales de ejemplo para demostración
CONJUNTOS_DEMO = {
    'A': {1, 2, 3, 4, 5},
    'B': {3, 4, 5, 6, 7},
    'C': {5, 6, 7, 8, 9},
    'U': {1, 2, 3, 4, 5, 6, 7, 8, 9, 10},
}

class SetParser:
    def __init__(self):
        # Operadores de conjuntos soportados
        self.operators = ['∪', '∩', '\\', 'Δ', '∇', '⊆', '∈']
        self.conjuntos = dict(CONJUNTOS_DEMO)

    def is_set_expression(self, expression):
        for op in self.operators:
            if op in expression:
                return True
        # Also detect uppercase letter followed by uppercase letter (set expression)
        if re.search(r'[A-Z][∪∩\\Δ∇⊆∈]|[∪∩\\Δ∇⊆∈][A-Z]', expression):
            return True
        return False

    def _get_conjuntos_en_expresion(self, expression):
        """Extrae los conjuntos identificados en la expresión."""
        return sorted(set(re.findall(r'[A-Z]', expression)))

    def _evaluar_token(self, token):
        """Devuelve el conjunto correspondiente a un token."""
        if token in self.conjuntos:
            return self.conjuntos[token]
        # Complemento: 'A° or ¬A - not used directly but via expression
        return set()

    def _aplicar_operacion(self, set_a, op, set_b, universo=None):
        """Aplica una operación binaria entre dos conjuntos."""
        if universo is None:
            universo = self.conjuntos.get('U', set_a | set_b)
        if op == '∪':
            return set_a | set_b
        elif op == '∩':
            return set_a & set_b
        elif op == '\\':
            return set_a - set_b
        elif op == 'Δ':
            return set_a.symmetric_difference(set_b)
        elif op == '∇':
            return set_a.symmetric_difference(set_b)
        return set()

    def _tokenize(self, expression):
        """Tokeniza la expresión separando conjuntos y operadores."""
        tokens = []
        i = 0
        while i < len(expression):
            char = expression[i]
            if char.isupper():
                tokens.append(('SET', char))
            elif char in ['∪', '∩', '\\', 'Δ', '∇']:
                tokens.append(('OP', char))
            elif char == '⊆':
                tokens.append(('REL', '⊆'))
            elif char == '∈':
                tokens.append(('REL', '∈'))
            elif char == '(':
                tokens.append(('LPAREN', '('))
            elif char == ')':
                tokens.append(('RPAREN', ')'))
            i += 1
        return tokens

    def _evaluar_expresion(self, expression):
        """Evalúa la expresión de conjuntos de forma iterativa (izquierda a derecha)."""
        tokens = self._tokenize(expression)
        
        # Resolver paréntesis anidados primero (simplificado)
        # Para expresiones simples: A OP B OP C
        result = None
        current_op = None
        universo = self.conjuntos.get('U', set(range(1, 11)))
        
        for tipo, valor in tokens:
            if tipo == 'SET':
                conj = self.conjuntos.get(valor, set())
                if result is None:
                    result = set(conj)
                elif current_op:
                    result = self._aplicar_operacion(result, current_op, conj, universo)
                    current_op = None
            elif tipo == 'OP':
                current_op = valor
        
        return result if result is not None else set()

    def solve(self, expression):
        steps = []
        venn_data = None
        
        conjuntos_en_exp = self._get_conjuntos_en_expresion(expression)
        universo = self.conjuntos.get('U', set(range(1, 11)))
        
        steps.append(f"📌 Expresión recibida: {expression}")
        steps.append(f"─────────────────────────────────")
        
        # Mostrar los conjuntos con sus valores
        steps.append("📦 Conjuntos utilizados:")
        for c in conjuntos_en_exp:
            conj = self.conjuntos.get(c, set())
            steps.append(f"   {c} = {{{', '.join(map(str, sorted(conj)))}}}")
        steps.append(f"   U = {{{', '.join(map(str, sorted(universo)))}}}")
        steps.append(f"─────────────────────────────────")

        # Detectar operación principal
        tokens = self._tokenize(expression)
        operadores = [v for t, v in tokens if t == 'OP']
        
        # Evaluar paso a paso
        steps.append("⚙️  Evaluación paso a paso:")
        
        result_set = None
        current_op = None
        step_num = 1

        for tipo, valor in tokens:
            if tipo == 'SET':
                conj = self.conjuntos.get(valor, set())
                if result_set is None:
                    result_set = set(conj)
                elif current_op:
                    prev_set = set(result_set)
                    result_set = self._aplicar_operacion(result_set, current_op, conj, universo)
                    op_name = self._nombre_operacion(current_op)
                    steps.append(f"   Paso {step_num}: {{{', '.join(map(str, sorted(prev_set)))}}} {current_op} {{{', '.join(map(str, sorted(conj)))}}} = {{{', '.join(map(str, sorted(result_set)))}}}")
                    steps.append(f"   ({op_name})")
                    step_num += 1
                    current_op = None
            elif tipo == 'OP':
                current_op = valor
            elif tipo == 'REL':
                # Relación de subconjunto o pertenencia
                if valor == '⊆' and len(conjuntos_en_exp) >= 2:
                    set_a = self.conjuntos.get(conjuntos_en_exp[0], set())
                    set_b = self.conjuntos.get(conjuntos_en_exp[1], set()) if len(conjuntos_en_exp) > 1 else set()
                    es_subconj = set_a.issubset(set_b)
                    steps.append(f"   Paso {step_num}: ¿{conjuntos_en_exp[0]} ⊆ {conjuntos_en_exp[1]}? → {'✅ Verdadero' if es_subconj else '❌ Falso'}")
                    step_num += 1

        steps.append(f"─────────────────────────────────")
        if result_set is not None:
            steps.append(f"✅ Resultado: {{{', '.join(map(str, sorted(result_set)))}}}")
            steps.append(f"   Cardinalidad: |resultado| = {len(result_set)}")

        # Generar datos para el diagrama de Venn
        if len(conjuntos_en_exp) >= 2:
            set_a = self.conjuntos.get(conjuntos_en_exp[0], set())
            set_b = self.conjuntos.get(conjuntos_en_exp[1], set())
            set_c = self.conjuntos.get(conjuntos_en_exp[2], set()) if len(conjuntos_en_exp) > 2 else None

            if set_c:
                venn_data = {
                    "tipo": "venn3",
                    "labels": [conjuntos_en_exp[0], conjuntos_en_exp[1], conjuntos_en_exp[2]],
                    "solo_a": sorted(set_a - set_b - set_c),
                    "solo_b": sorted(set_b - set_a - set_c),
                    "solo_c": sorted(set_c - set_a - set_b),
                    "a_b": sorted(set_a & set_b - set_c),
                    "a_c": sorted(set_a & set_c - set_b),
                    "b_c": sorted(set_b & set_c - set_a),
                    "a_b_c": sorted(set_a & set_b & set_c),
                    "resultado": sorted(result_set) if result_set else [],
                    "operacion": ''.join([v for t, v in tokens if t == 'OP'])
                }
            else:
                venn_data = {
                    "tipo": "venn2",
                    "labels": [conjuntos_en_exp[0], conjuntos_en_exp[1]],
                    "solo_a": sorted(set_a - set_b),
                    "solo_b": sorted(set_b - set_a),
                    "interseccion": sorted(set_a & set_b),
                    "resultado": sorted(result_set) if result_set else [],
                    "operacion": ''.join([v for t, v in tokens if t == 'OP'])
                }

        return steps, venn_data

    def _nombre_operacion(self, op):
        nombres = {
            '∪': 'Unión: todos los elementos de ambos conjuntos',
            '∩': 'Intersección: elementos comunes a ambos conjuntos',
            '\\': 'Diferencia: elementos en el primero pero no en el segundo',
            'Δ': 'Diferencia simétrica: elementos en uno u otro, pero no en ambos',
            '∇': 'Diferencia simétrica',
        }
        return nombres.get(op, op)
