/* 
 * File:   tmsiAmpServer.cpp
 * Author: Macias
 * 
 * Created on 19 październik 2010, 14:22
 */

#include "tmsiAmpServer.h"

void TmsiAmpServer::check_status(std::vector<int>& isamples){
    return;
    if (tmsi_driver->is_onoff_pressed())
    {
        printf("TmsiAmpServer: On/Off is pressed\n");
    }
    if (tmsi_driver->is_battery_low())
    {
        printf("TmsiAmpServer: Amplifier battery is low\n");
    }
    if (tmsi_driver->is_trigger())
    {
        printf("TmsiAmpServer: Trigger is active\n");
    }
}
void print_help()
{
     printf("Usage: \n"\
                            "[-a multiplexer_addres] default=\"127.0.0.1\"\n"\
                            "[-p port] defaut=\"31889\"\n"\
                            "[-d device_path or bluetooth address] default=\"/dev/fusbi0\"\n"\
                            "[-b] if set device path is bluetooth address\n"\
                            "[-r file] file with stored amplifier responses\n"\
                            "[-l nr_of_samples] print log message after number_of_samples\n" \
                            "[-D file] whole amplifier output will be dumped to file\n"\
                            "[-s sampling_rate] force set sampling rate in Hz\n"\
                            "[-h] show this message\n");
}
int main(int argc, char**argv)
{
    const char * device="/dev/fusbi0",*host="127.0.0.1",*read_db=NULL, *dump_file=NULL;
    int port=31889,type=USB_AMPLIFIER,sampling_rate=-1;
    Logger *log=NULL;

    for (int i =1; i<argc; i++)
    {
        if (argv[i][0]=='-' && i<argc)
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
                    print_help();
                    exit(0);
                case 'D':
                    dump_file=argv[i+1]; break;
                case 's':
                    sampling_rate=atoi(argv[i+1]); break;
                default:
                    printf("Unknown option -%c",argv[i][1]);
                    print_help();
            }

    }
    TmsiAmplifier driver(device,type,read_db,dump_file);
    TmsiAmpServer server(host,port,&driver);
    server.set_logger(log);
    if (sampling_rate>0)
        server.set_sampling_rate(sampling_rate);
    server.start_sampling();
    server.loop();
    return 0;
}