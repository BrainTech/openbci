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
	try{
	FileAmplifier driver;
	TagAmplifierServer server(&driver);
	run_server(argc,argv,&server);
	}
	catch (FileAmplifierException *e){
		cerr << e->what()<<"\n";
	}
}



