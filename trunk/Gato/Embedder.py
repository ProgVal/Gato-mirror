################################################################################
#
#       This file is part of Gato (Graph Animation Toolbox) 
#       version _VERSION_ from _BUILDDATE_. You can find more information at 
#       http://www.zpr.uni-koeln.de/~gato
#
#	file:   Embedder.py
#	author: Ramazan Buzdemir
#
#       _COPYRIGHT_
#
#       This file is version $Revision$ 
#                       from $Date$
#             last change by $Author$.
#
################################################################################

from GatoGlobals import *

class Embedder:
    """ This class provides an abstract Embedder as
        a base for actual Embedder implementations """
    
    def Name(self):
	""" Return a short descriptive name for the embedder e.g. usable as 
	    a menu item """
	return "none"

    def Embed(self, theGraphEditor):
	""" Compute the Embedding. Changed display through theGraphEditor.
            Return value != none designates error/warning message """
	return none

def RedrawGraph(theGraphEditor):
    theGraphEditor.SetGraphMenuGrid(0)
    for v in theGraphEditor.G.vertices:
        theGraphEditor.MoveVertex(v, theGraphEditor.G.xCoord[v],
                                  theGraphEditor.G.yCoord[v], 1)

#----------------------------------------------------------------------
import whrandom

def RandomCoords(G):
    G.xCoord={}
    G.yCoord={}
    for v in G.vertices:
        G.xCoord[v]=whrandom.randint(10,990)
        G.yCoord[v]=whrandom.randint(10,990)
    return 1

class RandomEmbedder(Embedder):

    def Name(self):
	return "Randomize Layout"
    
    def Embed(self, theGraphEditor):
        if theGraphEditor.G.Order()==0:
            return

	theGraphEditor.config(cursor="watch")
	theGraphEditor.update()

        if RandomCoords(theGraphEditor.G):
            RedrawGraph(theGraphEditor)

	theGraphEditor.config(cursor="")
        
#----------------------------------------------------------------------
from math import pi, sin, cos

def CircularCoords(G):
    G.xCoord={}
    G.yCoord={}
    distance = 2*pi/G.Order()
    degree = 0
    xMiddle=500; yMiddle=500; radius=450
    for v in G.vertices:
        G.xCoord[v]=radius*cos(degree)+xMiddle
        G.yCoord[v]=radius*sin(degree)+yMiddle
        degree=degree+distance
    return 1

class CircularEmbedder(Embedder):

    def Name(self):
	return "Circular Layout"
    
    def Embed(self, theGraphEditor):
        if theGraphEditor.G.Order()==0:
            return

	theGraphEditor.config(cursor="watch")
	theGraphEditor.update()

        if CircularCoords(theGraphEditor.G):
            RedrawGraph(theGraphEditor)

	theGraphEditor.config(cursor="")
                
#----------------------------------------------------------------------
from PlanarEmbedding import *

class FPP_PlanarEmbedder(Embedder):

    def Name(self):
	return "Planar Layout (FPP)"
    
    def Embed(self, theGraphEditor):

	theGraphEditor.config(cursor="watch")
	theGraphEditor.update()

        if theGraphEditor.G.Order()==0:
            return
        if FPP_PlanarCoords(theGraphEditor.G):
            RedrawGraph(theGraphEditor)

	theGraphEditor.config(cursor="")

class Schnyder_PlanarEmbedder(Embedder):

    def Name(self):
	return "Planar Layout (Schnyder)"
    
    def Embed(self, theGraphEditor):
        if theGraphEditor.G.Order()==0:
            return

	theGraphEditor.config(cursor="watch")
	theGraphEditor.update()

        if Schnyder_PlanarCoords(theGraphEditor.G):
            RedrawGraph(theGraphEditor)

	theGraphEditor.config(cursor="")
        
#----------------------------------------------------------------------
from Tkinter import *
import tkSimpleDialog 
import string
from tkMessageBox import showwarning

from DataStructures import Stack

"""
def center(G):

    # Floyd-Algorithm
    INFTY=9999999
    dist={}
    for v in G.vertices:
	for w in G.vertices:
	    if w in G.InOutNeighbors(v):
		dist[v,w]=1
	    elif v==w: 
		dist[v,w]=0
	    else:
		dist[v,w]=INFTY

    for u in G.vertices:
	for v in G.vertices:
	    for w in G.vertices:		
		if dist[v,u]+dist[u,w]<dist[v,w]:
		    dist[v,w]=dist[v,u]+dist[u,w]

    max1=INFTY
    center=G.vertices[0]
    for u in G.vertices:
	max2=0
	for v in G.vertices:
	    if dist[u,v]>max2:
		max2=dist[u,v]
	if max2<max1: 
	    center=u
	    max1=max2

    return center
"""

class TreeLayoutDialog(tkSimpleDialog.Dialog):

    def __init__(self, master):
        self.G = master.G
        tkSimpleDialog.Dialog.__init__(self, master, "Tree Layout")
        

    def body(self, master):
        self.resizable(0,0)
        
        self.root=StringVar()
	self.root.set(self.G.vertices[0])
        #self.root.set(center(self.G))
        label = Label(master, text="root :", anchor=W)
        label.grid(row=0, column=0, padx=0, pady=2, sticky="w")
        entry=Entry(master, width=6, exportselection=FALSE,textvariable=self.root)
        entry.selection_range(0,"end")
        entry.focus_set()
	entry.grid(row=0,column=1, padx=2, pady=2, sticky="w")
        
        self.orientation=StringVar()
        self.orientation.set("vertical")
        
	radio=Radiobutton(master, text="vertical", variable=self.orientation, 
			  value="vertical")
	radio.grid(row=0, column=2, padx=2, pady=2, sticky="w") 
	radio=Radiobutton(master, text="horizontal", variable=self.orientation,
			  value="horizontal")
	radio.grid(row=1, column=2, padx=2, pady=2, sticky="w") 

    def validate(self):
        try: 
            if (string.atoi(self.root.get())<0 or 
		string.atoi(self.root.get()) not in self.G.vertices):
                raise rootError
            self.result=[]
            self.result.append(string.atoi(self.root.get()))
            self.result.append(self.orientation.get())
            return self.result
        except:
	    showwarning("Warning", 
			"Invalid root !!!\n"
                        "Please try again !")
	    return 0


def TreeCoords(G, root, orientation):
    S = Stack()
    visited = {}
    d = {}
    leaves = []
    number_of_leaves = 0
    height = 0
    nodes = {}
    children = {}
    father = {}

    for v in G.vertices:
        visited[v] = 0	
    visited[root] = 1
    S.Push(root)
    d[root] = 0
    nodes[0] = []
    children[root] = []
    father[root] = None 

    while S.IsNotEmpty():
        v = S.Pop()
        if orientation=="vertical":
            nodes[d[v]].insert(0,v)
            if v!=root: children[father[v]].insert(0,v)
        else:
            nodes[d[v]].append(v)
            if v!=root: children[father[v]].append(v)
        isleaf = 1
        for w in G.InOutNeighbors(v):
            if visited[w] == 0:
                isleaf = 0
                visited[w] = 1
                d[w] = d[v] + 1
                children[w] = []
                father[w] = v
                if d[w]>height:
                    height = d[w]
                    nodes[height] = []
                S.Push(w)
        if isleaf:
            number_of_leaves = number_of_leaves + 1
            if orientation=="vertical":
                leaves.insert(0,v)
            else:
                leaves.append(v)

    # Test whether the graph is connected and
    # acyclic.(=test whether the graph is a tree)
    for v in G.vertices:
            
        if visited[v]==0:
            showwarning("Warning", 
                        "Graph is not a tree,\n"
                        "not connected !!!")
            return 0
            
        ch_len = len(children[v])
        if v!=root: ch_len = ch_len + 1
        if ch_len<len(G.InOutNeighbors(v)):
            showwarning("Warning", 
                        "Graph is not a tree,\n"
                        "contains cycles !!!")                
            return 0


    if number_of_leaves<=19:
        dist1 = 50
    else:
        dist1 = 900 / (number_of_leaves-1)

    if height+1<=19:
        dist2 = 50
    else:
        dist2 = 900 / height

    if dist1<25 or dist2<30: 
        showwarning("Warning", 
                    "Tree-Layout not possible,\n"
                    "the tree is too large !!!")
        return 0


    Coord1 = {}
    Coord2 = {}
    i = 0
    for v in leaves:
        Coord1[v] = 50 + i * dist1
        Coord2[v] = 50 + d[v] * dist2
        i = i + 1
	    
    i = height - 1
    while i>=0:
        for v in nodes[i]:
            if children[v]!=[]:
                Coord2[v] = 50 + d[v] * dist2
                if len(children[v])==1:
                    Coord1[v] = Coord1[children[v][0]]
                else:
                    Coord1[v] = ( Coord1[children[v][0]] +
                                  (Coord1[children[v][-1]] - 
                                   Coord1[children[v][0]]) / 2)  
        i=i-1

    if orientation=="vertical":
        G.xCoord=Coord1
        G.yCoord=Coord2
    else:
        G.xCoord=Coord2
        G.yCoord=Coord1

    return 1


class TreeEmbedder(Embedder):

    def Name(self):
	return "Tree Layout"

    def Embed(self, theGraphEditor):
        if theGraphEditor.G.Order()==0:
            return
        
	theGraphEditor.config(cursor="watch")

	dial = TreeLayoutDialog(theGraphEditor)
	if dial.result is None:
	    theGraphEditor.config(cursor="")
	    return	

        if TreeCoords(theGraphEditor.G, dial.result[0], dial.result[1]):
            RedrawGraph(theGraphEditor)

	theGraphEditor.config(cursor="")

#----------------------------------------------------------------------
from GraphUtil import BFS

class BFSLayoutDialog(tkSimpleDialog.Dialog):

    def __init__(self, master):
        self.G = master.G
        tkSimpleDialog.Dialog.__init__(self, master, "BFS Layout")
        

    def body(self, master):
        self.resizable(0,0)
        
        self.root=StringVar()
        self.root.set(self.G.vertices[0])
        label = Label(master, text="root :" , anchor=W)
        label.grid(row=0, column=0, padx=0, pady=2, sticky="w")
        entry=Entry(master, width=6, exportselection=FALSE,textvariable=self.root)
        entry.selection_range(0,"end")
        entry.focus_set()
	entry.grid(row=0,column=1, padx=2, pady=2, sticky="w")
        
        self.direction=StringVar()
        self.direction.set("forward")
        if self.G.QDirected():
            radio=Radiobutton(master, text="forward", variable=self.direction, 
                               value="forward")
            radio.grid(row=0, column=2, padx=2, pady=2, sticky="w") 
            radio=Radiobutton(master, text="backward", variable=self.direction,
                               value="backward")
            radio.grid(row=1, column=2, padx=2, pady=2, sticky="w") 


    def validate(self):
        try: 
            if (string.atoi(self.root.get())<0 or
		string.atoi(self.root.get()) not in self.G.vertices):
                raise rootError
            self.result=[]
            self.result.append(string.atoi(self.root.get()))
            self.result.append(self.direction.get())
            return self.result
        except:
	    showwarning("Warning", 
			"Invalid root !!!\n"
                        "Please try again !")
	    return 0

def BFSTreeCoords(G, root, direction):
    BFSdistance = BFS(G,root,direction)[0]
    maxDistance=0
    maxBreadth=0
    list = {}
    for v in G.vertices:
        list[BFSdistance[v]] = []
    for v in G.vertices:
        list[BFSdistance[v]].append(v)
    maxDistance=len(list)
    for d in list.values():
        if len(d)>maxBreadth: maxBreadth=len(d)
    xDist=900/(maxDistance-1)
    yDist=900/(maxBreadth-1)
    Coord1=950

    G.xCoord={}
    G.yCoord={}
    for d in list.values():
        Coord2=500-(len(d)-1)*yDist/2
        for v in d:
            G.xCoord[v]=Coord1+whrandom.randint(-20,20)
            G.yCoord[v]=Coord2
            Coord2=Coord2+yDist 
        Coord1=Coord1-xDist
    return 1


class BFSTreeEmbedder(Embedder):

    def Name(self):
	return "BFS-Tree Layout"

    def Embed(self, theGraphEditor):
        if theGraphEditor.G.Order()==0:
            return
        
	theGraphEditor.config(cursor="watch")

	dial = BFSLayoutDialog(theGraphEditor)
	if dial.result is None: 
	    theGraphEditor.config(cursor="")
	    return	

        if BFSTreeCoords(theGraphEditor.G, dial.result[0], dial.result[1]):
            RedrawGraph(theGraphEditor)

	theGraphEditor.config(cursor="")

#----------------------------------------------------------------------

""" Here instantiate all the embedders you want to make available to
    a client. """
embedder = [RandomEmbedder(), CircularEmbedder(),
            FPP_PlanarEmbedder(), Schnyder_PlanarEmbedder(),
            TreeEmbedder(), BFSTreeEmbedder()]
