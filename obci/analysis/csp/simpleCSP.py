#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""Set of functions for calculation of CSP filter

This is a set of functions for calculating CSP filters
when there are only two matrices to diagonalize.


For diagonalization of more than two matrices see ffdiag module

Piotr Milanowski, Warsaw, October 2011
"""

import numpy as np
from scipy.linalg import eigh, eig

def pfu_csp(R_A, R_B):
    """This function implements CSP filter creation proposed in
    Designing optimal spatial filters for single-trial EEG classification in a movement task;
    Johannes Mueller-Gerking, Gert Pfurtscheller, Henrik Flyvbjerg
    Clinical Neurophysiology vol.110(1999), pp.787--798
    
    Parameters:
    ===========
    R_A : 2darray
        first array to diagonalize
    R_B : 2darray
        second array to diagonalize

    Returns:
    ========
    P : 2darray
        CSP filter array
    """
    #dane1 i dane2 - macierze o ksztalcie N_kanalow x N_sampli
    #znormalizowane macierze cov dla kazdego z patternow
    #dane1 = np.matrix(dane1)
    #dane2 = np.matrix(dane2)
    #R_A = dane1*dane1.T/np.trace(dane1*dane1.T)
    #R_B = dane2*dane2.T/np.trace(dane2*dane2.T)
    #print 'RA',R_A
    #print 'RB',R_B
    R_C = R_A + R_B
    #lam,B = eig(R_C, b=None, right=0,left=1, overwrite_a=0, overwrite_b=0)
    lam,B = eigh(R_C)

    lam=np.matrix(np.eye(len(lam))*np.power(lam,(-0.5)))
    #print 'lam',lam
    #print 'B',B[:,1]
    # whitening transformation
    
    W= lam*B.T
    #print 'W',W
    S_A=W*R_A*W.T
    S_B=W*R_B*W.T
    psi_A, U_A = eig(S_A)
    psi_B, U_B = eig(S_B)

    P=U_B.T*W
    return np.array(P)

def csp(c_max, c_min):
    """This is the simplest diagonalization.

    Function returns array. Each column is a filter sorted
    in descending order i.e. first column represents filter
    that explains most energy, second - second most, etc.

    Parameters:
    ===========
    c_max : ndarray
        covariance matrix of signal to maximalize.
    c_min : ndarray
        covariance matrix of signal to minimalize.

    Returns:
    ========
    P : ndarray
        each column of this matrix is a CSP filter sorted in descending order
    vals : array-like
        corresponding eigenvalues
    """
    vals, vects = eig(c_max, c_min)
    vals = vals.real
    vals_idx = np.argsort(vals)[::-1]
    P = np.zeros([len(vals), len(vals)])
    for i in xrange(len(vals)):
        P[:,i] = vects[:,vals_idx[i]] / np.sqrt(vals[vals_idx[i]])
    return P, vals[vals_idx]
