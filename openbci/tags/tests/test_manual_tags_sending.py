from tags import tagger
import time

TAGGER = tagger.get_tagger()
import random
def run():
    while True:
        i = raw_input()
        print("LEN i: "+str(len(i)))
        if len(i) == 0:
            i = "XYZ"
        i =  i.strip()
        t= time.time()
        print("SEND TAG name"+i+" with time: "+repr(t))
        TAGGER.send_tag(t, t+3.0*random.random()+1.0, i, {'a':1, 'b':2.2, 'c':'napis_jakis', 'annotation':"ANNOTACJA JAKAS"})

if __name__ == "__main__":
    print("Type anything to send tag!!!")
    run()
