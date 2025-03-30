#!/usr/bin/env python

from sitegen import load_terms

def count_terms():
    num_terms = len(load_terms())
    return num_terms

if __name__ == '__main__':
    print(f'{count_terms()} téarma :D')