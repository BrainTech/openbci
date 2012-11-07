using namespace std;
#include <boost/program_options.hpp>
namespace po = boost::program_options;
po::options_description get_simple_options() {
	po::options_description options("Gtec Simple Driver Options");
	options.add_options()
			("device_name,n",po::value<string>(),
					"Amplifer to use")
			("device_index,i",po::value<int>()->default_value(1),
					"Amplifier index from list (starting from 1)")
			("sampling_rate,s",	po::value<uint>()->default_value(512),
					"Sampling rate to use")
			("command,c", po::value<string>()->default_value("show"),
					"Command to execute. Available commands:\n"
					"  show: \tShow list of available devices\n"
					"  calibrate: \tCalibrate device\n"
					"  reset: \tReset devices scales and offsets to 1 and 0\n"
					"  sampling: \tStart sampling and write sample data on stdin\n"
					"  measure: \t Print calibration accuracy\n")
			("mode,m",po::value<string>()->default_value("counter"),
					"Data mode of amplifier:\n"
					"  normal: \treturn all channels\n"
					"  counter: \t return sample counter on last channel\n"
					"  function: \t return function on all channel\n")
			("function,f",po::value<string>()->default_value("sinus"),
					"Function on all channels:\n"
					"  sinus: \t Sinus function\n"
					"  saw: \t Saw (triangle function)\n"
					"  square: \t Square function \n"
					"  noise: \t Noise\n")
			("amplitude,a",po::value<int>()->default_value(1),
					"Amplitude of a function in mV, integer in range [-250,250]")
			("frequency,h",po::value<int>()->default_value(10),
					"Frequency of a function in Hz, integer in range [1,100]")
			("offset,o",po::value<int>()->default_value(0),
					"Offset of a function in mV, integer in range [-200,200]")
			("calib_duration,d",po::value<int>()->default_value(60),
					"Duration of calibration");
	return options;
}
