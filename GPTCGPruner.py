import subprocess
import sys
import json
from openai import OpenAI
from config import *
from Loc import *

client = OpenAI(
    api_key = GPT_key,
    base_url = "https://api.chatanywhere.tech/v1"
)

cmd = [
    'codeql', 'database', 'analyze', 
    db_path,
    '--format=sarifv2.1.0',
    f'--output={output_path}', 
    ql_path
]

process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                           stdout=sys.stdout, universal_newlines=True, shell=True, bufsize=1)

process.communicate()

def isInter(locInfo1, locInfo2):
    return locInfo1.filePath != locInfo2.filePath or locInfo1.mIdx != locInfo2.mIdx

def designQuery(loc1, loc2):
    l1 = LocInfo(loc1)
    l2 = LocInfo(loc2)
    if isInter(l1, l2): # inter
        callSitePos = l1.getTokenPos()['sl']
        methodBody = l1.javaInfo['file_lines']
        class2 = l2.javaInfo['class']
        method2Sig = l2.javaInfo['method_lines'][l2.mIdx]['sig']
        methodBody = "\n".join(methodBody)
        query = f"""please analyze the java code snippet surrounded by ```. First, retirve the callsite at line {callSitePos} of the code snippet. Then Based on the knwoledge of call graph construction, tell me whether the callsite can call the method {method2Sig} of class {class2}. Response in the provided format without other content: {{"Reason": "Explain the reason of your conclusion", "Answer": "one word Yes or No of the question"}}
```{methodBody}```
"""
    else: # intra
        tokenPos1 = l1.getTokenPos()
        tokenPos2 = l2.getTokenPos()
        methodBody = getMethodBody(l1.javaInfo, tokenPos1['sl'], tokenPos2['sl'])
        token1 = methodBody[0][tokenPos1['sc'] : tokenPos1['ec']]
        line2 = tokenPos2['sl'] - tokenPos1['sl']
        token2 = methodBody[line2][tokenPos2['sc'] : tokenPos2['ec']]
        methodBody = "\n".join(methodBody)
        query = f"""please analyze the java code surrounded by ```. Given that '{token1}' at line 1 of the code is tainted, decide whether '{token2}' at line {line2 + 1} of the code is tainted by data flow analysis. When analyzing a method call, use your existing knowledge to determine its changes to the variable's taint state. If you are not sure, you can also judge by inferring its behavior based on the semantics of the method name. In cases dealing with string manipulation APIs, if the origin string is tainted, then the result is also tainted. Response in the provided format without other content: {{"Reason": "Explain the reason of your conclusion", "Answer": "one word Yes or No of the question"}}
```{methodBody}```
"""
    # print(query)
    return query

def queryGPT(query):
    resp = client.chat.completions.create(
        messages = [
            {"role": "system", "content": "You are an expert in call graph construction, data flow analysis and taint analysis for Java programs"},
            {"role": "user", "content": query}
        ],
        model = "gpt-3.5-turbo"
    )
    content = resp.choices[0].message.content
    # print(content)
    return content

def loadJson(text):
    try:
        ret = json.loads(text)
    except:
        start = text.find('{') 
        end = text.find('}', start)
        ret = json.loads(text[start : end + 1])
    return ret

output = json.load(open(output_path))
results = output['runs'][0]['results']
for i in range(len(results)):
    result = results[i]
    codeFlows = result['codeFlows']
    for j in range(len(codeFlows)):
        codeFlow = codeFlows[j]
        threadFlows = codeFlow['threadFlows']
        for k in range(len(threadFlows)):
            threadFlow = threadFlows[k]
            isFP = False
            locations = threadFlow['locations']
            for v in range(len(locations) - 1):
                cur = locations[v]['location']
                nex = locations[v + 1]['location']
                query = designQuery(cur, nex)
                resp = loadJson(queryGPT(query))
                if resp['Answer'] != 'Yes':
                    isFP = True
                    break
            if isFP == True:
                print(f"result_{i}-path_{j} is a FP. Reason below:")
                print(resp['Reason'] + "\n")
            else:
                print(f"result_{i}-path_{j} is a TP.\n")