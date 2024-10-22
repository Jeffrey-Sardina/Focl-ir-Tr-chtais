import json
import glob

def load_terms():
    terms = {}
    term_files = glob.glob('terms/*.json')
    for term_file in term_files:
        with open(term_file, 'r') as inp:
            term = json.load(inp)
            terms[term['term']] = term
    terms_sorted = {key:terms[key] for key in sorted(list(terms.keys()))}
    return terms

def render_term(term):
    render_str = ""

    # term translation
    render_str += f"**{term['term']}: {term['citation-form']}**\n"
    
    # declension paradigm
    render_str += f"- NS: {term['ns']}\n"
    render_str += f"- GS: {term['gs']}\n"
    render_str += f"- NP: {term['np']}\n"
    render_str += f"- GP: {term['gp']}\n"
    render_str += f"\n"

    return render_str

if __name__ == '__main__':
    terms = load_terms()
    for term_id in terms:
        render_str = render_term(terms[term_id])
        print(render_str)
