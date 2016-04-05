classdef SmartTagDurationDefinition < SmartTagDefinition
    %SmartTagDurationDefinition Get Smart tags with given duration
    %     The class is to be used for following requirement:
    %     'We want to extract bunches of samples starting from some particular
    %     tag type and lasting x miliseconds.
    %     It is a constructor parameter for SmartTagsManager.
    %     Constructor`s parameters and (at the same time) public slots:
    %     - start_tag_name - string
    %     - start_offset - float (default 0)
    %     - end_offset - float (default 0)
    %     - duration - float
    %
    %     x = SmartTagDuration(    duration=100.0
    %                              start_tag_name='ugm_config', 
    %                              start_offset=-10.0,
    %                              end_offset=20.0,
    %                              )
    % 
    %     Consider samples file f, and tag scattered on the timeline like that:
    %     ---100ms------------------300ms-----------400ms---------500ms-------------
    %     ugm_config             ugm_config       ugm_break  ugm_config
    % 
    %     Using x definition means:
    %     Generate following samples bunches:
    %     - 90ms;220ms
    %     - 290ms;420ms
    %     - 490ms;620ms

    properties
        duration
    end
    
    methods
        function self=SmartTagDurationDefinition(duration,varargin)
            self=self@SmartTagDefinition(varargin{:});
            self.duration=duration;
        end
         function smart_tags=get_smart_tags(self,read_manager)
            tags=read_manager.get_tags(self.start_tag_name);
            if isempty(tags)
                smart_tags=[];
                return
            end
            smart_tags(1,length(tags))=SmartTagDuration();
            for i=1:length(tags)
                smart_tags(i)=SmartTagDuration(self,tags(i));
                smart_tags(i).initialize(read_manager)
            end
         end
    end
    
end

