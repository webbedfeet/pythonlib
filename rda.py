#!/usr/bin/python

from re import compile
from re import search 
from datetime import datetime
import os, glob
import networkx as nx

def getRfiles(d):
    rfiles = glob.glob(os.path.join(d,'*.R'))
    rfiles.extend(glob.glob(os.path.join(d, '*.Rnw')))
    return(rfiles)

def getRDA(d):
    rdafiles = glob.glob('*.rda')
    rdafiles.extend(glob.glob('*.RData'))
    return(rdafiles)

def RDAprovenance(rdir,rdadir):
    rfiles = getRfiles(rdir)
    rdafiles = getRDA(rdadir)
    
    rda = RDA()
    rda.initialize(rdafiles)
    
    for fs in rfiles:
        x = Rfile(fs)
        x.parseRDA() # extract rda info from R files
        rda.RDAparse(x) # align rda provenance and use
    return(rda)

def RDAreport(rda, pdfname = 'rdafiles.html',graphname='DirStructure'):
    #print rdaOrigin
    rda.Table(fname=pdfname)
    
    # Create a graphical representation
    rda.Graph(fname=graphname)

class Rfile(list):
    def __init__(self, fname):
        self.fname = fname
        
    def readFile(self):
        self.f = open(self.fname, 'r')
        self.x = self.f.readlines()
        self.f.close()

    def findSavedRDA(self):
        x = self.x
        v = compile('[A-Za-z0-9\.]+\.[r|R][d|D]a[at]*')
        bl = [v.findall(u) for u in x if
                search('save', u) is not None]
        bl = [u[0] for u in bl if len(u)>0]
        self.saved = bl

    def findLoadedRDA(self):
        x = self.x
        v = compile('[A-Za-z0-9\.]+\.[r|R][d|D]a[at]*')
        bl = [v.findall(u) for u in x if 
                search('load', u) is not None]
        bl = [u[0] for u in bl if len(u)>0]
        self.loaded = bl

    def findLonelyRDA(self):
        x = self.x
        v = compile('[A-Za-z0-9\.]+\.[r|R][d|D]a[at]*')
        bl = {'save':[], 'load':[]}
        for i,y in enumerate(x):
            if search('save',y) is None and search('load',y) is None:
                u = v.findall(y)
                if len(u)>0:
                    if search('save', x[i-1]) is not None:
                        bl['save'].extend(u)
                    if search('load', x[i-1]) is not None:
                        bl['load'].extend(u)
        self.saved.extend(bl['save'])
        self.loaded.extend(bl['load'])

    def parseRDA(self):
        self.readFile()
        self.findSavedRDA()
        self.findLoadedRDA()
        self.findLonelyRDA()

class RDA():
    def __init__(self):
        self.rdaOrigin={}
        self.rdaLoad={}

    def initialize(self, rdafiles):
        self.rdafiles=rdafiles
        for k in rdafiles:
            self.rdaOrigin[k]=[]
            self.rdaLoad[k]=[]


    def RDAparse(self, rfiles):
        def parse(d, rfiles, f):
            for j in range(len(rfiles)):
                if rfiles[j] in d.keys():
                    d[rfiles[j]].append(os.path.basename(f.name))
                else:
                    d[rfiles[j]]=[os.path.basename(f.name)]
            return(d)
        self.rdaOrigin = parse(self.rdaOrigin, rfiles.saved, rfiles.f)
        self.rdaLoad = parse(self.rdaLoad, rfiles.loaded, rfiles.f)
        KeysOrigin = self.rdaOrigin.keys()
        KeysLoad = self.rdaLoad.keys()
        for k in set(KeysOrigin).difference(set(KeysLoad)):
            self.rdaLoad[k] = []
        for k in set(KeysLoad).difference(set(KeysOrigin)):
            self.rdaOrigin[k]=[]

    def Table(self, fname='rdafiles.html'):
        """
        Create a HTML table with information about the provenance and use of every 
        R data file (*.rda, *.Rnw) in a directory
    
        d1 = a dictionary with key=R data file; values = R files generating it
        d2 = a dictionary with key=R data file; values = R files using it
        """
        d1=self.rdaOrigin
        d2 = self.rdaLoad
        rdafiles=self.rdafiles
        output = "<html>\n"
        output+="<head><link href='tables.css' rel='stylesheet' type='text/css'></head><body>\n"
        output +="<h2> Provenance of R data files "
        output += "("+datetime.now().strftime("%A, %d %B %Y %I:%M%p")+")<br/>\n"
        output += "<br/>\n <table>\n"
        output += "<tr><th>File</th><th>Source</th><th>Loaded in</th><th>Available</th></tr>\n"
        Keys = d1.keys()
        Keys.sort()
        for key in Keys:
            bl = list(set(d1[key]))
            loaded = list(set(d2[key]))
            if key in rdafiles:
                orphan = ''
            else:
                orphan = 'Missing'
            bl.sort()
            loaded.sort()
            output +="<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" % (key,
                    ', '.join(bl), ', '.join(loaded), orphan)
        output += "</table></body></html>"
        f = open(fname,'w')
        f.writelines(output)
        f.close()
        return 0

    def Graph(self, fname='DirStructure'):
        d1 = self.rdaOrigin
        d2 = self.rdaLoad
        DG = nx.DiGraph()
        DG.add_nodes_from(d1.keys())
        DG.add_nodes_from(d2.keys())
        bl = d1.values()
        bl.extend(d2.values())
        bl2=[]
        for u in bl:
            bl2.extend(u)
        DG.add_nodes_from(bl2)
        for k in d2.keys():
            for u in d2[k]:
                DG.add_edge(k,u)
        for k in d1.keys():
            for u in d1[k]:
                DG.add_edge(u,k)
        nx.write_dot(DG, fname+'.dot')
        os.system('dot -Tpdf %s.dot -o %s.pdf' % (fname, fname))
        return 0


