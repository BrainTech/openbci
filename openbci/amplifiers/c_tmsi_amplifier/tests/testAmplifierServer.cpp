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

/*
 * Simple C++ Test Suite
 */

void test1(AmplifierServer &server) {
    std::cout << "testAmplifierServer test 1" << std::endl;
    server.start_sampling();
    sleep(10);
    server.stop_sampling();
}

void test2() {
    std::cout << "testAmplifierServer test 2" << std::endl;
    std::cout << "%TEST_FAILED% time=0 testname=test2 (testAmplifierServer) message=error message sample" << std::endl;
}

int main(int argc, char** argv) {
    std::cout << "%SUITE_STARTING% testAmplifierServer" << std::endl;
    AmplifierDriver driver;
    AmplifierServer server("127.0.0.1", 31889,&driver);
    server.loop_in_thread();
    std::cout << "%SUITE_STARTED%" << std::endl;
    std::cout << "%TEST_STARTED% test1 (testAmplifierServer)" << std::endl;
    test1(server);
    std::cout << "%TEST_FINISHED% time=0 test1 (testAmplifierServer)" << std::endl;

    return (EXIT_SUCCESS);
}

