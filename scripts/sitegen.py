#!/usr/bin/env python

from constants import version
import glob
import json
import os
from utils import termsort, term_norm

SPACES_PER_INDENT = 4

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
        print("loading", term_file)
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
        list_str += ' '*SPACES_PER_INDENT + f"<li>{render_str}</li>\n"
    list_str += "</ul>\n"
    return list_str

def ordered_list(render_strs):
    list_str = "<ol>\n"
    for render_str in render_strs:
        list_str += ' '*SPACES_PER_INDENT + f"<li>{render_str}</li>\n"
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

def render_term(term, indent):
    print(f'rendering {term["term"]}')
    render_str = ""

    # header
    render_str += f"<h1>{term['term']} | {term['citation-form']}</h1>"

    # term translation
    render_str += bold(f"{term['term']} ({term['part-of-speech']}): {term['citation-form']}")
    render_str += "<br>\n"

    # term definitions
    render_str += italics("Sainmhíniú (ga):") + " " + ga_italics_filter(term['def-ga']) + "<br>"
    render_str += "\n"
    render_str += italics("Sainmhíniú (en):") + " " + term['def-en'] + "\n"
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
            start = item.index("'")
            ref = item[(start + 1):]
            end = ref.index("'")
            full_phrase = ref[:end]
            delim = ref.index(' / ')
            ref = ref[:delim]
            ref = ref.replace(' ', '-')
            ref_file_path = ref + '.html'
            link_html = f"<a href='{ref_file_path}'>'{full_phrase}'</a>"
            item = f"""{item[:item.index("féach ar an téarma '")]}féach ar an téarma {link_html}"""

        prov_list_citations.append(item)
    render_str += unordered_list(prov_list_citations)
    render_str += "\n"

    # term notes
    render_str += "Nótaí Aistriúcháin:\n"
    notes = []
    for item in term["notes"]:
        if "féach ar an téarma '" in item.lower() or "féach chomh maith ar an téarma '" in item.lower():
            start = item.index("'")
            ref = item[(start + 1):]
            end = ref.index("'")
            full_phrase = ref[:end]
            delim = ref.index(' / ')
            ref = ref[:delim]
            ref = ref.replace(' ', '-')
            ref_file_path = ref + '.html'
            link_html = f"<a href='{ref_file_path}'>'{full_phrase}'</a>"
            if "féach ar an téarma '" in item.lower():
                item = f"Féach ar an téarma {link_html}."
            else:
                item = f"Féach chomh maith ar an téarma {link_html}."
        item = ga_italics_filter(item)
        notes.append(item)
    render_str += unordered_list(notes)

    # fix math
    render_str = render_str.replace('$', '')

    # format nicely
    indent_str = ' ' * SPACES_PER_INDENT * indent # indent with 4 spaces
    render_str_fmt = ""
    render_str_lines = render_str.split("\n")
    for i, line in enumerate(render_str_lines):
        if i != len(render_str_lines) - 1:
            render_str_fmt += indent_str + line + "\n"
        else:
            render_str_fmt += indent_str + line

    return render_str_fmt

def get_abbrv(to_abbrv):
    # remove parenthetical statements
    try:
        paren_start = to_abbrv.index('(')
        to_abbrv = to_abbrv[:paren_start]
    except:
        # no parens
        pass

    # rm unneeded whitespace
    to_abbrv = to_abbrv.strip()
    return to_abbrv

def fmt_html_indents(html):
    # format index page nicely. 
    # We have 2 extra tabs (8 spaces) in the code above due to the use of 
    # Pythons multi-line strings and intending the code to look nice in the 
    # Python, and we want to remove those.
    html_fmt = ""
    html_lines = html.split("\n")
    for i, line in enumerate(html_lines):
        whitespace_to_rm = ' ' * 8 # 2 tabs of python code in this file is 8 spaces
        if whitespace_to_rm in line:
            line = line[8:]
        if i != len(html_lines) - 1:
            html_fmt += line + "\n"
        else:
            html_fmt += line
    return html_fmt

def gen_term_page(term, prev_term_id, next_term_id):
    if prev_term_id is not None:
        link = get_term_file_name(prev_term_id["term"])
        text = get_abbrv(prev_term_id['term'])
        prev_term_html = f'<a href="{link}">&lt;&lt; {text}</a>'
    else:
        prev_term_html = '&lt;&lt; (Téarma ar bith roimhe seo)'
    if next_term_id is not None:
        link = get_term_file_name(next_term_id["term"])
        text = get_abbrv(next_term_id['term'])
        next_term_html = f'<a href="{link}">{text} &gt;&gt;</a>'
    else:
        next_term_html = '(Téarma ar bith ina dihaidh seo) &gt;&gt;'
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
            <div class='centerbox'>\n{render_term(term, indent=4)}
                <br><hr>
                <table table border='0' style='width:100%'>
                    <tr>
                        <td style='width: 33%; text-align: left;'>{prev_term_html}</td>
                        <td style='width: 34%; text-align: center;'><a href="../">foclóir</a></td>
                        <td style='width: 33%; text-align: right;'>{next_term_html}</td>
                    </tr>
                </table>
                <div id="footerBar"></div>
            </div>
        </body>
        </html>
    """

    html = fmt_html_indents(html)
    return html

def get_term_file_name(term_name):
    return term_name.replace(' ', '-') + '.html' 

def gen_term_pages(terms):
    for i, term_id in enumerate(terms):
        term = terms[term_id]
        if i == 0:
            prev_term_id = None
        else:
            prev_term_id = terms[list(terms.keys())[i-1]]
        if i == len(terms) - 1:
            next_term_id = None
        else:
            next_term_id = terms[list(terms.keys())[i+1]]
        term_page_html = gen_term_page(term, prev_term_id, next_term_id)
        file_name = get_term_file_name(term["term"])
        if not os.path.exists(TERMS_FOLDER_WRITE):
            os.makedirs(TERMS_FOLDER_WRITE)
        with open(os.path.join(TERMS_FOLDER_WRITE, file_name), 'w') as out:
            print(term_page_html, file=out)

def gen_index(terms, version):
    searchbar = """<input type="text" id="termInput" onkeyup="termSearch()" placeholder="Cuardaigh téarma i mBéarla nó i nGaeilge...">\n"""
    
    termlist_indent = ' '*4*SPACES_PER_INDENT
    termslist = termlist_indent + """<ul id="dict-idx">\n"""

    curr_header = ''
    header_printed = False
    header_ids = []
    for term_id in terms:
        line_before_heade = True
        first_char = term_norm(term_id)[0].upper()
        if first_char != curr_header:
            header_printed = False
        if not header_printed:   
            try:
                # if it is a number
                int(first_char)
                curr_header = '#'
                line_before_heade = False
            except:
                # if it is a letter
                curr_header = first_char
            header_ids.append(curr_header)
            if line_before_heade:
                termslist += '\n'
            termslist += termlist_indent + ' '*SPACES_PER_INDENT +  f'<li><h2 id="{curr_header}" class="letter-header">{curr_header}</h2></li>\n'
            header_printed = True
            
        term = terms[term_id]
        term_file_name = get_term_file_name(term["term"])
        termslist += termlist_indent + ' '*SPACES_PER_INDENT +  f"""<li><a href="{TERMS_FOLDER_READ + term_file_name}">{term["term"]} | {term["citation-form"]}</a></li>\n"""
    termslist += termlist_indent + """</ul>\n"""

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
    
    # format script code nicely
    js_script_fmt = ""
    js_lines = js_script.split('\n')
    for i, line in enumerate(js_lines):
        if i == 0:
            js_script_fmt += line + "\n"
        elif i == len(js_lines) - 1:
            js_script_fmt += ' '*1*SPACES_PER_INDENT + line
        else:
            js_script_fmt += ' '*2*SPACES_PER_INDENT + line + "\n"
    
    header_nav = "<p class='center-text'> Téigh chuig: \n"
    header_nav += '\n'.join(' '*5*SPACES_PER_INDENT + f'<a href="#{header_id}">{header_id}</a>' for header_id in header_ids)
    header_nav += "\n" + ' '*4*SPACES_PER_INDENT + "</p>"

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
                <h1 id="mainHeader">Foclóir Tráchtais</h1>
                <p id="versionNum">v{version}, le Jeffrey Seathrún Sardina</p>
                {header_nav}
                {searchbar + termslist}
                <div id="footerBar"></div>
            </div>
            {js_script_fmt}
        </body>
        </html> 
    """

    html = fmt_html_indents(html)
    with open(os.path.join(SITE_FOLDER, "index.html"), 'w') as out:
        print(html, file=out)

def main():
    terms = load_terms()
    gen_term_pages(terms)
    gen_index(terms, version)

if __name__ == '__main__':
    main()