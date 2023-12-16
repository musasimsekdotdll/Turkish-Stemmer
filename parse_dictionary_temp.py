# coding: utf-8
from time import time
from bs4 import BeautifulSoup

from glob import glob

from re import search
from re import IGNORECASE

from pickle import dump



fnames = glob('Turkce TDK Sozluk\\Sozluk\\*\\HARF_*.xml')


nouns, verbs = [], []
for fname in fnames:
    print(fname)
    with open(fname, 'r', encoding='utf8') as f:
        data = f.read()

    bs_data = BeautifulSoup(data, 'xml')
    entries = bs_data.find_all('entry')


    for entry in entries:
        txt = entry.find('name').text[1:-1]
        src = search('\s+', txt)

        if src is None:
            word_class = entry.find('lex_class').text
            if search('fiil', word_class, IGNORECASE):
                verbs.append(txt[:-3])
            else:
                nouns.append(txt)

                
with open('nouns.pkl', 'wb') as f:
    dump(nouns, f)

with open('verbs.pkl', 'wb') as f:
    dump(verbs, f)
    
