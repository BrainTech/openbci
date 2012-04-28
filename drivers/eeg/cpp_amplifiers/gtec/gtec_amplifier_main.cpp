/*
 * gtec_driver_server.cpp
 *
 *  Created on: 24-04-2012
 *      Author: Macias
 */

#include "run_server.h"
#include "Logger.h"
#include "GTecAmplifier.h"
#include "AmplifierServer.h"

int main(int argc, char**argv)
{
	GTecAmplifier driver;
	AmplifierServer server(&driver);
	try{
	run_server(argc,argv,&server);
	}
	catch (exception &e){
		cerr << "Exception: "<<e.what();
	}
}



