/* 
 * File:   testAmplifierServer.cpp
 * Author: Macias
 *
 * Created on 2010-10-19, 12:36:46
 */

#include <stdlib.h>
#include <iostream>
#include "AmplifierServer.h"
#include "AmplifierDriver.h"
#include "Logger.h"

/*
 * Simple C++ Test Suite
 */

void test1(AmplifierServer &server) {
    std::cout << "testAmplifierServer test 1" << std::endl;
    server.start_sampling();
    sleep(100);
    server.stop_sampling();
}

int main(int argc, char** argv) {
    debug("test\n");
    std::cout << "%SUITE_STARTING% testAmplifierServer" << std::endl;
    AmplifierDriver driver;
    std::cout << "Amplifier driver created" << std::endl;
    AmplifierServer server("127.0.0.1", 31889,&driver);
    Logger log(2048,"testServer");
    server.set_logger(&log);
    server.set_sampling_rate(2048);
    std::cout << "%SUITE_STARTED%" << std::endl;
    server.loop_in_thread();
    std::cout << "%TEST_STARTED% test1 (testAmplifierServer)" << std::endl;
    test1(server);
    std::cout << "%TEST_FINISHED% time=0 test1 (testAmplifierServer)" << std::endl;

    return (EXIT_SUCCESS);
}

