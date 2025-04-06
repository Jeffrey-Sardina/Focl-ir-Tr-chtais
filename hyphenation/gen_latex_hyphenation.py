import glob
import os

TERM_FOLDERS = [
    "./BuNaMo/adjective/",
    "./BuNaMo/noun/",
    "./BuNaMo/verb/"
]
PREFIX_FILE = "./irish-prefixes.txt"
SUFFIX_FILE = "./irish-suffixes.txt"
OUT_FILE = "hyphenation-ga.sty"

VOWELS = set(char for char in "aeiouáéíóú")
CAN_LENITE = set(char for char in "bcdfgmpst")

def extract_all_forms(file):
    forms = set()
    with open(file, 'r', encoding="utf8") as inp:
        for line in inp:
            if 'default="' in line:
                # get word form
                line = line.strip()
                form_start = line.index('"')
                line = line[1+form_start:]
                form_end = line.index('"')
                line = line[:form_end]
                forms.add(line)
    return forms

def load_all_words():
    words = set()
    for folder in TERM_FOLDERS:
        files = glob.glob(os.path.join(folder, "*.xml"))
        print(f'Reading {len(files)} terms from {folder}')
        for i, file in enumerate(files):
            if i % 1000 == 0:
                print(f'{i} terms loaded so far...')
            forms = extract_all_forms(file)
            for form in forms:
                words.add(form)
    return words

def load_affixes(file):
    affixes = set()
    with open(file, 'r', encoding="utf-8") as inp:
        for line in inp:
            affixes.add(line.strip())
    return affixes

def hyphenate(term):
    '''
    hyphenate based on known prefixes and suffixes
    this will be imperfect, but should be ok most of the time
    '''
    prefixes = load_affixes(PREFIX_FILE)
    longest_valid_prefix = None
    curr_prefix_len = 0
    # get the longest prefix that is in the word and hyphenate based on that
    for prefix in prefixes:
        if prefix in term:
            # only do this if its actually a prefix (at the start)
            if term.index(prefix) == 0:
                if len(prefix) > curr_prefix_len:
                    curr_prefix_len = len(prefix)
                    longest_valid_prefix = prefix

    if longest_valid_prefix:
        # replace first occurrence only
        term = term.replace(longest_valid_prefix, longest_valid_prefix+'-', 1)

    suffixes = load_affixes(SUFFIX_FILE)
    longest_valid_suffix = None
    curr_suffix_len = 0
    # get the longest suffix that is in the word and hyphenate based on that
    for suffix in suffixes:
        if suffix in term:
            # only do this if its actually a suffix (at the end)
            if term.index(suffix) + len(suffix) == len(term):
                if len(suffix) > curr_suffix_len:
                    curr_suffix_len = len(suffix)
                    longest_valid_suffix = suffix
    
    if longest_valid_suffix:
        # replace last occurrence only
        lemma = term[:term.index(longest_valid_suffix)]
        term = lemma + "-" + longest_valid_suffix

    # rm double hyphens
    term = term.replace("--", "-")
    
    return term

def augment_word(word):
    '''Introduce all possible initial mutations (even non-sensical ones)'''
    alts = set()
    if word[0] in VOWELS:
        alts.add("n-" + word)
        alts.add("n" + word)
        alts.add("h-" + word)
        alts.add("h" + word)
    else:
        # lenition rules
        if word[0] in CAN_LENITE:
            alts.add(word[0] + "h" + word[1:])
        if word[0] == 's':
            alts.add("t" + word)

        # eclipsis rules
        if word[0] == "b":
            alts.add("m" + word)
        elif word[0] == "c":
            alts.add("g" + word)
        elif word[0] == "d":
            alts.add("n" + word)
        elif word[0] == "f":
            alts.add("bh" + word)
        elif word[0] == "g":
            alts.add("n" + word)
        elif word[0] == "p":
            alts.add("b" + word)
        elif word[0] == "t":
            alts.add("d" + word)
    return alts

def main():
    words = load_all_words()
    print(f"loaded a total of {len(words)} term forms")

    print('generating hyphenations')
    all_forms = set()
    for i, word in enumerate(words):
        if i % 1000 == 0:
            print(f'generating hyphenation for word {i} / {len(words)}')
        hyphenated = hyphenate(word)
        all_forms.add(hyphenated)
        alt_forms = augment_word(hyphenated)
        for alt_form in alt_forms:
            all_forms.add(alt_form)

    # write sty file
    # see: https://tex.stackexchange.com/questions/27890/how-to-add-global-hyphenation-rules
    print('sorting and writing words to file')
    all_forms = sorted(list(all_forms))
    with open(OUT_FILE, 'w', encoding="utf-8") as out:
        print("\\usepackage{hyphenat}", file=out)
        for word in all_forms:
            print("\\hyphenation{" + word + "}", file=out)

if __name__ == '__main__':
    main()