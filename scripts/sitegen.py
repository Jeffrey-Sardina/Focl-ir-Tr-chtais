#!/usr/bin/env python

import glob
import json
import os
from utils import termsort, term_norm

'''
references:
- https://www.w3schools.com/howto/howto_js_filter_lists.asp
'''

SITE_FOLDER = '../sitegen/'
TERMS_FOLDER_WRITE = '../sitegen/terms/'
TERMS_FOLDER_READ = 'terms/'

def load_terms():
    terms = {}
    term_files = glob.glob('../terms/*.json')
    for term_file in term_files:
        with open(term_file, 'r') as inp:
            term = json.load(inp)
            if term['term'] in terms:
                assert False, f"duplicate found for term: {term['term']}"
            terms[term['term']] = term
    terms_sorted = {key:terms[key] for key in termsort(terms)}
    return terms_sorted

def bold(text):
    return f"<strong>{text}</strong>"

def italics(text):
    return f"<i>{text}</i>"

def unordered_list(render_strs):
    list_str = "<ul>\n"
    for render_str in render_strs:
        list_str += f"\t<li>{render_str}</li>\n"
    list_str += "</ul>\n"
    return list_str

def ordered_list(render_strs):
    list_str = "<ol>\n"
    for render_str in render_strs:
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

    # header
    render_str += f"<h1>{term['term']} | {term['citation-form']}</h1>"

    # term translation
    render_str += bold(f"{term['term']} ({term['part-of-speech']}): {term['citation-form']}")
    render_str += "<br>\n"

    # term definitions
    render_str += italics("sainmhíniú (ga):") + " " + ga_italics_filter(term['def-ga']) + "<br>"
    render_str += "\n"
    render_str += italics("sainmhíniú (en):") + " " + term['def-en'] + "\n"
    render_str += "\n"
    render_str += '<br>'

    # term provenance
    render_str += "<br>Tagairtí:\n"
    prov_list = [f"{key}: {term['prov'][key]}" for key in term["prov"]]
    prov_list_citations = []
    for item in prov_list:
        item = item.replace("de-bhaldraithe", "De Bhaldraithe (1978)")
        item = item.replace("dineen", "Dineen (1934)")
        item = item.replace("focloir-beag", "Ó Dónaill et al. (1991)")
        item = item.replace("odonaill", "Ó Dónaill (1977)")
        item = item.replace("storchiste", "Williams et al. (2023)")

        if "féach ar an téarma '" in item.lower():
            # print(item)
            start = item.index("'")
            ref = item[(start + 1):]
            end = ref.index("'")
            full_phrase = ref[:end]
            delim = ref.index(' / ')
            ref = ref[:delim]
            ref = ref.replace(' ', '-')
            ref_file_path = ref + '.html'
            link_html = f"<a href='{ref_file_path}'>'{full_phrase}'</a>"
            item = f"{item[:item.index("féach ar an téarma '")]}féach ar an téarma {link_html}."

        prov_list_citations.append(item)
    render_str += unordered_list(prov_list_citations)
    render_str += "\n"

    # term notes
    render_str += "Nótaí Aistriúcháin:\n"
    notes = []
    for item in term["notes"]:
        if "féach ar an téarma '" in item.lower() or "féach chomh maith ar an téarma '" in item.lower():
            # print(item)
            start = item.index("'")
            ref = item[(start + 1):]
            end = ref.index("'")
            full_phrase = ref[:end]
            delim = ref.index(' / ')
            ref = ref[:delim]
            ref = ref.replace(' ', '-')
            ref_file_path = ref + '.html'
            link_html = f"<a href='{ref_file_path}'>'{full_phrase}'</a>"
            item = f"Féach ar an téarma {link_html}."
        item = ga_italics_filter(item)
        notes.append(item)
    render_str += unordered_list(notes)
    render_str += "\n"

    # fix math
    render_str = render_str.replace('$', '')

    return render_str

def gen_term_page(term):
    html = f"""<!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-type" content="text/html; charset=UTF-8">
        <title>{term["term"]} | {term["citation-form"]}</title>
        <link rel="stylesheet" href="/css/gnath.css">
        <!-- function to allow loading from another HTML file
        see: https://stackoverflow.com/questions/8988855/include-another-html-file-in-a-html-file -->
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
        <script> 
            $(function(){{
                $("#headerBar").load("/header.html"); 
            }});
            $(function(){{
                $("#footerBar").load("/footer.html"); 
            }});
        </script> 
        </head>
        <body>
        <div id="headerBar"></div>
        <div class='centerbox'>
            {render_term(term)}
            <div id="footerBar"></div>
        </div>
        </body>
        </html> 
    """
    return html

def get_term_file_name(term_name):
    return term_name.replace(' ', '-') + '.html' 

def gen_term_pages(terms):
    for term_id in terms:
        term = terms[term_id]
        term_page_html = gen_term_page(term)
        file_name = get_term_file_name(term["term"])
        if not os.path.exists(TERMS_FOLDER_WRITE):
            os.makedirs(TERMS_FOLDER_WRITE)
        with open(os.path.join(TERMS_FOLDER_WRITE, file_name), 'w') as out:
            print(term_page_html, file=out)

def gen_index(terms, version):
    searchbar = """<input type="text" id="termInput" onkeyup="termSearch()" placeholder="Cuardaigh téarma i mBéarla nó i nGaeilge...">\n"""
    termslist = """<ul id="dict-idx">\n"""

    curr_header = ''
    header_printed = False
    header_ids = []
    for term_id in terms:
        first_char = term_norm(term_id)[0].upper()
        if first_char != curr_header:
            header_printed = False
        if not header_printed:   
            try:
                # if it is a number
                int(first_char)
                curr_header = '#'
            except:
                # if it is a letter
                curr_header = first_char
            header_ids.append(curr_header)
            termslist += f'\t<li><h2 id="{curr_header}" style="margin-bottom: 0px;">{curr_header}</h2></li>\n'
            header_printed = True
            
        term = terms[term_id]
        term_file_name = get_term_file_name(term["term"])
        termslist += f"""\t<li><a href="{TERMS_FOLDER_READ + term_file_name}">{term["term"]} | {term["citation-form"]}</a></li>\n"""
    termslist += """</ul>\n"""

    js_script = """<script>
        function termSearch() {
            // Prep data
            let input = document.getElementById('termInput');
            let filter = input.value.toUpperCase();
            let ul = document.getElementById("dict-idx");
            let li = ul.getElementsByTagName('li');

            // hide elems that do not contain the search substring
            let a, h2, txtValue;
            for (let i = 0; i < li.length; i++) {
                a = li[i].getElementsByTagName("a")[0];
				h2 = li[i].getElementsByTagName("h2")[0]
				elem = a || h2
                txtValue = elem.textContent || elem.innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    li[i].style.display = "";
                } else {
                    li[i].style.display = "none";
                }
				if (filter && filter.length > 0 && h2) {
					li[i].style.display = "none";
				}
            }
        }
        </script>\n"""
    
    header_nav = "<p style='text-align: center;'> Téigh chuig: \n"
    header_nav += '\n'.join(' '*16 + f'<a href="#{header_id}">{header_id}</a>' for header_id in header_ids)
    header_nav += "</p>"

    html = f"""<!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-type" content="text/html; charset=UTF-8">
        <meta property="og:image" content="/images/site.png" />
        <title>Foclóir Tráchtais</title>
        <link rel="stylesheet" href="/css/gnath.css">
        <!-- function to allow loading from another HTML file
        see: https://stackoverflow.com/questions/8988855/include-another-html-file-in-a-html-file -->
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
        <script> 
            $(function(){{
                $("#headerBar").load("/header.html"); 
            }});
            $(function(){{
                $("#footerBar").load("/footer.html"); 
            }});
        </script> 
        </head>
        <body>
        <div id="headerBar"></div>
        <div class='centerbox' id='indexlist'>
            <h1 style="margin-bottom: 0px;">Foclóir Tráchtais</h1>
            <p id="versionNum" style="margin-top: 0px">v{version}, le Jeffrey Seathrún Sardina</p>
            {header_nav}
            {searchbar + termslist}
            <div id="footerBar"></div>
        </div>
        {js_script}
        </body>
        </html> 
    """

    with open(os.path.join(SITE_FOLDER, "index.html"), 'w') as out:
            print(html, file=out)

def main():
    version = '1.3 alfa'
    terms = load_terms()
    gen_term_pages(terms)
    gen_index(terms, version)

if __name__ == '__main__':
    main()