# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 19:43:02 2020

@author: Timothy Fleck
"""
import Dominion
import random
import itertools
import numpy
from collections import defaultdict, Counter
import scipy.stats as stats

active_rows="Adventurer,Bureaucrat,Council Room,Festival,Laboratory,\
Market,Militia,Moat,Smithy,Village,Witch,Gardens".split(",")

def optimize(adf_origin,active_rows,rounds,gamesperround):
    adfstep=adf_origin.copy()
    for r in range(rounds):
        print("Optimization round " + str(r+1))
        adfstep=optimize_step(adfstep,active_rows,gamesperround)
    return adfstep

def optimize_step(adf_base,active_rows=[],games=32000):
    comps=['*Adam1','*Adam2',('Base_table1',adf_base),('Base_table2',adf_base)]
#The rows are cards that may or may not be present in the game,
#whose presence (and presumed use) could affect the values of other cards.
#The column in the card whose value changes.
#For example, the presence of Militia in the game could make Moat more valuable.
#So the value in the Militia row and Moat column would likely be positive in 
#an optimized matrix.
#Where the row and column headings are the same, this is the base value of
#the card before any positive or negative adjustments from other cards.
    always_in="Copper,Silver,Gold,Estate,Duchy,Province".split(",")
    active_columns=active_rows+always_in
#indices is a list of tuples of strings
    indices=list(itertools.product(active_rows,active_columns))
    indices=indices+[(c,c) for c in always_in]
    L=len(indices)    
#dictionary key is the (row,column) tuple index of the matrix
#dictionary value is the list of all values that led to a win (for wd) or a loss (for ld)
    wd=defaultdict(list)
    ld=defaultdict(list)
    for g in range(games):
#deltas are random adjustments to matrix entries.
        deltas=[random.randint(-50,50) for e in range(L)]
        adf=adf_base.copy()
        for d,ij in zip(deltas,indices):
            adf.loc[ij]+=d
#Randomly select 1-3 computer or table opponents.
        players = comps[:]
        random.shuffle(players)
        players=players[:random.randint(1,3)]
        players.append(('Zoe',adf))
        random.shuffle(players)
#Play a game and analyze wins.
#winners is a tuple. The first entry is a list of name(s) of the winning player(s).
#The second entry is the output of the Dominion analyze_results function.
#The analyze_results function in the Dominion module has been modified
#to provide the lsi. The lsi (list supply index) is all the cards that have
#been selected for this particular game. Win/loss stats are only recorded
#for cards that were available in the game, to avoid noise.
        winners=Dominion.playgame(players,True)
        lsi=winners[1]#supply lsi
#Record value of each relevant matrix cell in either winning or losing dictionary.
        for ij in indices:
            if ij[0] in lsi and ij[1] in lsi:
                if 'Zoe' in winners[0]:
                    wd[ij].append(adf.loc[ij])
                else:
                    ld[ij].append(adf.loc[ij])

#After all simluated games are complete, model which adjustments affected win %
    adf_new=adf_base.copy()
    for ij in indices:
        wdij=wd[ij]
        ldij=ld[ij]
        a=adf_base.loc[ij]-50
        b=a+100
        y,q,z = bestvalue(wdij,ldij,a,b)
        x=list(range(a,b+1))
        s,r=stats.pearsonr(x,y)
#Base values of cards have an easier threshold for tinkering than interaction values.
        if r<1e-18 or (r<1e-12 and ij[0]==ij[1]):
            adf_new.loc[ij]=z
            print(str(ij) + ":" + str(adf_base.loc[ij]) + " --> " + str(z))
    return adf_new
            

#bestvalue calculates the value that gives the highest probability of a win
#W is a list of winning values. L is a list of losing values
#a and b are endpoint values. The smoothing factor must be an odd integer.
def bestvalue(W,L,a,b,smooth=11):
    length=b-a+1 #number of integers between a and b inclusive
    half=(smooth-1)//2#default 5
    left=-half#default -5
    right=half+1 #because slicing and ranges exclude last number, default 6
    CW=Counter(W) #convert list of winning values to counts of wins at each value
    CL=Counter(L) #same for losing values
    #first step provides proportions of wins in each smoothing window
    m=[0]*length
    for i in range(length):
        wins=sum([CW[a+i+j] for j in range(left,right)])
        losses=sum([CL[a+i+j] for j in range(left,right)])
        m[i]=wins/(wins+losses)
    #second step provides further smoothing, for finding best value
    n=[0]*length
    for i in range(half):
        n[i]=numpy.mean(m[:i+right])
    for i in range(half,length+left):
        n[i]=numpy.mean(m[i+left:i+right])
    for i in range(length+left,length):
        n[i]=numpy.mean(m[i+left:])
    #return smoothed ratios, further smoothed ratios, and value with best smoothed win%
    return (m,n,a+n.index(max(n)))