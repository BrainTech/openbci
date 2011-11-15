/* 
 * File:   tmsiAmpServer.cpp
 * Author: Macias
 * 
 * Created on 19 październik 2010, 14:22
 */

#include "tmsiAmpServer.h"

void print_help()
{
     printf("Usage: \n"\
                            "[-a multiplexer_addres] default=\"127.0.0.1\"\n"\
                            "[-p port] defaut=\"31889\"\n"\
                            "[-d device_path ] amplifier address default=\"/dev/tmsi0\"\n"\
                            "[-b bluetooth address] amplifier bluetooth address\n"\
                            "[-r file] file with stored amplifier responses\n"\
                            "[-l nr_of_samples] print log message after number_of_samples\n" \
                            "[-D file] whole amplifier output will be dumped to file\n"\
                            "[-s sampling_rate] force set sampling rate in Hz\n"\
                            "[-c channels] string with channel names or indexes, or \"*\" for all channels. Default is \"*\""\
                            "[-i] interactive mode. Listen for commands on stdin:\n	s sampling_rate\n	c channels\n	start - starts sampling\n sending SIG_INT stops sampling"\
                            "[-h] show this message\n");
}
int main(int argc, char**argv)
{
    const char * device="/dev/tmsi0",*host="127.0.0.1",*read_db=NULL, *dump_file=NULL, *channels="*";
    int port=31889,type=USB_AMPLIFIER,sampling_rate=-1;
    bool interactive=false;

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
                    type=BLUETOOTH_AMPLIFIER; 
                    device=argv[i+1];break;
                    break;
                case 'r':
                    read_db=argv[i+1]; break;
                case 'p':
                    port=atoi(argv[i+1]); break;
                case 'l':
                    log=new Logger(atoi(argv[i+1]),"tmsiAmpServer"); break;
                case 'h':
                    print_help();
                    exit(0);
                case 'D':
                    dump_file=argv[i+1]; break;
                case 's':
                    sampling_rate=atoi(argv[i+1]); break;
                case 'i':
                	interactive=true; break;
                case 'c':
                	channels=argv[i+1]; break;
                default:
                    printf("Unknown option -%c",argv[i][1]);
                    print_help();
                    exit(0);
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
