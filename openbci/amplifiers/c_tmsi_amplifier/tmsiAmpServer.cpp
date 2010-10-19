/* 
 * File:   tmsiAmpServer.cpp
 * Author: Macias
 * 
 * Created on 19 październik 2010, 14:22
 */

#include "tmsiAmpServer.h"

void TmsiAmpServer::check_status(std::vector<int>& isamples){
    if (tmsi_driver->is_onoff_pressed())
    {
        printf("TmsiAmpServer: On/Off is pressed\n");
    }
    if (tmsi_driver->is_battery_low())
    {
        printf("TmsiAmpServer: Amplifiers battery is low\n");
    }
    if (tmsi_driver->is_trigger())
    {
        printf("TmsiAmpServer: Trigger is active\n");
    }
}

int main(int argc, char**argv)
{
    char * device="/dev/fusbi0",*host="127.0.0.1",*read_db=NULL;
    int port=31889,type=USB_AMPLIFIER;
    Logger *log=NULL;;
    for (int i =1; i<argc; i++)
    {
        if (argv[i][0]=='-' && i<argc-1)
            switch (argv[i][1])
            {
                case 'a':
                    host=argv[i+1]; break;
                case 'd':
                    device=argv[i+1];break;
                case 'b':
                    type=BLUETOOTH_AMPLIFIER; break;
                case 'r':
                    read_db=argv[i+1]; break;
                case 'p':
                    port=atoi(argv[i+1]);
                case 'l':
                    log=new Logger(atoi(argv[i+1]),"tmsiAmpServer"); break;
                case 'h':
                default:
                    printf("Usage: \n"\
                            "[-a multiplexer_addres] default=\"127.0.0.1\"\n"\
                            "[-p port] defaut=\"31889\"\n"\
                            "[-d device_path or bluetooth address] default=\"/dev/fusbi0\"\n"\
                            "[-b] if set device path is bluetooth address\n"\
                            "[-r file] file with stored amplifier responses\n"\
                            "[-l nr_of_samples] print log message after number_of_samples" \
                            "[-h] show this message\n");
            }

    }
    TmsiAmplifier driver(device,type,read_db);
    TmsiAmpServer server(host,port,&driver);
    server.set_logger(log);
    server.start_sampling();
    clock_t cl=clock();
    server.loop();
    return 0;
}