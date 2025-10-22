
def text_normalizer(text):
    import re
    import unidecode
    text = text.upper().strip()
    text = unidecode.unidecode(text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text
