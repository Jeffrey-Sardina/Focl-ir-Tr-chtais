from gen_site import load_terms

def main():
    num_terms = len(load_terms())
    print(f'{num_terms} téarma :D')

if __name__ == '__main__':
    main()