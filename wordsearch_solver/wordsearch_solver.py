#!/usr/bin/env python
# -*- coding: utf-8 -*-
# this expects a directory structure like:
# ├──tests
# │  └──computer_terms
# │     ├──puzzle.txt
# │     ├──solution.txt
# │     └──words.txt
# └──wordsearch_solver.py
import os
import pprint
import time
from colored import fg, bg, attr

pp = pprint.PrettyPrinter(indent=2)
reset = attr('reset')

here = os.path.dirname(os.path.realpath(__file__))


def timeme(method):
    def wrapper(*args, **kw):
        start_time = int(round(time.time() * 1000))
        result = method(*args, **kw)
        end_time = int(round(time.time() * 1000))

        print(end_time - start_time, 'ms')
        return result

    return wrapper


# https://reterwebber.wordpress.com/2014/01/22/data-structure-in-python-trie/
def make_trie(*args):
    """
    Make a trie by given words.
    """
    trie = {}

    for word in args:
        # if type(word) != str:
        #    raise TypeError("Trie only works on str!")
        temp_trie = trie
        for letter in word:
            temp_trie = temp_trie.setdefault(letter, {})
        temp_trie.setdefault('_end_', '_end_')

    return trie


def in_trie(trie, word):
    """
    Detect if word in trie.
    """
    # if type(word) != str:
    #     raise TypeError("Trie only works on str!")

    temp_trie = trie
    for letter in word:
        if letter not in temp_trie:
            return False
        temp_trie = temp_trie[letter]
    return True


def import_raw(puzzle_name, ftype):
    path = os.path.join(here, 'tests', puzzle_name, "{}.txt".format(ftype))
    with open(path, 'r') as f:
        return [line.strip() for line in f.readlines() if line]


def import_puzzle(lines):
    return [line.strip().split() for line in lines if line]


def print_intro(puzzle, words):
    print("solving puzzle: ")
    print("----------------")
    print("")
    pp.pprint(puzzle)
    print("")
    print("Words to find:")
    print("----------------")
    print("")
    pp.pprint(words)


# the brute force algorithm is to loop through each item in the puzzle jagged array,
# and within a nested loop, generate potential words (3 letter minimum) from each direction
# each potential word is looked up in the words dict, and if there's a match, we can mark that as found
# example:
#
# F O D R
# P E O Z
# Z S E A
# Y E P T
#
# we'd generate these "potential words":
# Direction + Word
# East  - FOD
# East  - FODR
# South - FPZ
# South - PPZY
# West  - (this would not be done until we are at least in column 3)
# SouthEast - FEET
#
# We are **NOT** brute-forcing with the below implementation, instead
# this leverages a trie in order to fail as quick as possible.
#
@timeme
def solve(puzzle, words):
    max_height = len(puzzle)
    max_width = len(puzzle[0])
    print("puzzle h: {} w: {}".format(max_height, max_width))
    trie = make_trie(*words)

    def check_word_found(word, words, trie):
        print("looking for {}".format(word))
        if not in_trie(trie, word):
            print(fg(196) + "word not in trie" + reset)
            return False

        if word in words:
            print(fg(82) + "found word!" + reset)
            words[word] = fg(82) + "True" + reset

        return True

    for row_idx, row in enumerate(puzzle):
        for col_idx, letter in enumerate(row):
            print("row: {} col: {}".format(row_idx, col_idx))
            # skip any letter that does not have a corresponding word that starts with it
            print("looking for first letter {}".format(letter))

            if not in_trie(trie, letter):
                continue

            # east ->
            if col_idx <= max_width - 3:
                test_word = letter
                for i in range(col_idx + 1, max_width):
                    test_word += row[i]
                    if not check_word_found(test_word, words, trie):
                        break

            # south v
            if row_idx <= max_height - 3:
                test_word = letter
                for i in range(row_idx + 1, max_height):
                    test_word += puzzle[i][col_idx]
                    if not check_word_found(test_word, words, trie):
                        break

            # west <-
            if col_idx >= 2:
                test_word = letter
                for i in range(col_idx - 1, -1, -1):
                    test_word += row[i]
                    if not check_word_found(test_word, words, trie):
                        break

            # north ^
            if row_idx >= 2:
                test_word = letter
                for i in range(row_idx - 1, -1, -1):
                    test_word += puzzle[i][col_idx]
                    if not check_word_found(test_word, words, trie):
                        break

            # southeast \
            if row_idx <= max_height - 3 and col_idx <= max_width - 3:
                test_word = letter
                r = row_idx + 1
                c = col_idx + 1
                while r < max_height and c < max_width:
                    print("r {} c {}".format(r, c))
                    test_word += puzzle[r][c]
                    if not check_word_found(test_word, words, trie):
                        break
                    r += 1
                    c += 1


def main(puzzle_name):
    p_raw = import_raw(puzzle_name, 'puzzle')
    words_list = import_raw(puzzle_name, 'words')
    words = {word: False for word in words_list}

    print_intro(p_raw, words_list)
    puzzle = import_puzzle(p_raw)
    solve(puzzle, words)

    print("")
    for word, found in words.items():
        print("{}: {}".format(word, found))


main('computer_terms')
