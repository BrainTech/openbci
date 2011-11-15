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

void test1(AmplifierServer &server, int duration) {
    std::cout << "testAmplifierServer test 1" << std::endl;
    server.start_sampling();
    sleep(duration);
    server.stop_sampling();
}

int main(int argc, char** argv) {
    std::cout << "%SUITE_STARTING% testAmplifierServer" << std::endl;
    AmplifierDriver driver;
    std::cout << "Amplifier driver created" << std::endl;
    std::cout << driver.get_json();
    AmplifierServer server("127.0.0.1", 31889,&driver);
    int sampling_rate=128; int duration = 100;
    for (int i=1;i<argc;i++)
        if (argv[i][0]=='-'){
            if (argv[i][1]=='s')
                sampling_rate=atoi(argv[i+1]);
            else if (argv[i][1]=='d' && (i+1 <argc))
                duration=atoi(argv[i+1]);
            }

    Logger log(sampling_rate,"testServer");
    server.set_logger(&log);
    std::cout << "%SUITE_STARTED% sampling_rate:" <<sampling_rate <<std::endl;
    std::cout << "%SUITE_STARTED% duration:" <<duration <<std::endl;
    //server.loop();
    std::cout << "%TEST_STARTED% test1 (testAmplifierServer)" << std::endl;
    test1(server, duration);
    std::cout << "%TEST_FINISHED% time=0 test1 (testAmplifierServer)" << std::endl;

    return (EXIT_SUCCESS);
}

