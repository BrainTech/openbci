#include "test_amplifier.h"
int main(int argc,char** argv){
	Amplifier amp;
	amp.set_description(new DummyAmpDesc(&amp));
	test_driver(argc,argv,&amp);
}
