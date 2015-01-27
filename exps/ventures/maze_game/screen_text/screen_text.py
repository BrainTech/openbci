# -*- coding: utf-8 -*-
#!/usr/bin/env python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#     Anna Chabuda <anna.chabuda@gmail.com>
#


def get_start_session_text(training_number, session_type, session_condition):
    if session_type == 'experiment':
        return u"\n\n\nWitamy! Trening na dzisiaj jest gotowy! \n\n\nNumer dzisiejszego treningu: {}\nIlość treningów do końca: {}\n\n\n\n\n\n<aby przejść dalej naciśnij spację>".format(training_number, 10-training_number)
    else:
        return  u"\n\n\nWitamy! \nAby rozpocząć sesję treningową naciśnij spację."

def get_win_level_text(session_type, session_condition):
    if session_condition == 'motor':
        return u"\n\n\nGratulacje!\nPoszło ci bardzo dobrze. \nPrzechodzisz na wyższy poziom trudności!\n\n"
    else:
        return u"\n\nGratulacje!\nPoszło ci bardzo dobrze. \nPrzechodzisz na wyższy poziom trudności!\n\nPamiętaj! Staraj się najpierw zaplanować trasę, a następnie rozpocząć wykonywanie ruchów.\n\n" 

def get_finish_session_text(training_number, session_type, session_condition):
    if session_type == 'experiment':
        if training_number != 10:
            return u"\n\n\nTwój trening na dzisiaj dobiegł końca. Przypominamy o jutrzejszym treningu!"
        else:
            return u"\n\n\nTwój trening na dobiegł końca. Dziękujemy za udział w eksperymencie."
    else:
        return u"\n\n\nKoniec sesji treningowej"

def get_repeat_level_text(repeat_number, session_type, session_condition):
    if session_condition != 'motor': 
        if 3-repeat_number == 1:
            return u"\n\n\nWpadłeś w dziurę! \nPozostała Ci jeszcze {} szansa. \nSpróbuj ponownie!".format(3-repeat_number)
        if 3-repeat_number in [2, 3]:
            return u"\n\n\nWpadłeś w dziurę! \nPozostały Ci jeszcze {} szansy. \nSpróbuj ponownie!".format(3-repeat_number)
        else:
            return u"\n\n\nWpadłeś 3 razy w czarną dziurę.\n Poćwicz jeszcze raz na niższym poziomie trudności. \n\nPamiętaj! Staraj się najpierw zaplanować trasę, a następnie rozpocząć wykonywanie ruchów."
    else:
        if 3-repeat_number == 1:
            return u"\n\n\nZboczyłeś ze ścieżki! \nPozostała Ci jeszcze {} szansa. \nSpróbuj ponownie!".format(3-repeat_number)
        if 3-repeat_number in [2, 3]:
            return u"\n\n\nZboczyłeś ze ścieżki! \nPozostały Ci jeszcze {} szansy. \nSpróbuj ponownie!".format(3-repeat_number)
        else:
            return u"\n\n\nNiestety zboczyłeś ze ścieżki 3 razy.\n Być może aktualny poziom jest dla ciebie jeszcze zbyt trudny. Spróbuj lepiej się skoncentrować i ponownie poćwiczyć na niższym poziomie trudności.\n\n"

def get_pause_text(session_type, session_condition):
    return u"\n\n\nCzas treningu został zatrzymany. \n\nNaciśnij:'p', aby powrócić do treningu."

def get_timeout_level(session_type, session_condition):
    return u"\n\n\nPrzekroczyłeś dwukrotny czas potrzebny do wykonania tego poziomu trudności. \nByć może zadanie jest dla ciebie jeszcze zbyt trudne. Spróbuj lepiej się skoncentrować i ponownie poćwiczyć na niższym poziomie trudności."

def get_instruction_1(session_type, session_condition):
    ret = u"\nMasz przed sobą trening składający się z labiryntów o wzrastającym poziomie trudności.\nPoruszasz się zieloną kulką, a celem jest dotarcie do zielonego krzyżyka.\n\nKulka za każdym razem wykonuje ruch 'wszystko, albo nic', co w praktyce oznacza, że zatrzymuje się dopiero, gdy napotka którąś ze ścian. Nie można zatem zatrzymać się na środku planszy."
    if session_condition in ['cognitive', 'key_motor']:
        ret += u"\n\nKulką kieruje się przy użyciu strzałek na klawiaturze."
    else:
        ret += u"\n\nKulką kieruje się poprzez wychylenie się w odpowiednią stronę i pozostanie w takiej pozycji przez kilka sekund. Należy wychylać się tak, aby wyświetlona strzałka stawała się coraz bardziej zielona."
    if session_condition != 'motor':
        ret = u"\n\n"
    ret = ret + u"\n<aby przejść dalej naciśnij spację>" 
    return ret

def get_instruction_2(session_type, session_condition):
    if not (session_condition in ['motor', 'key_motor']): 
        ret = u"\nNależy omijać czarne dziury, które są rozmieszczone na każdej planszy tak, aby utrudnić dowolne poruszanie się po labiryncie.\nUważaj, wpadając w dziurę tracisz jedną szansę.\nPo stracie trzech szans spadasz poziom niżej!\n\n"
    else:
        ret = u"\nNależy poruszać się wyłącznie po wyznaczonej ścieżce. Dla ułatwienia dwa najbliższe kroki będą zawsze podświetlone na ścieżce.\nUważaj, wykonując ruch zbaczający ze ściezki tracisz jedną szansę. Po stracie trzech szans spadasz poziom niżej!\n\n"


    ret += u"Staraj się przejść labirynt jak najszybciej.\nUważaj, przechodząc labirynt zbyt wolno, także spadasz poziom niżej!\n\n"

    if not (session_condition in ['motor', 'key_motor']):
        ret += u"Pamiętaj! Staraj się najpierw zaplanować trasę, a następnie rozpocząć wykonywanie ruchów.\n\n"
    else:
        ret += u'\n\n'
    return ret + u"<aby rozpocząć trening naciśnij spację>"
    
def get_exit_text(session_type, session_condition):
    return u"\n\n\nCzy na pewno chcesz zakończyć sesję?\n\njeżeli tak naciśnij: 't',\njeżeli chcesz powrócić do gry naciśnij: 'n'"







