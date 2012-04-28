/* 
 * File:   test_logger.cpp
 * Author: Macias
 *
 * Created on 2010-10-19, 20:34:10
 */

#include <stdlib.h>
#include <iostream>


#include "Logger.h"



int main()
{
    Logger log(2,"ble");
    for(int i=0; i<10; i++)
        log.next_sample();

    return 0;
}
