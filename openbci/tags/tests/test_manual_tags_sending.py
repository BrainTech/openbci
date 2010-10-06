from tags import tagger
import time

TAGGER = tagger.get_tagger()
def run():
    while True:
        raw_input()
        t= time.time()
        print("SEND TAG name 'XYZ' with time: "+repr(t))
        TAGGER.send_tag(t, t , 'XYZ', {'a':1, 'b':2.2, 'c':'napis_jakis'})

if __name__ == "__main__":
    print("Type anything to send tag!!!")
    run()
