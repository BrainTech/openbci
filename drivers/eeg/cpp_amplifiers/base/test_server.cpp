/* 
 * File:   testAmplifierServer.cpp
 * Author: Macias
 *
 * Created on 2010-10-19, 12:36:46
 */

#include <stdlib.h>
#include <iostream>
#include "AmplifierServer.h"
#include "Amplifier.h"
#include "Logger.h"
#include <boost/program_options.hpp>
namespace po=boost::program_options;
int main(int argc, char** argv) {
    std::cout << "%SUITE_STARTING% testAmplifierServer" << std::endl;
    Amplifier driver;
    AmplifierServer server(&driver);
    driver.set_description(new DummyAmpDesc(&driver));
    std::cout << "Amplifier driver created" << std::endl;
    std::cout << driver.get_description()->get_json();
    po::options_description options("Program Options");
	options.add_options()
			("help,H","Show program options and help");
	options.add(driver.get_options()).add(server.get_options());
	po::variables_map vm;
	po::store(po::parse_command_line(argc,argv,options),vm);
	if (vm.count("help"))
		cout << options <<"\n";
	po::notify(vm);
	Logger log(driver.get_sampling_rate(),"testServer");
    server.set_logger(&log);
	server.init(vm);
	if (!vm.count("start"))
		server.start_sampling();
    return (EXIT_SUCCESS);
}

