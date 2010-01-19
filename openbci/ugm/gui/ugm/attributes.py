UGM_attributes_def = {
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
				'depend_from':'position_vertical_type'},
			'color':{'value':'string'},
			'stimulus_type':{'value':['rectangle', 'image', 'text']},
			'image_path':{'value':'string'},
			'message':{'value':'string'},
			'font_family':{'value':'string'},
			'font_color':{'value':'string'},
			'font_size':{'value':'int'}
			}
UGM_attributes_for_elem = {
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
