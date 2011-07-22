classdef SmartTagEndTagDefinition < SmartTagDefinition
    %SmartTafEndTagDefinition Definition of tags, which are ended with
    %certain type of tag.
    %     The class is to be used for following requirement:
    %     'We want to extract bunches of samples starting from some particular
    %     tag type and ending with some particular tag type.'
    %     It is a constructor parameter for SmartTagsManager.
    %     Constructor`s parameters and (at the same time) public slots:
    %     - start_tag_name - string
    %     - start_offset - float (default 0)
    %     - end_offset - float (default 0)
    %     - end_tags_names - list of strings.
    % 
    %     x = SmartTagEndTagDefinition(
    %                                   end_tags_names={'ugm_config', 'ugm_break'}
    %                                   start_tag_name='ugm_config', 
    %                                   start_offset=-10.0,
    %                                   end_offset=20.0,
    %                              )
    % 
    %     Consider samples file f, and tag scattered on the timeline like that:
    %     ---100ms------------------300ms-----------400ms---------500ms----------700ms
    %     ugm_config             ugm_config       ugm_break  ugm_config
    % 
    %     Using x definition means:
    %     Generate following samples bunches:
    %     - 90ms;320ms
    %     - 290ms;420ms
    
    properties
        end_tag_names
    end
    
    methods
        function self=SmartTagEndTagDefinition(end_tag_names,varargin)            
            self=self@SmartTagDefinition(varargin{:});
            self.end_tag_names=end_tag_names;
        end
        function smart_tags=get_smart_tags(self,p_read_manager)
            q={};
            head=1;
            smart_tags={};
            for tag=p_read_manager.get_tags()
                if ~isempty(find(ismember(self.end_tag_names,tag.name),1))
                    while head<=numel(q)
                        q{head}.set_end_tag(tag);
                        smart_tags{end+1}=q{head};
                        head=head+1;
                    end
                end
                if strcmp(self.start_tag_name,tag.name)
                    st=SmartTagEndTag(self,tag);
                    if ~isempty(find(ismember(self.end_tag_names,'self'),1))
                        st.set_end_tag(tag)
                        smart_tags{end+1}=st;
                    else
                        q{end+1}=st;
                    end
                end
            end
            smart_tags=[smart_tags{:}];
            for st=smart_tags
                st.initialize(p_read_manager)
            end
        end        
    end
    
end

