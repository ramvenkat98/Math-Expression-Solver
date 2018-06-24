import math
import copy

#convert math expression string to list of operators and numbers
def convertToList(s):
    acceptedSymbols = ["+", "-", "*", "/", "(", ")"]
    L = []
    for i in range(len(s)):
        if s[i] in acceptedSymbols: L.append(s[i])
        elif len(L) == 0 or L[-1] in acceptedSymbols: L.append(s[i])
        else: L[-1] = L[-1] + s[i]
    for i in range(len(L) - 2):
        if L[i] == "(" and L[i+1] not in acceptedSymbols and L[i+2] == ")":
            L[i], L[i+2] = None, None
    newL = []
    for x in L:
        if x != None: newL.append(x)
    return newL

def mainEval(s):
    L = convertToList(s)
    newS = "".join(L)
    try:
        res = list(map(lambda x: "".join(x), evaluateExpression(L)))
    except:
        res = ["Error; could not evaluate"]
    res = list(map(lambda x: " = " + x, res))
    return "\n".join([newS] + res)

def evaluateExpression(expression):
    if len(expression) == 1: return [expression]
    expression, result = evalSymbols(copy.deepcopy(expression), [], ["*", "/"])
    expression, result = evalSymbols(copy.deepcopy(expression), copy.deepcopy(result), ["+", "-"])
    return result

def evalSymbols(expression, result, symbols):
    #assert(len(symbols) == 2) #can generalize to more than 2 later if needed
    while symbols[0] in expression or symbols[1] in expression:
        #print("current result = ", result)
        i = math.inf
        if symbols[0] in expression: i = expression.index(symbols[0])
        if symbols[1] in expression: i = min(expression.index(symbols[1]), i)
        assert(i != 0 and i != len(expression) - 1)
        if expression[i-1] == ")":
            assert(i != 1)
            #print("orig expr", expression)
            expression, steps = evalBefore(expression, i-1)
            #print("steps", steps)
            result += steps
        elif expression[i+1] == "(":
            assert(i != len(expression) - 2)
            expression, steps = evalAfter(expression, i+1)
            result += steps
        else:
            #print("exp, i", expression, i)
            step = evalElementary(expression[i], expression[i-1], expression[i+1])
            #print("step", step)
            if i-1 !=0 and i+1 != len(expression) - 1 and expression[i-2] == "(" and expression[i+2] == ")":
                expression = expression[:i-2] + [step] + expression[i+3:]
            else:    
                expression = expression[:i-1] + [step] + expression[i+2:]
            #print("fin1", expression)
            result.append(expression)
    return expression, result

#Performs elementary operation
def evalElementary(opr, op1, op2):
    op1, op2 = float(op1), float(op2)
    toNum = lambda op: int(op) if math.isclose(op, int(op)) else op
    op1, op2 = toNum(op1), toNum(op2)
    op1, op2 = float(op1), float(op2)
    if opr == "*": result = op1 * op2
    if opr == "/": result = op1 / op2
    if opr == "+": result = op1 + op2
    if opr == "-": result = op1 - op2
    res = toNum(float(result))
    if isinstance(res, int): return str(res)
    else: return "%.4f"%res

#evaluate bracketed expression before operator
def evalBefore(expression, j):
    #print("expr = ", expression)
    i = j+1
    start = getBefore(expression, i-1)
    if start == j-2: return expression[:start]+[expression[start+1]]+expression[start+3:], []
    #print("Start = ", start)
    #print("expr = ", expression[start:i-1])
    res = evaluateExpression(expression[start+1:i-1])
    resList = [expression[:start] + step + expression[i-1:] for step in res[:-1]]
    expression = expression[:start] + res[-1] + expression[i:]
    resList.append(expression)
    #print("fin expr", expression)
    return expression, resList

#evaluate bracketed expression after operator
def evalAfter(expression, j):
    #print("expr", expression)
    i = j-1
    end = getAfter(expression, i+1)
    if end == j+2: return expression[:j]+[expression[j+1]]+expression[j+3:], []
    res = evaluateExpression(expression[i+2:end])
    #print("res = ", res)
    resList = [expression[:i+2] + step + expression[end:] for step in res[:-1]]
    expression = expression[:i+1] + res[-1] + expression[end+1:]
    resList.append(expression)
    #print("fin expr", expression)
    return expression, resList
    
#find opening bracket that matches closing bracket at j
def getBefore(expression, j):
    openers, closers = 0, 0
    for i in range(j, -1, -1):
        if expression[i] == "(": openers += 1
        if expression[i] == ")": closers += 1
        if openers == closers: return i

#find closing bracket that matches opening bracket at j
def getAfter(expression, j):
    openers, closers = 0, 0
    for i in range(j, len(expression)):
        if expression[i] == "(": openers += 1
        if expression[i] == ")": closers += 1
        if openers == closers: return i
    