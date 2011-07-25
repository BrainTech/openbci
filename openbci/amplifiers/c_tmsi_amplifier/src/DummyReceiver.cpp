/* 
 * File:   DummyReceiver.cpp
 * Author: Macias
 * 
 * Created on 3 listopad 2010, 15:11
 */

#include "DummyReceiver.h"

int main(int argc,char ** argv)
{

  int port=31889,sampling_rate=128;
    char *host = "127.0.0.1";
    for (int i=1;i<argc;i++)
        if (argv[i][0]=='-')
            switch (argv[i][1])
            {
                case 's': sampling_rage=atoi(argv[i+1]); break;
                case 'p': port=atoi(argv[i+1]); break;
                case 'h': host=argv[i+1];
            }
    
    DummyReceiver dr(host,port,sampling_rate);
    dr.loop();
}
