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
        
        file_prefix = osp.expanduser(file_prefix)
        
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

        self.montage = 0

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

    def getSamplingFrequency(self):
        return self.sampling_frequency


    def __get_channel_list(self):
        """Returns list of channels from .xml file"""

        fxml = minidom.parse(self.xml_file)
        return [x.firstChild.data for x in fxml.getElementsByTagName('rs:label')]

    def getChannelList(self):
        return self.__get_channel_list()
            
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

    def setMontage(self, montage):
        self.montage = self.extract_channel(montage).mean(axis=0)

    def getData(self, channels):
        s = self.extract_channel(channels)
        return s - self.montage
    
    def getAllTags(self,inSamples=True):
        ftags = minidom.parse(self.tag_file)
        tagArray = []
        for tag in ftags.getElementsByTagName('tag'):
            tagTime = float(tag.attributes['position'].value)
            if  tagTime - t > approxTimeDiff:
                tagArray.append(tagTime)
        if inSamples:
            return np.array(tagArray)*self.sampling_frequency
        else:
            return np.array(tagArray)
    
    def getTrialTags(self, approxTimeDiff=2, inSamples=True):
        ftags = minidom.parse(self.tag_file)
        tagArray = []
        t = 0
        for tag in ftags.getElementsByTagName('tag'):
            tagTime = float(tag.attributes['position'].value)
            if  tagTime - t > approxTimeDiff:
                tagArray.append(tagTime)
            t = tagTime
        if inSamples:
            return np.array(tagArray)*self.sampling_frequency
        else:
            return np.array(tagArray)

    
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
#######################################################

    def get_all_tags(self, idx=1, samples = True, Fs = None):

        ftag = minidom.parse(self.tag_file)
        tag_list = [e for e in ftag.getElementsByTagName('tag') \
                    if e.attributes['name'].value == 'blink']
        exp_list = {}

        fsp = self.sampling_frequency
        if(samples):
            if Fs != None:
                fsp = Fs
        else: fsp = 1.0
        for e in tag_list:
            index = e.getElementsByTagName('index')[0].firstChild.data
            if idx > 0:
                timestamp = float(e.attributes['position'].value)
                exp_list[timestamp*fsp] = int(index)
            else:
                if int(index) !=  abs(idx):
                    exp_list.append(float(e.attributes['position'].value))
                    
        return exp_list
        
    def get_not_p300_tags(self, idx=1, samples = True, Fs = None):
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
            if idx > 0:
                if int(index) != idx:
                    exp_list.append(float(e.attributes['position'].value))
            else:
                if int(index) !=  abs(idx):
                    exp_list.append(float(e.attributes['position'].value))
        return np.array(exp_list) * fsp 
        
    def get_p300_tags(self, idx=1, samples = True, Fs = None):
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
            if idx > 0:
                if int(index) == idx:
                    exp_list.append(float(e.attributes['position'].value))
            else:
                if int(index) !=  abs(idx):
                    exp_list.append(float(e.attributes['position'].value))
        return np.array(exp_list) * fsp 

 
    def getTargetNontarget(self, signal, trgTags, ntrgTags):
        self.chL = signal.shape[0]
        self.Fs = self.getSamplingFrequency()
        self.arrL = self.Fs
        
        print "self.chL: ", self.chL
        
        ## Get target data and stuck it into dictionary
        target = {}

        # for each target blink
        for tag in trgTags:
            
            index = int(tag)
            #~ s *= 0
            s = np.zeros( (self.chL, self.arrL) )
            for idx in range(self.chL):
                s[idx] = signal[idx][index:index+self.Fs]
            
            target[tag] = s

        
        ## Get nontarget data and stuck it into dictionary
        nontarget = {}
        
        # for each target blink
        for tag in ntrgTags:
            index = int(tag)
            #~ s *= 0
            s = np.zeros( (self.chL, self.arrL) )
            for idx in range(self.chL):
                s[idx] = signal[idx][index:index+self.Fs]
            
            nontarget[tag] = s
        
        return target, nontarget
