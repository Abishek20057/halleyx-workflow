import re
from typing import Any, Dict

def evaluate_condition(condition: str, data: Dict[str, Any]) -> bool:
    if condition.strip().upper() == "DEFAULT":
        return True
    try:
        expr = condition
        expr = expr.replace("&&", " and ").replace("||", " or ")
        expr = re.sub(r'contains\((\w+),\s*["\'](.+?)["\']\)',
                      lambda m: f'"{m.group(2)}" in str({m.group(1)})', expr)
        expr = re.sub(r'startsWith\((\w+),\s*["\'](.+?)["\']\)',
                      lambda m: f'str({m.group(1)}).startswith("{m.group(2)}")', expr)
        expr = re.sub(r'endsWith\((\w+),\s*["\'](.+?)["\']\)',
                      lambda m: f'str({m.group(1)}).endswith("{m.group(2)}")', expr)
        result = eval(expr, {"__builtins__": {}}, data)
        return bool(result)
    except Exception as e:
        print(f"[RuleEngine] Error: {e}")
        return False

def find_next_step(rules, data: Dict[str, Any]):
    sorted_rules = sorted(rules, key=lambda r: r.priority)
    evaluated = []
    for rule in sorted_rules:
        result = evaluate_condition(rule.condition, data)
        evaluated.append({"rule": rule.condition, "priority": rule.priority, "result": result})
        if result:
            return rule.next_step_id, evaluated
    return None, evaluated

def validate_condition_syntax(condition: str) -> bool:
    if condition.strip().upper() == "DEFAULT":
        return True
    try:
        dummy = {w: 0 for w in re.findall(r'\b[a-zA-Z_]\w*\b', condition)}
        evaluate_condition(condition, dummy)
        return True
    except Exception:
        return False
