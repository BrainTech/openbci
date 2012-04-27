import sys
import subprocess
import signal
sys.path.append("../../../multiplexer-install/lib/python2.6/site-packages/")
sys.path.append("../../../obci_control")
sys.path.append("../../../")
sys.path.append("../../")
from openbci.core import  core_logging as logger
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import peer.peer_config_control
from subprocess import Popen
import json
LOGGER = logger.get_logger("DriverServer","info")
class DriverServer(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(DriverServer, self).__init__(addresses=addresses, type=peers.ETR_SERVER)
        self.config = peer.peer_config_control.PeerControl(self)
        self.config.initialize_config(self.conn)
        args=self.get_run_args(addresses[0])
        LOGGER.info("Executing: "+' '.join(args))
        self.driver=Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        out = self._communicate()
        self.load_params(out)
        self.config.send_peer_ready(self.conn)
#        self.config.synchronize_ready(self.conn)
        
        self.set_sampling_rate(self.config.get_param("sampling_rate"))
        self.set_active_channels(self.config.get_param("active_channels"))
        
        self.start_sampling()
    
    def get_run_args(self,multiplexer_address):
        host,port=multiplexer_address
        exe=self.config.get_param('driver_executable')
        args=[exe,"-h",str(host),'-p',str(port)]
        if self.config.get_param("usb_device"):
            args.extend(["-d",self.config.get_param("usb_device")])
        elif self.config.get_param("bluetooth_device"):
            args.extend(["-b",self.config.get_param("bluetooth_device")])
        else:
            raise Exception("usb_device or bluetooth_device is required")
        if self.config.get_param("amplifier_responses"):
            args.extend(["-r", self.config.get_param("amplifier_responses")])
        if self.config.get_param("dump_responses"):
            args.extend(["--save_responses", self.config.get_param("amplifier_responses")])
        return args
    def load_params(self,output):
        amp_desc=json.loads(output)
        self.config.set_param('amplifier_name',amp_desc[u"name"])
        self.config.set_param('physical_channels_no',amp_desc[u"physical_channels"])
        self.config.set_param('sampling_rates',json.dumps(amp_desc[u"sampling_rates"]))
        self.config.set_param('channels',json.dumps(amp_desc[u"channels"]))
    def do_sampling(self):
        self.driver.wait()    
    
    def set_sampling_rate(self,sampling_rate):
        LOGGER.info("Set sampling rate: %s "%sampling_rate)
        error=self._communicate("sampling_rate "+str(sampling_rate))
        if error:
            print error
    def set_active_channels(self,active_channels):
        LOGGER.info("Set Active channels: %s"%active_channels)
        error=self._communicate("active_channels "+str(active_channels))
        if error:
            print error
    def start_sampling(self):
        signal.signal(signal.SIGINT, self.stop_sampling)
        LOGGER.info("Start sampling")
        error=self._communicate("start")
        if error:
            print error
        LOGGER.info("Sampling started")
    def stop_sampling(self,_1=None,_2=None):
        sys.stderr.write("stop sampling")
        LOGGER.info("Stop sampling")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.driver.send_signal(signal.SIGINT)
        LOGGER.info("Sampling stopped")
    def _communicate(self,command=""):
        out=""
        self.driver.stdin.write(command+"\n")
        while True:
            line=self.driver.stdout.readline()
            if line=="\n": break
            out+=line;
        return out
    def handle_message(self, mxmsg):
        # handle something
        self.no_response()

if __name__ == "__main__":
    import settings as settings
    print signal.getsignal(signal.SIGINT)
    srv = DriverServer(settings.MULTIPLEXER_ADDRESSES)
    srv.do_sampling()




