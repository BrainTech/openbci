from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from multiplexer.multiplexer_constants import peers, types

from classifier import get_epochs_fromfile
from classifier import evoked_pair_plot_smart_tags
from p300_class import P300EasyClassifier

from obci.utils.openbci_logging import log_crash
from obci.configs import settings
import os.path
import sys
from sklearn.externals import joblib

class P300OfflineLearner(ConfiguredMultiplexerServer):
    """Class to run after acquiring calibration signal"""
    @log_crash
    def __init__(self, addresses):
        super(P300OfflineLearner, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_P300_CSP)
        self._data_finished = False
        self._info_finished = False
        self._tags_finished = False
        
        self.ready()
        self.offline = int(self.config.get_param("offline"))
        self.logger.info("offline? {} ".format(self.offline))
        if  self.offline==1:
            self.logger.info("offline learning has started")
            self.learn()

    def _all_ready(self):
        return self._data_finished and self._info_finished and self._tags_finished
    
    def handle_message(self, mxmsg):
        if mxmsg.type == types.SIGNAL_SAVER_FINISHED:
            self._data_finished = True
        elif mxmsg.type == types.INFO_SAVER_FINISHED:
            self._info_finished = True
        elif mxmsg.type == types.TAG_SAVER_FINISHED:
            self._tags_finished = True
        else:
            self.logger.warning("Unrecognised message received!!!!")
        self.no_response()

        if self._all_ready():
            self.learn()

    def learn(self):
        '''Function that reads saved calibration signal, splits it
        to epochs and trains classifier'''
        self.logger.info("STARTING LEARNING")
        f_name = self.config.get_param("data_file_name")
        f_dir = self.config.get_param("data_file_path")
        cl_fname= self.config.get_param("cl_filename")
        cl_fname = os.path.expanduser(os.path.join(f_dir, cl_fname))
        
        filter = None
        baseline = -.2 #read from file
        window = 0.6
        montage = [self.config.get_param("montage")]
        chnls = self.config.get_param("montage_channels").strip().split(';')
        self.logger.info("reference channels {}".format(chnls))
        montage = montage+chnls
        ds = os.path.expanduser(os.path.join(f_dir, f_name))+'.obci'
        
        
        
        ept, epnt = get_epochs_fromfile(ds, filter = filter, duration = 1,
                                    montage = montage,
                                    start_offset = baseline,
                                    )
        self.logger.info("GOT {} TARGET EPOCHS AND {} NONTARGET".format(len(ept), len(epnt)))
        if self.offline ==1:
            self.logger.info('EPOCH PARAMS:\n{}'.format(ept[0].get_params()))
            evoked_pair_plot_smart_tags(ept, epnt, labels=['target', 'nontarget'], chnames=['O1', 'O2'])
            
        cl = P300EasyClassifier(decision_stop=3,
                                max_avr=1000, 
                                targetFs = 24,
                                feature_reduction = None,
                                fname = cl_fname)
        result = cl.calibrate(ept, epnt, bas=baseline, window=window)
        
        self.logger.info('classifier self score on training set: {}'.format(result))
        
        joblib.dump(cl, cl_fname, compress=3)
                            
        self.logger.info("classifier -- DONE")
        sys.exit(0)
        

if __name__ == '__main__':
    P300OfflineLearner(settings.MULTIPLEXER_ADDRESSES).loop()
