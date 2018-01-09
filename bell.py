#!/usr/bin/python

import mmh3

PRIMES = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67]

def h1(k):
    return mmh3.hash(bytes(k), signed=False)


def h2(k, m):
    return max(1, k % m)


def get_pseudo_scheme(scheme):
    if len(scheme) in PRIMES:
        return scheme[:]
    else:
        for i in PRIMES:
            if i > len(scheme):
                return scheme[:] + [255]*(i - len(scheme))


def gen_scheme(size, raids):
    raid_size = size // raids
    scheme = []
    for i in range(raids - 1):
        scheme += [i]*raid_size
    scheme += [scheme[-1] + 1]*(size - len(scheme))
    return scheme


def get_place(stripe, scheme, place, chunks):
    new_place = (h1(stripe) + place*h2(stripe, chunks)) % len(scheme)
    while scheme[new_place] == 255 and scheme[place] != 255:
        new_place = (h1(stripe) + new_place*h2(stripe, chunks)) % len(scheme)
    return scheme[new_place]


def shuffle(stripe, scheme, pseudo_scheme):
    m = len(pseudo_scheme)
    result = [get_place(stripe, pseudo_scheme, place, m) for place in range(m)]
    return result[:len(scheme)]


def model_failure(length, raids, failed, iterations):
    scheme = gen_scheme(length, raids)
    pseudo_scheme = get_pseudo_scheme(scheme)
    bell = [0] * length
    for i in range(iterations):
        shuffled = shuffle(i, scheme, pseudo_scheme)
        failure = shuffled[failed]
        if sorted(shuffled) != scheme:
            print("FAILURE! stripe #{}: {}", i, shuffled)
            break
        for strip in range(len(shuffled)):
            if strip != failed and shuffled[strip] == failure:
                bell[strip] += 1
    return bell 


for length in range(5, 65):
    for failure in range(length):
        for raids in range(2, max(3, length // 8 + 1)):
            print("Test with {} disks, {} groups, failed disk #{}".format(length, raids, failure+1))
            x = model_failure(length, raids, failure, 10000) 
            print(x)
