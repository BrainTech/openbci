# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

from Xlib import X, display, Xutil, XK
import Xlib
special_X_keysyms = {
    ' ' : "space",
    '\t' : "Tab",
    '\n' : "Return",  # for some reason this needs to be cr, not lf
    '\r' : "Return",
    '\e' : "Escape",
    '!' : "exclam",
    '#' : "numbersign",
    '%' : "percent",
    '$' : "dollar",
    '&' : "ampersand",
    '"' : "quotedbl",
    '\'' : "apostrophe",
    '(' : "parenleft",
    ')' : "parenright",
    '*' : "asterisk",
    '=' : "equal",
    '+' : "plus",
    ',' : "comma",
    '-' : "minus",
    '.' : "period",
    '/' : "slash",
    ':' : "colon",
    ';' : "semicolon",
    '<' : "less",
    '>' : "greater",
    '?' : "question",
    '@' : "at",
    '[' : "bracketleft",
    ']' : "bracketright",
    '\\' : "backslash",
    '^' : "asciicircum",
    '_' : "underscore",
    '`' : "grave",
    '{' : "braceleft",
    '|' : "bar",
    '}' : "braceright",
    '~' : "asciitilde"
    }

display = display.Display()
window = display.screen().root

def wait(p_keys_list):
    """Block the whole keyboard!!! And wait until some key from p_keys_list
    is pressed. By now p_keys_list is a list of strings, so use single
    ascii symbols.
    There is a way out of this hell - hit 'Escape'.
    The function returns hit button`s string representation
    Eg. for p_keys_list == ['1','2','3'] the function will hand untill
    1,2 or 3 key is preseed or Escape is pressed."""
    ds = display
    window.grab_keyboard(1, X.GrabModeAsync, X.GrabModeAsync, X.CurrentTime)
    while True:
        ev = ds.next_event()
        if ev.type == X.KeyPress:
            keysym = ds.keycode_to_keysym(ev._data['detail'], 0)
            keystr = XK.keysym_to_string(keysym)
            print("Got keysym/keystr: "+str(keysym)+ ' / '+str(keystr))
            if keystr in p_keys_list:
                ds.ungrab_keyboard(X.CurrentTime)
                ds.flush()
                return keystr
            elif str(keysym) in p_keys_list:
                ds.ungrab_keyboard(X.CurrentTime)
                ds.flush()
                return keysym
            elif keysym == 65307:
                ds.ungrab_keyboard(X.CurrentTime)
                ds.flush()
                return 'Escape'

def char_to_keysym(ch) :
    keysym = Xlib.XK.string_to_keysym(ch)
    if keysym == 0 :
        # Unfortunately, although this works to get the correct keysym
        # i.e. keysym for '#' is returned as "numbersign"
        # the subsequent display.keysym_to_keycode("numbersign") is 0.
        keysym = Xlib.XK.string_to_keysym(special_X_keysyms[ch])
    return keysym

def keysym_to_keycode(keysym):
    keycode = display.keysym_to_keycode(keysym)
    shift_mask = 0
    return keycode, shift_mask

def char_to_keycode(ch) :
    keysym = char_to_keysym(ch)
    keycode = display.keysym_to_keycode(keysym)
    if keycode == 0 :
        print "Sorry, can't map", ch

    if (is_shifted(ch)) :
        shift_mask = Xlib.X.ShiftMask
    else :
        shift_mask = 0

    return keycode, shift_mask


def is_shifted(ch) :
    if ch.isupper() :
        return True
    if "~!@#$%^&*()_+{}|:\"<>?".find(ch) >= 0 :
        return True
    return False


def send_string(str) :
    """I am not working. I dont know why:("""
    for ch in str :
        #print "sending", ch, "=", display.keysym_to_keycode(Xlib.XK.string_to_keysym(ch))
        keycode, shift_mask = char_to_keycode(ch)
        event = Xlib.protocol.event.KeyPress(
            time = int(time.time()),
            root = display.screen().root,
            window = window,
            same_screen = 0, child = Xlib.X.NONE,
            root_x = 0, root_y = 0, event_x = 0, event_y = 0,
            state = shift_mask,
            detail = keycode
            )
        window.send_event(event, propagate = True)
        event = Xlib.protocol.event.KeyRelease(
            time = int(time.time()),
            root = display.screen().root,
            window = window,
            same_screen = 0, child = Xlib.X.NONE,
            root_x = 0, root_y = 0, event_x = 0, event_y = 0,
            state = shift_mask,
            detail = keycode
            )
        window.send_event(event, propagate = True)


if __name__ == "__main__":
    import sys,time
    print(wait(sys.argv[1:]))
    #send_string("aBcd")
    #time.sleep(10)
    
    
