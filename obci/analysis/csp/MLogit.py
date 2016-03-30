#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""This is a class for Multinomial Logit Regression

Class uses scipy.optimize package for minimalization of a cost function.
The gradient of the cost function is passed to the minimizer.

Piotr Milanowski, November 2011, Warsaw
"""

from scipy.optimize import fmin_ncg, fmin_bfgs, fmin
import numpy as np
import matplotlib.pyplot as plt

def mix(x1, x2, deg=6):
    out = np.zeros([len(x1), sum(range(deg+2))])
    k = 0
    for i in xrange(deg+1):
        for j in range(i+1):
            out[:,k] = x1**(i-j)*x2**(j)
            k += 1

    return out

class logit(object):
    """This is a class for a normal two-class logistic regression

    The hypothesis of this regression is a sigmoid (logistic, logit) function.
    It returns the probability of the data belonging to the first class.

    The minimalization of a cost function is based on NCG algorithm from scipy.optimize package.

    The regression can account the regularization factors.
    """
    def __init__(self, data, classes, labels=None):
        """Initialization of data
        
        A column of ones is added to the data array.

        Parameters:
        ===========
        data : 2darray
            NxM array. Rows of this array represent data points, columns represent features.
        classes : 1darray
            a N dimensional vector of classes. Each class is represented by either 0 or 1.
        class_dict [= None] : dictionary
            a 2 element dictionary that maps classses to their names.

        Example:
        =========
            >>>X = np.random.rand(20, 4)     #data
            >>>Y = np.random.randint(0,2,20) #classes
            >>>labels = ['class 1','class 2']
            >>>MLogit.logit(X, Y, labels)
        """
        self.dataNo, self.featureNo = data.shape
        if len(classes) != self.dataNo:
            raise ValueError, 'Not every data point has its target lable!'
        #Adding a columns of 1s and normalizing data - NO NORMALIZATION NEEDED
        self.X = np.concatenate((np.ones([self.dataNo, 1]), data), axis = 1)
        self.Y = classes

    def _sigmoid(self, z):
        """This returns the value of a sigmoid function.

        Sigmoid/Logistic/Logit finction looks like this:
            f(z) = over{1}{1 + exp(-z)}

        Parameters:
        ===========
        z : ndarray
            the parameter of the function
        Returns:
        sig : ndarray
            values of sigmoid function at z
        """
        return 1/(1 + np.exp(-z))

    def cost_function(self, theta, reg = 0):
        """The cost function of logit regression model

        It looks like this:
            J(theta) = -((1/M)*sum_{i=1}^{M}(y_i*log(h(theta;x_i))+(1-y_i)*log(1-h(theta;x_i)))) +
                        + (reg/2*m)sum_{i=1}^{N}(theta_i)^2
        Parameters:
        ===========
        theta : 1darray
            the array of parameters. It's a (N+1) dimensional vector
        reg [= 0] : float
            the regularization parameter. This parameter penalizes theta being too big (overfitting)
        Returns:
        ========
        J : float
            the value of cost function for given theta
        """

        z = self._sigmoid(np.dot(self.X, theta))
        regular = (reg/(2.0*self.dataNo))*sum(theta[1:]*theta[1:])
        J = self.Y * np.log(z) + (1 - self.Y)*np.log(1 - z)
        J = -(1.0 / self.dataNo) * sum(J)
        return regular + J

    def gradient_function(self, theta, reg = 0):
        """The gradient of cost function

        The gradient looks like this:
            g[0] = 1/N * sum_{i=1}^{N}(h(theta;x_i) - y_i)*x_i^0 
            g[j] = 1/N * sum_{i=1}^{N}(h(theta;x_i) - y_i)*x_i^j - theta[j]*reg/N
        Parameters:
        ===========
        theta : 1darray
            the vector of parameters
        reg : float
            the regularization parameter
        Returns:
        ========
        fprime : 1darray
            the gradient of cost function.
        """
        gradient = np.zeros(self.featureNo + 1)
        N = 1.0 / self.dataNo
        z = np.dot(self.X, theta)
        cost = self._sigmoid(z) - self.Y
#        gradient[0] = N * sum(cost * self.X[:, 0])
#        for j in xrange(self.featureNo):
#            gradient[j] = N * sum(cost * self.X[:, j]) - reg * N * theta[j]
        gradient = N * np.dot(cost, self.X)
        gradient[1:] += reg * N *  theta[1:]
        return gradient

    def fit(self, maxiter, reg = 0, initial_gues = None):
        """Minimizing function

        Based on NCG function from scipy.optimize package

        Parameters:
        ===========
        maxiter : int
            maximal number of iterations
        reg [= 0] : float
            regularization parameter
        initial_gueas [= None] : 1darray
            a vector of #features + 1 size. If None zeros will be asumed.
        Returns:
        ========
        theta : 1darray
            optimal model parameters
        """
        if initial_gues is None:
            initial_gues = np.zeros(self.featureNo + 1)

        out = fmin_bfgs(self.cost_function, initial_gues, \
                self.gradient_function, args = ([reg]))
        self.theta = out
        return out

    def predict(self, x, val=0.9):
        """For prediction of x

        Returns predicted probability of x being in class 1
        """
        x = np.insert(x, 0, 1) #inserting one at the beginning
        z = np.dot(x, self.theta)
        #if self._sigmoid(z) >=val:
            #return 1
        #else:
            #return 0
        return self._sigmoid(z)
    
    def plot_features(self, show=True):
        y = self.Y
        idx = np.argsort(y)
        x = self.X[idx, :]
        y = y[idx]
        N, feats = x.shape
        if feats == 3:
            idx1 = np.where(y==1)[0][0]
            x1 = x[:idx1, :]
            x2 = x[idx1:, :]
            plt.plot(x1[:,1],x1[:,2],'ro',x2[:,1],x2[:,2],'go')
            for x in np.arange(-5, 5, 0.5):
                for y in np.arange(-3, 3, 0.5):
                    if self.predict(np.array([x,y])) <=0.5:
                        plt.plot(x,y,'r+')
                    else:
                        plt.plot(x,y,'g+')
            plt.legend(('Class 0','Class 1'))
            if show:
                plt.show()
        elif feats == 2:
            idx1 = np.where(y==1)[0][0]
            x1 = x[:idx1, :]
            x2 = x[idx1:, :]
            for x in np.arange(x1.min(), x1.max(), 0.1):
                for y in np.arange(x2.min(), x2.max(), 0.1):
                    if self.predict(np.array([x,y])) <=0.01:
                        plt.plot(x,y,'r+')
                    else:
                        plt.plot(x,y,'g+')
            plt.plot(x1[:,1],'ro',x2[:,1],'go')
            if show:
                plt.show()
        else:
            print "More than 2 dimmensions",x.shape 

#    def plot_fitted(self):
#        N, feats = self.X.shape
#        if feats == 3:
#            x1 = se

    def __normalization(self, data):
        """Function normalizes the data

        Normalization is done by subtracting the mean of each column from each column member
        and dividing by the column variance.

        Parameters:
        ===========
        data : 2darray
            the data array
        Returns:
        ========
        norms : 2darray
            normalized values
        """
        mean = data.mean(axis = 0)
        variance = data.std(axis = 0)
        return (data - mean) / variance

class mlogit(logit):
    """This is a multivariate variation of logit model

    """
    def __init__(self, data, classes, labels=None):
        """See logit description"""
        super(mlogit, self).__init__(data, classes, labels)
        self.classesNo, classesIdx = np.unique(classes, return_inverse = True)
        self.count_table = np.zeros([len(classes), len(self.classesNo)])
        self.count_table[range(len(classes)), classesIdx] = 1.0

    def fit(self, maxiter, reg = 0, initial_gues = None):
        """Fitting logit model for multiclass case"""
        theta = np.zeros([self.featureNo + 1, len(self.classesNo)])
        for i in range(len(self.classesNo)):
            self.Y = self.count_table[:,i]
            theta[:, i] = super(mlogit, self).fit(maxiter, reg = reg, initial_gues = initial_gues)
        self.theta = theta
        return theta

    def predict(self, x, val=0.9):
        """Class prediction"""
        x = np.insert(x, 0, 1)
        z = np.dot(x, self.theta)
        probs = super(mlogit, self)._sigmoid(z)
        idx = np.argmax(probs)
        if probs[idx] >= val:
            return self.classesNo[idx]
        else:
            return None

    def plot_features(self):
        cn = len(self.classesNo)
        idx = np.argsort(self.Y)
        y = self.Y[idx]
        x = self.X[idx,:]
        classes = []
        if x.shape[1] == 3:
            for i in range(cn):
                beg, end = np.where(y==i)[0][[0,-1]]
                plt.plot(x[beg:end+1, 1], x[beg:end +1, 2],'o')
                classes.append('Class'+str(i))
            plt.legend(classes)
            plt.show()
        else:
            print "More than 2 dimmesions"
            
#class diagnostics(object):

#    def __init__(self, classifier_obj, division=[0.6, 0.2, 0.2]):
#        self.obj = classifier_obj
#        self.div = division
#        self.N, self.ft = self.obj.dataNo, self.obj.featureNo
#        self.cvNo = self.N * division[1]
#        self.testNo = self.N * division[2]
#        self.trainNo = self.N * division[0]

#    def diagnose(self, iters, reg, odrer=1, val=0.9):
#        idx = np.linspace(0, self.N-1, self.N)
#        TP, FP, TN, FN
#        train_ok = {'tp':0,'fp':0,'fn':0,'fp':0}
#        cv_ok = {'tp':0,'fp':0,'fn':0,'fp':0}
#        test_ok = {'tp':0,'fp':0,'fn':0,'fp':0}
#        X = self.obj.X
#        Y = self.obj.Y
#        for i in xrange(iters):
#            np.random.shuffle(idx)
#            train_set = X[idx[:self.trainNo], :]
#            cv_set = X[idx[self.trainNo:self.trainNo+self.cvNo], :]
#            test_set = X[idx[self.trainNo+self.cvNo:], :]
#            classes_train = Y[idx[:self.trainNo], :]
#            classes_cv = Y[idx[self.trainNo:self.trainNo+self.cvNo], :]
#            classes_test = Y[idx[self.trainNo+self.cvNo:], :]
#            Training
#            self.obj.X = train_set
#            self.obj.Y = classes_train
#            self.obj.fit(100)
#            for j, row in enumerate(train_set):
#                cl = self.obj.predict(row, val)
#                if cl == classes_train[j]:
#                    train_ok['tp'] += 1
#                elif cl is None:
#                    train_ok['fn'] += 1
#                else:
#                    train_ok['fp'] += 1
#            Crossvalidation
#            for j, row in enumerate(cv_set):
#                cl = self.obj.predict(row, val)
#                if cl == classes_cv[j]:
#                    cv_ok['tp'] += 1
#                elif cl in None:
#                    cv_ok['fn'] += 1
#                else:
#                    cv_ok['fp'] += 1
#            Test set
#            for j, row in enumerate(test_set):
#                cl = self.obj.predict(row, val)
#                if cl == classes_test[j]:
#                    test_ok['tp'] += 1
#                elif cl is None:
#                    test_ok['fn'] += 1
#                else:
#                    test_ok['fp'] += 1

#    def power_set(self, lst, l):
#        """Create a powerset of a list for given length"""
#        r = [[]]
#        for e in lst:
#            r.extend([s + [e] for s in r])
#        return set([j for j in r if len(j) <= l])

#    def next_order(self, kernel, next_o):

#    def make_order(self, p):
#        init_featsNo = self.featNo

