import numpy 
import numpy as np
import sys
import pylab as py


print 'Usage: filename1 filename2 type1 type2 channum'


channum = int(sys.argv[5])
file_name_1 = sys.argv[1]
file_name_2 = sys.argv[2]

print 'Files: '+str(file_name_1)+' ('+sys.argv[3]+'), '+str(file_name_2)+' ('+sys.argv[4]+')'

s_1 = numpy.fromfile(file_name_1,sys.argv[3])
s_2 = numpy.fromfile(file_name_2,sys.argv[4])

l = np.min((len(s_1)/channum, len(s_2)/channum))

_1 = np.zeros((channum, l))
_2 = np.zeros((channum, l))

for i in range(channum):
    _1[i] = s_1[i::channum][:l]# - s_1[i::channum].mean()
    _2[i] = s_2[i::channum][:l]# - s_2[i::channum].mean()
#_1 *= 0.0715
#_2 *= 0.0715

#print _1.shape
#print _2.shape


for i in range(channum):
    if np.max(_1[i]) != np.min(_1[i]) and np.min(_2[i]) != np.max(_2[i]):
        roznica = False
        roznica2 = False
        prze = 0
        while roznica == False and roznica2 == False:
            if prze != 0:
                 roznica = (_1[i, prze:] == _2[i, :-prze]).all()
                 roznica2 =  (_2[i, prze:] == _1[i, :-prze]).all()
            else:
                roznica = (_1[i] == _2[i]).all()
                roznica2 = roznica
            prze += 1
        #print roznica, roznica2
        if prze > l:
            print 'Kanaly '+str(i)+' sa rozne!!!'
        else:
            print 'Przesuniecie dla kanalow '+str(i)+' wynosi: '+str(prze)
            #print 'Suma roznic dla kanalow '+str(i)+' wynosi: '+str(roznica)
    else:
        print "Kanaly "+str(i)+" sa puste!"
