/*
 * file_driver_server.cpp
 *
 *  Created on: 20-03-2012
 *      Author: Macias
 */

#include "server_main.h"
#include "Logger.h"
#include "FileAmplifier.h"
#include "TagAmplifierServer.h"

int main(int argc, char**argv)
{
	FileAmplifier driver;
	TagAmplifierServer server(&driver);
	try{
	run(argc,argv,&server);
	}
	catch (exception &e){
		cerr << "Exception: "<<e.what();
	}
}



