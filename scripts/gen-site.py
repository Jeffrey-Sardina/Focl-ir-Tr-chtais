import glob
import json
import os

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
            terms[term['term']] = term
    terms_sorted = {key:terms[key] for key in sorted(list(terms.keys()))}
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

def render_term(term):
    render_str = ""

    # header
    render_str += f"<h1>{term['term']} | {term['citation-form']}</h1>"

    # term translation
    render_str += bold(f"{term['term']} ({term['part-of-speech']}): {term['citation-form']}")
    render_str += "<br>\n"

    # term definitions
    render_str += italics("sainmhíniú (ga):") + " " + term['def-ga'] + "<br>"
    render_str += "\n"
    render_str += italics("sainmhíniú (en):") + " " + term['def-en'] + "\n"
    render_str += "\n"
    render_str += '<br>'

    # term provenance
    render_str += "<br>tagairtí:\n"
    prov_list = [f"{key}: {term['prov'][key]}" for key in term["prov"]]
    prov_list_citations = []
    for item in prov_list:
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
        <link rel="stylesheet" href="../../css/gnath.css">
        <!-- function to allow loading from another HTML file
        see: https://stackoverflow.com/questions/8988855/include-another-html-file-in-a-html-file -->
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
        <script> 
            $(function(){{
                $("#headerBar").load("../../header.html"); 
            }});
        </script> 
        </head>
        <body>
        <div id="headerBar"></div>
        <div class='centerbox'>
        {render_term(term)}
        </div>
        </body>
        </html> 
    """
    return html

def gen_term_pages(terms):
    for term_id in terms:
        term = terms[term_id]
        term_page_html = gen_term_page(term)
        with open(os.path.join(TERMS_FOLDER_WRITE, f"{term["term"]}.html"), 'w') as out:
            print(term_page_html, file=out)

def gen_index(terms):
    searchbar = """<input type="text" id="termInput" onkeyup="myFunction()" placeholder="Cuardach téarma i mBéarla nó i nGaeilge...">\n"""
    
    longest_len_eng = 0
    for term_id in terms:
        term = terms[term_id]
        if len(term) > longest_len_eng:
            longest_len_eng = len(term)
    termslist = """<ul id="dict-idx">\n"""
    for term_id in terms:
        term = terms[term_id]
        termslist += f"""<li><a href="{TERMS_FOLDER_READ + term["term"]}.html">{term["term"]} | {term["citation-form"]}</a></li>\n"""
    termslist += """</ul>\n"""

    js_script = """<script>
        function myFunction() {
            // Declare variables
            var input, filter, ul, li, a, i, txtValue;
            input = document.getElementById('termInput');
            filter = input.value.toUpperCase();
            ul = document.getElementById("dict-idx");
            li = ul.getElementsByTagName('li');

            // Loop through all list items, and hide those who don't match the search query
            for (i = 0; i < li.length; i++) {
                a = li[i].getElementsByTagName("a")[0];
                txtValue = a.textContent || a.innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    li[i].style.display = "";
                } else {
                    li[i].style.display = "none";
                }
            }
        }
        </script>\n"""

    html = f"""<!DOCTYPE html>
        <html>
        <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-type" content="text/html; charset=UTF-8">
        <title>Foclóir Tráchtais</title>
        <link rel="stylesheet" href="../css/gnath.css">
        <!-- function to allow loading from another HTML file
        see: https://stackoverflow.com/questions/8988855/include-another-html-file-in-a-html-file -->
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
        <script> 
            $(function(){{
                $("#headerBar").load("../header.html"); 
            }});
        </script> 
        </head>
        <body>
        <div id="headerBar"></div>
        <div class='centerbox' id='indexlist'>
        <h1>Foclóir Tráchtais</h1>
        {searchbar + termslist + js_script}
        </div>
        </body>
        </html> 
    """

    with open(os.path.join(SITE_FOLDER, "index.html"), 'w') as out:
            print(html, file=out)

def general_header():
    header_html = """
     
    """
    return header_html

def main():
    terms = load_terms()
    gen_term_pages(terms)
    gen_index(terms)

if __name__ == '__main__':
    main()