import sys
import glob
import json
from gen_site import load_terms

def dump_ga():
    dump = ""
    for term_id in terms:
        term = terms[term_id]
        dump += f'{term["citation-form"]}\n'
        dump += f'{term["part-of-speech"]}\n'
        dump += f'{term["def-ga"]}\n'
        for note in term["notes"]:
            dump += f'{note}\n'
        dump += '\n'
    return dump

def dump_en():
    dump = ""
    for term_id in terms:
        term = terms[term_id]
        dump += f'{term["term"]}\n'
        dump += f'{term["def-en"]}\n'
        dump += '\n'
    return dump

def main():
    if DUMP_GAEILGE:
        dump = dump_ga()
        tag = "ga"
    else:
        dump = dump_en()
        tag = "en"

    with open(f'../dump-{tag}.txt', 'w') as out:
        print(dump, file=out)

if __name__ == '__main__':
    if '-ga' in sys.argv:
        DUMP_GAEILGE = True
    elif '-en' in sys.argv:
        DUMP_GAEILGE = False
    else: # default to Gaeilge
        DUMP_GAEILGE = True

    if '-nv' in sys.argv:
        DUMP_NON_VALIDATED_ONLY = True
    else:
        DUMP_NON_VALIDATED_ONLY = False

    DEBUG = False
    terms = load_terms()
    main()