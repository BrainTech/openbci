/* 
 * File:   tmsiAmpServer.h
 * Author: Macias
 *
 * Created on 19 październik 2010, 14:22
 */

#ifndef TMSIAMPSERVER_H
#define	TMSIAMPSERVER_H

#include "AmplifierServer.h"
#include "TmsiAmplifier.h"

class TmsiAmpServer:public AmplifierServer{
private:
    TmsiAmplifier *tmsi_driver;

public:
    TmsiAmpServer(const std::string& host, boost::uint16_t port,AmplifierDriver *driver):AmplifierServer(host,port,driver)
    {
        tmsi_driver=(TmsiAmplifier *)driver;
    }
};

#endif	/* TMSIAMPSERVER_H */

