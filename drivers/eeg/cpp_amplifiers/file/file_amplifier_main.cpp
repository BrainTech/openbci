/*
 * file_driver_server.cpp
 *
 *  Created on: 20-03-2012
 *      Author: Macias
 */

#include "run_server.h"
#include "Logger.h"
#include "FileAmplifier.h"
#include "TagAmplifierServer.h"

int main(int argc, char**argv)
{
	FileAmplifier driver;
	TagAmplifierServer server(&driver);
	try{
	run_server(argc,argv,&server);
	}
	catch (exception &e){
		cerr << "Exception: "<<e.what();
	}
}



