#!/usr/bin/python

class UgmConfigManager(object):
    def __init__(self):
        self._configs = dict()
    def get_config(self, p_id):
        return self._configs[p_id]
    def ugm_fields(self):
        l_fields = []
        h = 100
        w = 100
        d = {
            'id':1,
            'width_type':'absolute',
            'width':w, 
            'height_type':'absolute',
            'height':h,
            'position_horizontal_type':'absolute',
            'position_horizontal':0,
            'position_vertical_type':'absolute',
            'position_vertical':0,
            'color':'#d4d4d4'
            }
        self._configs[d['id']] = d
        stims = [
            {
                'id':11,
                'width_type':'absolute',
                'width':70, 
                'height_type':'absolute',
                'height':70, 
                'position_horizontal_type':'absolute',
                'position_horizontal':0,
                'position_vertical_type':'absolute',
                'position_vertical':0,
                'color':'#ffffff', 
                'stimulus_type':'rectangle'
             },
            {
                'id':12,
                'width_type':'absolute',
                'width':60, 
                'height_type':'absolute',
                'height':40, 
                'position_horizontal_type':'relative',
                'position_horizontal':3,
                'position_vertical_type':'relative',
                'position_vertical':3, 
               'color':'#000000', 
                'stimulus_type':'rectangle'
             }
            ]
        d['stimuluses'] = stims
        for i_stim in stims:
            self._configs[i_stim['id']] = i_stim
        l_fields.append(d)

        d = {
            'id':2,
            'width_type':'absolute',
            'width':w, 
            'height_type':'absolute',
            'height':h,
            'position_horizontal_type':'absolute',
            'position_horizontal':0,
            'position_vertical_type':'absolute',
            'position_vertical':100,
            'color':'#eee4d4'
            }
        self._configs[d['id']] = d
        stims = [
            {
                'id':21,
                'width_type':'absolute',
                'width':60, 
                'height_type':'absolute',
                'height':40, 
                'position_horizontal_type':'aligned',
                'position_horizontal':'right',
                'position_vertical_type':'aligned',
                'position_vertical':'center',
                'color':'#ffffff', 
                'stimulus_type':'rectangle'
                },
            {
                'id':22,
                'width_type':'relative',
                'width':2, 
                'height_type':'relative',
                'height':2, 
                'position_horizontal_type':'aligned',
                'position_horizontal':'center',
                'position_vertical_type':'aligned',
                'position_vertical':'bottom',
                'color':'#000000', 
                'stimulus_type':'rectangle'
                }

            ]
        d['stimuluses'] = stims
        for i_stim in stims:
            self._configs[i_stim['id']] = i_stim

        l_fields.append(d)
        d = {
            'id':3,
            'width_type':'relative',
            'width':3, 
            'height_type':'relative',
            'height':3,
            'position_horizontal_type':'absolute',
            'position_horizontal':100,
            'position_vertical_type':'absolute',
            'position_vertical':100,
            'color':'#eeefff'
            }
        self._configs[d['id']] = d
        stims = [
            {
                'id':31,
                'width_type':'absolute',
                'width':60, 
                'height_type':'absolute',
                'height':40, 
                'position_horizontal_type':'aligned',
                'position_horizontal':'right',
                'position_vertical_type':'aligned',
                'position_vertical':'center',
                'color':'#ffffff', 
                'stimulus_type':'rectangle'
                },
            {
                'id':32,
                'width_type':'relative',
                'width':2, 
                'height_type':'relative',
                'height':2, 
                'position_horizontal_type':'aligned',
                'position_horizontal':'center',
                'position_vertical_type':'aligned',
                'position_vertical':'center',
                'color':'#000000', 
                'stimulus_type':'rectangle'
                }

            ]

        d['stimuluses'] = stims
        for i_stim in stims:
            self._configs[i_stim['id']] = i_stim

        l_fields.append(d)
        return l_fields


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
            self.width = p_parent.width / p_config_dict['width']
        else:
            raise UgmUnknownConfigValue('width_type',
                                        p_config_dict)

        #set height
        if p_config_dict['height_type'] == 'absolute':
            self.height = p_config_dict['height']
        elif p_config_dict['height_type'] == 'relative':
            self.height = p_parent.width / p_config_dict['height']
        else:
            raise UgmUnknownConfigValue('height_type',
                                        p_config_dict)
        
        #set horizontal position
        if p_config_dict['position_horizontal_type'] == 'absolute':
            self.position_x = p_config_dict['position_horizontal']
        elif p_config_dict['position_horizontal_type'] == 'relative':
            self.position_x = p_parent.width / p_config_dict['position_horizontal']
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
            self.position_y = p_parent.height / p_config_dict['position_vertical']
        elif p_config_dict['position_vertical_type'] == 'aligned': #TODO - alligned? aligned?
            if p_config_dict['position_vertical'] == 'top':
                self.position_y = 0
            elif p_config_dict['position_vertical'] == 'bottom':
                self.position_y = p_parent.width - self.height
            elif p_config_dict['position_vertical'] == 'center':
                self.position_y = p_parent.height/2 - self.height/2
            else:
                raise UgmUnknownConfigValue('position_vertical',
                                            p_config_dict)
        else:
            raise UgmUnknownConfigValue('position_vertical_type',
                                        p_config_dict)
            
            
        #set color
        self.color = p_config_dict['color']

