import tagger
import time
def run():
    tagger.send_tag(time.time(), time.time(), 'A', {'a':1, 'b':2.2, 'c':'napis_jakis'})
    time.sleep(1)
    tagger.send_tag(time.time(), time.time(), 'B', {'x':100, 'y':2, 'z':'napis_jakisdsfsdfdsfdsfd'})

if __name__ == "__main__":
    run()
