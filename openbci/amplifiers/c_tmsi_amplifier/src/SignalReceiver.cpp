/* 
 * File:   DummyReceiver.cpp
 * Author: Macias
 * 
 * Created on 3 listopad 2010, 15:11
 */

#include "SignalReceiver.h"
#include "Logger.h"
#include <boost/shared_ptr.hpp>
#include <boost/date_time/posix_time/ptime.hpp>
#include <vector>
using namespace multiplexer;

SignalReceiver::SignalReceiver(const std::string& host, boost::uint16_t port, int cache_size, int monitor_last_channel):
    BaseMultiplexerServer(new Client(peers::SIGNAL_STREAMER), peers::SIGNAL_STREAMER)
    {
      this->cached_index = -1;
        conn->connect(host, port);
        printf("SignalReceiver: Connecting to: %s:%d\n",host.c_str(),port);
	shared_ptr<MultiplexerMessage> msg =
            conn->query("SamplingRate", types::DICT_GET_REQUEST_MESSAGE).second;

	int samp_rate = atoi(msg->message().c_str());
	msg = conn->query("NumOfChannels", types::DICT_GET_REQUEST_MESSAGE).second;
	this->num_of_channels = atoi(msg->message().c_str());
	logger = new Logger(samp_rate,"SignalReceiver");
        logger->restart();
	this->prev_last_channel = 0.0;
	this->monitor_last_channel = monitor_last_channel;
	this->sample_count = 0;
	this->cache_size = cache_size;
	this->cached_samples = new double*[num_of_channels];
	for (int i = 0; i < num_of_channels; i++)
	  *(this->cached_samples+i) = new double[cache_size];
	this->cached_index = 0;
    }

void SignalReceiver::handle_message(MultiplexerMessage & mxmsg)
    {
      if (this->cached_index == -1)
	return;

      if (mxmsg.type() == types::AMPLIFIER_SIGNAL_MESSAGE) {
	this->sample_count ++;
        this->logger->next_sample();
	variables::SampleVector s_vector;
	s_vector.ParseFromString(mxmsg.message());
	for (int i = 0; i < s_vector.samples_size(); i++) {
	  for (int j = 0; j < s_vector.samples(i).channels_size(); j++) {
	    this->cached_samples[j][this->cached_index] = s_vector.samples(i).channels(j);//->value();
	    //samp->set_timestamp(ti);
	  }
	  
	  if (this->monitor_last_channel) {
	    double last_channel = this->cached_samples[this->num_of_channels-1][this->cached_index];
	    if (this->prev_last_channel+1 != last_channel)
	      printf("Lost samples in number:%i\n", (int) (last_channel - this->prev_last_channel + 1));
	    this->prev_last_channel = last_channel;
	  }
	  
	  this->cached_index ++;
	  if (this->cached_index == this->cache_size) {
	    this->cached_index = 0;
	    //dump cache to file in the future
	  }
	}
      }
      this->no_response();
    }

int main(int argc,char ** argv)
{
    char *host = "127.0.0.1";
    int cache = 1024;
    int monitor = 1;
    for (int i=1;i<argc;i++)
        if (argv[i][0]=='-')
            switch (argv[i][1])
            {
	    case 'h': host=argv[i+1]; break;
	    case 'c': cache = atoi(argv[i+1]); break;
	    case 'm': monitor = atoi(argv[i+1]);
            }
    
    SignalReceiver dr(host,31889, cache, monitor);
    dr.loop();
}
