import javalang
from config import *

class LocInfo(object):
    def __init__(self, loc):
        self.filePath = getFilePath(loc)
        self.javaInfo = parseJavaFile(self.filePath)
        self.region = getRegin(loc)
        self.mIdx = mIndex(self.region, self.javaInfo)

    def getTokenPos(self):
        return {'sl': self.region['startLine'],
                'sc': self.region['startColumn'] - 1,
                'ec': self.region['endColumn'] - 1}
    
def getMethodBody(method, start, end):
    methodBody = method['file_lines'][start-1 : end]
    return methodBody

def getFilePath(loc):
    return loc['physicalLocation']['artifactLocation']['uri']

def parseJavaFile(file):
    file = project_path + "/" + file
    with open(file, 'r') as file:
        content = file.read()
        file_lines = content.split("\n")

    tree = javalang.parse.parse(content)
    method_lines = []
    for _, node in tree:
        if isinstance(node, javalang.tree.MethodDeclaration):
            start_line = node.position.line
            if len(method_lines) != 0 :
                method_lines[-1]['end'] = start_line - 1 # 模拟的end

            method_name = node.name
            param_types = [param.type.name for param in node.parameters]
            signature = f"{method_name}({', '.join(param_types)})"

            method_lines.append({
                'start': start_line,
                'end': len(file_lines),
                'sig': signature
            })
        elif isinstance(node, javalang.tree.ClassDeclaration):
            class_name = node.name # TODO 最好是有一个类型继承系统

    info = {'file_lines': file_lines, 'method_lines': method_lines, 'class': class_name}
    return info

def getRegin(loc):
    return loc['physicalLocation']['region']

def mIndex(region, jInfo):
    start = region['startLine']
    methods_lines = jInfo['method_lines']
    for i in range(len(methods_lines)):
        method = methods_lines[i]
        if start >= method['start'] and start < method['end']:
            return i