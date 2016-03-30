import appliance2 as a
b = a.Blinker('/dev/ttyUSB0')
b.open()
b.on()
