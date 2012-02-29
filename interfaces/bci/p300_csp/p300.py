#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
"Classes for BCI based on p300 paradigm
"Training and on-line analysis
"
"Piotr Milanowski, Feb. 2012, Warsaw
"""
import numpy as np
from analysis.csp import signalParser as sp
import matplotlib.pyplot as plt
from scipy.linalg import eig
import scipy.signal as ss
from analysis.csp.filtfilt import filtfilt
from analysis.csp.artifactsClassifier import artifactCalibration


class p300_train(object):
    def __init__(self, fn, channels, to_freq, montage_channels, montage, idx=1, csp_time=[0, 0.3]):
        self.data = sp.signalParser(fn)
        self.tags = self.data.get_p300_tags(idx=idx, samples=False)
        
        signal = self.data.prep_signal(to_freq, channels, montage_channels, montage)
        signal2 = np.zeros(signal.shape)
        self.fs = to_freq
        signal2 = np.zeros(signal.shape)
        self.wrong_tags = self.data.get_p300_tags(idx=idx, rest=True, samples=False)
        #artifacts_data = np.zeros([len(channels), self.fs*a_time, len(self.tags)])
        #for i,p in enumerate(self.tags):
            #artifacts_data[...,i] = signal[:, p:p+p*self.fs]
        #self.a_features, self.bands = artifactCalibration(artifacts_data, self.fs)
        self.channels = channels
        self.idx = idx
        b,a = ss.butter(3, 2*1.0/self.fs, btype = 'high')
        b_l, a_l = ss.butter(3, 20.0*2/self.fs, btype = 'low')
        for e in xrange(len(self.channels)):
            tmp = filtfilt(b,a,signal[e, :])
            signal2[e, :] = filtfilt(b_l, a_l, tmp)
        self.signal_original = signal2
        self.t1, self.t2 = self.show_mean(csp_time, 'Cz', dont_plot=False)
        P, vals = self.train_csp(signal2, [self.t1, self.t2])
        self.P = P
        self.signal = np.dot(P[:, 0], signal2)
        
    def __c2n(self, channel):
        return self.channels.index(channel)
    
    def show_mean(self, time, channel, dont_plot=True, plt_all=False, mean_only=True, suggest=True):
        pre = time[0]
        post = time[1]
        #b,a = ss.butter(3, 2*1.0/self.fs, btype = 'high')
        #b_l,a_l = ss.butter(3, 2*20.0/self.fs, btype = 'low')
        to_see = np.zeros((post + pre) * self.fs)
        other = np.zeros((post + pre) * self.fs)
        tags2 = self.data.get_p300_tags(idx=self.idx, rest=True, samples=False)
        sigs_trg = np.zeros([len(self.tags), len(to_see)])
        sigs = np.zeros([len(tags2), len(to_see)])
        for j, i in enumerate(self.tags):
            if (i + post) * self.fs < self.data.sample_count:
                #sig = filtfilt(b,a, self.signal_original[self.__c2n(channel), (i - pre) * self.fs : (i - pre) * self.fs + len(to_see)])
                #sig = filtfilt(b_l, a_l, sig)
                sig =  self.signal_original[self.__c2n(channel), (i - pre) * self.fs : (i - pre) * self.fs + len(to_see)]
                sigs_trg[j, :] = sig
                to_see += sig - sig.mean()
        for j, i in enumerate(tags2):
            if (i + post) * self.fs < self.data.sample_count:
                #sig = filtfilt(b,a, self.signal_original[self.__c2n(channel), (i - pre) * self.fs : (i - pre) * self.fs + len(other)])
                #sig = filtfilt(b_l, a_l, sig)
                sig = self.signal_original[self.__c2n(channel), (i - pre) * self.fs : (i - pre) * self.fs + len(other)]
                sigs[j, :] = sig
                other += sig - sig.mean()
        to_see /= len(self.tags)
        other /= len(tags2)
        t_vec = np.linspace(-pre, post, len(to_see))
        sug1 = 0
        sug2 = 0
        if mean_only:
            to_draw1 = to_see
            to_draw2 = other
            if suggest:
                x1 = np.where(t_vec > 0.0)[0][0]
                x2 = np.where(t_vec < 0.4)[0][-1]
                mx_idx = to_draw1[x1 : x2].argmax() + x1
                plus = int(0.1 * self.fs)
                if mx_idx - plus < 0:
                    pass
                else:
                    sug1 = t_vec[mx_idx - plus]
                if mx_idx + plus >= len(t_vec):
                    sug2 = t_vec[-1]
                else:
                    sug2 = t_vec[mx_idx + plus]
        else: 
            to_draw1 = sigs_trg.T
            to_draw2 = sigs.T
        if dont_plot:
            if suggest:
                return sug1, sug2
        else:
            plt.figure(2)
        if plt_all:
            plt.plot(t_vec, to_draw2, 'b-',[0, 0],[max(to_draw1),min(to_draw1)], 'r-', t_vec, to_draw1, 'g-')
        else:
            plt.plot(t_vec, to_draw1, 'g-', [0, 0], [max(to_draw1), min(to_draw1)],'b-')
            plt.plot(t_vec, to_draw2, 'b-',[0, 0],[max(to_draw1),min(to_draw1)], 'r-', t_vec, to_draw1, 'g-')
            if suggest:
                plt.plot([sug1, sug1], [max(to_draw1), min(to_draw1)], 'r-', [sug2, sug2], [max(to_draw1), min(to_draw1)], 'r-',\
                    [t_vec[mx_idx], t_vec[mx_idx]],[min(to_draw1), max(to_draw1)], 'b-')
        plt.title('Cz')
        plt.show()
        if suggest:
            return sug1, sug2
    
    
    def train_csp(self, signal, time):
        pre = time[0]
        post = time[1]
        N = (post + pre) * self.fs
        b,a = ss.butter(3, 2*1.0/self.fs, btype = 'high')
        chNo, smpl = signal.shape
        cov_trg = np.zeros([len(self.channels), len(self.channels)])
        cov = np.zeros([len(self.channels), len(self.channels)])
        tags2 = self.data.get_p300_tags(idx=self.idx,rest=True, samples=False)
        for i in self.tags:
            if (i + post) * self.fs < self.data.sample_count:
                A = np.matrix(signal[:, (i - pre) * self.fs : (i - pre) * self.fs + N])
                cov_trg += A * A.T/ np.trace(A * A.T)
        cov_trg /= len(self.tags)
        for i in tags2:
            if (i + post) * self.fs < self.data.sample_count:
                A = np.matrix(signal[:, (i - pre) * self.fs : (i - pre) * self.fs + N])
                cov += A * A.T/ np.trace(A * A.T)
        cov /= len(tags2)
        P, vals = self.__get_filter(cov_trg, cov_trg + cov)
        return P, vals
        
    def show_mean_CSP(self, time, tags=None):
        if tags is None:
            tags = self.tags
        sigs_trg, sigs = self.__get_data(time, tags)            
        t_vec = np.linspace(-time[0], time[1], sigs.shape[1])
        plt.figure(1)
        plt.plot(t_vec, sigs.T,'b-', t_vec, sigs_trg.T, 'g-')
        plt.title('CSP')
        return t_vec
        #plt.show()
        
    def get_n_perms(self, n, m, rg):
        """From a set of numbers [0, rg] returns m sets of n numbers each"""
        generated = []
        rng = np.arange(0, rg)
        i = 0
        while i < m:
            np.random.shuffle(rng)
            to_ad = np.copy(rng[:n])
            to_ad.sort()
            to_ad = list(to_ad)
            if not (to_ad in generated):
                generated.append(to_ad)
                i += 1
        return generated
            
    def get_n_mean(self, n, tags, time, xc_time):
        sign_trg, sigs = self.__get_data(time, tags)
        tags2 = self.data.get_p300_tags(idx=self.idx,rest=True, samples=False)
        mean, l, r = self.get_mean(tags, time)
        #mean /= np.sqrt(np.dot(mean, mean))
        mean[:l] = 0
        mean[r:] = 0
        trg = []
        no_trg =[]
        s_l = sign_trg.shape[1]
        s_l2 = sigs.shape[1]
        if n == 1:
            z_trg, z_no_trg, mu, sigma = self.get_stats(time, tags)
        else:
            target_sets = self.get_n_perms(n, len(tags), len(tags))
            no_target_sets = self.get_n_perms(n, len(tags2), len(tags2))
            for i in target_sets:
                tmp_sig = np.zeros(s_l)
                for j in xrange(n):
                    tmp_sig += sign_trg[i[j], :]
                tmp_sig /= n
                tmp_sig[:l] = 0
                tmp_sig[r:] = 0
                #tmp_sig /= np.sqrt(np.dot(tmp_sig, tmp_sig))
                xcor = np.correlate(tmp_sig, mean, 'full')[s_l - xc_time * self.fs : s_l + xc_time * self.fs]
                trg.append(xcor.max())
            for i in no_target_sets:
                tmp_sig = np.zeros(s_l2)
                for j in xrange(n):
                    tmp_sig += sigs[i[j], :]
                tmp_sig /= n
                #tmp_sig /= np.sqrt(np.dot(tmp_sig, tmp_sig))
                tmp_sig[:l] = 0
                tmp_sig[r:] = 0
                xcor = np.correlate(tmp_sig, mean, 'full')[s_l2 - xc_time * self.fs : s_l2 + xc_time * self.fs]
                no_trg.append(xcor.max())
            trg = np.array(trg)
            no_trg = np.array(no_trg)
            mu, sigma = no_trg.mean(), no_trg.std()
            z_trg = (trg - mu) / sigma
            z_no_trg = (no_trg - mu)/sigma
        return z_trg, z_no_trg, mu, sigma
                    
    
    def __get_data(self, time, tags, tags2=None):
        pre = time[0]
        post = time[1]
        sl = (post + pre) * self.fs
        sigs_trg = np.zeros([len(tags), sl])
        if tags2 is None:
            tags2 = self.data.get_p300_tags(idx=self.idx,rest=True, samples=False)
        sigs =  np.zeros([len(tags2), sl])
        for j, i in enumerate(tags):
            if (i + post) * self.fs < self.data.sample_count:
                sig = self.signal[(i - pre) * self.fs : (i - pre)*self.fs + sigs_trg.shape[1]]
                sigs_trg[j, :] = sig
        for j, i in enumerate(tags2):
            if (i + post) * self.fs < self.data.sample_count:
                sig = self.signal[(i - pre) * self.fs : (i - pre)*self.fs + sigs.shape[1]]
                sigs[j, :] = sig
        return sigs_trg, sigs
                
    def get_stats(self, time, tags, xc_time=0.05, show=False):
        sigs_trg, sigs = self.__get_data(time, tags)
        mean, l,r = self.get_mean(tags, time)
        mean[:l] = 0
        mean[r:] = 0
        #mean /= np.sqrt(np.dot(mean, mean))
        trg = []
        non_trg = []
        for i in sigs_trg:
            #i = i / np.sqrt(np.dot(i, i))
            i -= i.mean()
            i[:l] = 0
            i[r:] = 0
            sl = len(i)
            xcor = np.correlate(i, mean, 'full')[sl - xc_time*self.fs:sl + xc_time*self.fs]
            trg.append(xcor.max())
            #trg.append(i.var())
        for i in sigs:
            #i = i / np.sqrt(np.dot(i, i))
            i -= i.mean()
            i[:l] = 0
            i[r:] = 0
            sl = len(i)
            xcor = np.correlate(i, mean, 'full')[sl - xc_time*self.fs:sl + xc_time*self.fs]
            non_trg.append(xcor.max())
            #non_trg.append(i.var())
        trg = np.array(trg)
        non_trg = np.array(non_trg)
        z_trg = (trg - non_trg.mean())/non_trg.std()
        z_non_trg = (non_trg - non_trg.mean())/non_trg.std()
        if show:
            plt.figure(3)
            plt.hist(z_trg, normed=True, label='Target')
            plt.hist(z_non_trg, normed=True, alpha=0.5, label='Non target')
            plt.legend()
            plt.show()
        return z_trg, z_non_trg, non_trg.mean(), non_trg.std()
    
    def wyr(self, tags=None, time=[0.1, 0.5], its=10, xc_time=0.1):
        if tags is None:
            new_tags = self.tags[:]
        else:
            new_tags = tags[:]
        go = True
        max_cor = 0
        t_vec = np.linspace(-time[0], time[1], sum(time) * self.fs)
        while go:
            mean, l, r = self.get_mean(new_tags, m_time=time)
            max_cor = 0
            for j, i in enumerate(new_tags):
                beg = (i - time[0]) * self.fs
                sig = self.signal[beg : beg +  len(mean)]
                xcor = np.correlate(sig, mean, 'full')[len(sig) - xc_time*self.fs:len(sig) + xc_time * self.fs]
                max_idx = xcor.argmax()
                cor = len(xcor) / 2 - max_idx
                new_tags[j] -= cor/float(self.fs)
                if abs(cor) > max_cor:
                    max_cor = abs(cor)
                #if j == 1:
                    #plt.plot(t_vec, sig, 'b-', t_vec, mean, 'g-')
                    #plt.title(str(cor))
                    #plt.show()
            #print max_cor
            if max_cor < 2:
                go = False
        return new_tags
                
    def prep_classifier(self, sr, P_vectors=3, mean_time=[0, 0.5], xc_time=0.05, reg=1):
        trg = np.zeros([P_vectors, sr, len(self.tags)])
        non_trg = np.zeros([P_vectors, sr, len(self.wrong_tags)])
        mu = np.zeros([P_vectors, sr])
        sigma = np.zeros([P_vectors, sr])
        classifiers = []
        mean = np.zeros([P_vectors, sum(mean_time)*self.fs])
        left = np.zeros(P_vectors)
        right = np.zeros(P_vectors)
        for v in xrange(P_vectors):
            self.signal = np.dot(self.P[:, v], self.signal_original)
            nt = self.wyr()
            mean[v, :], left[v], right[v] = self.get_mean(nt, mean_time)
            for n in xrange(1, sr+1):
                z1, z2, me, s = self.get_n_mean(n, nt, mean_time, xc_time)
                trg[v, n-1, :] = z1
                non_trg[v, n-1, :] = z2
                mu[v, n-1] = me
                sigma[v, n-1] = s
        for i in xrange(sr):
            data = np.vstack((trg[:, i, :].T, non_trg[:, i, :].T))
            classes = np.hstack((np.zeros(trg.shape[2]), np.ones(non_trg.shape[2])))
            cl = logit(data, classes, ['target', 'non target'])
            cl.fit(100, reg=reg)
            classifiers.append(cl)
        self.signal = np.dot(self.P[:, 0], self.signal_original)
        return classifiers, mu, sigma, mean, left, right
            
                
    def get_mean(self, tags, m_time=[0.1, 0.5], plot_mean=False):
        mean = np.zeros(sum(m_time) * self.fs)
        for i in tags:
            beg = (i - m_time[0]) * self.fs
            mean += self.signal[beg:beg + len(mean)]
        mean /= len(tags)
        idx = np.argmax(np.abs(mean))
        left = idx
        right = idx
        if mean[idx] < 0:
            tmp_mean = -mean
        else:
            tmp_mean = mean
        while left > 0 and tmp_mean[left - 1] - tmp_mean[left] < 0:
            left -= 1
        while right < len(tmp_mean)-1 and tmp_mean[right + 1] - tmp_mean[right] < 0:
            right += 1
        while left > 0 and tmp_mean[left - 1] - tmp_mean[left] > 0:
            left -= 1
        while right < len(tmp_mean)-1 and tmp_mean[right + 1] - tmp_mean[right] > 0:
            right += 1
        print left, right
        if plot_mean:
            plt.plot(mean, 'r-')
            plt.plot([left, left], [min(mean), max(mean)])
            plt.plot([right, right], [min(mean), max(mean)])
            plt.show()
          
        return mean, left, right
    
    def __get_filter(self, c_max, c_min):
        """This retzurns CSP filters

            Function returns array. Each column is a filter sorted in descending order i.e. first column represents filter that explains most energy, second - second most, etc.

            Parameters:
            -----------
            c_max : ndarray
                covariance matrix of signal to maximalize.
            c_min : ndarray
                covariance matrix of signal to minimalize.

            Returns:
            --------
            P : ndarray
                each column of this matrix is a CSP filter sorted in descending order
            vals : array-like
                corresponding eigenvalues
        """
        vals, vects = eig(c_max, c_min + c_max)
        vals = vals.real
        vals_idx = np.argsort(vals)[::-1]
        P = np.zeros([len(vals), len(vals)])
        for i in xrange(len(vals)):
            P[:,i] = vects[:,vals_idx[i]] / np.sqrt(vals[vals_idx[i]])
        return P, vals[vals_idx]

class p300analysis(object):
    def __init__(self, z_trg, z_no_trg, mean, mu, sigma, left, right, no_fields=8):
        """Parameters:
           -----------
           z_trg : 2darray
                a distribution of target correlations
            z_no_trg : 2darray
                a distribution of non target correlations
            mean : 1darray
                a mean to correlate with
            no_fields [= 8] : int
                a number of blinking fields
        """
        self.trg = z_trg
        self.no_trg = z_no_trg
        self.buffer = np.zeros([no_fields, z_trg.shape[0], len(mean)])
        self.trg.sort()
        self.no_trg.sort()
        self.mu, self.sigma = mu, sigma
        self.mean = mean# / np.sqrt(np.dot(mean, mean))
        self.signal_len = len(mean)
        self.left = left
        self.right = right
    
    def __get_array_feature(self, arr, xc_points=20):
        """
        Parameters:
        -----------
        arr : 2darray
            an array of signals
        xc_points : int
            points considered in cross--correlation
        """
        N = arr.shape[0]
        mean = arr.sum(0)
        mean /= np.sqrt(np.dot(mean, mean))
        return self.__get_feature(mean, idx = N - 1, xc_points = xc_points)
    
    def __get_feature(self, signal, idx=0, xc_points=20):
        """This returns a xcorrelation of a given signal with the mean signal
        
        Parameters:
        ===========
        signal : 1darray
            signal to be analyzed
        xc_points : int
            how many points to consider in xcorrelation
        idx [= 0] : int
            which mean is being considered
            
        Returns:
        ========
        zscore : float
            a Z-score of a given signal
        """
        N = len(signal)
        xcor = np.correlate(signal, self.mean, 'full')[N - xc_points : N + xc_points]
        zscore = (xcor.max() - self.mu[idx]) / self.sigma[idx]
        return zscore
    
    def safety(func):
        def wrapper(self, *args):
            try:
                return func(self, *args)
            except ZeroDivisionError:
                print 'WARNING! ZeroDivision occured!',
                Xt = self.trg[arg[1], :]
                Xn = self.no_trg[arg[1], :]
                print args[0], Xt.max(), Xt.mean(), Xn.min(), Xn.min()
                raise ZeroDivisionError('Oops!')
        return wrapper
    
    @safety
    def __get_prob(self, feature, no):
        """Returns the Bayes probability of a given feature.
        
        Parameters:
        ===========
        feature : float
            a feature to consider
        no : int
            which mean to consider
        
        Returns:
        ========
        probability : Bayes probability
        """
        Xt = self.trg[no, :]
        Xn = self.no_trg[no, :]
        N = len(Xt) + len(Xn)
        P_t = len(Xt) / float(N)
        P_n = len(Xn) / float(N)
        P_xt = len(np.where(Xt < feature)[0]) / float(len(Xt))
        P_xn = len(np.where(Xn > feature)[0]) / float(len(Xn))
        return P_xt * P_t / (P_xt * P_t + P_xn * P_n)
    
    def woody(self, sig, xc_points=10, left=None, right=None, mean=None):
        if mean is None:
            mean = self.mean
        xcor = np.correlate(mean, sig, 'full')[self.signal_len - xc_points : self.signal_len + xc_points]
        max_idx = xcor.argmax()
        #sig = sig / np.sqrt(np.dot(sig,sig))
        sig -= sig.mean()
        cor = len(xcor)/2 - max_idx
        new_sig = np.zeros(sig.shape)
        if left is None:
            left = self.left
        if right is None:
            right = self.right
        if left + cor <= 0:
            cor = -left
        if right + cor >= len(sig):
            cor = len(sig) - right - 1
        new_sig[left:right] = np.copy(sig[left+cor:right+cor])
        #plt.plot(self.mean, 'r-')
        #plt.plot(sig,'g-')
        #plt.plot(new_sig,'b-')
        #plt.show()
        return new_sig
    
    def analyze(self, signal, index, tr=0.05):
        """The main classifier
        
        Parameters:
        ===========
        signal : 1darray
            a signal to analyze
        index : int
            the index of the field that signal corresponds to
        tr [=0.05] : float
            a threshold of probability above which the decision is made
        
        Returns:
        ========
        indx : idx
            the index of field that corresponds to a signal positively calssified
        """
        I, N, J = self.buffer.shape
        sig = self.woody(signal)
        feature = self.__get_feature(sig)
        prob = self.__get_prob(feature, 0)
        if prob >= tr:
            return index
        tmp = np.delete(self.buffer[index,...], N - 1, 0)
        tmp = np.insert(tmp, 0, sig, axis=0)
        self.buffer[index,...] = np.copy(tmp)
        for i in xrange(N):
            feature = self.__get_array_feature(tmp[:i + 1])
            prob = self.__get_prob(feature, i)
            if prob >= tr:
                plt.figure()
                for k in xrange(I):
                    plt.subplot(2, 4, k+1)
                    plt.plot(self.mean, 'r-')
                    plt.plot(self.buffer[k,...].T, 'g-')
                plt.show()
                self.buffer = np.zeros(self.buffer.shape)
                return index
        if index == 1:
            print i + 1
        return -1
    
class p300analysis2(p300analysis):
    def __init__(self, classifiers, P, P_vect, mean, mu, sigma, left, right, no_fields=8):
        self.classifiers = classifiers
        self.P = P
        self.P_vect = P_vect
        self.mu, self.sigma, self.left, self.right, self.mean = mu, sigma, left, right, mean
        self.buffer = np.zeros([no_fields, mu.shape[1], mean.shape[1], P_vect])
        self.signal_len = mean.shape[1]
        
    def __get_feature(self, arr, xc_points=6):
        N, M, K = arr.shape
        tmp = np.zeros(M)
        zscores = np.zeros(K)
        for i in xrange(K):
            for j in xrange(N):
                tmp += arr[j,:,i] - arr[j,:, i].mean()
            tmp /= N
            #tmp /= np.sqrt(np.dot(tmp,tmp))p
            xcor = np.correlate(tmp, self.mean[i], 'full')[M - xc_points:M+xc_points]
            zscores[i] = (xcor.max() - self.mu[i, N - 1])/self.sigma[i, N - 1]
        return zscores
            
    def analyze(self, signal, index, tr=0.05):
        I, N, J, PV = self.buffer.shape
        
        feature = np.zeros([self.P_vect, N])
        for k in xrange(PV):
            sig = np.dot(self.P[:, k], signal)
            sig = self.woody(sig, left=self.left[k], right=self.right[k], mean=self.mean[k])
            tmp = np.delete(self.buffer[index,...,k], N-1, 0)
            tmp = np.insert(tmp, 0, sig, axis=0)
            self.buffer[index,...,k] = np.copy(tmp)
        
        for j in xrange(1, N+1):
            zscores = self.__get_feature(self.buffer[index,:j,...])
            prob = self.classifiers[j-1].predict(zscores)
            if j==1:
                if index==1:
                    plt.plot(zscores[0], zscores[1],'ro')
                else:
                    plt.plot(zscores[0], zscores[1], 'go')
            if prob <= tr:
                return index
        return -1
