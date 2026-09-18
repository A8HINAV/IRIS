import re
import operator

import re
import operator

# Added '%' and '^' to the regex
MATH_PATTERN = re.compile(r'.*?([\d\.]+)\s*([\+\-\*\/xX\%\^])\s*([\d\.]+).*')

WHO_PATTERN = re.compile(r'^(?:who\s+(?:is|was|were))\s+(.+)', re.IGNORECASE)
WHERE_PATTERN = re.compile(r'^(?:where\s+(?:is|are)|map\s+of|location\s+of)\s+(.+)', re.IGNORECASE)
WHAT_PATTERN = re.compile(r'^(?:what\s+(?:is|are)|define|explain|how\s+does)\s+(.+)', re.IGNORECASE)

CITATION_RE = re.compile(r'\[.*?\]')
PRONUNCIATION_RE = re.compile(r'\(\s*/.*?/\s*\)')
EMPTY_PARENS_RE = re.compile(r'\(\s*;\s*\)|\(\s*\)')
MULTI_SPACE_RE = re.compile(r'\s+')

OPERATORS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    'x': operator.mul,
    'X': operator.mul,
    '%': operator.mod,  # Modulo support
    '^': operator.pow   # Exponent support
}

def secure_math_eval(query: str) -> dict:
    match = MATH_PATTERN.match(query.strip())
    if not match:
        return None
    try:
        num1 = float(match.group(1))
        op = match.group(2)
        num2 = float(match.group(3))
        
        # Guard against zero-division for both division and modulo
        if op in ['/', '%'] and num2 == 0:
            return {"entity": "Math Error", "category": "MATH EVALUATION", "result": "Cannot divide or modulo by zero."}
            
        result = OPERATORS[op](num1, num2)
        return {"entity": f"{num1} {op} {num2}", "category": "MATH EVALUATION", "result": f"{result:g}"}
    except Exception:
        return None

def secure_math_eval(query: str) -> dict:
    match = MATH_PATTERN.match(query.strip())
    if not match:
        return None
    try:
        num1 = float(match.group(1))
        op = match.group(2)
        num2 = float(match.group(3))
        
        if op == '/' and num2 == 0:
            return {"entity": "Math Error", "category": "MATH EVALUATION", "result": "Cannot divide by zero."}
            
        result = OPERATORS[op](num1, num2)
        return {"entity": f"{num1} {op} {num2}", "category": "MATH EVALUATION", "result": f"{result:g}"}
    except Exception:
        return None

def parse_natural_query(query: str) -> dict:
    clean_q = query.strip().rstrip("?.,!")
    
    # Check Math FIRST
    math_result = secure_math_eval(clean_q)
    if math_result:
        return math_result
    
    if match := WHO_PATTERN.match(clean_q):
        return {"entity": match.group(1).strip(), "category": "person"}
    if match := WHERE_PATTERN.match(clean_q):
        return {"entity": match.group(1).strip(), "category": "location"}
    if match := WHAT_PATTERN.match(clean_q):
        return {"entity": match.group(1).strip(), "category": "concept"}
        
    return {"entity": clean_q, "category": "general"}

def clean_scraped_text(raw_text: str, max_sentences: int = 5) -> list[str]:
    text = CITATION_RE.sub('', raw_text)
    text = PRONUNCIATION_RE.sub('', text)
    text = EMPTY_PARENS_RE.sub('', text)
    text = MULTI_SPACE_RE.sub(' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', text)
    return [s.strip() for s in sentences if len(s.strip()) > 15][:max_sentences]