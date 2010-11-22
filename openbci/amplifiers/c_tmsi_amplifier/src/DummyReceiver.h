/* 
 * File:   DummyReceiver.h
 * Author: Macias
 *
 * Created on 3 listopad 2010, 15:11
 */

#ifndef DUMMYRECEIVER_H
#define	DUMMYRECEIVER_H
#include "multiplexer/Multiplexer.pb.h"
#include "multiplexer/multiplexer.constants.h"
#include "multiplexer/Client.h"
#include "multiplexer/backend/BaseMultiplexerServer.h"
#include "variables.pb.h"
#include "azouk/util/kwargs.h"
#include "Logger.h"
using namespace multiplexer;
class DummyReceiver:public backend::BaseMultiplexerServer {
private:
    Logger logger;
public:
    DummyReceiver(const std::string& host, boost::uint16_t port,int log):
    BaseMultiplexerServer(new Client(peers::SIGNAL_CATCHER), peers::SIGNAL_CATCHER),logger(log,"DummyReceiver")
    {
        conn->connect(host, port);
        logger.restart();
        printf("DummyReceiver: Logging every %d samples. Connecting to: %s:%d\n",log,host.c_str(),port);
    }
    virtual void handle_message(MultiplexerMessage & msg)
    {
        logger.next_sample();
    }
    virtual ~DummyReceiver(){};
};

#endif	/* DUMMYRECEIVER_H */

