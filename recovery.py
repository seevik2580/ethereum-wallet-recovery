#!/usr/bin/python

from keys import decode_keystore_json
from joblib import Parallel, delayed

import json
import itertools
import sys
import os
import getopt
import traceback
import multiprocessing
import time
import string   
import argparse

maxvlaken=multiprocessing.cpu_count()
pocetvlaken=maxvlaken
parser = argparse.ArgumentParser()  
group = parser.add_mutually_exclusive_group(required=True)                                             
parser.add_argument("-W", "--wallet", type=str, required=True, help="keystore file")
parser.add_argument("-t", "--threads", type=int, required=False, help="number of threads")
group.add_argument("-w", "--wordlist", type=str, required=False, help="wordlist file")
group.add_argument("-b", "--brute", type=str, required=False, help="numbers / letters / characters / ASCII")
parser.add_argument("-l", "--length", type=int, required=False, help="length of repeating characters")
parser.add_argument("-e", "--end", type=str, required=False, help="file with trailing characters")
parser.add_argument("-s", "--start", type=str, required=False, help="file with initial characters")
parser.add_argument("-d", "--debug", help="enable debug", action='store_true')
args = parser.parse_args()        
debug = 1

if args.debug is False:
    debug = 0;
    f = open(os.devnull, 'w')
    sys.stderr = f
    sys.tracebacklimit = 0

def debug(msg):
    print "%s" % msg

if args.brute is not None:
    k=1
    if args.length is not None:
        k = args.length
    else:
        k = 1
    l = args.brute
    if args.brute == "ascii" or args.brute == "ASCII":
        print "using ascii table"
        l = string.printable
        print l
    z = []
    for s in xrange(k):
        a = [i for i in l]
        for y in xrange(s):
            a = [x+i for i in l for x in a]
        z = z+a

if args.threads is not None:
    pocetvlaken = args.threads

if args.wordlist is not None:
    wordlist=args.wordlist
    with open(wordlist, 'rb') as f:
        dictlist = f.read().splitlines()

if args.end is not None:
    konec = args.end
    with open(konec) as k:
        nakonci = k.read().splitlines()

if args.start is not None:
    zacatek = args.start
    with open(zacatek) as d:
        nazacatku = d.read().splitlines()


with open(args.wallet) as fd:
     json_data = json.load(fd)

grammar=['']

if args.start is not None and args.end is not None and args.wordlist is not None:
  grammar=[nazacatku, dictlist, nakonci]
elif args.start is not None and args.end is not None and args.brute is not None:
  grammar=[nazacatku, z, nakonci]
elif args.start is not None and args.wordlist is not None:
  grammar=[nazacatku, dictlist]
elif args.start is not None and args.brute is not None:
  grammar=[nazacatku, z]
elif args.start is not None and args.end is not None:
  grammar=[nazacatku, nakonci]
elif args.end is not None and args.wordlist is not None:
  grammar=[dictlist, nakonci]
elif args.end is not None and args.brute is not None:
  grammar=[z, nakonci]
elif args.brute is not None:
  grammar=[z]
elif args.wordlist is not None:
  grammar=[dictlist]

time1 = time.time()
w = json_data
print "Wallet processing: ", w["address"]

def generate_all(el, tr):
    
    if el:
        for j in xrange(len(el[0])):
            for w in generate_all(el[1:], tr + el[0][j]):
                yield w
    else:
        yield tr

pwds = []
pwds = itertools.chain(pwds, generate_all(grammar,''))
pwds = sorted(pwds, key=len)
n_pws = len(list(pwds))

def attempt(w, pw):
    sys.stdout.flush()
    counter.increment()
    jakdlouho=time.time() - time1
    cas="\t%.2f sec \t\t" % jakdlouho
        
    print counter.value, "\t", n_pws-counter.value, cas, [pw]
        
    try:
        o = decode_keystore_json(w,pw)
      
      
        print (
            """\n\n*************************\nPASSWORD FOUND:\n%s\n*************************\n\n""" % pw)
        f = open("result.txt",'w')
        f.write("""\n\n*************************\nPASSWORD FOUND:\n%s\n*************************\n\n""" % pw)
        f.close()
	sys.exit(0)
#	try:
#	    sys.exit(0)
#	except SystemExit as e:                                                   
#	    sys.exit(e)
#	except:
#	    raise
   
    except ValueError as e:
        return ""
                
class Counter(object):
    def __init__(self):
        self.val = multiprocessing.Value('i', 0)

    def increment(self, n=1):
        with self.val.get_lock():
            self.val.value += n

    @property
    def value(self):
        return self.val.value

def __main__():  
    global counter
    counter = Counter()
    try:
        Parallel(n_jobs=pocetvlaken, backend = 'multiprocessing', batch_size=1, pre_dispatch=pocetvlaken, verbose=0)(delayed(attempt)(w, pw) for pw in pwds)
        print "Done, nothing found!"
        
    except Exception, e:
        try:
            print "\n\n"
            print e
            print "Done!"
        except SystemExit as e:
            sys.exit(e)
        except:
            raise


if __name__ == "__main__":
    __main__()
