/* 
 * File:   DummyReceiver.cpp
 * Author: Macias
 * 
 * Created on 3 listopad 2010, 15:11
 */

#include "DummyReceiver.h"

int main()
{
    DummyReceiver dr("127.0.0.1",31889);
    dr.loop();
}