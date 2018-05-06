import sys
import os
import re
from sets import Set

print("Rise to ECMAScript 5 transpiler")

def transpale(line, className):
    
    global entityType, classDeclarations, methodDeclarations
    
    outputLine = line
    
    classMatch = re.match(r'class ([a-zA-Z]*)', line, re.M|re.I)
    if classMatch != None:
        
        classDeclarations = Set()
        
        className = classMatch.group(1)
        
        entityType = "class"
        
        return "function " + className + "()\n"

    protocolMatch = re.match(r'protocol ([a-zA-Z]*)', line, re.M|re.I)
    if protocolMatch != None:
        protocolName = protocolMatch.group(1)
        
        entityType = "protocol"
        
        return "function " + protocolName + "()\n"
    
    builtinPrintMatch = re.match(r'(.*)RiseBuiltInMethods\.print\((.*)\)', line, re.M|re.I)
    if builtinPrintMatch != None:
        prefix = builtinPrintMatch.group(1)
        arguments = builtinPrintMatch.group(2)
        return prefix + "console.log(" + arguments + ");\n"
    
    builtinMapClassMatch = re.match(r'(.*) = RiseBuiltInClasses\.Map.*', line, re.M|re.I)
    if builtinMapClassMatch != None:
        prefix = builtinMapClassMatch.group(1)
        return prefix + " = {};\n"

    builtinListClassMatch = re.match(r'(.*) = RiseBuiltInClasses\.List.*', line, re.M|re.I)
    if builtinListClassMatch != None:
        prefix = builtinListClassMatch.group(1)
        return prefix + " = [];\n"
    
    methodMatch = re.match(r'(.*) (method) ([a-zA-Z]*)\((.*)\)', line, re.M|re.I)
    if methodMatch != None:
        
        methodDeclarations = Set()
        
        methodName = methodMatch.group(3)
        arguments = methodMatch.group(4)
        print(methodName)
        print(arguments)
        
        parsedArguments = []
        
        argumentsMatches = re.findall(r'([a-zA-Z]*) :', line, re.M|re.I)
        for argumentsMatch in argumentsMatches:
            print(argumentsMatch)
            parsedArguments.append(argumentsMatch)
            methodDeclarations.add(argumentsMatch)
        
        if className == "main":
            prefix = "var "
        else:
            prefix = "\tthis."
            
        postfix = ""
        
        if entityType == "protocol":
            postfix = " {}"
        
        return prefix + methodName + " = function("+ ", ".join(parsedArguments) +")" + postfix + "\n"
    
    classVariableDeclarationMatch = re.match(r'(.*) (declare) ([a-zA-Z]*) .*', line, re.M|re.I)
    if classVariableDeclarationMatch != None:
        classVariable = classVariableDeclarationMatch.group(3)
        
        classDeclarations.add(classVariable)
        
        return "\tthis." + classVariable + " = null;\n"
    
    localVariableDeclarationMatch = re.match(r'(.*)(declare) ([a-zA-Z]*)(.*)', line, re.M|re.I)
    if localVariableDeclarationMatch != None:
        space = localVariableDeclarationMatch.group(1)
        localVariable = localVariableDeclarationMatch.group(3)
        value = localVariableDeclarationMatch.group(4)
        
        methodDeclarations.add(localVariable)
        
        return space + "var " + localVariable + value + ";\n"
        
    methodCallMatch = re.match(r'(.*)(\(.*\))', line, re.M|re.I)
    if methodCallMatch != None:
        prefix = methodCallMatch.group(1)
        
        formattedString = line.replace("\t", "")
        formattedString = formattedString.replace("\n", "")
        
        if len(formattedString) < 4:
            return line
        
        if formattedString[:3] == "if ":
            return line
        
        if formattedString[:4] == "for":
            return line
        
        arguments = methodCallMatch.group(2)
        print(prefix)
        print(arguments)
        
        parsedArguments = []
        
        argumentsMatches = re.findall(r' : ([" a-zA-Z]*)', line, re.M|re.I)
        for argumentsMatch in argumentsMatches:
            print(argumentsMatch)
            
            if argumentsMatch in classDeclarations:
                argumentsMatch = "this." + argumentsMatch
            
            parsedArguments.append(argumentsMatch)
        
        if len(parsedArguments) < 1:
            return line
        
        return prefix + "("+ ", ".join(parsedArguments) +");\n"
                
    formattedLine = line.replace("\t","")
    formattedLine = formattedLine.replace("\n", "") 
    
    if len(formattedLine) > 1 and formattedLine[:4] != "else":
        return line[:len(line) - 1] + ";\n"
    
    return line

if len(sys.argv) < 2:
    print("Not enough arguments: " + str(sys.argv))
    print("Command: python rise2es5.py [Sources Directory] [Output ES5 file]")
    print("Example: python rise2es5.py src /usr/user/sources/app/riseLibrary.es5")
    
sourceDirectory = sys.argv[1]
outputFilePath = sys.argv[2]
    
buffer = ""

entityType = None
classDeclarations = Set()
methodDeclarations = Set()

def addScopeToDeclarations(line):
    
    global classDeclarations, methodDeclarations
    
    allowedList = ["this", "console", "globalTapController", "globalMainController", "window"]
    
    if "framesCounter += 1" in line:
        print("stop")
    
    variableCallMatch = re.match(r'\t*([a-zA-Z]*)\.', line, re.M|re.I)
    if variableCallMatch != None:
        variableCall = variableCallMatch.group(1)
        print("scope for variable: " + variableCall)
        
        if variableCall in allowedList:
            pass
        
        elif variableCall in classDeclarations:
            line = re.sub(r'(\t*)([a-zA-Z]*)\.', r'\1this.\2.', line, 1)
            
            return line
        
        elif variableCall not in methodDeclarations:
            print("error for line: " + line + "; no declaration '" + variableCall + "' in class or method")
            exit(1)

    variableCallMatch = re.match(r'\t*([a-zA-Z]*)\[', line, re.M|re.I)
    if variableCallMatch != None:
        variableCall = variableCallMatch.group(1)
        print("scope for variable: " + variableCall)
        
        if variableCall in allowedList:
            pass
        
        elif variableCall in classDeclarations:
            line = re.sub(r'(\t*)([a-zA-Z]*)\[', r'\1this.\2[', line, 1)
            
            return line
        
        elif variableCall not in methodDeclarations:
            print("error for line: " + line + "; no declaration '" + variableCall + "' in class or method")
            exit(1)
        
    variableCallMatch = re.match(r'\t*([a-zA-Z]*) =', line, re.M|re.I)
    if variableCallMatch != None:
        variableCall = variableCallMatch.group(1)
        print("scope for variable: " + variableCall)
        
        if variableCall in allowedList:
            pass
        
        elif variableCall in classDeclarations:
            line = re.sub(r'(\t*)([a-zA-Z]*) =', r'\1this.\2 = ', line, 1)
            
            return line
        
        elif variableCall not in methodDeclarations:
            print("error for line: " + line + "; no declaration '" + variableCall + "' in class or method")
            exit(1)
    
    variableCallMatch = re.match(r'\t*if \(([a-zA-Z]*)\.', line, re.M|re.I)
    if variableCallMatch != None:
        variableCall = variableCallMatch.group(1)
        print("scope for variable: " + variableCall)
        
        if variableCall in allowedList:
            pass
        
        elif variableCall in classDeclarations:
            line = re.sub(r'(\t*if \()([a-zA-Z]*)\.', r'\1this.\2.', line, 1)
            
            return line
        
        elif variableCall not in methodDeclarations:
            print("error for line: " + line + "; no declaration '" + variableCall + "' in class or method")
            exit(1)     

    variableCallMatch = re.match(r'\t*if \(([a-zA-Z]*) ', line, re.M|re.I)
    if variableCallMatch != None:
        variableCall = variableCallMatch.group(1)
        print("scope for variable: " + variableCall)
        
        if variableCall in allowedList:
            pass
        
        elif variableCall in classDeclarations:
            line = re.sub(r'(\t*if \()([a-zA-Z]*) ', r'\1this.\2 ', line, 1)
            
            return line
        
        elif variableCall not in methodDeclarations:
            print("error for line: " + line + "; no declaration '" + variableCall + "' in class or method")
            exit(1)     
        
    variableCallMatch = re.match(r'\t*return ([a-zA-Z]*)\.', line, re.M|re.I)
    if variableCallMatch != None:
        variableCall = variableCallMatch.group(1)
        print("scope for variable: " + variableCall)
        
        if variableCall in allowedList:
            pass
        
        elif variableCall in classDeclarations:
            line = re.sub(r'(\t*return )([a-zA-Z]*)\.', r'\1this.\2.', line, 1)
            
            return line
        
        elif variableCall not in methodDeclarations:
            print("error for line: " + line + "; no declaration '" + variableCall + "' in class or method")
            exit(1)          

    variableCallMatch = re.match(r'\t*return ([a-zA-Z]*)\[', line, re.M|re.I)
    if variableCallMatch != None:
        variableCall = variableCallMatch.group(1)
        print("scope for variable: " + variableCall)
        
        if variableCall in allowedList:
            pass
        
        elif variableCall in classDeclarations:
            line = re.sub(r'(\t*return )([a-zA-Z]*)\[', r'\1this.\2[', line, 1)
            
            return line
        
        elif variableCall not in methodDeclarations:
            print("error for line: " + line + "; no declaration '" + variableCall + "' in class or method")
            exit(1)

    variableCallMatch = re.match(r'\t*return ([a-zA-Z]*)\;', line, re.M|re.I)
    if variableCallMatch != None:
        variableCall = variableCallMatch.group(1)
        print("scope for variable: " + variableCall)
        
        if variableCall in allowedList:
            pass
        
        elif variableCall in classDeclarations:
            line = re.sub(r'(\t*return )([a-zA-Z]*)\;', r'\1this.\2;', line, 1)
            
            return line
        
        elif variableCall not in methodDeclarations:
            print("error for line: " + line + "; no declaration '" + variableCall + "' in class or method")
            exit(1)          

    variableCallMatch = re.match(r'\t*([a-zA-Z]*)\ ', line, re.M|re.I)
    if variableCallMatch != None:
        variableCall = variableCallMatch.group(1)
        print("scope for variable: " + variableCall)
        
        if len(variableCall) < 1:
            pass
        
        elif variableCall in allowedList:
            pass
        
        elif variableCall in classDeclarations:
            line = re.sub(r'(\t*)([a-zA-Z]*)\ ', r'\1this.\2 ', line, 1)
            
            return line        
        
    return line

for root, dirs, files in os.walk(sourceDirectory):
    for file in files:
        if file.endswith(".rise"):
            
            entityType = None
            
            filePath = os.path.join(root, file) 
            
            className = file[:len(file) - len(".rise")]
            
            print(filePath)
            
            file = open(filePath, 'r')
            for line in file:
                buffer = buffer + addScopeToDeclarations(transpale(line, className))
                
            buffer = buffer + "\n\n"
            
print(buffer)

file = open(outputFilePath, 'w')
file.write(buffer)

