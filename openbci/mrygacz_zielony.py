import serial

ser = serial.Serial('/dev/ttyUSB0', baudrate=9600)

def ct(a):
	return 16 *  (10 ** 6) / 256 / a

def to_hex_word(a):
	return chr(a / 256) + chr(a % 256)

def magic(a, x=0.5):
	w = ct(a)
	return to_hex_word(int(w * x)) + to_hex_word(int(w * (1 - x)))

def mrygaj(czym, jak, x=0.5, on=True):
	ser.write(chr(czym) + chr(0 if on else 2) + magic(jak, x))


  
