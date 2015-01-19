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


def get_start_sesion_text(training_number):
    return u"\n\n\nWitamy! Trening na dzisiaj jest gotowy! \n Odbyłeś {}/10 treningów. \n Do końca pozostało {} treningów.".format(training_number, 10-training_number)

def get_win_level_text():
    return u"\n\n\nGratulacje!\nTwoje wyniki jak dotąd były bardzo dobre. \nPrzechodzisz na kolejny poziom!"

def get_finish_sesion_text(training_number):
    if training_number != 10:
        return u"\n\n\nTwój trening na dzisiaj dobiegł końca, przypominamy o jutrzejszym treningu!"
    else:
        return u"\n\n\nTwój trening na dobiegł końca, dziękujemy za udział w eksperymencie."

def get_repeat_level_text(repeat_number):
    if 3-repeat_number == 1:
        return u"\n\n\nWpadłeś w dziurę! \nPozostała Ci jeszcze {} szansa. \nSpróbuj ponownie!".format(3-repeat_number)
    if 3-repeat_number in [2, 3]:
        return u"\n\n\nWpadłeś w dziurę! \nPozostały Ci jeszcze {} szansy. \nSpróbuj ponownie!".format(3-repeat_number)
    else:
        return u"\n\n\nWpadłeś 3 razy w czarną dziurę.\n Poćwicz jeszcze raz na niższym poziomie trudności."

def get_pause_text():
    return u"\n\n\nCzas treningu został zatrzymany. \n\nNaciśnij:'p', aby powrócić do treningu."

def get_timeout_level():
    return u"\n\n\nPrzekroczyłeś dwukrotny czas potrzebny do wykonania tego poziomu trudności. \nByć może zadanie jest dla ciebie jeszcze zbyt trudne. Spróbuj lepiej się skoncentrować i ponownie poćwiczyć na niższym poziomie trudności."

def get_instruction_1():
    return u"Masz przed sobą trening składający się z labiryntów o wzrastającym poziomie trudności.\n\nPoruszasz się zieloną kulką, a celem jest dotarcie do zielonego krzyżyka.\nKulką kieruje się przy użyciu strzałek na klawiaturze.\n\n Należy omijać czarne dziury, które są rozmieszczone na każdej planszy tak, aby utrudnić dowolne poruszanie się po labiryncie.\n\nKulka za każdym razem wykonuje ruch 'wszystko, albo nic', co w praktyce oznacza, że zatrzymuje się dopiero, gdy napotka którąś ze ścian. Nie można zatem zatrzymać się na środku planszy.\n\n <aby przejść dalej naciśnij spację>" 


def get_instruction_2():
    return u"Twoim zadaniem jest takie przejście drogi, aby omijając wszystkie dziury dotrzeć do zielonego krzyżyka.\nUważaj, wpadając w dziurę tracisz jedną szansę.\n\nPo stracie trzech szans spadasz poziom niżej!\n\nStaraj się przejść labirynt jak najszybciej.\nUważaj, przechodząc labirynt zbyt wolno, także spadasz poziom niżej!\n\n<aby rozpocząć trening naciśnij spację>"

def get_exit_text():
    return u"\n\n\nCzy na pewno chcesz zakończyć sesję?\n\njeżeli tak naciśnij: 't',\njeżeli chcesz powrócić do gry naciśnij: 'n'"







