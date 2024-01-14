# %load test_stemmer.py
from time import time
from trie import searchStems
from tqdm import tqdm
from pickle import load as pickle_load
# coding: utf-8
import requests
import re
from random import sample


def morphologicalAnalysis(query):
    res = requests.post('http://localhost:4444/evaluate', json={'textarea':query})
    resp = res.json()


    output_list = resp['text'].split('\n\t')[1:]
    output_list[-1] = output_list[-1].split('\n')[0]

        
    transformations = {
        'H': ['ı','i','u','ü'],
        'A': ['e','a'],
        'Y': ['y'],
        'S': ['s'],
        'N': ['n'],
        'D': ['d', 't'],
        'C': ['c', 'ç'],
        'G': ['g', 'k'],
        'B': ['b', 'p']
    }


    possible_combinations = []
    possible_roots = set()
    for output in output_list:
        char_index = 0
        combination = ''
        tokens = [token.strip().split('[')[0].split('(')[0] for token in output.split(']')]
        tokens[0] = tokens[0].lower()
        for token in tokens:
            if token != '':
                real_suffix = ''
                for char in token:
                    if char.isupper():
                        found_match = False
                        for version in transformations[char]:
                            if version == query[char_index]:
                                real_suffix += version
                                found_match = True
                                break
                        if found_match:
                            char_index += 1
                    else:
                        real_suffix += char
                        if char == query[char_index]:
                            char_index += 1
                combination = combination + '-' + real_suffix

        combination = re.split('-', combination[1:], 1)
        possible_roots.add(combination[0])

        if len(combination) == 2:
            possible_combinations.append((combination[0], '-' + combination[1]))
        else:
            possible_combinations.append((combination[0], ''))

    return set(possible_combinations), possible_roots



with open('test_strings.pkl', 'rb') as f:
    vocabulary = pickle_load(f)

start = time()
full_results, root_results = [], []

vocabulary_sample = sample(vocabulary, 200000)
for vocab in tqdm(vocabulary_sample):
    try:
        full_stemmer_result, root_stemmer_result = searchStems(vocab)
        full_tulap_result, root_tulap_result = morphologicalAnalysis(vocab)
    except Exception as e:
        print('vocab:', vocab, 'exception:', e)
        continue


    full_intersect = len(full_stemmer_result.intersection(full_tulap_result))
    root_intersect = len(root_stemmer_result.intersection(root_tulap_result))


    full_stemmer_length, full_tulap_length, root_stemmer_length, root_tulap_length = len(full_stemmer_result), len(full_tulap_result), len(root_stemmer_result), len(root_tulap_result)
    
    if full_stemmer_length == 0 and full_tulap_length == 0:
        full_stemmer_length, full_tulap_length, full_intersect = 1, 1, 1
    elif full_stemmer_length == 0 and full_tulap_length != 0:
        full_stemmer_length = 1
    elif full_tulap_length == 0:
        full_tulap_length = 1

    if root_stemmer_length == 0 and root_tulap_length == 0:
        root_stemmer_length, root_tulap_length, root_intersect = 1, 1, 1
    elif root_stemmer_length == 0 and root_tulap_length != 0:
        root_stemmer_length = 1
    elif root_tulap_length == 0:
        root_tulap_length = 1

    full_results.append((full_intersect / full_stemmer_length, full_intersect / full_tulap_length))
    root_results.append((root_intersect / root_stemmer_length, root_intersect / root_tulap_length))

end = time()

from pickle import dump
with open('full_results.pkl', 'wb') as f:
    dump(full_results, f)
    
with open('root_results.pkl', 'wb') as f:
    dump(root_results, f)
    
import numpy as np
full_result_np = np.asarray(full_results)
root_result_np = np.asarray(root_results)

print('morphological variants precision:', np.average(full_result_np[:, 0]))
print('morphological variants recall:',np.average(full_result_np[:, 1]))
print('roots precision:',np.average(root_result_np[:, 0]))
print('roots:',np.average(root_result_np[:, 1]))
