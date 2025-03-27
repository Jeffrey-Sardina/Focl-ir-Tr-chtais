#!/usr/bin/env python

from constants import version
import json
import glob
import sys
import random
import os
from utils import termsort

BUILDS_FOLDER_WRITE = "../builds/"

def load_terms():
    terms = {}
    term_files = glob.glob('../terms/*.json')
    for term_file in term_files:
        if DEBUG:
            print(f"loading from file: {term_file}")
        with open(term_file, 'r') as inp:
            term = json.load(inp)
            if not INDEX_GAEILGE:
                if not term['term'] in terms:
                    terms[term['term']] = term
                else:
                    de_dupe_id = "#" + str(int(random.random() * 1_000_000))
                    terms[term['term'] + de_dupe_id] = term
            else:
                if not term['citation-form'] in terms:
                    terms[term['citation-form']] = term
                else:
                    de_dupe_id = "#" + str(int(random.random() * 1_000_000))
                    terms[term['citation-form'] + de_dupe_id] = term
    terms_sorted = {key:terms[key] for key in termsort(terms)}
    return terms_sorted

def term_heading(render_str):
    if MODE == 'latex':
        if not THESIS_FMT:
            return f"\\subsection*{{{render_str}}} \\addcontentsline{{toc}}{{subsection}}{{{render_str}}}"
        else:
            return f"\\subsubsection*{{{render_str}}}"
    elif MODE == 'markdown':
        return f"### {render_str}"
    else: # html
        return f"<h3>{render_str}</h3>"

def bold(render_str):
    if MODE == 'latex':
        return f"\\textbf{{{render_str}}}"
    elif MODE == 'markdown':
        return f"**{render_str}**"
    else: # html
        return f"<strong>{render_str}</strong>"

def italics(render_str):
    # for italic headings only!
    if MODE == 'latex':
        return f" \\noindent \\textit{{{render_str}}}"
    elif MODE == 'markdown':
        return f"*{render_str}*"
    else: # html
        return f"<i>{render_str}</i>"
    
def simple_italics(render_str):
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

def ga_italics_filter(render_str):
    # some terms are not translated and should be italicised
    to_italicise = [
        "softmax",
        "ReLU"
    ]
    for item in to_italicise:
        render_str = render_str.replace(item, italics(item))
    return render_str

def render_term(term):
    render_str = ""

    # term translation
    if not INDEX_GAEILGE:
        render_str += term_heading(f"{term['term']} ({term['part-of-speech']}): {term['citation-form']}")
    else:
        render_str += term_heading(f"{term['citation-form']} ({term['part-of-speech']}): {term['term']}")
    if MODE != 'latex':
        render_str += "<br>"
    render_str += "\n"

    # term definitions
    render_str += italics("Sainmhíniú (ga):") + " " + ga_italics_filter(term['def-ga']) + "\n"
    if MODE != 'latex':
        render_str += "<br>"
    else:
        render_str += "\\\\"
    render_str += "\n"
    render_str += italics("Sainmhíniú (en):") + " " + term['def-en'] + "\n"
    if MODE == 'latex':
        render_str += "\\\\"
    render_str += "\n"
    if MODE == 'html':
        render_str += '<br>'

    # term provenance
    render_str += italics("Tagairtí:") + "\n"
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
    render_str += italics("Nótaí Aistriúcháin:") + "\n"
    render_str += ga_italics_filter(unordered_list(term["notes"]))
    render_str += "\n"

    if MODE == 'html':
        render_str = render_str.replace('$', '')
    if MODE == 'latex':
        render_str = render_str.replace(" '", " `")
        render_str = render_str.replace(' "', ' ``')

        # hard coded exceptions that are hard to automaticlly detect
        render_str = render_str.replace("1 / (meán-rang)", "1 / (me\\acute{a}n-rang)")
        render_str = render_str.replace("meán(1 / rang_i)", "1 / (me\\acute{a}n(1 / rang_i)")

    return render_str

def render_terms(terms):
    render_strs = []

    if MODE == 'latex':
        if not THESIS_FMT:
            render_strs.append("\\newpage \\section{Téarmaí}")
        else:
            render_strs.append("\\newpage \\subsection{Téarmaí}")
    elif MODE == 'markdown':
        render_strs.append("## Téarmaí")
    else: # html
        render_strs.append("<h2>Téarmaí</h2>")

    for term_id in terms:
        render_strs.append(render_term(terms[term_id]))
    return render_strs

def render_table(terms):
    if MODE == 'latex':
        if not THESIS_FMT:
            render_str = "\\newpage \\section{Achoimre na dTéarmaí}\n"
        else:
            render_str = "\\subsection{Achoimre na dTéarmaí}\n"
        render_str += "\\begin{longtable}{|l|l|}\n"
        render_str += "\t\\hline\n"
        if not INDEX_GAEILGE:
            render_str += "\t\t\\textbf{Béarla} & \\textbf{Gaeilge}\\\\ \\hline \n"
        else:
            render_str += "\t\t\\textbf{Gaeilge} & \\textbf{Béarla}\\\\ \\hline \n"
        for term_id in terms:
            term = terms[term_id]
            if not INDEX_GAEILGE:
                render_str += "\t\t" + term['term'] + "&" + term['citation-form'] + "\\\\ \\hline \n"
            else:
                render_str += "\t\t" + term['citation-form'] + "&" + term['term'] + "\\\\ \\hline \n"
        if not INDEX_GAEILGE:
            render_str += "\\caption{Liosta na dtéarma Béarla ar fad agus a leagan Gaeilge, curtha in ord de réir na dtéarmaí Béarla.}\n"
            render_str += "\\label{tab-terms-en-ga}\n"
        else:
            render_str += "\\caption{Liosta na dtéarma Béarla ar fad agus a leagan Gaeilge, curtha in ord de réir na dtéarmaí Gaeilge.}\n"
            render_str += "\\label{tab-terms-ga-en}\n"
        render_str += "\\end{longtable}"
    elif MODE == 'markdown':
        render_str = "## Achoimre na dTéarmaí\n"
        longest_en = 0
        longest_ga = 0
        for term_id in terms:
            term = terms[term_id]
            if len(term['term']) > longest_en:
                longest_en = len(term['term'])
            if len(term['citation-form']) > longest_ga:
                longest_ga = len(term['citation-form'])
        longest_en += 1 # extra spacing around the term to make it easuier to read in source
        longest_ga += 1 # extra spacing around the term to make it easuier to read in source
        en_col = "**Béarla**".ljust(longest_en)
        ga_col = "**Gaeilge**".ljust(longest_ga)
        if not INDEX_GAEILGE:
            render_str += f"| {en_col}| {ga_col}|\n"
            render_str += f"|{'-'*(1+longest_en)}|{'-'*(1+longest_ga)}|\n"
        else:
            render_str += f"| {ga_col}| {en_col}|\n"
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
        render_str = "<h2>Achoimre na dTéarmaí</h2>"
        render_str += "<table>\n"
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

def get_header():
    if MODE == 'latex':
        if not THESIS_FMT:
            header = f"""\\documentclass{{article}}
                \\usepackage[a4paper, margin=1in]{{geometry}}
                \\usepackage{{graphicx}} % Required for inserting images
                \\usepackage{{longtable}}
                \\usepackage[hidelinks]{{hyperref}} %custom
                \\hypersetup{{
                    colorlinks,
                    linktoc=all,
                    citecolor=black,
                    filecolor=black,
                    linkcolor=black,
                    urlcolor=blue
                }}

                \\title{{Focloir Tráchtais v{version}}}
                \\author{{Jeffrey Seathrún Sardina}}
                \\date{{Márta 2025}}

                % setup bibliography
                \\usepackage[
                    backend=biber,
                    style=numeric,
                    sorting=ynt
                ]{{biblatex}}
                \\addbibresource{{refs.bib}}

                \\begin{{document}}

                \\maketitle

                \\newpage
                \\tableofcontents
            """
        else:
            header = "\\section{An Foclóir Tráchtais} \\label{focloir-trachtais-content}\n"
            if not INDEX_GAEILGE:
                header += f"The full contents of the latest version of the \\textit{{Foclóir Tráchtais}}, version {version} \\cite{{focloir-trachtais}}, are reproduced below.\n"
            else:
                header += f"Tá na téarmaí uilig sa bhFoclóir Tráchtais, leagan {version} \\cite{{focloir-trachtais}}, le feiceáil thíos.\n"
    elif MODE == 'markdown':
        header = f"# Foclóir Tráchtais v{version}\n"
        header += "**Jeffrey Seathrún Sardina**<br>\n"
        header += "**Eanáir 2025**\n"
    else: # html
        header = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <meta http-equiv="Content-type" content="text/html; charset=UTF-8">
            </head>

            <body>

            <body>
            <h1>Foclóir Tráchtais v{version}</h1>
            <strong>Jeffrey Seathrún Sardina</strong>
            <br>
            <strong>Eanáir 2025</strong>

        """
    return header

def get_footer():
    if MODE == 'latex':
        if not THESIS_FMT:
            footer = """
                \\newpage
                \\printbibliography[
                    title={Tagairtí},
                    heading=bibintoc
                ]
                \\end{document}
            """
        else:
            footer = ""
    elif MODE == 'markdown':
        footer = ""
    else: # html
        footer = "</body>"
    return footer

def write_terms(table_str, render_strs):
    if INDEX_GAEILGE:
        out_name = f"focloir-trachtais-v{version}-ga"
    else:
        out_name = f"focloir-trachtais-v{version}-en"
    if THESIS_FMT:
        out_name += "-thesis"
    if MODE == 'markdown':
        ext = '.md'
    elif MODE == 'latex':
        ext = '.tex'
    else:
        ext = '.html'

    header = get_header()
    footer = get_footer()
    
    if not os.path.exists(BUILDS_FOLDER_WRITE):
        os.makedirs(BUILDS_FOLDER_WRITE)
    out_file = os.path.join(BUILDS_FOLDER_WRITE, out_name + ext)
    with open(out_file, 'w') as out:
        print(header, file=out)
        print(table_str, file=out)
        for render_str in render_strs:
            print(render_str, file=out)
        print(footer, file=out)

    num_terms = len(terms)
    return num_terms, out_file

def main():
    global terms
    terms = load_terms()
    table_str = render_table(terms)
    render_strs = render_terms(terms)
    num_terms, out_file = write_terms(table_str, render_strs)
    print(f"Wrote {num_terms} terms to {out_file}")

def get_index_ga():
    if '-ga' in sys.argv:
        assert not '-en' in sys.argv, "Only index language can be set"
        index_ga = True
    elif '-en' in sys.argv:
        assert not '-ga' in sys.argv, "Only index language can be set"
        index_ga = False
    else: # default to Gaeilge
        assert False, "Must give a index language via -en or -ga"
    return index_ga

def get_format():
    if '-md' in sys.argv:
        assert not '-tex' in sys.argv, "Only one mode can be set"
        assert not '-html' in sys.argv, "Only one mode can be set"
        mode = 'markdown'
    elif '-tex' in sys.argv:
        assert not '-html' in sys.argv, "Only one mode can be set"
        assert not '-md' in sys.argv, "Only one mode can be set"
        mode = 'latex'
    elif '-html' in sys.argv:
        assert not '-md' in sys.argv, "Only one mode can be set"
        assert not '-tex' in sys.argv, "Only one mode can be set"
        mode = 'html'
        mode = 'html'
    else: #default to markdown
        assert False, "Must give a mode via -md, -tex, or -html"
    return mode

if __name__ == '__main__':
    #defaults
    DEBUG = False
    THESIS_FMT = False

    # general args
    if '-debug' in sys.argv:
        DEBUG = True

    if '-nv' in sys.argv:
        # run all versions
        assert not '-thesis' in sys.argv, "-nv and -thesis cannot be used together as arguments"
        assert not '-en' in sys.argv, "-nv already produces output in -en and -ga, and cannot accept those arguments"
        assert not '-ga' in sys.argv, "-nv already produces output in -en and -ga, and cannot accept those arguments"
        assert not '-md' in sys.argv, "-nv already produces output in all format and does not accept specific formatting arguments"
        assert not '-tex' in sys.argv, "-nv already produces output in all format and does not accept specific formatting arguments"
        assert not '-html' in sys.argv, "-nv already produces output in all format and does not accept specific formatting arguments"
        for MODE in ['markdown', 'latex', 'html']:
            for INDEX_GAEILGE in [True, False]:
                DEBUG = False
                main()

    elif '-thesis' in sys.argv:
        # make the output in the format needed for inclusion in my thesis
        assert not '-nv' in sys.argv, "-thesis and -nv cannot be used together as arguments"
        assert not '-md' in sys.argv, "-thesis internally sets -tex, and cannot accept formatting arguments"
        assert not '-tex' in sys.argv, "-thesis internally sets -tex, and cannot accept formatting arguments"
        assert not '-html' in sys.argv, "-thesis internally sets -tex, and cannot accept formatting arguments"
        MODE = 'latex'
        INDEX_GAEILGE = get_index_ga()
        THESIS_FMT = True
        main()

    else:
        INDEX_GAEILGE = get_index_ga()
        MODE = get_format()
        main()
