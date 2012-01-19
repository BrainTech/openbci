/*
 * Speedtest copied from messagepack.org && modified by jt
 *
 */ 


#include <string.h>
#include <sys/time.h>
#include <iostream>
#include <stdexcept>
#include <string>
#include <limits>

#include <google/protobuf/io/coded_stream.h>
#include <google/protobuf/io/zero_copy_stream_impl.h>

#include <boost/date_time/posix_time/posix_time.hpp>
#include "variables.pb.h"
#include "variables.pb.cc"

class simple_timer {
public:
	void reset() { gettimeofday(&m_timeval, NULL); }
	double show_stat(size_t bufsz, size_t sampn)
	{
		struct timeval endtime;
		gettimeofday(&endtime, NULL);
		double sec = (endtime.tv_sec - m_timeval.tv_sec)
			+ (double)(endtime.tv_usec - m_timeval.tv_usec) / 1000 / 1000;
		std::cout << sec << " sec" << std::endl;
		std::cout << (double(bufsz)/1024/1024) << " MB" << std::endl;
		std::cout << (bufsz/sec/1000/1000*8) << " Mbps" << std::endl;
                std::cout << (sampn/sec) << " samples/sec" << std::endl;
		return sec;
	}
private:
	timeval m_timeval;
};

//char* TASK_STR_PTR;
//static const unsigned int TASK_STR_LEN = 1<<9;

void test_protobuf(unsigned int num, unsigned int chan_num, unsigned int log_interval)
{

	simple_timer timer;
        variables::SampleVector s_vector;
        for (unsigned int i = 0; i < 1; i++) {
            s_vector.add_samples();
        }
	std::cout << "-- Cpp Protocol Buffers serialize" << std::endl;
	timer.reset();

	std::string msg;
        size_t encoded_b = 0;
        size_t encoded_n = 0; 
	variables::Sample *samp;
	{
		for(unsigned int i = 0; i < num; ++i) {

                    boost::posix_time::ptime t = boost::posix_time::microsec_clock::local_time();
                    double ti = time(NULL);

                    ti += (t.time_of_day().total_nanoseconds() % 1000000000) / 1000000000.0;
		    samp = s_vector.mutable_samples(0);
		    samp->Clear();
                    for (int i = 0; i < chan_num; i++) {
		      samp->add_channels((double) i);

                    }
		    samp->set_timestamp(ti);
                    s_vector.SerializeToString(&msg);
                    encoded_b += msg.size();
                    encoded_n ++;
		}
	}

	timer.show_stat(encoded_b, encoded_n);

	std::cout << "-- Cpp Protocol Buffers deserialize" << std::endl;
	timer.reset();
	{
                variables::SampleVector s_msg;
		for(unsigned int i=0; i < num; ++i) {
                    s_msg.ParseFromString(msg);
		}
	}
	timer.show_stat(encoded_b, encoded_n);
        std::cout << "Encoded " << chan_num << " channel sample size: " << msg.size() << std::endl << std::endl;
}

int main(int argc, char* argv[])
{
//	TASK_STR_PTR = (char*)malloc(TASK_STR_LEN+1);
//	memset(TASK_STR_PTR, 'a', TASK_STR_LEN);
//	TASK_STR_PTR[TASK_STR_LEN] = '\0';

	if(argc != 4) {
		std::cout << "usage: "<<argv[0]<<" <num samples> <num channels> <log interval>" << std::endl;
		exit(1);
	}

	unsigned int num = atoi(argv[1]);
        unsigned int chan_num = atoi(argv[2]);
        unsigned int log_interval = atoi(argv[3]);

        std::cout << "Generate " << num << " samples, with " << chan_num << " channels." << std::endl << std::endl;

	test_protobuf(num, chan_num, log_interval); std::cout << "\n";
}

