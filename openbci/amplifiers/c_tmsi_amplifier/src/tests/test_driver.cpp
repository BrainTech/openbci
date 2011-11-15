#include "test_driver.h"
int main(int argc,char** argv){
	AmplifierDriver amp;
	amp.set_description(new DummyAmplifier(&amp));
	test_driver(argc,argv,&amp);
}
