classdef SmartTagDuration < SmartTag
    %SmartTagDuration created by SmartTagDurationDefinition
    % see help SmartTagDurationDefinition
    
    properties
    end
    
    methods
        function self=SmartTagDuration(varargin)
            self=self@SmartTag(varargin{:});            
        end
        function end_ts=get_end_timestamp(self)
            end_ts=self.tag_def.start_param_func(self.start_tag)+self.tag_def.duration+self.tag_def.end_offset;
        end
    end
    
end

