#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Count how many wiki links it takes to get to the Philosophy page
    To run 500:
    ./philosophy.py
    To run 10 with print statements:
    ./philosophy.py -v -n 10
"""
import re
import datetime
import argparse
import math
from urllib2 import urlopen
import numpy
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from termcolor import colored


def get_outer_indices(indices, left_parens, right_parens):
    """ To handle nested parentheses
        Gets indices of outermost left and right parentheses --
        Given lists left_parens, right_parens of left and right indices,
        generates a list of (x,y) for the starting point x, and endpoint y
        of the outermost indices.
        Ex: For '(())(x)'  left_parens=[0, 1, 4], right_parens=[2, 3, 6]
            output: [(0,3), (4,6)]
    """
    count_left, count_right, i, j = 0, 0, 0, 0
    num_left, num_right = len(left_parens), len(right_parens)
    if num_left == 0 or num_right == 0:
        return []
    while i < num_left and j < num_right:
        if left_parens[i] < right_parens[j]:
            count_left += 1
            i += 1
            k = 0
        else:
            count_right += 1
            j += 1
            k = 1
        if count_left == count_right:
            indices.append((left_parens[0], right_parens[j-k]))
            return get_outer_indices(indices, left_parens[i:], right_parens[j:])
    indices.append((left_parens[0], right_parens[-1]))
    return indices


def get_paren_hrefs(paragraph):
    "Get list of wiki hrefs inside of parentheses (could be nested)"
    str_par = unicode.join(u'\n', map(unicode, paragraph))
    # get list of indices of left and right parentheses
    left_parens = [m.start() for m in re.finditer('\(', str_par)]
    right_parens = [m.start() for m in re.finditer('\)', str_par)]
    if len(left_parens) == 0:
        return []
    indices = get_outer_indices([], left_parens, right_parens)
    in_parens = [str_par[s:e+1] for (s, e) in indices]
    wiki_hrefs = [re.findall('href=\"/wiki/(.*?)\"', u'{}'.format(f)) for f in in_parens]
    flatten = [item for sublist in wiki_hrefs for item in sublist]
    return flatten


def get_ital_hrefs(paragraph):
    "Get list of wiki hrefs inside of italics tags"
    str_par = unicode.join(u'\n', map(unicode, paragraph))
    in_ital = re.findall('<i>.*?</i>', str_par)
    if len(in_ital) == 0:
        return []
    wiki_hrefs = [re.findall('href=\"/wiki/(.*?)\"', u'{}'.format(f)) for f in in_ital]
    flatten = [item for sublist in wiki_hrefs for item in sublist]
    return flatten


def get_first_href(main_body):
    "Finds first url on page that is non-italicized & non-parenthesized"
    first_href = None
    # Get paragraphs in body (not inside another div)
    pars = [p for p in main_body.findAll('p') if p.parent.get('id') == 'mw-content-text']
    # Find anchors with href='/wiki/...'
    for p in pars:
        all_anchors = p.findAll('a')
        if len(all_anchors) == 0:
            continue
        hrefs = [(a.get('href'), str(a)) for a in all_anchors]
        wiki_hrefs = [x[0].split('/wiki/')[1] for x in hrefs if x[0][:6] == '/wiki/'
                      and '<i>' not in x[1]]
        bad_hrefs = get_paren_hrefs(p) + get_ital_hrefs(p)
        # Only want wiki anchors that are not inside of parentheses or italics
        good_hrefs = [x for x in wiki_hrefs if x not in bad_hrefs]
        if len(good_hrefs) == 0:
            continue
        else:
            first_href = good_hrefs[0]
            break
    return first_href


def count_from_dict(parents, child, count, all_the_parents, verbose=False):
    """ Use dictionary {link: [list of hyperlinks with first href == link], ... }
        From a dictionary {parent: [children], ...}, return number of num_steps
        to first gen parent (Philosophy). Returns -1 for a loop
    """
    if child == 'Philosophy':
        return count
    for (parent, children) in all_the_parents.items():
        if child in children:
            if parent in parents:
                if verbose:
                    print "In a loop!"
                return -1
            parents.append(parent)
            count += 1
            if verbose:
                print colored("{} :  {}".format(count, parent), "grey")
            return count_from_dict(parents, parent, count, all_the_parents, verbose)
    return count


def count_steps(wiki_href, count, all_the_parents, verbose=False):
    """ Returns count for number of steps to reach Philosophy page
        Writes to a dictionary so that if at any time we've seen a link before,
        we can avoid visiting each page in the path.
    """
    # Try to use dictionary of parents to avoid time consuming requests
    num_steps = count_from_dict([wiki_href], wiki_href, count, all_the_parents, verbose)
    if num_steps != count:
        return num_steps
    try:
        html_str = urlopen('https://en.wikipedia.org/wiki/' + wiki_href).read()
    except:
        # Link is invalid (will never lead to Philosophy)
        return -1
    soup = BeautifulSoup(html_str, 'html.parser')
    main_body = soup.find('div', attrs={'id':'mw-content-text'})
    first_href = get_first_href(main_body)
    if not first_href:
        return -1
    count += 1
    if verbose:
        print count, ": ", first_href
    # Add to dictionary
    if first_href in all_the_parents.keys():
        all_the_parents[first_href] += [wiki_href]
    else:
        all_the_parents[first_href] = [wiki_href]

    if first_href == 'Philosophy':
        return count
    return count_steps(first_href, count, all_the_parents, verbose)


def get_random_wikis(num):
    "Get n random wikipedia pages by visiting random article link"
    random_wiki = 'https://en.wikipedia.org/wiki/Special:Random'
    out = []
    for i in range(num):
        res = urlopen(random_wiki)
        out.append(res.geturl().split('/wiki/')[1])
    return out


def main():
    """ Count steps to philosophy page for n wikipedia pages (default 500)
        Prints the percent of n pages that get to Philosophy
        With verbose flags, prints entire path
    """
    parser = argparse.ArgumentParser(description='Count steps to Philosophy wikipedia page')
    parser.add_argument('-n', dest="num", default=500, type=int, help="choose how many pages to run on")
    parser.add_argument('-v', dest="verbose", action='store_true', default=False,
                        help="verbose flag")
    args = parser.parse_args()

    num_random = int(args.num)
    verbose = args.verbose

    if num_random < 1:
        print "Input n must be a positive integer"
        return

    wiki_list = get_random_wikis(num_random)

    all_the_parents, num_steps_dict = dict(), dict()
    avg_time_per_page, all_counts = [], []
    total_time = 0

    for i, wiki_href in enumerate(wiki_list):
        if verbose:
            print "\n0 :  {}".format(wiki_href)
        else:
            print "{} :  {}".format(i+1, wiki_href)
        start_time = datetime.datetime.now()
        count = count_steps(wiki_href, 0, all_the_parents, verbose)
        end_time = datetime.datetime.now()
        total_time += (end_time - start_time).seconds + (end_time - start_time).microseconds/1E6
        avg_time_per_page.append(total_time/float(i+1))
        if count in num_steps_dict.keys():
            num_steps_dict[count].append(wiki_href)
        else:
            num_steps_dict[count] = [wiki_href]
        if count > -1:
            all_counts.append(count)

    num_successful = len(all_counts)
    print("Percentage successful: %.2f" % (100.0*num_successful/num_random))

    if len(all_counts) > 0:
        print "Average: %.2f" % numpy.mean(all_counts)
        print "Standard Deviation: %.2f" % numpy.std(all_counts)

    # # To plot data and time per page
    # # How many pages took n steps
    # max_num_pages = max([len(x) for x in num_steps_dict.values()])
    # steps_per_page = [len(num_steps_dict.get(i+1) or []) for i in range(max_num_pages)]

    # # Plot number of steps frequency
    # plt.plot([i+1 for i in range(max_num_pages)], steps_per_page)
    # plt.title('Number of Steps to Philosophy')
    # plt.xlabel('Number of steps')
    # plt.ylabel('Number of pages taking n steps')
    # plt.savefig('steps_to_philosophy.png')
    # plt.clf()
    # # Plot average time per page
    # plt.plot([i+1 for i in range(num_random)], avg_time_per_page)
    # plt.axis([0, num_random, 0, math.ceil(max(avg_time_per_page))])
    # plt.title('Average Time Per Page')
    # plt.xlabel('Number of pages tested')
    # plt.ylabel('Average time per page (in seconds)')
    # plt.savefig('avg_time_per_page.png')


if __name__ == "__main__":
    main()
