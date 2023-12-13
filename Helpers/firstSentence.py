# EXTRACTING FIRST SENTENCE FROM TEXT (given string)
import regex as re
def first_sentence(content):
    content = ''.join(content.split('\r\n\r\n')[2:])
    no_acronyms = re.sub(r'(?<!\w)([A-Z])\.', r'\1', content)
    pattern = r"^([^.!?]+)"
    print(re.findall(pattern, no_acronyms))



