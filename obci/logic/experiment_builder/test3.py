#!/usr/bin/env python
"""Demonstrate harmonic synthesis in Python.

Python itself is slow enough that if we had to execute multiple Python
bytecodes per sample, we'd probably not keep up, even on modern
hardware.  But with Numerical Python ("Numeric") we can run the inner
loops of harmonic synthesis in C and have "NSL" --- no stinking loops!

And PyGame is awesome in that (a) it's easy to get stuff up and
running quickly and (b) it comes with an interface to Numeric.

"""
from pygame import *
import pygame, time, random, Numeric, pygame.sndarray
from matplotlib import pyplot


sample_rate = 44100

def sine_array_onecycle(hz, peak):
    "Compute one cycle of an N-Hz sine wave with given peak amplitude."
    length = sample_rate / float(hz)
    omega = Numeric.pi * 2 / length
    xvalues = Numeric.arange(int(length)) * omega
    return (peak * Numeric.sin(xvalues)).astype(Numeric.Int16)
def sine_array(hz, peak, n_samples = sample_rate):
    """Compute N samples of a sine wave with given frequency and peak amplitude.

    Defaults to one second."""
    return Numeric.resize(sine_array_onecycle(hz, peak), (n_samples,))
def second_harmonic(hz):
    "Compute a wave with a strong second harmonic."
    return sine_array(hz, 16384) + sine_array(hz * 2, 16384)
def brass(hz):
    "Compute a sound with some odd harmonics.  Doesn't really sound brassy."
    return sum([sine_array(hz, 4096),
                sine_array(hz * 3, 4096),
                sine_array(hz * 5, 4096)])
def play_for(sample_array, ms):
    "Play given samples, as a sound, for N ms."
    sound = pygame.sndarray.make_sound(sample_array)
    beg = time.time()
    sound.play(-1)
    pygame.time.delay(ms)
    sound.stop()
    end = time.time()
    return beg, end


def action(f1, f2):
    pygame.mixer.pre_init(sample_rate, -16, 1) # 44.1kHz, 16-bit signed, mono
    pygame.init()
    fc = sine_array(f1, 10)
    fm = sine_array(f2, 10)
    res = fc * fm
    return play_for(res * 600, 5000) #440, 4096, 500
 

    
def main():
    "Play some funky sounds, as a demo."
    #print time.time()
    pygame.mixer.pre_init(sample_rate, -16, 1) # 44.1kHz, 16-bit signed, mono
    pygame.init()
    fc = sine_array(440, 10)
    fm = sine_array(20, 10)
    res = fc * fm
    #pyplot.plot(res)
    #pyplot.show()
    tstamp =  time.time()
    play_for(fc * 6000, 5000) #440, 4096, 500
    #print time.time()
    #play_for(sine_array(12, 8192), 500) #440, 4096, 500
    #play_for(second_harmonic(440), 500)
    #play_for(brass(440), 500)
    return tstamp
if __name__ == '__main__': main()

