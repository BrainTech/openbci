/*
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Author:
 *     Maciej Pawlisz <maciej.pawlisz at titanis.pl>
*/

#include <boost/program_options.hpp>
namespace po= boost::program_options;


#include <iostream>
#include <sstream>
#include "AmplifierServer.h"
#include "AmplifierDriver.h"
#include "Logger.h"

int run(int argc, char**argv,AmplifierServer * server)
{
	string line;
	AmplifierDriver *driver=server->get_driver();
	Logger log(128,"Amplifier Server");
	server->set_logger(&log);
	po::options_description options("Program Options");
	options.add_options()
			("help,H","Show program options and help");
	options.add(driver->get_options()).add(server->get_options());
	po::variables_map vm;
	po::store(po::parse_command_line(argc,argv,options),vm);
	po::notify(vm);
	if (vm.count("help"))
		cout << "This program connects to amplifier and prints its description in JSON, including name, available sampling rates "\
				" and available channels. \n After initialization it waits on stdin for parameters:\n"<<server->get_commands()<<"\nCommand line options:\n" << options;
	driver->init(vm);
	cout <<driver->get_description()->get_json() <<"\n\n";
	server->init(vm);
	while (!(cin>>line).fail()){
		if (server->do_command(line,cin))
			cout <<line<<" OK\n";
		else if (line=="exit"){
			cout <<line<<" OK\n";
			break;
		}
		else
			cout <<line<<" Error\n";
	}
	cerr <<driver->get_description()->get_name()<< " driver server exit\n";
	return 0;
}
