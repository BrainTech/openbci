"""
"Class creation of CSP filters,
"The CSP calculation procedure is based on the paper:
"Designing optimal spatial filters for single-trial EEG classification in a movement task;
"Johannes Mueller-Gerking, Gert Pfurtscheller, Henrik Flyvbjerg
"Clinical Neurophysiology vol.110(1999), pp.787--798
"
"Piotr Milanowski, July 2011, Warsaw.
"Corrected Dec. 2011, Warsaw
"For University of Warsaw
"""
from signalParser import signalParser as sp
import numpy as np
from scipy.signal import hamming, ellip, cheby2
from filtfilt import filtfilt
from scipy.linalg import eig
import pickle
from matplotlib.pyplot import plot, show, legend, title, xlabel, ylabel
from simpleCSP import pfu_csp


def quantile(x, q, method = 5):
    """This calculates q quantiles of x.
    
    A pth quantile Q, of a distribution F of observations X, is defined as:
        Q(p) = inf{x in X: F(x) >= p}
    Methods based on [1]

    Parameters:
    ===========
    x : 1d array
        A vector of samples
    q : 1d array
        A vector of quantiles
        method [= 5] : integer 1 - 9
        1 : inverse empirical distribution function
        2 : similar to 1 but with averaging at discontiunities3
        3 : nearest even order satistic. As definded by SAS
        4 : linear interpolation of empirical cdf
        5 : a piecewise linear function where the knots are the values midway
            through the steps of the empirical cdf. Used by Matlab
        6 : used by SPSS and Minitab
        7 : used by S
        8 : median unbiased
        9 : unbiased for the expected order statistics if x is nomally distributed
        See [1] for explicit definitions of methods above.

    Returns:
    ========
    quantiles : array of length of q
        The quantiles that correspond to q
    References:
    ===========
    [1] 'Sample Quantiles in Statistical Packages', Hyndman, Rob J. and Fan, Yanan;
        The American Statistician (1996), Vol. 50, pp 361 -- 365
    """
    y = np.array(sorted(x))
    quantiles = []
    n = len(x)
    for p in q:
        if method in [1, 2, 3]:
            m, kappa, gm = {1:(0, 1, 0), 2:(0, 1, 0.5), 3:(-0.5, 0, 0.5)}[method]
            j = int(p * n + m)
            g = p * n + m - j
            g = kappa and g or g * (j/2.0 - j/2)
            gamma = g and 1 or gm
            if j <= 0:
                quantiles.append(y[0])
            elif j >= n:
                quantiles.append(y[-1])
            else:
                quantiles.append(y[j - 1] * (1 - gamma) + y[j] * gamma)
        elif method in [4, 5, 6, 7, 8, 9]:
            alfa, beta = {4:(0, 1), 5:(0.5, 0.5), \
                    6:(0, 0), 7:(1, 1), 8:(1.0/3, 1.0/3), \
                    9:(3.0/8, 3.0/8)}[method]
            m = alfa + p * (1 - alfa - beta) 
            j = int(p * n + m)
            gamma = p * n + m - j
            if j <= 0:
                quantiles.append(y[0])
            elif j >= n:
                quantiles.append(y[-1])
            else:
                quantiles.append(y[j - 1] * (1 - gamma) + y[j] * gamma)
        else:
            raise ValueError, 'Unknown method! Please select one from 1-9.'
    return quantiles

class modCSP(object):
    """This class performs a calculation of CSP filter

    The CSP method finds such combination of channels that maximizes the variance (power) of first class while minimizing the variance (power) of the second class.

    The class, given a signal, frequency and electrodes, calculates CSP filter optimizing SSVEP response (at given frequency)

    THIS VERSION CALCULATES ONE CSP FILTER FOR ALL FREQUENCIES

    Parameters:
    -----------
    name : string
        the name of the signal. The program looks for files name.raw (containing raw signal), name.xml (containing experiment setup information) and name.tag (containing experiment information)
    frequencies : array-like
        frequencies of stimulation.
    electrodes : array of ints or an array of strings
        array containig names or numbers of electrodes to process. Names or numbers should be the same as in name.xml file.
    """

    def __init__(self, name, frequency, electrodes):
        """Begin here"""
        self.parsed_data = sp(name)
        self.name = name
        self.electrodes = electrodes
        self.frequencies = frequency
        N = len(electrodes)
        self.P = np.zeros([N, N])
        self.vals = np.zeros(N)
        self.method = 'not calculated'
        
    def set_frequencies(self, frequencies):
        """Sets frequencies to analyze

        Parameter:
        ---------
        frequencies : array-like
            frequencies of stimulation
        """
        self.frequencies = frequencies

    def set_electrodes(self, electrodes):
        """Sets electrodes to process

        Parameters:
        -----------
        electrodes : array of ints or an array of strings
            array containig names or numbers of electrodes to process. Names or numbers should be the same as in name.xml file.
        """
        self.electrodes = electrodes

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
        
    def __get_min_entropy(self, c_max):

        vals, vects = eig(c_max)
        vals = vals.real
        vals_idx = np.argsort(vals)
        P = np.zeros([len(vals), len(vals)])
        for i in xrange(len(vals)):
            P[:,i] = vects[:, vals_idx[i]] / np.sqrt(vals[vals_idx[i]])
        return P, vals[vals_idx]

    def __get_model_matrix(self, freq, Nt, fs):

        Nh = int((fs / 2.0 - 10) / freq)
        X = np.zeros([2 * Nh, Nt])
        t_vec = np.array(range(Nt)) * 1.0 / fs
        for i in xrange(Nh):
            X[2*i, :] = np.sin(2 * np.pi * (i + 1) * freq * t_vec)
            X[2*i + 1, :] = np.cos(2 * np.pi * (i + 1) * freq * t_vec)
        return X

    def __is_int(self, x):
        """Checks if x is an integer.

        Parameters:
        -----------
        x : something
            a value to be tested
        
        Returns:
        --------
        y : bool
            True if x is an integer
        """
        if int(x) == x:
            return True
        else:
            return False

    def read_matlab_filters(self, txt_file='ba_filters.txt'):
        """Function reads filter coefficient from txt file

        Paramesters:
        ===========
        txt_file : string
            the name of file with filter coefficients
        """
        filter_file = open(txt_file,'r')
        filter_tmp = filter_file.read().split('\n')[:-1]
        frq_range = range(5,46)
        idx = [frq_range.index(j) for j in self.frequencies]
        ba_filters = [[float(y) for y in x.split(',')[:-1]] for x in filter_tmp]
        needed_filters_b = [ba_filters[2*ix] for ix in idx]
        needed_filters_a = [ba_filters[2*ix+1] for ix in idx]

        return needed_filters_b, needed_filters_a

    def start_CSP(self, signal_time, to_frequency = 128, baseline = True,\
            base_time = 4, filt = 'ellip', method = 'pfu', train_tags = None):
        """Produces CSP filter from the data.

        THIS VERSION CALCULATES ONE FILTER FOR ALL FREQUENCIES
        The filter is stored in a variable P

        Parameters:
        -----------
        signal_time : float
            Time in seconds of signal to take as a class for maximalization   
        to_frequency [= 128Hz] : int
            The frequency to which signal will be resampled
        baseline [= True] : bool
            If true a base line of base_time seconds will be taken as a class for minimalization
        [If baseline = True]
        base_time [= 4] : float
            Time in seconds of baseline to take as minimalization class
        filt [= 'ellip']: string ['ellip', 'cov', 'cheby', None]
            a filter to use. If method is 'maxcontrast' the variable is set to None
        method [= 'pfu'] : string ['pfu', 'regular','maxcontrast']
            method of calculation CSP filter
        train_tags : list
            a list of tags to process. Each list entry is a tuple with first element position of tag in seconds, and second is a frequency of stimulation
        """

        if not self.__is_int(to_frequency):
            raise ValueError, 'to_frequency is not int!'
        self.method = method
        signal = self.parsed_data.prep_signal(to_frequency, self.electrodes)
        if train_tags == None:
            all_tags = self.parsed_data.get_train_tags(ccof = True)
        else:
            all_tags = train_tags
        N = len(self.electrodes)
        if method == 'maxcontrast' or method == 'minimalentropy':
            baseline = True
            filt = None
        cov_pre = np.zeros([N, N])
        cov_post = np.zeros([N, N])
        pre_i = 0
        post_i = 0
        for i, frq in enumerate(self.frequencies):
            if filt == 'ellip':
                filt_b, filt_a = ellip(3, 0.1 , 100, \
                [2*(frq - 1) / float(to_frequency), 2*(frq + 1) / float(to_frequency)],\
                btype='pass')
                signal_tmp = np.array([filtfilt(filt_b, filt_a, x) for x in signal])
            elif filt == 'cheby':
                filt_b, filt_a = cheby2(1, 10, [2*(frq - 1)/float(to_frequency), 2*(frq + 1)/float(to_frequency)], 'pass')
                signal_tmp = np.array([filtfilt(filt_b, filt_a, x) for x in signal])
            elif filt == 'conv':
                t_vec = np.linspace(0, 0.5-1.0/to_frequency, 0.5 * to_frequency)
                sin = np.sin(t_vec * 2 * np.pi)
                sin /= sum(sin**2)
                M = len(sin)
                K = len(signal[0,:])
                signal_tmp = np.array([np.convolve(sin, x, mode = 'full')[M:K + M] for x in signal])
            elif filt == None:
                signal_tmp = signal
            tags = [x for (x, y) in all_tags if y == frq]
            rest_tags = [x for (x, y) in all_tags if y != frq]
            for idx in xrange(min(len(tags),len(rest_tags))):
                s_post = signal_tmp[:, to_frequency * (tags[idx] ) : to_frequency * (tags[idx] +\
                         signal_time)]
                dane_B = np.matrix(s_post)
                R_B = dane_B * dane_B.T / np.trace(dane_B * dane_B.T)
                cov_post += R_B
                post_i += 1
                if baseline:
                    if method == 'maxcontrast' or method == 'minimalentropy':
                        s_pre = signal_tmp[:, to_frequency *\
                                (tags[idx] + 1) : to_frequency * (tags[idx] + signal_time)]
                        dane_A = np.matrix(s_pre)
                        X = np.matrix(self.__get_model_matrix(frq, s_pre.shape[1], to_frequency))
                        Y = dane_A - (X.T * np.linalg.inv(X * X.T) * X * dane_A.T).T
                        cov_pre += Y * Y.T / np.trace(Y * Y.T)
                        pre_i += 1
                    else:
                        s_pre = signal_tmp[:, to_frequency * (tags[idx] -\
                            1 - base_time) : to_frequency * (tags[idx] -1)]
                        dane_A = np.matrix(s_pre)
                        R_A = dane_A * dane_A.T / np.trace(dane_A * dane_A.T)
                        cov_pre += R_A
                        pre_i += 1
            if not baseline:
                for idx in rest_tags:
                    s_pre = signal_tmp[:, to_frequency * (idx ) : to_frequency *\
                            (idx  + signal_time)]
                    dane_A = np.matrix(s_pre)
                    R_A = dane_A * dane_A.T / np.trace(dane_A * dane_A.T)
                    cov_pre += R_A
                    pre_i += 1
        if method == 'regular' or method == 'maxcontrast':
            self.P[:,:], self.vals =  self.__get_filter(cov_post / post_i, cov_pre / pre_i)
        elif method == 'pfu':
            self.P[:, :] = pfu_csp(cov_pre / pre_i, cov_post / post_i)
        elif method == 'minimalentropy':
            self.P[:, :], self.vals = self.__get_min_entropy(cov_pre / pre_i)
    
    def count_stats(self, signal_time, to_freq, tags):
        """Calculates variance and mean"""        
        signal = np.dot(self.P[:,0], self.parsed_data.prep_signal(to_freq, self.electrodes))
        t_vec = np.linspace(0, signal_time - 0.5, (signal_time - 0.5)*to_freq)
        max_lag = int(0.1*to_freq)
        this_cors = [[] for i in range(len(self.frequencies))]
        other_cors = [[] for i in range(len(self.frequencies))]
        N = signal_time * to_freq
        for fr in self.frequencies:
            sin = np.sin(2*np.pi*fr*t_vec)
            sin /= np.sqrt(np.sum(sin * sin))
            for pos, f in tags:
                tmp_sig = signal[(pos+0.5)*to_freq:(pos + 0.5 + signal_time)*to_freq]
                tmp_sig -= np.mean(tmp_sig)
                tmp_sig /= np.sqrt(np.sum(tmp_sig*tmp_sig))
                xcor = np.correlate(tmp_sig, sin, 'full')[N - 1 - max_lag: N + max_lag]
                idx = self.frequencies.index(f)
                if f == fr:
                    this_cors[idx].append(np.max(xcor))
                else:
                    other_cors[idx].append(np.max(xcor))
        oc = np.array(other_cors).flatten()
        mu, sigma = oc.mean(), oc.std()
        oc = (oc - oc.mean())/oc.std()
        return quantile(oc, [0.95]), mu, sigma
        #return this_cors, other_cors
    
    def dump_filters(self, name, mode = 'pkl', first = False):
        """Function dumps filters and values into file

        Parameters:
        -----------
        name  : string
            the name of file to create. Only the prefix, a frequency and an exptension will be added
            I.e.: 
                >>>q=modCSP.modCSP('some/file', [10,20,30], [0,1,2,3])
                >>>dump_filters('joe_data', mode='pkl')
                will create files joe_data_10.pkl, joe_data_20.pkl and joe_data_30.pkl
        mode [= 'pkl'] : string ['pkl' | 'txt']
            defines mode of file. If 'pkl', pickle file is used. If 'txt' csv is used
        first [= False] : bool
            if True only first column of filter matrix will be written
        """
        file_name = name
        for i, frs in enumerate(self.frequencies):
            if mode == 'pkl':
                f = open(file_name +'_'+ str(frs) + '.pkl','w')
                if first:
                    pickle.dump(self.P[:, 0, i], f)
                else:
                    pickle.dump(self.P[:, :, i],  f)
                f.close()
            elif mode == 'txt':
                f = open(file_name + '.txt','w')
                if first:
                    f.write(",".join([str(x) for x in self.P[:,0]]))
                for y in self.P:
                    f.write(",".join([str(x) for x in y]))
                    f.write('\n')
                f.write(",".join([str(x) for x in self.vals]))
                f.close()

    def test_filter(self, frequency, pfu=True, to_frequency = 128):
        """This function draws spectras of filtered signal.

        Parameters:
        -----------
        frequency : int
            a frequnecy of filter
        to_frequency [= 128] : int
            a frequency to decimate signal to
        """
        if pfu:
            filt = self.P[:, :]#, self.frequencies.index(frequency)]
        else:
            filt = self.P[:, 0]#, self.frequencies.index(frequency)]

        tags_all = self.parsed_data.get_train_tags(screen = True)#, tag_filter = ('screen','allFrequencies'))
        tags = [x for (x,y) in tags_all if y == frequency]
        tags_rest = [x for (x, y) in tags_all if y != frequency]
        #np.random.shuffle(tags_rest)
        #tags_rest = tags_rest[0:len(tags)]
        signal = self.parsed_data.prep_signal(to_frequency, self.electrodes)
        print self.P 
        if pfu:
            csp = np.dot(filt, signal)[0, :]
        else:
            csp = np.dot(filt, signal)
        sig = np.zeros(4 * to_frequency)
        sig_comp = np.zeros(4 * to_frequency)
        hamm = hamming(len(sig))
        for j in xrange(len(tags)):
            sig += np.abs(np.fft.fft(csp[int(tags[j]*to_frequency):int((tags[j]+4)*to_frequency)] * hamm)) ** 2 / len(hamm)
        for j in xrange(len(tags_rest)):
            sig_comp += np.abs(np.fft.fft(csp[int((tags_rest[j])*to_frequency):int((tags_rest[j]+4)*to_frequency)] * hamm)) ** 2 / len(hamm)
        sig /= len(tags)
        sig_comp /= len(tags_rest)
        fft_freqs = np.fft.fftfreq(len(sig), 1.0 / to_frequency)
        idx = np.where(fft_freqs < 0)[0][0]
        fft_freqs = fft_freqs[:idx]
        #sig_fft = (abs(np.fft.fft(sig)) ** 2 ) / len(hamm)
        sig_fft = sig[:idx]
        #comp_fft = (abs(np.fft.fft(sig_comp)) ** 2) / len(hamm)
        comp_fft = sig_comp[:idx]
        plot(fft_freqs[40:], sig_fft[40:],fft_freqs[40:],comp_fft[40:],)
        legend(('SSVEP','COMP'))
        title(str(frequency))
        xlabel('Frequency (Hz)')
        ylabel('Power')
        show()