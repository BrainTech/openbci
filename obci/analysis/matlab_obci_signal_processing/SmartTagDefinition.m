classdef SmartTagDefinition
    %SmartTagDefinition is used to create SmartTags, with given parameters  
    
    properties
        start_tag_name
        start_offset=0.0
        end_offset=0.0
        start_param_func=@(t) t.start_timestamp
        end_param_func=@(t) t.start_timestamp
    end
    
    methods
        function self=SmartTagDefinition(start_tag_name,start_offset,end_offset,start_param_func,end_param_func)
            %SMARTTAGDEFINITION(start_tag_name,start_offset=9,
            % end_offset=0,start_param_func=@(t) t.start_timestamp,
            % end_param_func=@(t) t.start_timestamp)
            %   start_tag_name - tag_name from which smart tag will start
            %   start_offset - value added to first_tag.start_time, data is
            %   taken from extended range
            %   end_offset - same as start_offset but with the end
            %   start_param_Func - function used for getting tags
            %   start_time
            %   end_param_func - function used for getting end_timestamp
            
            default('end_param_func',@eval,'@(t) t.start_timestamp')
            default('start_param_func',@eval,'@(t) t.start_timestamp')
            default('end_offset',0.0)
            default('start_offset',0.0)            
            self.start_tag_name=start_tag_name;
            self.start_offset=start_offset;
            self.end_offset=end_offset;
            self.start_param_func=start_param_func;
            self.end_param_func=end_param_func;            
        end
        function ans=is_type(self,p_type)
            ans=0;
        end
        function smart_tags=get_smart_tags(self,p_read_manager)
            smart_tags=[];       
        end
    end
    
end

