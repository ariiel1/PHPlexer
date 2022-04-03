import re


# list of tokens
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


# function to deal with identifiers
def identifier(row, col, line, result, file):
    length = 0
    while (re.match("[a-zA-Z]", line[col + length]) or re.match("[0-9]", line[col + length]) or re.match("_", line[col + length])):
        if (length == 0) and (re.match("[0-9]", line[col + length])):
            raise SyntaxError(f"{file}:{row + 1}:{col + length + 1}:INVALID VARIABLE NAME") 

        else:
            length += 1
    result.append([row + 1, col + 1, "type-identifier", line[col:(col + length)]])

    return length

# function to deal with string-literals
def string_literal(row, col, line, result, file):
    length = 1
    stringlit = []
    while (re.match("[a-zA-Z]", line[col + length]) or re.match("[0-9]", line[col + length]) or re.match("[\'$= ]", line[col + length])):
        length += 1      
        if (re.match("\"", line[col + length])):
            stringlit.append(line[col+1:(col + length)])          
            stringlits = " ".join(map(str, stringlit)).replace(" ", "&nbsp").replace("'", "\'")
            stringlits = "\"" + stringlits + "\""
            result.append([row + 1, col + 1, 'string-literal', stringlits])
            
        elif (line[col:(col + len("?>"))] == "?>"):
            raise SyntaxError(f"{file}:{row + 1}:{col + length + 1}:STRING LITERAL NOT TERMINATED") 

    return length


# reads file and loops through to turn it into tokens
def lexer(file):
    lines = []
    with open(file) as f:
        for i in f:
            lines.append(i)

    result = []
    in_comment = False
    for row, line in enumerate(lines):
        
        col = 0
        while (col < len(line)):
            
            # SINGLE LINE COMMENT
            if ((line[col:(col + len("//"))] == "//") or (line[col:(col + len("#"))] == "#")):
                break

            # MULTI LINE COMMENT
            if ((line[col:col + len("/*")] == "/*") and (not in_comment)):
                in_comment = True
                start_row = row    # for keeping position of comment tag in case of error
                start_col = col
                col += len("/*")
            if ((line[col:col + len("*/")] == "*/") and (in_comment)):
                in_comment = False
                col += len("*/")

            # OPENING PHP TAG
            if (line[col:(col + len("<?php"))] == "<?php" and (not in_comment)):
                result.append([row + 1, col + 1, TOKEN["<?php"]])
                col += len("<?php")

            # CLOSING PHP TAG
            elif (line[col:(col + len("?>"))] == "?>" and (not in_comment)):
                result.append([row + 1, col + 1, TOKEN["?>"]])
                col += len("?>")
                if (in_comment == True):
                    raise SyntaxError(f"{file}:{row + 1}:{col + 1}:COMMENT NOT TERMINATED")

            # CLASS
            elif (line[col: col + len("class")] == "class" and (not in_comment)):
                result.append([row + 1, col + 1, TOKEN["class"]])
                col += len("class") + 1 
                col += identifier(row, col, line, result, file)

            # SPACE
            elif (line[col].isspace()):
                col += 1

            # FUNCTION
            elif (line[col:(col + len("function"))] == "function" and (not in_comment)):
                result.append([row + 1, col + 1, TOKEN["function"]])
                col += len("function") + 1
                col += identifier(row, col, line, result, file)

            # CHARACTERS
            elif (line[col] in ".;(){}*-/+=" and (not in_comment)):
                result.append([row + 1, col + 1, TOKEN[line[col]]])
                col += 1

            # VARIABLE
            elif (line[col] == '$' and (not in_comment)):
                result.append([row + 1, col + 1, TOKEN['$']])
                col += 1
                col += identifier(row, col, line, result, file)

            # NUMBERS
            elif (re.match("[0-9]", line[col]) and (not in_comment)):
                length = 0
                while (re.match("[0-9]", line[col+length])):
                    length += 1
                result.append([row + 1, col + 1, "number", int(line[col: col + length])])
                col += length

             # ECHO
            elif (line[col: col + len("echo")] == "echo" and (not in_comment)):
                result.append([row + 1, col + 1, TOKEN["echo"]])
                col += len("echo")

            # STRING LITERAL
            elif (re.match("\"", line[col]) and (not in_comment)):
                col += string_literal(row, col, line, result, file)

            # BREAKS IF IN A COMMENT
            elif(in_comment):
                break

            # GENERAL SYNTAX ERROR
            else:
                raise SyntaxError(f"{file}:{row + 1}:{col + 1}:INVALID SYNTAX")
    
    # COMMENT NOT TERMINATED ERROR
    if (in_comment):
        raise SyntaxError(f"{file}:{start_row + 1}:{start_col + 1}:COMMENT NOT TERMINATED")
                      
    return result


# crude way of formatting the output
def print_output(result):
    for i in result:
        print(str(i).replace(", ", ",").replace(",'",",").replace("',",",").replace("']"," ").strip("[]"))

# main
def main():
    file = 'code.php'
    result = lexer(file)
    print_output(result)
    

main()
