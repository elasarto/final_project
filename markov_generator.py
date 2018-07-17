from random import randint, choice, choices
from os import remove, makedirs
from functools import reduce

from os.path import isfile, isdir, abspath, splitext, join as os_join, expanduser

import json
from re import compile as re_compile

from collections import deque
from shutil import copy2

import pickle

import pronouncing


class MarkovTextExcept(Exception):
    "Something is wrong!"
    pass


class MarkovTextGenerator(object):
    
    # RUS = tuple(map(chr, range(1072, 1104))) + ("ё",)
    ENG = tuple(map(chr, range(97, 123)))
    # upper case: tuple(map(chr, range(65, 91))) 
    
    word_symb = re_compile(r"\w+|[\.\!\?…,;:]+")
    words = re_compile(r"\w+")
    symbols = re_compile(r"[\.\!\?…,;:]+")
    finish = re_compile(r"[\.\!\?…]+")
    
    def __init__(self, chain = 2, *filepath):
        #chain - chain length >=1
        
        self.chain = chain
        self.tokens_array = ()
        self.base_dict = {}
        self.start_arrays = ()

        self.vocabulars = {}

        self.temp_folder = abspath(
            os_join(expanduser("~"), "textGeneratorTemp")
        )
        if not isdir(self.temp_folder):
            makedirs(self.temp_folder)

        for _path in frozenset(filter(isfile, map(abspath, filepath))):
            self.update(_path)

    @classmethod
    def is_eng_word(cls, word):
        if not word:
            return False
        return all(map(lambda s: (s.lower() in cls.ENG), word))

    def token_is_correct(self, token):
        if self.is_eng_word(token):
            return True
        elif self.symbols.search(token):
            return True
        elif self.finish.search(token):
            return True
        elif token in "$^":
            return True
        return False

    def get_corrected_arrays(self, arr):
        for tokens in arr:
            if all(map(self.token_is_correct, tokens)):
                yield tokens

    def get_optimal_variant(self, variants, start_words, **kwargs):
        if not start_words:
            return (choice(variants), {})

        _variants = []
        _weights = []
        for tok in frozenset(variants):
            if not self.token_is_correct(tok):
                continue
            weight = variants.count(tok)
            for word in start_words:
                for token in self.words.finditer(word.strip().lower()):
                    if token.group() == tok:
                        weight <<= 1
            _variants.append(tok)
            _weights.append(weight)

        if not _variants:
            return (choice(variants), {})

        return (choices(_variants, weights=_weights, k=1)[0], {})

    def syllable_count(self, word):
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if count == 0:
            count += 1
        return count

    def _get_generate_tokens(self, *start_words, **kwargs):
        _string_len = kwargs.pop("size", None)
        _syllables = kwargs.pop("syllables", None)
        if not isinstance(_string_len, int):
            _string_len = randint(1, 5)
        start_data = self.get_start_array(*start_words, **kwargs)
        if isinstance(start_data[0], tuple):
            start_data, kwargs["need_rhyme"] = start_data
        __text_array = list(start_data)
        key_array = deque(__text_array, maxlen=self.chain)
        yield from __text_array
        string_counter = 0
        syllable_counter = reduce((lambda x, y: x + y), 
                                  [self.syllable_count(word) for word in __text_array if self.is_eng_word(word)])
        if _syllables > 0:
            if syllable_counter >= _syllables:
                return
        kwargs["current_string"] = __text_array
        kwargs["start_words"] = start_words
        while True:
            tuple_key = tuple(key_array)
            # limit number of options per key to 1000
            _variants = self.base_dict.get(tuple_key, None)[:1000]
            if not _variants:
                break
            next_token, kwargs_update = self.get_optimal_variant(
                variants=_variants,
                **kwargs
            )
            kwargs.update(kwargs_update)
            if _string_len > 0:
                if next_token in "$^":
                    string_counter += 1
                    if string_counter >= _string_len:
                        break
            key_array.append(next_token)
            kwargs["current_string"].append(next_token)
            yield next_token
            if _syllables > 0:
                if not next_token in "$^,":
                    syllable_counter += self.syllable_count(next_token)
                    if syllable_counter >= _syllables:
                        break

    def start_generation(self, *start_words, **kwargs):
        out_text = ""
        reverse = kwargs.pop("reverse", None) != None
        _need_capitalize = not reverse
        last_token = ""
        last_word = ""
        last_word_text = ""
        for token in self._get_generate_tokens(*start_words, **kwargs):
            if token in "$^":
                if not reverse:
                    _need_capitalize = True
                continue
            if self.words.search(token) or self.symbols.search(token):
                if reverse:
                    # don't add space if the next token is a symbol
                    if not self.symbols.search(last_token):
                        out_text = " " + out_text
                else:
                    out_text = out_text + " "
                if reverse and self.finish.search(token):
                    # new sentence - capitalize starting from the last word
                    out_text = " " + last_word.title() + last_word_text
            if self.words.search(token) or self.symbols.search(token):
                # save the last token (could be a word or a symbol)
                last_token = token
            if self.words.search(token):
                # save the last word and the current version of the text 
                last_word = token
                last_word_text = out_text
            if _need_capitalize:
                _need_capitalize = False
                token = token.title()
            if reverse:
                out_text = token + out_text
            else:
                out_text = out_text + token
        if reverse:
            out_text = last_word.title() + last_word_text
        return out_text.strip()

    def get_start_array(self, *start_words, **kwargs):
        if not start_words:
            return choice(self.start_arrays)

        _variants = []
        _weights = []
        for word in start_words:
            word = word.strip().lower()
            if not (word in self.start_first_word):
                continue;
            filtered_tokens = self.start_first_word[word]
            tokens_per_word = 0
            for tokens in filtered_tokens:
                # TODO: it's fast now, but simple - do something more intelligent here
                weight = randint(0,10000)
                _variants.append(tokens)
                _weights.append(weight)
                tokens_per_word += 1
                # limit number of tokens per word to 1000
                if (tokens_per_word > 1000):
                    break

        if not _variants:
            return choice(self.start_arrays)

        return choices(_variants, weights=_weights, k=1)[0]

    def create_base(self, reverse):
        self.base_dict = {}
        _start_arrays = []
        for tokens, word in self.chain_generator():
            # tokens - chain of words
            # word - the next word after the chain
            # build a dictionary: for each chain store a list of possible next words
            self.base_dict.setdefault(tokens, []).append(word) 
            if reverse or (tokens[0] == "^"):  # special symbol - beginning of a sentence
                                                # if reverse then we add ALL tokens 
                _start_arrays.append(tokens)

        self.start_arrays = tuple(
            frozenset(self.get_corrected_arrays(_start_arrays))
        )
        # create dictionary [first word] -> [chain/full token]
        self.start_first_word = {}
        for tokens in self.start_arrays:
            self.start_first_word.setdefault(tokens[0], []).append(tokens)

    def chain_generator(self):
        n_chain = self.chain # >=1
        n_chain += 1  
        changing_array = deque(maxlen=n_chain)
        for token in self.tokens_array:
            changing_array.append(token)
            if len(changing_array) < n_chain:
                continue  # array not full yet
            yield (tuple(changing_array)[:-1], changing_array[-1])


    def create_dump(self, name=None):
        name = name or "vocabularDump"
        backup_dump_file = os_join(
            self.temp_folder,
            "{0}.backup".format(name)
        )
        dump_file = os_join(
            self.temp_folder,
            "{0}.json".format(name)
        )
        with open(backup_dump_file, "w", encoding="utf-8") as js_file:
            json.dump(self.tokens_array, js_file, ensure_ascii=False)
        copy2(backup_dump_file, dump_file)
        remove(backup_dump_file)

    def load_dump(self, name=None):
        name = name or "vocabularDump"
        dump_file = os_join(
            self.temp_folder,
            "{0}.json".format(name)
        )
        with open(dump_file, "rb") as js_file:
            self.tokens_array = tuple(json.load(js_file))
        self.create_base()

    def from_text(self, text):
        text = text.strip().lower()
        need_start_token = True
        token = "$"  # if the line is empty
        for token in self.word_symb.finditer(text):
            token = token.group()
            if need_start_token:
                need_start_token = False
                yield "^"
            yield token
            if self.finish.search(token):
                need_start_token = True
                yield "$"
        if token != "$":
            yield "$"

    def from_file(self, filepath):
        filepath = abspath(filepath)
        with open(filepath, "rb") as txt_file:
            for line in txt_file:
                text = line.decode("utf-8", "ignore").strip()
                if not text:
                    continue
                yield from self.from_text(text)
    
    def update(self, data, fromfile=True):
        # update existing base
        func = (self.from_file if fromfile else self.from_text)
        new_data = tuple(func(data))
        if new_data:
            self.tokens_array += new_data
            self.create_base(False)
            
    def update_reverse_tokens(self, tokens):
        # reverse tokens array
        if tokens:
            tokens_list = list(reversed(tokens))
            replace_dict = {'$':'^', '^':'$'}
            tokens_list = [replace_dict.get(token, token) for token in tokens_list]       
            self.tokens_array += tuple(tokens_list)
            self.create_base(True)

class RhymeGenerator:

    def __init__(self, filename):
        if isfile(filename):
            self.my_rev_generator = pickle.load(open(filename, "rb"))
        else:
            chain_size = 3
            my_generator = MarkovTextGenerator(chain_size)
            #self.my_generator.update('dorian_eng.txt')
            my_generator.update('lyrics1.txt')
            my_generator.update('lyrics2.txt')
            my_generator.update('lyrics3.txt')
            my_generator.update('lyrics4.txt')
            my_generator.create_dump()
            self.my_rev_generator = MarkovTextGenerator(chain_size)
            self.my_rev_generator.update_reverse_tokens(my_generator.tokens_array)
            pickle.dump(self.my_rev_generator, open(filename, "wb"))

    def generate(self, user_input):
        to_rhyme = user_input
        user_syl_count = self.my_rev_generator.syllable_count(user_input)
        print(user_input)
        word = (to_rhyme[to_rhyme.rfind(' ')+1:])
        word_list = list(pronouncing.rhymes(word))[:10]
        reverse_rhyme = self.my_rev_generator.start_generation(*word_list, syllables=user_syl_count, reverse=1)
        print(reverse_rhyme)
        return reverse_rhyme