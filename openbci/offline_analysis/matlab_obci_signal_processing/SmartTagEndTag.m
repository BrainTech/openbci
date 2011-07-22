classdef SmartTagEndTag < SmartTag
    %SmartTagEndTag created by SmartTagEndTagDefinition
    % see help SmartTagEndTagDefinition    
    
    properties %(SetAccess=protected,GetAccess=protected)
        end_tag
    end
    
    methods
        function self=SmartTagEndTag(p_tag_def,p_start_tag)
            self=self@SmartTag(p_tag_def,p_start_tag);
        end
        function set_end_tag(self,p_end_tag)
            self.end_tag=p_end_tag;
        end
        function end_ts=get_end_timestamp(self)
            end_ts=self.tag_def.end_param_func(self.end_tag)+self.tag_def.end_offset;
        end
        function end_tag=get_end_tag(self)
            end_tag=self.end_tag;
        end
    end
    
end

