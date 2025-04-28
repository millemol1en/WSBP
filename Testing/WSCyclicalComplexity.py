import ast
import re

class WSCyclicalComplexity(ast.NodeVisitor):
    def __init__(self):
        self.function_metrics = {}
        self._current_function_name = None
        self.grades = []

    # []
    def calc_wscc(self, code : str) -> ( dict | int ):
        self.function_metrics.clear()
        tree = ast.parse(code)
        self.visit(tree)
        aggregate_wscc = sum(func["wsc_score"] for func in self.function_metrics.values())
        return (self.function_metrics, aggregate_wscc)

    # [] Handle a function declaration:
    def visit_FunctionDef(self, node):
        # []
        self._current_function_name = node.name                                                             # Save the name of the function we are currently working with
        keyword_count, max_depth, selector_score, regex_score = self._analyze_function(node.body)           # Retrieve the number of keywords, max depth, selector score and regex score [if present]
        function_calls = self.function_metrics.get(node.name, {}).get("function_calls", 0)                  # Retrieve the number of function calls within a function

        # []
        wsc_score = keyword_count + (1.5 * max_depth) + (0.5 * selector_score) + (0.75 * function_calls) + (2 * regex_score)
        self.function_metrics[node.name] = {
            "keywords": keyword_count,
            "depth": max_depth,
            "selector_complexity": selector_score,
            "function_calls": function_calls,
            "regex_score": regex_score,
            "wsc_score": round(wsc_score, 2),
            "grade": self.grade(wsc_score)
        }
        self.grades.append(self.grade(wsc_score))
        self.generic_visit(node)  # In case there are inner functions

    # [] Handle an asynchronous function:
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    # []
    def _analyze_function(self, body):
        self._current_keyword_count = 0
        self._current_selector_score = 0
        self._current_regex_score = 0
        for stmt in body:
            self.visit(stmt)
        max_depth = self._compute_depth(body, 0)
        return self._current_keyword_count, max_depth, self._current_selector_score, self._current_regex_score

    # [] 
    def _compute_depth(self, nodes, current_depth):
        max_depth = current_depth
        for node in nodes:
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.Match, ast.match_case, ast.Yield)):
                self._current_keyword_count += 1
                nested = self._compute_depth(ast.iter_child_nodes(node), current_depth + 1)
                max_depth = max(max_depth, nested)
            elif hasattr(node, 'body'):
                for field in ('body', 'orelse', 'finalbody', 'handlers'):
                    inner = getattr(node, field, [])
                    if isinstance(inner, list):
                        nested = self._compute_depth(inner, current_depth)
                        max_depth = max(max_depth, nested)
        return max_depth
    
    # [] 
    #    Take note that multiplication indicates a higher emphasis on their typical impact on complexity
    def css_complexity(self, selector: str) -> int:
        score = 0
        score += selector.count(' ')               # Descendant
        score += selector.count('>') * 2           # Child
        score += selector.count('+') * 2           # Adjacent sibling
        score += selector.count('~') * 3           # General sibling
        score += selector.count(':') * 3           # Pseudo-class
        score += selector.count('::') * 3          # Pseudo-element
        score += selector.count('[') * 2           # Attribute
        score += selector.count('.')               # Class
        score += selector.count('#')               # ID
        score += selector.count('*') * 2           # Universal selector
        score += selector.count(',') * 2           # Multiple selectors
        return score
    
    # []
    #    Take note that multiplication indicates a higher emphasis on their typical impact on complexity
    def xpath_complexity(self, query: str) -> int:
        score = 0
        score += query.count('/')                                                                           # Basic path depth
        score += query.count('//') * 2                                                                      # Double slash increases scope
        score += query.count('[') * 2                                                                       # Attribute specification
        score += query.count('@')                                                                           # Targeting specific ID or Class
        score += query.count('text()')                                                                      # Text node access
        score += query.count('./')                                                                          # Context-based navigation
        score += len(re.findall(r'\b(?:and|or)\b', query)) * 2                                              # Logic operands      
        score += len(re.findall(r'\b(?:contains|starts-with|normalize-space|position|last)\(', query)) * 2  # Built-in functions
        return score

    def regex_complexity(self, pattern: str) -> int:
        score = 0
        score += len(pattern) // 6                   # 1 point per 6 characters
        score += pattern.count('(')                  # 1 point per group
        score += pattern.count('(?:') * 2            # Non-capturing groups are tricky
        score += pattern.count('(?=') * 2            # Lookaheads are tricky
        score += pattern.count('|')                  # Branching
        return score

    # []
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            # []
            attr_name = node.func.attr

            # [] Handle '.xpath' and '.css' queries:
            if attr_name in {'xpath', 'css'} and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    query = arg.value
                    if attr_name == 'xpath':
                        self._current_selector_score += self.xpath_complexity(query)
                    else:
                        self._current_selector_score += self.css_complexity(query)

            # [] Handle BeautifulSoup queries
            elif attr_name in {'find', 'find_all'} and node.args:
                tag_arg = node.args[0]
                if isinstance(tag_arg, ast.Constant) and isinstance(tag_arg.value, str):
                    query = tag_arg.value
                    score = 1      
                    if len(node.args) > 1 or any(kw.arg in {"class_", "id", "attrs"} for kw in node.keywords):
                        score += 2
                    self._current_selector_score += score

            # [] 
            elif isinstance(node.func, ast.Attribute) and node.func.attr in {'match', 'search'}:
                if isinstance(node.func.value, ast.Name) and node.func.value.id == 're' and node.args:
                    arg = node.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        pattern = arg.value
                        self._current_regex_score += self.regex_complexity(pattern)

            # [] Track all 'self.some_func()' calls within a function to calculate its extent of dependency:
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "self":
                if self._current_function_name:
                    self.function_metrics.setdefault(self._current_function_name, {}).setdefault("function_calls", 0)
                    self.function_metrics[self._current_function_name]["function_calls"] += 1

        self.generic_visit(node)

    # [] Specifically used to handle cases in which a ".xpath()" or ".css()" call is chained together 
    def post_selector_chain_complexity(self, node):
        """Traverse chained calls after .xpath() or .css() to account for method chaining complexity."""
        score = 0
        current = node
        while isinstance(current.parent, ast.Call) or isinstance(current.parent, ast.Attribute) or isinstance(current.parent, ast.Subscript):
            current = current.parent
            if isinstance(current, ast.Call) and isinstance(current.func, ast.Attribute):
                score += 1  # Each method call like .get(), .strip(), etc.
            elif isinstance(current, ast.Subscript):
                score += 1  # Slicing like [1:], [:2], etc.
        return score
    
    # [] Grading system is based entirely on the "radon" package:
    #    
    def grade(self, score):
        if score <= 5:
            return "A"
        elif score <= 10:
            return "B"
        elif score <= 14:
            return "C"
        elif score <= 18:
            return "D"
        elif score <= 20:
            return "E"
        else:
            return "F"