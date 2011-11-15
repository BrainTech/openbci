#include <iostream>
#include "AmplifierDriver.h"
#include "Logger.h"

int main(int argc, char** argv) {
    std::cout << "%SUITE_STARTING% testAmplifierServer" << std::endl;
    AmplifierDriver driver;
    driver.set_description(new DummyAmplifier());
    std::cout << "Amplifier driver created" << std::endl;
    std::cout << driver.get_description()->get_json();
    int sampling_rate=128; int duration = 100;
    vector<string> channels;
    for (int i=1;i<argc;i++)
        if (argv[i][0]=='-'){
            if (argv[i][1]=='s')
                sampling_rate=atoi(argv[i+1]);
            else if (argv[i][1]=='d' && (i+1 <argc))
                duration=atoi(argv[i+1]);
            else if (argv[i][1]=='c' && (i+1 <argc)){
            	istringstream names(argv[i+1]);
            	string name;
            	while (!(names>>name).fail())
            		channels.push_back(name);
            	}
            }

    Logger log(sampling_rate,"testServer");
    driver.set_active_channels(channels);
    cout << "Active channels:\n";
    for (uint i=0;i<driver.get_active_channels().size();i++)
    	cout << driver.get_active_channels()[i]->get_json()<<"\n";
//    server.set_logger(&log);
//    server.set_sampling_rate(sampling_rate);
    std::cout << "%SUITE_STARTED% sampling_rate:" <<sampling_rate <<std::endl;
    std::cout << "%SUITE_STARTED% duration:" <<duration <<std::endl;
    //server.loop();
    std::cout << "%TEST_STARTED% test1 (testAmplifierServer)" << std::endl;

    std::cout << "%TEST_FINISHED% time=0 test1 (testAmplifierServer)" << std::endl;

    return (EXIT_SUCCESS);
}

