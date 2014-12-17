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
    return u"Witamy! Trening na dzisiaj jest gotowy! \n Odbyłeś {}/10 treningów. \n Do końca pozostało {} treningów.".format(training_number, 10-training_number)

def get_win_level_text():
    return u"Gratulacje!\nTwoje wyniki jak dotąd były bardzo dobre. \nPrzechodzisz na kolejny poziom!"

def get_finish_sesion_text(training_number):
    if training_number != 10:
        return u"Twój trening na dzisiaj dobiegł końca, przypominamy o jutrzejszym treningu!"
    else:
        return u"Twój trening na dobiegł końca, dziękujemy za udział w eksperymencie"

def get_repeat_level_text(repeat_number):
    if repeat_number < 3:
        return u"Wpadłeś w dziurę! \nMasz jeszcze {}/3 szans. \nSpróbuj ponownie!".format(3-repeat_number)
    else:
        return u"Wpadłeś 3 razy w czarną dziurę.\n Poćwicz jeszcze raz na niższym poziomie trudności."

def get_pause_text():
    return u"Czas treningu został zatrzymany. \n\nNaciśnij:'p', aby powrócić do treningu."

def get_timeout_level():
    return u"Przekroczyłeś dwukrotny czas potrzebny do wykonania tego poziomu trudności. \nByć może zadanie jest dla ciebie jeszcze zbyt trudne. Spróbuj lepiej się skoncentrować i ponownie poćwiczyć na niższym poziomie trudności."

def get_instruction():
    return u"Instrukcja"

def get_exit_text():
    return u"Czy na pewno chcesz zakończyć sesję?\n\njeżeli tak naciśnij: 't',\njeżeli chcesz powrócić do gry naciśnij: 'n'"







