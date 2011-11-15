/* 
 * File:   Logger.h
 * Author: Macias
 *
 * Created on 19 październik 2010, 18:36
 */

#ifndef LOGGER_H
#define	LOGGER_H
#include <ctime>
#include <stdio.h>
#include <cmath>
#include <iostream>
#include <stdarg.h>
#include <boost/date_time/posix_time/posix_time.hpp>
using namespace boost::posix_time;
using namespace std;
class Logger{
public:
    int sampling;
    int number_of_samples;
    ptime start_time,last_pack_time;
    const char * name;
    Logger(int p_sampling, const char * p_name)
    {
        sampling=p_sampling;
        name = p_name;
        restart();
    }
    void restart()
    {
        start_time=microsec_clock::local_time();
        last_pack_time=start_time;
        number_of_samples=0;
    }
    void next_sample()
    {
        if (++number_of_samples%sampling==0)
        {
            char buffer[100];
            ptime now=boost::posix_time::microsec_clock::local_time();
            sprintf(buffer,"Time of last %d samples / all avg:"\
                    "%f / %f",sampling,
                    ((double)(now-last_pack_time).total_microseconds())/1000000,
                    ((double)sampling*(now-start_time).total_microseconds())/1000000/number_of_samples);
            info(buffer);
            last_pack_time=now;
        }
    }
    char * header(char * buffer){
    	ptime now=boost::posix_time::microsec_clock::local_time();
		struct tm  timeinfo=to_tm(now);
		strftime(buffer,100,"%Y-%m-%d %H:%M:%S",&timeinfo);
		sprintf(buffer,"%s,%.3lld - %s - ",buffer,now.time_of_day().total_microseconds()%1000000/1000,name);
		return buffer;
    }
    void info(const char * string,...){
    	va_list ap;
    	char buffer[100];
		fprintf(stderr,"%s INFO - ",header(buffer));
		int n;
		va_start(ap, string);
		n = fprintf(stderr, string, ap);
		va_end(ap);
		fprintf(stderr,"\n");
    }
    ostream & info(){
    	char buffer[100];
    	return cerr<<"\n" << header(buffer) << "INFO - ";
        }

};


#endif	/* LOGGER_H */

