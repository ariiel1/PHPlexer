import re


TOKEN = {
    "<?php": "php-opening-tag",
    "?>": "php-closing-tag",
    "+": "addition_sign",
    "-": "minus_sign",
    "*": "multiply",
    "/": "divide",
    "=": "assign",
    "class": "class",
    "function": "function",
    "echo": "print-output",
    "$": "variable",
    ";": "semicolon",
    ".": "concate",
    "(": "bracket-opening",
    ")": "bracket-closing",
    "{": "curly-bracket-opening",
    "}": "curly-bracket-closing",
}


def identifier(row, col, line, result, file):
    length = 0
    while (re.match("[a-zA-Z]", line[col + length]) or re.match("[0-9]", line[col + length]) or re.match("_", line[col + length])):
        if (length == 0) and (re.match("[0-9]", line[col + length])):
            raise SyntaxError(f"{file}:{row + 1}:{col + length + 1}:INVALID VARIABLE NAME") 
        else:
            length += 1
    result.append([row + 1, col + 1, "type-identifier", line[col:(col + length)]])
    return length

def string_literal(row, col, line, result):
    length = 1
    stringlit = []
    while (re.match("[a-zA-Z]", line[col + length]) or re.match("[0-9]", line[col + length]) or re.match("[\'$= ]", line[col + length])):
        length += 1      
        if (re.match("\"", line[col + length])):
            stringlit.append(line[col+1:(col + length)])          
            stringlits = " ".join(map(str, stringlit)).replace(" ", "&nbsp").replace("'", "\'")
            stringlits = "\"" + stringlits + "\""
            print(stringlits)
            result.append([row + 1, col + 1, 'string-literal', stringlits])
    return length


def token_lexer(file):
    lines = []
    with open(file) as f:
        for i in f:
            lines.append(i)

    result = []
    for row, line in enumerate(lines):
        
        col = 0
        while (col < len(line)):
            
            # OPENING PHP TAG
            if (line[col:(col + len("<?php"))] == "<?php"):
                result.append([row + 1, col + 1, TOKEN["<?php"]])
                col += len("<?php")

            # CLOSING PHP TAG
            elif (line[col:(col + len("?>"))] == "?>"):
                result.append([row + 1, col + 1, TOKEN["?>"]])
                col += len("?>")

            # CLASS
            elif (line[col: col + len("class")] == "class"):
                result.append([row + 1, col + 1, TOKEN["class"]])
                col += len("class") + 1 
                col += identifier(row, col, line, result, file)

            # SPACE
            elif (line[col].isspace()):
                col += 1

            # FUNCTION
            elif (line[col:(col + len("function"))] == "function"):
                result.append([row + 1, col + 1, TOKEN["function"]])
                col += len("function") + 1
                col += identifier(row, col, line, result, file)

            # CHARACTERS
            elif (line[col] in ".;(){}*-/+="):
                result.append([row + 1, col + 1, TOKEN[line[col]]])
                col += 1

            # VARIABLE
            elif (line[col] == '$'):
                result.append([row + 1, col + 1, TOKEN['$']])
                col += 1
                col += identifier(row, col, line, result, file)

            # NUMBERS
            elif (re.match("[0-9]", line[col])):
                length = 0
                while (re.match("[0-9]", line[col+length])):
                    length += 1
                result.append([row + 1, col + 1, "number", int(line[col: col + length])])
                col += length

             # ECHO
            elif (line[col: col + len("echo")] == "echo"):
                result.append([row + 1, col + 1, TOKEN["echo"]])
                col += len("echo")

            # STRING LITERAL
            elif (re.match("\"", line[col])):
                # string_literal(row, col, line, result)
                col += string_literal(row, col, line, result)

            # ERROR
            else:
                raise Exception(f"{file}:{row + 1}:{col + 1}:INVALID SYNTAX")
                      

    return result


def print_output(result):
    for i in result:
        print(str(i).replace(", ", ",").strip("[]"))

def main():
    file = 'code.php'
    result = token_lexer(file)
    print_output(result)
    

main()