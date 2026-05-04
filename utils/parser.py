import re

def extract_commands(code):
    return re.findall(r'commands=\["(.*?)"\]', code)
