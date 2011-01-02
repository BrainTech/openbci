#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
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
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
import traceback
import classification_logging as logger
LOGGER = logger.get_logger("chain", "debug")

class ChainElement(object):
    """Represents an element for Chain object."""
    def __init__(self, class_template, params_sets):
        """Init object, parameters:
        - class_template - a class responding to .process(data) method
        - params_sets - a dictionary with keys contaning every
          class_template`s __init__ parameters and values representing
          alternative values for corresponding parameter, eg:
          for class:
          class A(object):
              def __init__(x,y):
                  ...
          where x is a number and y is a string, we would have:
          ChainElement(A, {'x':[1,2,3], 'y':['a', 'b']})

          For that ChainElement Chain object will create 6 A objects
          with every permutation of init parameters:
          A(1,'a'), A(1,'b'), A(2,'a'), A(2,'b'), A(3,'a'), A(3,'b')
          """
        self.class_template = class_template
        try:
            keys = params_sets.keys()
        except AttributeError:
            self.params = params_sets
        else:
            self.params = []
            self._init_params(params_sets, {}, keys)



    def _init_params(self, params_sets, init_set, keys):
        """Initialize self.params list.
        After that operation self.params should look like:
        [{'x':1, 'y':'a'}, {'x':1, 'y':'b'},..., {'x':3, 'y':'b'}]
        """
        if len(keys) == 0:
            self.params.append(init_set)
            return 

        for i_value in params_sets[keys[0]]:
            d = init_set.copy()
            d[keys[0]] = i_value
            self._init_params(params_sets, d, keys[1:])
        
class Chain(object):
    def __init__(self, *chain_elements):
        self.elements = chain_elements
        self.candidates = None
        self.results = None
        self.errors = []
        self.gather_errors = True

    def process(self, data_set=None, 
                select_winner=True, gather_errors=True):
        self.gather_errors = gather_errors
        self.candidates, self.results = self._process(data_set, 0)
        if select_winner:
            return self._select_winner(self.candidates, self.results)
        else:
            return None, None

    def _select_winner(self, candidates, results):
        best_result = max(results)
        ind = results.index(best_result)
        return candidates[ind], best_result

    def _process(self, data_set, element_index):
        try:
            current_element = self.elements[element_index]
        except IndexError:
            # data_set is a result of process method
            # of the last element in the chain
            return [[]], [data_set]
        ret_candidates = []
        ret_results = []
        for i_params_set in current_element.params:
            obj = current_element.class_template(**i_params_set)
            LOGGER.debug("Start processing with: "+str(obj.__class__)+"("+str(i_params_set)+")")
            if self.gather_errors:
                try:
                    new_data_set = obj.process(data_set)
                except Exception, e:
                    self.errors.append(traceback.format_exc())
                else:
                    candidates, results = self._process(new_data_set, element_index + 1)
                    for i_cand in candidates:
                    # prepend to every list of candidate a current object
                        i_cand.insert(0, obj)
                    ret_candidates += candidates
                    ret_results += results
            else: #dont gather errors
                new_data_set = obj.process(data_set)
                candidates, results = self._process(new_data_set, element_index + 1)
                for i_cand in candidates:
                    # prepend to every list of candidate a current object
                    i_cand.insert(0, obj)
                ret_candidates += candidates
                ret_results += results

                

        return ret_candidates, ret_results

    def print_errors(self):
        print("****************************************************")
        print("*************** Start printing errors **************")
        for er in self.errors:
            print("*********** NEXT ERROR *****************")
            for l in er.splitlines():
                print(l)
        print("*************** End printing errors ****************")
        print("****************************************************")

    def print_candidate(self, candidate):
        print("****************************************************")
        print("*************** Start printing candidate ***********")
        for cnd in candidate:
            c = eval(str(cnd))
            print("****** next candidate **********")
            print("CLASS: "+c['CLASS'])
            for k, v in c.iteritems():
                print(k, ": ", v)
        print("*************** End printing candidate**************")
        print("****************************************************")
        
        
            
