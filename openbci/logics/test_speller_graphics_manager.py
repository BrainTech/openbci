"""
>>> import logic_speller_engine as l

>>> m = l.SpellerGraphicsManager()

>>> s = ['a', 'b', 'c', 'd']

>>> x = m.pack(s)

>>> print(x)
 | a :: | b :: | c :: | d 

>>> y = m.unpack(x)

>>> print(y)
[['', 'a'], ['', 'b'], ['', 'c'], ['', 'd']]
""" 
if __name__ == '__main__':
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")
