import os
import gflags

gflags.DEFINE_string('pidfile', '', """Name of the pidfile where pid of this
proccess should be written""")

def pidfile():
    print "pidfile =", gflags.FLAGS.pidfile
    pidfile = gflags.FLAGS.pidfile
    if not pidfile:
        print "No pidfile specified."
    else:
        file(pidfile, "w").write(str(os.getpid()))

