import json
import glob
import sys

def load_terms():
    terms = {}
    term_files = glob.glob('../terms/*.json')
    for term_file in term_files:
        if DEBUG:
            print(f"loading from file: {term_file}")
        with open(term_file, 'r') as inp:
            term = json.load(inp)
            if not INDEX_GAEILGE:
                terms[term['term']] = term
            else:
                terms[term['citation-form']] = term
    terms_sorted = {key:terms[key] for key in sorted(list(terms.keys()))}
    return terms_sorted

def bold(render_str):
    if MODE == 'latex':
        return f"\\textbf{{{render_str}}}"
    elif MODE == 'markdown':
        return f"**{render_str}**"
    else: # html
        return f"<strong>{render_str}</strong>"

def italics(render_str):
    if MODE == 'latex':
        return f"\\textit{{{render_str}}}"
    elif MODE == 'markdown':
        return f"*{render_str}*"
    else: # html
        return f"<i>{render_str}</i>"
    
def unordered_list(render_strs):
    list_str = ""
    if MODE == 'latex':
        list_str += "\\begin{itemize}\n"
        for render_str in render_strs:
            list_str += f"\t\\item {render_str}\n"
        list_str += "\\end{itemize}\n"
    elif MODE == 'markdown':
        for render_str in render_strs:
            render_str = render_str.replace('*', '\\*')
            list_str += f"- {render_str}\n"
    else: # html
        list_str += "<ul>\n"
        for i, render_str in enumerate(render_strs):
            list_str += f"\t<li>{render_str}</li>\n"
        list_str += "</ul>\n"
    return list_str

def ordered_list(render_strs):
    list_str = ""
    if MODE == 'latex':
        list_str += "\\begin{enumerate}\n"
        for render_str in render_strs:
            list_str += f"\t\\item {render_str}\n"
        list_str += "\\end{enumerate}\n"
    elif MODE == 'markdown':
        for i, render_str in enumerate(render_strs):
            render_str = render_str.replace('*', '\\*')
            list_str += f"{i}. {render_str}\n"
    else: # html
        list_str += "<ol>\n"
        for i, render_str in enumerate(render_strs):
            list_str += f"\t<li>{render_str}</li>\n"
        list_str += "</ol>\n"
    return list_str

def render_term(term):
    render_str = ""

    # term translation
    if not INDEX_GAEILGE:
        render_str += bold(f"{term['term']} ({term['part-of-speech']}): {term['citation-form']}")
    else:
        render_str += bold(f"{term['citation-form']} ({term['part-of-speech']}): {term['term']}")
    render_str += "<br>\n"

    # term definitions
    render_str += italics("sainmhíniú (ga):") + " " + term['def-ga'] + "<br>"
    render_str += "\n"
    render_str += italics("sainmhíniú (en):") + " " + term['def-en'] + "\n"
    render_str += "\n"
    if MODE == 'html':
        render_str += '<br>'

    # term provenance
    render_str += "tagairtí:\n"
    prov_list = [f"{key}: {term['prov'][key]}" for key in term["prov"]]
    prov_list_citations = []
    for item in prov_list:
        if MODE == 'latex':
            item = item.replace("de-bhaldraithe", "De Bhaldraithe (1978) \\cite{de-bhaldraithe}")
            item = item.replace("dineen", "Dineen (1934) \\cite{dineen}")
            item = item.replace("focloir-beag", "Ó Dónaill et al. (1991) \\cite{focloir-beag}")
            item = item.replace("odonaill", "Ó Dónaill (1977) \\cite{odonaill}")
            item = item.replace("storchiste", "Williams et al. (2023) \\cite{storchiste}")
        else:
            item = item.replace("de-bhaldraithe", "De Bhaldraithe (1978)")
            item = item.replace("dineen", "Dineen (1934)")
            item = item.replace("focloir-beag", "Ó Dónaill et al. (1991)")
            item = item.replace("odonaill", "Ó Dónaill (1977)")
            item = item.replace("storchiste", "Williams et al. (2023)")
        prov_list_citations.append(item)
    render_str += unordered_list(prov_list_citations)
    render_str += "\n"

    # term notes
    render_str += "nótaí aistriúcháin:\n"
    render_str += unordered_list(term["notes"])
    render_str += "\n"

    if MODE == 'html':
        render_str = render_str.replace('$', '')

    return render_str

def render_terms(terms):
    render_strs = []
    for term_id in terms:
        render_strs.append(render_term(terms[term_id]))
    return render_strs

def render_table(terms):
    if MODE == 'latex':
        render_str = "\\begin{table}[!ht]\n"
        render_str += "\t\\centering\n"
        render_str += "\t\\begin{tabular}{|l|l|}\n"
        render_str += "\t\\hline\n"
        if not INDEX_GAEILGE:
            render_str += "\t\t\\textbf{Béarla} & \\textbf{Gaeilge}\n"
        else:
            render_str += "\t\t\\textbf{Gaeilge} & \\textbf{Béarla}\n"
        for term_id in terms:
            term = terms[term_id]
            if not INDEX_GAEILGE:
                render_str += "\t\t" + bold(term['term']) + "&" + bold(term['citation-form']) + "\n"
            else:
                render_str += "\t\t" + bold(term['citation-form']) + "&" + bold(term['term']) + "\n"
        render_str += "\t\\end{tabular}\n"
        if not INDEX_GAEILGE:
            render_str += "\\caption{Liosta na dtéarma Béarla ar fad agus a leagan Gaeilge, cuirtear in ord de réir na dtéarma Béarla.}\n"
            render_str += "\\label{tab-terms-en-ga}\n"
        else:
            render_str += "\\caption{Liosta na dtéarma Béarla ar fad agus a leagan Gaeilge, cuirtear in ord de réir na dtéarma Gaeilge.}\n"
            render_str += "\\label{tab-terms-ga-en}\n"
        render_str += "\\end{table}"
    elif MODE == 'markdown':
        longest_en = 0
        longest_ga = 0
        for term_id in terms:
            term = terms[term_id]
            if len(term['term']) > longest_en:
                longest_en = len(term['term'])
            if len(term['citation-form']) > longest_ga:
                longest_ga = len(term['citation-form'])
        longest_en += 1 # extra spacing around the term to makeit easuier to read in source
        longest_ga += 1 # extra spacing around the term to makeit easuier to read in source
        en_col = "**Béarla**".ljust(longest_en)
        ga_col = "**Gaeilge**".ljust(longest_ga)
        if not INDEX_GAEILGE:
            render_str = f"| {en_col}| {ga_col}|\n"
            render_str += f"|{'-'*(1+longest_en)}|{'-'*(1+longest_ga)}|\n"
        else:
            render_str = f"| {ga_col}| {en_col}|\n"
            render_str += f"|{'-'*(1+longest_ga)}|{'-'*(1+longest_en)}|\n"
        for term_id in terms:
            term = terms[term_id]
            en_col = term['term'].ljust(longest_en)
            ga_col = term['citation-form'].ljust(longest_ga)
            if not INDEX_GAEILGE:
                render_str += f"| {en_col}| {ga_col}|\n"
            else:
                render_str += f"| {ga_col}| {en_col}|\n"
    else: # html
        render_str = "<table>\n"
        if not INDEX_GAEILGE:
            render_str += "\t<tr>\n"
            render_str += "\t\t<th>Béarla</th>\n"
            render_str += "\t\t<th>Gaeilge</th>\n"
            render_str += "\t</tr>\n"
        else:
            render_str += "\t<tr>\n"
            render_str += "\t\t<th>Gaeilge</th>\n"
            render_str += "\t\t<th>Béarla</th>\n"
            render_str += "\t</tr>\n"
        for term_id in terms:
            render_str += "\t<tr>\n"
            term = terms[term_id]
            if not INDEX_GAEILGE:
                render_str += "\t\t<td>" + bold(term['term']) + "</td>\n"
                render_str += "\t\t<td>" + bold(term['citation-form']) + "</td>\n"
            else:
                render_str += "\t\t<td>" + bold(term['citation-form']) + "</td>\n"
                render_str += "\t\t<td>" + bold(term['term']) + "</td>\n"
            render_str += "\t</tr>\n"
        render_str += "</table><br>\n"
    render_str += "\n"
    return render_str

def write_terms(table_str, render_strs):
    if INDEX_GAEILGE:
        out_name = "tearmai"
    else:
        out_name = "terms"
    if MODE == 'markdown':
        ext = '.md'
    elif MODE == 'latex':
        ext = '.tex'
    else:
        ext = '.html'
    
    out_file = "../" + out_name + ext
    with open(out_file, 'w') as out:
        print(table_str, file=out)
        for render_str in render_strs:
            print(render_str, file=out)
    
    num_terms = len(terms)
    return num_terms, out_file

if __name__ == '__main__':
    assert not ('-md' in sys.argv and '-tex' in sys.argv), "only one mode can be set"
    if '-md' in sys.argv:
        MODE = 'markdown'
    elif '-tex' in sys.argv:
        MODE = 'latex'
    elif '-html' in sys.argv:
        MODE = 'html'
    else: #default to markdown
        MODE = 'markdown'

    assert not ('-ga' in sys.argv and '-en' in sys.argv), "only one index language can be set"
    if '-ga' in sys.argv:
        INDEX_GAEILGE = True
    elif '-en' in sys.argv:
        INDEX_GAEILGE = False
    else: # default to Gaeilge
        INDEX_GAEILGE = True

    if '-debug' in sys.argv:
        DEBUG = True
    else:
        DEBUG = False

    terms = load_terms()
    table_str = render_table(terms)
    render_strs = render_terms(terms)
    num_terms, out_file = write_terms(table_str, render_strs)
    print(f"Wrote {num_terms} terms to {out_file}")
