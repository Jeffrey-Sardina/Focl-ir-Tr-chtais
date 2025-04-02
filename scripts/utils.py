# constants
version = '1.5'
SPACES_PER_INDENT = 4
THESIS_FOLDER_WRITE = "../builds/thesis"
DOWNLOADS_FOLDER_WRITE = "../builds/downloads"
SITE_FOLDER = '../builds/sitegen/'
TERMS_FOLDER_WRITE = '../builds/sitegen/terms/'
TERMS_FOLDER_READ = 'terms/'

# functions
def render_letter_header(letter):
    if letter == "A" or letter == "Á":
        return "A/Á"
    elif letter == "E" or letter == "É":
        return "E/É"
    elif letter == "I" or letter == "Í":
        return "I/Í"
    elif letter == "O" or letter == "Ó":
        return "O/Ó"
    elif letter == "U" or letter == "Ú":
        return "U/Ú"
    else:
        return letter

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
