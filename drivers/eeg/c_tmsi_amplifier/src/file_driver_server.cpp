/*
 * file_driver_server.cpp
 *
 *  Created on: 20-03-2012
 *      Author: Macias
 */

#include "server_main.h"
#include "Logger.h"
#include "FileAmplifier.h"

int main(int argc, char**argv)
{
	FileAmplifier driver;
	try{
	run(argc,argv,&driver);
	}
	catch (exception &e){
		cerr << "Exception: "<<e.what();
	}
}



