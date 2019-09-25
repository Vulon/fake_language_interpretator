import re

def readFile(path = r'sample program.txt'):
    with open(path, "r") as file:
        text = file.read()
        return text

def do_text_preprocess(text):
    text = re.sub(r'\b;', ' ;', text)
    text = re.sub(r'\s', ' ', text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def tokenize(text):
    return re.split(r'\s', text)

def getTokensFromFile(path = r'sample program.txt'):
    text = readFile(path)
    return tokenize(do_text_preprocess(text))


