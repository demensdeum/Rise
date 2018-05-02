import sys
import os
import re

print("Rise to ECMAScript 5 transpiler")

def transpale(line, className):
    
    outputLine = line
    
    classMatch = re.match(r'class ([a-zA-Z]*)', line, re.M|re.I)
    if classMatch != None:
        className = classMatch.group(1)
        return "function " + className + "()\n"
    
    methodMatch = re.match(r'(.*) (method) ([a-zA-Z]*)\((.*)\)', line, re.M|re.I)
    if methodMatch != None:
        methodName = methodMatch.group(3)
        arguments = methodMatch.group(4)
        print(methodName)
        print(arguments)
        
        parsedArguments = []
        
        argumentsMatches = re.findall(r'([a-zA-Z]*) :', line, re.M|re.I)
        for argumentsMatch in argumentsMatches:
            print(argumentsMatch)
            parsedArguments.append(argumentsMatch)
        
        
        if className == "main":
            prefix = "var "
        else:
            prefix = "\tthis."
        
        return prefix + methodName + " = function("+ ",".join(parsedArguments) +")\n"
    
    classVariableDeclarationMatch = re.match(r'(.*) (declare) ([a-zA-Z]*) .*', line, re.M|re.I)
    if classVariableDeclarationMatch != None:
        classVariable = classVariableDeclarationMatch.group(3)
        
        return "\tthis." + classVariable + " = null;\n"
    
    localVariableDeclarationMatch = re.match(r'(.*)(declare) ([a-zA-Z]*)(.*)', line, re.M|re.I)
    if localVariableDeclarationMatch != None:
        space = localVariableDeclarationMatch.group(1)
        localVariable = localVariableDeclarationMatch.group(3)
        value = localVariableDeclarationMatch.group(4)
        
        return space + "var " + localVariable + value + "\n"
        
    formattedLine = line.replace("\t","")
    formattedLine = formattedLine.replace("\n", "") 
    
    if len(formattedLine) > 1:
        return line[:len(line) - 1] + ";\n"
    
    return line

if len(sys.argv) < 2:
    print("Not enough arguments: " + str(sys.argv))
    print("Command: python rise2es5.py [Sources Directory] [Output ES5 file]")
    print("Example: python rise2es5.py src /usr/user/sources/app/riseLibrary.es5")
    
sourceDirectory = sys.argv[1]
outputFilePath = sys.argv[2]
    
buffer = ""

for root, dirs, files in os.walk(sourceDirectory):
    for file in files:
        if file.endswith(".rise"):
            
            filePath = os.path.join(root, file) 
            
            className = file[:len(file) - len(".rise")]
            
            print(filePath)
            
            file = open(filePath, 'r')
            for line in file:
                buffer = buffer + transpale(line, className)
                
            buffer = buffer + "\n\n"
            
print(buffer)

file = open(outputFilePath, 'w')
file.write(buffer)

