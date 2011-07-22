classdef SmartTagsManager < handle
    %SMARTTAGSMANAGER Creates SmartTags from given SmartTagDefinitions
    
    
    properties        
    end
    properties (SetAccess=private, GetAccess=private)
        read_manager
        smart_tags
    end
    methods
        function self=SmartTagsManager(p_tag_def,p_info_file,p_data_file,p_tags_file,p_read_manager)
            %SMARTTAGSMANAGER(p_tag_def,p_info_file=[],p_data_file=[],p_tags_file=[],p_read_manager=[])
            %   p_tag_def - SmartTagDefinition or Array of
            %   SmartTagDefinitions
            %   if p_read_manager is [], files are used to create new
            %   ReadManager
            %   see help ReadManager.ReadManager
            if nargin<5; p_read_manager=[]; end
            if isempty(p_read_manager)
                self.read_manager=ReadManager(p_info_file,p_data_file,p_tags_file);
            else
                self.read_manager=p_read_manager;
            end
            self.init_smart_tags(p_tag_def)
        end
        function smart_tags=get_smart_tags(self)
            %GET_SMART_TAGS() - returns an array of SmartTags
            smart_tags=self.smart_tags;
        end
    end
    methods (Access=private)
        function init_smart_tags(self,p_tag_def)
            try
                tag=p_tag_def(1);
            catch
                p_tag_def={p_tag_def};
            end
            self.smart_tags=[];
            for tag_def=p_tag_def
                self.smart_tags=[self.smart_tags tag_def.get_smart_tags(self.read_manager)];
            end
        end
    end
end

