#!/usr/bin/env python

import sys
import glob
import json

def load_terms():
    terms = {}
    if DUMP_NON_VALIDATED_ONLY:
        term_files = []
        with open('../utils/not-validated.txt' ,'r') as inp:
            for line in inp:
                term_file_name = line.strip()
                term_files.append(f'../terms/{term_file_name}')
    else:
        term_files = glob.glob('../terms/*.json')
    for term_file in term_files:
        if DEBUG:
            print(term_file)
        with open(term_file, 'r') as inp:
            term = json.load(inp)
            terms[term['term']] = term
    terms_sorted = {key:terms[key] for key in sorted(list(terms.keys()))}
    return terms_sorted

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

    out_path = f'../dump-{tag}.txt'
    with open(out_path, 'w') as out:
        print(dump, file=out)
        print(f'Dumped {len(terms)} terms to {out_path}')

if __name__ == '__main__':
    if '-all' in sys.argv:
        DUMP_NON_VALIDATED_ONLY = False
    else:
        DUMP_NON_VALIDATED_ONLY = True

    if '-silent' in sys.argv:
        DEBUG = False
    else:
        DEBUG = True

    terms = load_terms()
    if '-ga' in sys.argv:
        DUMP_GAEILGE = True
        main()
    elif '-en' in sys.argv:
        DUMP_GAEILGE = False
        main()
    else: # do both
        DUMP_GAEILGE = True
        main()
        DUMP_GAEILGE = False
        main()