# Configuraton for testing frequencies one by one - part I of 
# the calibration process

CONFIG = {}
CONFIG['screens'] = [
        ['kali/kali1', 'kali/kali1', 'kali/kali1', 'kali/kali1', 'kali/kali1', 'kali/kali1',  'kali/kali1', 'kali/kali1']
]
# 'concentrating_on_field', counted 'naturally', from 1
CONFIG['square_numbers'] = [
        [1,2,3,4,5,6,7,8]
        ]
CONFIG['readable_names'] = {
        'kali/kali1' : 'plansza kalibracyjna'
        }

# [square1, 2, 3, 4,
#        5, 6, 7, 8]
CONFIG['freqs'] = [
    [
        [12, 15, 17, 10, 11, 13, 16, 14],
        [12, 15, 17, 10, 11, 13, 16, 14],
        [12, 15, 17, 10, 11, 13, 16, 14], 
        [12, 15, 17, 10, 11, 13, 16, 14],
        [12, 15, 17, 10, 11, 13, 16, 14],
        [12, 15, 17, 10, 11, 13, 16, 14],
        [12, 15, 17, 10, 11, 13, 16, 14],
        [12, 15, 17, 10, 11, 13, 16, 14]
    ]
]
CONFIG['delay'] = 2
CONFIG['repeats'] = 1


CONFIG['make_breaks'] = True
CONFIG['break_len'] = CONFIG['delay']
CONFIG['break_freqs'] = [70, 70, 70, 70, 70, 70, 70, 70]

# set this to True and set DEFAULT_FREQS to use one frequencies set for all
# screens. Then you can omit defining CONFIG['freqs']
CONFIG['USE_DEFAULT_FREQS'] = False
