# constants
version = '1.5 alfa'

# functions
def term_norm(term_str):
    if term_str[0] == '(':
        term_str = term_str[1:]
    if term_str[0:3] == 'to ':
        term_str = term_str[3:]
    term_str = term_str.lower()
    term_str = term_str.replace('á', 'a')
    term_str = term_str.replace('é', 'e')
    term_str = term_str.replace('í', 'i')
    term_str = term_str.replace('ó', 'o')
    term_str = term_str.replace('ú', 'u')
    return term_str

def termsort(terms):
    terms_sorted = sorted(
        terms,
        key=term_norm
    )
    return terms_sorted