#!/usr/bin/python
import copy
class UgmAttributesManager(object):
    def __init__(self):
        self.attributes_def = {
            'id':{'value':'int'},
            'width_type':{'value':['absolute', 'relative']},
            'width':{'value':'int'},
            'height_type':{'value':['absolute', 'relative']},
            'height':{'value':'int'},
            'position_horizontal_type':{
                'value':['absolute', 'relative', 'aligned']},
            'position_horizontal':{
                'value':['int',['left','center','right'], 'int'],
                'depend_from':'position_horizontal_type'},
            'position_vertical_type':{
                'value':['absolute', 'relative', 'aligned']},
            'position_vertical':{
                'value':['int',['top','center','bottom'], 'int'],
                'depend_from':'position_horizontal_type'},
            'color':{'value':'string'},
            'stimulus_type':{'value':['rectangle', 'image', 'text']},
            'image_path':{'value':'string'},
            'message':{'value':'string'},
            'font_family':{'value':'string'},
            'font_color':{'value':'string'},
            'font_size':{'value':'int'}
            }
        self.attributes_for_elem = {
            'field':['id', 'width_type', 'width', 'height_type',
                     'height', 'position_horizontal_type',
                     'position_horizontal', 'position_vertical_type',
                     'position_vertical', 'color'],
            'rectangle':['id', 'width_type', 'width', 'height_type',
                         'height', 'position_horizontal_type',
                         'position_horizontal', 'position_vertical_type',
                         'position_vertical', 'color'],
            'image':['id', 'position_horizontal_type',
                     'position_horizontal', 'position_vertical_type',
                     'position_vertical', 'image_path'],
            'text':['id', 'position_horizontal_type',
                    'position_horizontal', 'position_vertical_type',
                    'position_vertical', 'message', 'font_family',
                    'font_size', 'font_color']
            }

class UgmConfigManager(object):
    def __init__(self, p_config_file='ugm_config'):
        self._config_file = p_config_file
        self._attributes_manager = UgmAttributesManager()
        self.update_from_file()
    # ----------------------------------------------------------------------
    # CONFIG FILE MANAGMENT ------------------------------------------------
    def update_from_file(self, p_config_file=None):
        if p_config_file == None: l_config_file = self._config_file
        else: l_config_file = p_config_file
        l_config_module = __import__(l_config_file)
        reload(l_config_module) # To be sure that the file is reloaded
        self.set_full_config(l_config_module.fields)
    def update_to_file(self, p_config_file=None):
        if p_config_file == None: l_config_file = self._config_file
        else: l_config_file = p_config_file
        f = open(l_config_file+'.py', 'w') #TODO -try except
        f.write(''.join(["fields = ", repr(self._fields)]))
        f.close()
    # CONFIG FILE MANAGMENT ------------------------------------------------
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # PUBLIC GETTERS -------------------------------------------------------
    def get_config_for(self, p_id):
        return copy.deepcopy(self._configs(p_id))
    def get_full_config(self):
        #TODO - implement
        pass
#        return copy.deepcopy(self._configs)

    def get_ugm_fields(self):
        """Return a list of dictionaries representing configuration
        of every UgmField.
        Notice, that we don`t return in-memory list, but we return 
        a deep copy, as gui might want to alter config while processing."""
        return copy.deepcopy(self._fields)
    def get_attributes_config(self):
        return {'attributes_def':
                    self._attributes_manager.attributes_def,
                'attributes_for_elem':
                    self._attributes_manager.attributes_for_elem
                }
    # PUBLIC GETTERS -------------------------------------------------------
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # PUBLIC SETTERS -------------------------------------------------------
    def _configs(self, p_id):
        return self._get_recursive_config(self._fields, p_id)
    def _get_recursive_config(self, p_fields, p_id):
        for i in p_fields:
            if i['id'] == p_id:
                return i
            j = self._get_recursive_config(i['stimuluses'], p_id)
            if j != None:
                return j
        return None
    def set_full_config(self, p_config_fields):
        #self._configs = dict()
        self._fields = p_config_fields
#        self._set_recursive_config(self._fields)

#    def _set_recursive_config(self, p_elems):
#        for i_field in p_elems:
#            #self._configs[i_field['id']] = i_field
#            self._set_recursive_config(i_field['stimuluses'])

    def set_config(self, p_elem_config):
        # Don`create a new entry, use existing one so 
        # that corresponding element in self._fields is also updated
        l_elem = self._configs(p_elem_config['id'])
        l_elem.clear()
        for i_key, i_value in p_elem_config.iteritems():
            l_elem[i_key] = i_value

    def set_config_for(self, p_elem_id, p_attr_id, p_attr_value):
        self._configs(p_elem_id)[p_attr_id] = p_attr_value
        # Notice - corresponding element in self._fields is also updated

    # PUBLIC SETTERS -------------------------------------------------------
    # ----------------------------------------------------------------------

class UgmUnknownConfigValue(Exception):
    def __init__(self, p_key, p_config_dict):
        self._key = p_key
        self._config_dict = p_config_dict
    def __str__(self):
        return ''.join(["Unrecognised config value: ",
                        self._config_dict[self._key],
                        " for key: ",
                        self._key,
                        " from config:\n",
                        str(self._config_dict)])


class UgmRectConfig(object):
    def _set_rect_config(self, p_parent, p_config_dict):
        #set width
        if p_config_dict['width_type'] == 'absolute':
            self.width = p_config_dict['width']
        elif p_config_dict['width_type'] == 'relative':
            self.width = p_parent.width * p_config_dict['width']
        else:
            raise UgmUnknownConfigValue('width_type',
                                        p_config_dict)

        #set height
        if p_config_dict['height_type'] == 'absolute':
            self.height = p_config_dict['height']
        elif p_config_dict['height_type'] == 'relative':
            self.height = p_parent.height * p_config_dict['height']
        else:
            raise UgmUnknownConfigValue('height_type',
                                        p_config_dict)
        
        #set horizontal position
        if p_config_dict['position_horizontal_type'] == 'absolute':
            self.position_x = p_config_dict['position_horizontal']
        elif p_config_dict['position_horizontal_type'] == 'relative':
            self.position_x = p_parent.width * p_config_dict['position_horizontal']
        elif p_config_dict['position_horizontal_type'] == 'aligned': #TODO - alligned? aligned?
            if p_config_dict['position_horizontal'] == 'left':
                self.position_x = 0
            elif p_config_dict['position_horizontal'] == 'right':
                self.position_x = p_parent.width - self.width
            elif p_config_dict['position_horizontal'] == 'center':
                self.position_x = p_parent.width/2 - self.width/2
            else:
                raise UgmUnknownConfigValue('position_horizontal',
                                            p_config_dict)
        else:
            raise UgmUnknownConfigValue('position_horizontal_type',
                                        p_config_dict)

       #set vertical position
        if p_config_dict['position_vertical_type'] == 'absolute':
            self.position_y = p_config_dict['position_vertical']
        elif p_config_dict['position_vertical_type'] == 'relative':
            self.position_y = p_parent.height * p_config_dict['position_vertical']
        elif p_config_dict['position_vertical_type'] == 'aligned': #TODO - alligned? aligned?
            if p_config_dict['position_vertical'] == 'top':
                self.position_y = 0
            elif p_config_dict['position_vertical'] == 'bottom':
                self.position_y = p_parent.height - self.height
            elif p_config_dict['position_vertical'] == 'center':
                self.position_y = p_parent.height/2 - self.height/2
            else:
                raise UgmUnknownConfigValue('position_vertical',
                                            p_config_dict)
        else:
            raise UgmUnknownConfigValue('position_vertical_type',
                                        p_config_dict)
            
            
        #set color #TODO ????
        try:
            self.color = p_config_dict['color']
        except:
            pass

