from xml.dom import minidom
import numpy as np
import os.path as osp
from scipy.signal import decimate

class signalParser(object):
    """This class can extract some information from signal and it's xml descriptors"""

    def __init__(self, file_prefix):
        """Check for file and it's descriptors

        This function initializes class and checks for files:
            .raw - contains the signal
            .xml - contains signal description
            .tag - contains experiment tags
        """
        if osp.exists(file_prefix+'.raw'):
            self.raw_file = file_prefix + '.raw'
        else:
            raise IOError(file_prefix+'.raw doest exist!')

        if osp.exists(file_prefix+'.xml'):
            self.xml_file = file_prefix + '.xml'
        else:
            raise IOError(file_prefix+'.xml does not exist!')

        if osp.exists(file_prefix+'.tag'):
            self.tag_file = file_prefix + '.tag'
        else:
            print "Warning: "+file_prefix+".tag does not exist!"

        self.channel_count, self.sample_count, self.sampling_frequency = self.__get_xml_elems()
        self.channel_list = self.__get_channel_list()

    def extract_channel(self,channel_list, filt = None):
        """This extracts channels from .raw file
        
        The filt parameter should be a function of len(channel_list) parameters.
        if filt is None than raw signals are returned.
        If not, the output of filt function is returned"""
        return self.__get_filtered_channels(self.__channels_no(channel_list), filt)

    def __get_xml_elems(self):
        """Returns number of channels"""

        fxml = minidom.parse(self.xml_file)
        return int(fxml.getElementsByTagName('rs:channelCount')[0].firstChild.data), \
                int(fxml.getElementsByTagName('rs:sampleCount')[0].firstChild.data), \
                float(fxml.getElementsByTagName('rs:samplingFrequency')[0].firstChild.data)


    def __get_channel_list(self):
        """Returns list of channels from .xml file"""

        fxml = minidom.parse(self.xml_file)
        return [x.firstChild.data for x in fxml.getElementsByTagName('rs:label')]

            
    def __get_filtered_channels(self, channel_list, filt):
        """Returns channels filtered wit filt function"""

        fxml = minidom.parse(self.xml_file)
        sample_type = fxml.getElementsByTagName('rs:sampleType')[0].firstChild.data
        ch_no = self.channel_count
        sig = np.fromfile(self.raw_file,sample_type.lower())
        signal = np.zeros([len(channel_list), self.sample_count])
        print channel_list
        for i,v in enumerate(channel_list):
            signal[i] = sig[v::ch_no][0:self.sample_count]
        if filt != None:
            return filt(signal)
        else: return signal

    def __channels_no(self, ch_list):
        """If in ch_list is string describing a channel, it is converted to channel no using .xml file"""

        ch_str_list = self.channel_list 
        real_ch_list = []
        for i in ch_list:
            if isinstance(i, int):
                real_ch_list.append(i)
            elif isinstance(i, str) or isinstance(i, unicode):
                try:
                    real_ch_list.append(ch_str_list.index(i))
                except ValueError:
                    print "Wrong channel name "+i
                    raise
            else:
                raise ValueError("Channel name must be a string or integer")

        return real_ch_list

    def get_channel(self, channel):
        """Returns number of channel (if channel is a string) or channel name (if channel is an integer)"""

        ch_str_list = self.channel_list 

        if isinstance(channel, int):
            return ch_str_list[channel]
        elif isinstance(channel, str):
            try:
                return ch_str_list.index(channel)
            except ValueError:
                print "Can not find this channel"
                raise
        else:
            raise ValueError("Channel must be a string or an integer")


    def get_freq_tags(self, samples = True, Fs = None):
        """Returns frequency tags with timestamps
        
        If samples is true, the time stamps are in samples.
        Procedure checks if tags positions are not greater than actual size of file
        """
        
        ftag = minidom.parse(self.tag_file)
        exp_update_list = [e for e in ftag.getElementsByTagName('tag')\
            if e.attributes['name'].value == 'experiment_update']
        frq_time_list = []
        fsp = 0
        if Fs == None:
            fsp = self.sampling_frequency
        else: fsp = Fs

        for i in exp_update_list:
            position = float(i.attributes['position'].value)
            if position < (self.sample_count / self.sampling_frequency) - 5:
                frq_list = np.array(eval(i.getElementsByTagName('Freqs')[0].firstChild.data))
                nz_frq_list = frq_list[np.nonzero(np.array(frq_list))[0]]
                frq = frq_list[int(i.getElementsByTagName('concentrating_on_field')[0].firstChild.data)]
                all_frq = np.zeros(len(nz_frq_list))
                all_frq[0] = frq
                all_frq[1::] = nz_frq_list[np.where(nz_frq_list != frq)[0]]
                frq_time_list.append((position, frq, all_frq))
        
        if(samples):
            return map(lambda x: (int(x[0]*fsp), x[1], x[2]), frq_time_list)

        return frq_time_list

    def get_train_tags(self, trial_separator_name='trial', screen = False, tag_filter = None, ccof = False ):
        """Extracts positions an stimulation frequencies from .tag file

        Parameters:
        ===========
        screen [= False] : bool
            if True a 'freq' tag will be considered when choosing stimulation frequency
        tag_filter [= None] : tuple
            a tuple of strings. First element is a name of a tag, second is value of the tag.
            This will limit the function to consider only tags specified in the tuple.
        ccof [= Flase] : bool
            if True a concentrating_on_field tag will be considered when choosing stimulation frequency

        Returns:
        ========
        tags : list
            a list of tuples. First element is time (in seconds) denoting start of the stimulation.
            Second element is frequency of the stimulation
        """
        ftags = minidom.parse(self.tag_file)
        exp_update_list_all = [e for e in ftags.getElementsByTagName('tag')\
                if e.attributes['name'].value == trial_separator_name]# \
                #or e.attributes['name'].value == 'experiment__screen_break']
        if tag_filter is None:
            exp_update_list = exp_update_list_all
        else:
            exp_update_list = [e for e in exp_update_list_all \
                    if e.getElementsByTagName(tag_filter[0])[0].firstChild.data == tag_filter[1]]
        tag_list = []
        for i,exp in enumerate(exp_update_list):
            position = float(exp.attributes['position'].value)
            if screen:
                #cor_tab = [36, 38, 40, 42]
                scr = exp.getElementsByTagName('freq')[0].firstChild.data
                #scr_idx = int(scr)#int(scr.split('_')[-1])
                #frq = cor_tab[scr_idx - 1]
                #frq = np.array(eval(exp.getElementsByTagName('freqs')[0].firstChild.data))[scr_idx - 1]
                frq = int(scr)
            elif ccof:
                scr = exp.getElementsByTagName('concentrating_on_field')[0].firstChild.data
                frq = np.array(eval(exp.getElementsByTagName('freqs')[0].firstChild.data))[int(scr)]
            else:
                f1 = exp.getElementsByTagName('freqs')[0].firstChild.data
                frq = eval(f1)[1]
            #frq = frq_list[int(exp.getElementsByTagName('concentrating_on_field')[0].firstChild.data)]
            #tag = screen_tag[0].firstChild.data
            tag_list.append((position, frq))
        return tag_list

    def get_multiple_tags(self, exact = False, no_fields = 4):
        """Returns frequency, time and class of tag
        
        If exact is true, TRIGGER channel will be used to determine exact beginings of stimulations"""
        ftag = minidom.parse(self.tag_file)
        exp_update_list = [e for e in ftag.getElementsByTagName('tag')\
            if e.attributes['name'].value == 'experiment_update']
        exp_start = [x for x in ftag.getElementsByTagName('tag')\
                if x.attributes['name'].value == 'experiment_start'][0].attributes['position'].value
        tag_list = []
        is_new_tag = 1
        a = self.tag_file.split('/')
        a.append('poprawione_'+a.pop()+'.xml')
        popr = '/'.join(a)
        try:
            f_class = open(popr,'r')
            class_list = f_class.read().split(';')

        except IOError:
            is_new_tag = 0
        corr_table = {'yellow':'kolzol','blue':'koln','red':'kolc','odl2':'pf1_odl2','':'',\
                'kolo':'kolo','odl1':'odl1','odl3':'odl3','wiel1':'wiel1','wiel2':'wiel2',\
                'wiel3':'wiel3','green':'kolziel','nocross':'pf0'}
        for i,exp in enumerate(exp_update_list):
            position = float(exp.attributes['position'].value)
            frq_list = np.array(eval(exp.getElementsByTagName('Freqs')[0].firstChild.data))
            frq = frq_list[int(exp.getElementsByTagName('concentrating_on_field')[0].firstChild.data)]
            screen_tag = exp.getElementsByTagName('screen')
            if len(screen_tag) == 0:
                if is_new_tag:
                    tag = corr_table[class_list[i]]
                else:
                    raise IOError("No screen tag and no correction file ["+popr+"]!")
            else:
                tag = screen_tag[0].firstChild.data
            tag_list.append((position, frq, tag))

        if exact:
            trigger = self.extract_channel(['TRIGGER'])[0]
            first = np.where(trigger > 0)[0]
            second = np.where(first / self.sampling_frequency < float(exp_start))[0][-1]
            trigger[0:first[second]]=1.0
            beg=1
            trigger_samples = []
            for i,sample in enumerate(trigger):
                if sample == 0 and beg == 1:
                    trigger_samples.append(i*1/self.sampling_frequency)
                    beg = 0        
                if sample == 1 and beg == 0:
                    beg = 1
            trigger_samples = trigger_samples[::no_fields]
            exact_list = []
            if len(trigger_samples) != len(tag_list):
                print trigger_samples[1], tag_list[0][0]
                print trigger_samples[-1], tag_list[-1][0]
                raise ValueError("Different trigger and tag lists lengths: "+str(len(trigger_samples))\
                        + " and " +str(len(tag_list)))
            print trigger_samples[0], tag_list[0][0]
            print trigger_samples[-1], tag_list[-1][0]
            for j,k in enumerate(tag_list):
                exact_list.append((trigger_samples[j], k[1], k[2]))
            return exact_list
        else:
            return tag_list

    def get_p300_tags(self, idx=1, rest=False, samples = True, Fs = None):
        """Returns tags with words from different groups
        
        Parameters:
        -----------
        idx [= 1]: int
            defines which tags to return
        samples : bool
            if true, positions will be returned as samples not in seconds
        Fs : float or None
            the sampling frequency used to convert positions to samples
        
        Returns:
        --------
        exp_list : list
            a list of positions of target
        """

        ftag = minidom.parse(self.tag_file)
        tag_list = [e for e in ftag.getElementsByTagName('tag') \
                    if e.attributes['name'].value == 'blink']
        exp_list = []

        fsp = self.sampling_frequency
        if(samples):
            if Fs != None:
                fsp = Fs
        else: fsp = 1.0
        for e in tag_list:
            index = e.getElementsByTagName('index')[0].firstChild.data
            if not rest:
                if int(index) == idx:
                    exp_list.append(float(e.attributes['position'].value))
            else:
                if int(index) !=  idx:
                    exp_list.append(float(e.attributes['position'].value))
        return np.array(exp_list) * fsp 

    def prep_signal(self, to_frequency, channels, montage_channels=['A1','A2'], montage='ears'):
        """This function preps signal to analysis.

        Function prepers signal for analysis, i.e. extracts indicated data from .raw file

        Parameters:
        -----------
        to_frequency : float
            The frequency to which signal will be resampled
        channels : array-like
            The channels to analyze. Can be strings or ints. Must correspond to .xml file
        montage_channels : list
            this is a list of channels that will be used in montage function
        montage : string ('ears'|'ident'|'diff')
            a montage function to use:
            'ears' - an ear montage - montage_channels should be two channels that
            correspond to ears
            'ident' - identity - montage_channels should be empty list
            'diff' - one electrode reference - a montage_channels should be the one
            that corresponds with reference
        Returns:
        --------
        signal : np.array
            An ch x n array where n is length of resampled signal, ch is the number of channels to analyze
        
        Example:
        --------
        >>> q = signalParser.signalParser('some_file',[10,20,30],['O1','O2','Pz'])
        >>> new_signal = q.prep_signal(128, ['O1','O2'], montage='diff', montage_channels='FCz')
        """
        
        Fs = self.sampling_frequency
        dec_no = Fs / float(to_frequency)
        if self.__is_int(dec_no / 2.0) or Fs == float(to_frequency):
            dec_no = int(dec_no)
            M = int(self.sample_count / dec_no)
            signal = np.zeros([len(channels), M])
            for i,e in enumerate(channels):
                #tmp = np.zeros(self.sample_count)
                if montage == 'ears':
                    tmp = self.extract_channel([e]+montage_channels, self.ears)
                elif montage == 'diff':
                    if isinstance(montage_channels, list):
                        tmp = self.extract_channel([e]+montage_channels, self.diff)
                    else:
                        tmp = self.extract_channel([e] + [montage_channels], self.diff)
                elif montage == 'ident':
                    tmp = self.extract_channel([e], self.ident)
                else:
                    raise ValueError, 'Wrong montage! Please choose one of: "ears", "diff", "ident"'
                #tmp = self.extract_channel([e], self.ident)
                #while dec_no > 1:
                #    dec_no /= 2
                #if not Fs == float(to_frequency):
                #    tmp = decimate(tmp, dec_no)
                signal[i,:] = tmp[0:M]
            return signal
        else:
            raise ValueError, 'The new sampling frequency is not even!'
            return 0

    def ears(self, ch):
        """Simple montage - from channel in ch[0] subtracts mean from ears (ch[1] and ch[2])"""
        e = ch[1] + ch[2]
        return ch[0] - e / 2.0
    
    def ident(self, ch):
        """Identity montage"""
        e = ch[0]
        return e
    
    def diff(self, ch):
        """reference montage"""
        e = ch[1] - ch[0]
        return e

    def __is_int(self, x):
        """Checks if x is an integer"""
        try:
            return int(x) == x
        except:
            return False
   
