import json
import glob
import sys

def load_terms():
    terms = {}
    term_files = glob.glob('terms/*.json')
    for term_file in term_files:
        with open(term_file, 'r') as inp:
            term = json.load(inp)
            if not REVERSE:
                terms[term['term']] = term
            else:
                terms[term['citation-form']] = term
    terms_sorted = {key:terms[key] for key in sorted(list(terms.keys()))}
    return terms_sorted

def bold(render_str):
    if MODE == 'latex':
        return f"\\textbf{{{render_str}}}"
    else:
        return f"**{render_str}**"
    
def italics(render_str):
    if MODE == 'latex':
        return f"\\textit{{{render_str}}}"
    else:
        return f"*{render_str}*"
    
def unordered_list(render_strs):
    list_str = ""
    if MODE == 'latex':
        list_str += "\\begin{itemize}\n"
        for render_str in render_strs:
            list_str += f"\t\\item {render_str}\n"
        list_str += "\\end{itemize}\n"
    else:
        for render_str in render_strs:
            list_str += f"- {render_str}\n"
    return list_str

def ordered_list(render_strs):
    list_str = ""
    if MODE == 'latex':
        list_str += "\\begin{enumerate}\n"
        for render_str in render_strs:
            list_str += f"\t\\item {render_str}\n"
        list_str += "\\end{enumerate}\n"
    else:
        for i, render_str in enumerate(render_strs):
            list_str += f"{i}. {render_str}\n"
    return list_str

def render_term(term):
    render_str = ""

    # term translation
    if not REVERSE:
        render_str += bold(f"{term['term']}: {term['citation-form']}")
    else:
        render_str += bold(f"{term['citation-form']}: {term['term']}")
    render_str += "\n\n"

    # term definitions
    render_str += bold("sainmhíniú (ga):") + " " + term['def-ga'] + "\n"
    render_str += "\n"
    render_str += italics("sainmhíniú (en):") + " " + term['def-en'] + "\n"
    render_str += "\n"

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

    return render_str

def render_table(terms):
    if MODE == 'latex':
        render_str = "\\begin{table}[!ht]\n"
        render_str += "\t\\centering\n"
        render_str += "\t\\begin{tabular}{|l|l|}\n"
        render_str += "\t\\hline\n"
        if not REVERSE:
            render_str += "\t\t\\textbf{Béarla} & \\textbf{Gaeilge}\n"
        else:
            render_str += "\t\t\\textbf{Gaeilge} & \\textbf{Béarla}\n"
        for term_id in terms:
            term = terms[term_id]
            if not REVERSE:
                render_str += "\t\t" + bold(term['term']) + "&" + bold(term['citation-form']) + "\n"
            else:
                render_str += "\t\t" + bold(term['citation-form']) + "&" + bold(term['term']) + "\n"
        render_str += "\t\\end{tabular}\n"
        if not REVERSE:
            render_str += "\\caption{Liosta na dtéarma Béarla ar fad agus a leagan Gaeilge, cuirtear in ord de réir na dtéarma Béarla.}\n"
            render_str += "\\label{tab-terms-en-ga}\n"
        else:
            render_str += "\\caption{Liosta na dtéarma Béarla ar fad agus a leagan Gaeilge, cuirtear in ord de réir na dtéarma Gaeilge.}\n"
            render_str += "\\label{tab-terms-ga-en}\n"
        render_str += "\\end{table}"
    else:
        longest_en = 0
        longest_ga = 0
        for term_id in terms:
            term = terms[term_id]
            if len(term['term']) > longest_en:
                longest_en = len(term['term'])
            if len(term['citation-form']) > longest_ga:
                longest_ga = len(term['citation-form'])
        en_col = "**Béarla**".ljust(longest_en)
        ga_col = "**Gaeilge**".ljust(longest_ga)
        if not REVERSE:
            render_str = f"|{en_col}|{ga_col}|\n"
            render_str += f"|{'-'*longest_en}|{'-'*longest_ga}|\n"
        else:
            render_str = f"|{ga_col}|{en_col}|\n"
            render_str += f"|{'-'*longest_ga}|{'-'*longest_en}|\n"
        for term_id in terms:
            term = terms[term_id]
            en_col = term['term'].ljust(longest_en)
            ga_col = term['citation-form'].ljust(longest_ga)
            if not REVERSE:
                render_str += f"|{en_col}|{ga_col}|\n"
            else:
                render_str += f"|{ga_col}|{en_col}|\n"
    render_str += "\n"
    return render_str

if __name__ == '__main__':
    MODE = sys.argv[1]
    REVERSE = sys.argv[2] == '1'
    assert MODE in ("latex", "markdown"), f"mode must be latex or maskdown but is {MODE}"

    terms = load_terms()
    table_str = render_table(terms)
    print(table_str)
    for term_id in terms:
        render_str = render_term(terms[term_id])
        print(render_str)
