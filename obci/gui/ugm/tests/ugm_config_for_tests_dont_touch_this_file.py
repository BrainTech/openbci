#For tests purposes only! 

# DO NOT MODIFY THIS FILE as test_ugm_config_manager relies on it...


fields = [
    {
        'id':1,
        'width_type':'absolute',
        'width':100, 
        'height_type':'absolute',
        'height':100,
        'position_horizontal_type':'absolute',
        'position_horizontal':0,
        'position_vertical_type':'absolute',
        'position_vertical':0,
        'color':'#d4d4d4',
        'stimuluses':
            [
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
        }, # End of 1 field definition
    {
        'id':2,
        'width_type':'absolute',
        'width':100, 
        'height_type':'absolute',
        'height':100,
        'position_horizontal_type':'absolute',
        'position_horizontal':0,
        'position_vertical_type':'absolute',
        'position_vertical':100,
        'color':'#eee4d4',
        'stimuluses':
            [
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
        }, #End of 2 field config
    {
        'id':3,
        'width_type':'relative',
        'width':3, 
        'height_type':'relative',
        'height':3,
        'position_horizontal_type':'absolute',
        'position_horizontal':100,
        'position_vertical_type':'absolute',
        'position_vertical':100,
        'color':'#eeefff',
        'stimuluses':
            [
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
                'position_horizontal_type':'aligned',
                'position_horizontal':'center',
                'position_vertical_type':'aligned',
                'position_vertical':'center',
                'stimulus_type':'image',
                'image_path':'nie_juhu.png'
                },
            {
                'id':33,
                'width_type':'absolute',
                'width':160, 
                'height_type':'absolute',
                'height':40, 
                'position_horizontal_type':'aligned',
                'position_horizontal':'center',
                'position_vertical_type':'aligned',
                'position_vertical':'center',
                'color':'#ffffff', 
                'stimulus_type':'rectangle'
                },
            {
                'id':34,
                'position_horizontal_type':'aligned',
                'position_horizontal':'left',
                'position_vertical_type':'aligned',
                'position_vertical':'center',
                'stimulus_type':'text',
                'message':'NIEEE JUHU',
                'font_family':"Times",
                'font_size':20,
                'font_color':"#000000"
                }
            ]
        }, #End of 3 field config
    {
        'id':4,
        'width_type':'relative',
        'width':4, 
        'height_type':'relative',
        'height':4,
        'position_horizontal_type':'absolute',
        'position_horizontal':600,
        'position_vertical_type':'absolute',
        'position_vertical':300,
        'color':'#eeefff',
        'stimuluses':
            [
            {
                'id':41,
                'position_horizontal_type':'aligned',
                'position_horizontal':'center',
                'position_vertical_type':'aligned',
                'position_vertical':'center',
                'color':'#ffffff', 
                'stimulus_type':'image',
                'image_path':'juhu.png'
                }
            ]
        } #End of 4 field config
    ]

