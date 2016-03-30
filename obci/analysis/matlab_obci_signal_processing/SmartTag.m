classdef SmartTag < ReadManager
    %SmartTag It is ReadManager with some context.
    %   It can by used to get some parts of the signal.
    
    properties
        start_tag
        tag_def
    end
    properties (SetAccess=protected)
        is_initialised
    end
    
    methods
        function self=SmartTag(p_tag_def,p_start_tag)
            %SmartTag(p_tag_def,p_start_tag)
            %   p_tag_def = SmartTagDefinition
            %   p_start_tag = starting tag of this SmartTag
            self=self@ReadManager(InfoSource(),MemoryDataSource(),TagsSource());
            self.is_initialised=false;
            if nargin==0
                return
            end
            self.start_tag=p_start_tag;
            self.tag_def=p_tag_def;          
        end
        function start_ts=get_start_timestamp(self)            
            start_ts=self.tag_def.start_param_func(self.start_tag)+self.tag_def.start_offset;
        end
        function end_ts=get_end_timestamp(self)            
            end_ts=self.get_start_timestamp();
        end
        function initialize(self,read_manager)
            %INITIALIZE - initializes itself with part of the data from read_manager
            %part is defined by this SmartTag
            start_ts=max(self.get_start_timestamp(),0);
            first_ts=read_manager.get_start_timestamp();
            sampling_freq=read_manager.get_param('sampling_frequency');
            samples_to_start=int32((start_ts-first_ts)*sampling_freq);
            end_ts=self.get_end_timestamp();
            samples_to_end=int32((end_ts-first_ts)*sampling_freq);            
            sample_count=read_manager.get_param('number_of_samples');
            samples_to_start=min(samples_to_start,sample_count);
            samples_to_end=min(samples_to_end,sample_count);            
            chan_names=read_manager.get_param('channels_names');
            self.info_source.set_params(read_manager.get_params());
            try
                first_sample_ts=read_manager.get_param('first_sample_timestamp');
                self.info_source.set_param('first_sample_timestamp',first_sample_ts+start_ts);
            end            
            samples=read_manager.get_samples(samples_to_start,samples_to_end-samples_to_start);
            self.set_samples(samples,chan_names);
            tags=read_manager.get_tags([],start_ts,(end_ts-start_ts));
            self.tags_source.set_tags(tags,0.0);            
            self.is_initialised=true;
        end
    end
    
end

