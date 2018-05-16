import sys, os
from itertools import permutations
import time
import re
import argparse

parser = argparse.ArgumentParser()  
group = parser.add_mutually_exclusive_group(required=True)   
group.add_argument("-s", "--slova", type=str, required=False, help="slova ze kterych generovat wordlist, oddeluj carkou")
group.add_argument("-v", "--vstupnisoubor", type=str, required=False, help="soubor ve kterem jsou slova ze kterych generovat wordlist")
parser.add_argument("-min", "--minimal", type=int, required=False, help="minimalni delka znaku")
parser.add_argument("-max", "--maximal", type=int, required=False, help="maximalni delka znaku")
group.add_argument("-a", "--ascii", action='store_true', required=False, help="generate from ascii table")

args = parser.parse_args() 

class RotatingFile(object):
    
    def __init__(self, directory='', filename='wordlist', max_files=sys.maxint,
        max_file_size=50000000):
        self.ii = 1
        self.directory, self.filename      = directory, filename
        self.max_file_size, self.max_files = max_file_size, max_files
        self.finished, self.fh             = False, None
        self.open()
        self.time1=time.time()
        self.c = 0
        self.muzes=1

    def rotate(self):
        
        if (os.stat(self.filename_template).st_size>self.max_file_size):
            self.close()
            self.ii += 1
            if (self.ii<=self.max_files):
                self.open()
            else:
                self.close()
                self.finished = True
                

    def open(self):
        self.fh = open(self.filename_template, 'w')

    def write(self, text=""):
        self.fh.write(text)
        self.fh.flush()
        self.rotate()

    def close(self):
        print self.filename_template, time.time() - self.time1
        self.fh.close()

    
    
    @property
    def filename_template(self): 
        return self.directory + self.filename + "_%0.2d.txt" % self.ii

if __name__=='__main__':
    print "Generuji variace hesel"
    myfile = RotatingFile(max_files=99999999)
    
    if args.ascii is True:	
	f="0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,!,\",#,$,%,&,',(,),*,+,-,.,/,:,;,<,=,>,?,@,[,\,],^,_,`,{,|,},~, "
	slova=f
	
    if args.slova is not None:
        f=args.slova
        slova=f
        
    if args.vstupnisoubor is not None:
        f=open(args.vstupnisoubor)
        slova=f.readline()
        
    if args.minimal is None:
	minimal = 1
    else:
	minimal = args.minimal

    if args.maximal is None:
	maximal = 64
    else:
   	maximal = args.maximal

    while not myfile.finished:
        maxpocet=len(slova.split(","))
        for pocet in xrange(maxpocet+1):
            for group in permutations(slova.split(","), pocet):
                slovo=''.join(group)
                delka=len(slovo)
                if delka >= minimal and delka <= maximal:
                    myfile.c+=1
                    myfile.write("%s\n" % slovo)
                    if myfile.c % 100000 == 0:
                        print "Generuji", myfile.c,". heslo" 
        
        print myfile.filename_template, time.time() - myfile.time1
        print "Hotovo, vygenerovano %s kombinaci" % myfile.c
        print "Vytvoreno %s souboru" % myfile.ii
        break

    
