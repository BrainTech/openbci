#include "test_amplifier.h"
#include "GTecAmplifier.h"
int main(int argc,char** argv){
	GTecAmplifier amp;
	if (!amp.run_simple(argc,argv))
		test_driver(argc,argv,&amp);
}
