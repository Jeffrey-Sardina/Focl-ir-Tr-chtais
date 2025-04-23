'''
no longtable
new preamble
'''

#!/usr/bin/env python

import json
import glob
import sys
import random
import os
from utils import version, termsort, term_norm, render_letter_header, SPACES_PER_INDENT, THESIS_FOLDER_WRITE, DOWNLOADS_FOLDER_WRITE

def load_terms():
    terms = {}
    term_files = glob.glob('../terms/*.json')
    for term_file in term_files:
        if DEBUG:
            print(f"loading from file: {term_file}")
        with open(term_file, 'r') as inp:
            term = json.load(inp)
            if not term['term'] in terms:
                terms[term['term']] = term
            else:
                de_dupe_id = "#" + str(int(random.random() * 1_000_000))
                terms[term['term'] + de_dupe_id] = term
    terms_sorted = {key:terms[key] for key in termsort(terms)}
    return terms_sorted

def term_heading(render_str):
    return f"\\subsubsection*{{{render_str}}}"

def bold(render_str):
    return f"\\textbf{{{render_str}}}"

def italics(render_str):
    return f" \\noindent \\textit{{{render_str}}}"
    
def simple_italics(render_str):
    return f"\\textit{{{render_str}}}"
    
def unordered_list(render_strs):
    list_str = ""
    list_str += "\\begin{itemize}\n"
    for render_str in render_strs:
        list_str += f"\t\\item {render_str}\n"
    list_str += "\\end{itemize}\n"
    return list_str

def ordered_list(render_strs):
    list_str = ""
    list_str += "\\begin{enumerate}\n"
    for render_str in render_strs:
        list_str += f"\t\\item {render_str}\n"
    list_str += "\\end{enumerate}\n"
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
    render_str += term_heading(f"{term['term']}: {term['citation-form']}")
    render_str += "\n"
    render_str += term['part-of-speech']
    render_str += "\n\n"

    # term definitions
    render_str += italics("Sainmhíniú (ga):") + " " + ga_italics_filter(term['def-ga']) + "\n"
    render_str += "\\\\"
    render_str += "\n"
    render_str += italics("Sainmhíniú (en):") + " " + term['def-en'] + "\n"
    render_str += "\\\\"
    render_str += "\n"

    # term provenance
    render_str += italics("Tagairtí:") + "\n"
    prov_list = [f"{key}: {term['prov'][key]}" for key in term["prov"]]
    prov_list_citations = []
    for item in prov_list:
        item = item.replace("de-bhaldraithe", "De Bhaldraithe (1978) \\cite{de-bhaldraithe}")
        item = item.replace("dineen", "Dineen (1934) \\cite{dineen}")
        item = item.replace("focloir-beag", "Ó Dónaill et al. (1991) \\cite{focloir-beag}")
        item = item.replace("odonaill", "Ó Dónaill (1977) \\cite{odonaill}")
        item = item.replace("storchiste", "Williams et al. (2023) \\cite{storchiste}")
        prov_list_citations.append(item)
    render_str += unordered_list(prov_list_citations)
    render_str += "\n"

    # term notes
    render_str += italics("Nótaí Aistriúcháin:") + "\n"
    render_str += ga_italics_filter(unordered_list(term["notes"]))
    render_str += "\n"

    # formatting
    render_str = render_str.replace(" '", " `")
    render_str = render_str.replace(' "', ' ``')
    render_str = render_str.replace('->', '$\\rightarrow$')

    # hard coded exceptions that are hard to automaticlly detect
    render_str = render_str.replace("1 / (meán-rang)", "1 / (me\\acute{a}n-rang)")
    render_str = render_str.replace("meán(1 / rang_i)", "1 / (me\\acute{a}n(1 / rang_i)")
    render_str = render_str.replace("meán(earráid^2)", "me\\acute{a}n(earr\\acute{a}id^2)")

    return render_str

def render_terms(terms):
    render_strs_2, header_ids = render_terms_defs(terms)
    render_strs_1 = render_terms_header(header_ids)
    render_strs = render_strs_1 + render_strs_2
    return render_strs

def to_md_standard_link(header_id):
    header_id = header_id.lower() # lower case
    header_id = header_id.replace('/', '-').replace(' ', '-').replace('.', '-') # alphanumeric only
    return header_id

def render_terms_header(header_ids):
    render_strs = []
    # render_strs.append("\\section*{Téarmaí}")
    return render_strs

def render_terms_defs(terms):
    render_strs = []
    curr_header = ''
    header_ids = []
    for term_id in terms:
        first_char = term_norm(term_id)[0].upper()
        if first_char != curr_header:
            try:
                # if it is a number
                int(first_char)
                curr_header = '#'
            except:
                # if it is a letter
                curr_header = first_char
            header_ids.append(curr_header)
            if curr_header == "#":
                curr_header = "\\#"
            render_strs.append("\\phantomsection \\subsection*{" + render_letter_header(curr_header) + "}")
            render_strs.append(f"\\addcontentsline{{toc}}{{subsection}}{{{render_letter_header(curr_header)}}}")
            render_strs.append(f"\\markboth{{{render_letter_header(curr_header)}}}{{{render_letter_header(curr_header)}}}\n")
        render_strs.append(render_term(terms[term_id]))
    return render_strs, header_ids

def write_terms(render_strs):
    out_name = f"focloir-trachtais-v{version}-leabhar"
    ext = '.tex'

    if not os.path.exists(DOWNLOADS_FOLDER_WRITE):
        os.makedirs(DOWNLOADS_FOLDER_WRITE)
    out_file = os.path.join(DOWNLOADS_FOLDER_WRITE, out_name + ext)

    with open(out_file, 'w') as out:
        for render_str in render_strs:
            print(render_str, file=out)

    num_terms = len(terms)
    return num_terms, out_file

def main():
    global terms
    terms = load_terms()
    render_strs = render_terms(terms)
    num_terms, out_file = write_terms(render_strs)
    print(f"Wrote {num_terms} terms to {out_file}")

if __name__ == '__main__':
    DEBUG = True
    main()
