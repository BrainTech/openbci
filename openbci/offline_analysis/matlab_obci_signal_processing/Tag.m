classdef Tag
    %TAG Value class represents one Tag    
    
    properties
        length='0'
        name=''
        position
        channelNumber
        start_timestamp
        end_timestamp
        children=struct()
    end
    
    methods
        function self=Tag(xmltag)
            %Tag(xmltag = []) - Creates Tag from xmlElement.
            %   children of this Element are in the preprety children, as a
            %   struct of tagname, and values
            if nargin<1                
                return
            end
            self.name=char(xmltag.getAttribute('name'));
            self.length=char(xmltag.getAttribute('length'));
            self.position=char(xmltag.getAttribute('position'));
            try
                self.channelNumber=str2double(xmltag.getAttribute('channelNumber'));
            catch
                self.channelNumber=xmltag.getAttribute('channelNumber');
            end
            self.start_timestamp=str2double(self.position);
            self.end_timestamp=self.start_timestamp+str2double(self.length);            
            child=xmltag.getFirstChild;
            self.children=struct();
            while ~isempty(child) && child.getNodeType==child.ELEMENT_NODE
               try
                    self.children.(char(child.getTagName))=char(child.getFirstChild.getData);
               end
               child=child.getNextSibling;
            end
        end
        function tag=get_xml_element(self,docNode)            
            tag=docNode.createElement('tag');
            tag.setAttribute('name',num2str(self.name));
            tag.setAttribute('length',num2str(self.length));
            tag.setAttribute('channelNumber',num2str(self.channelNumber));
            tag.setAttribute('position',num2str(self.position));
            fn=fieldnames(self.children);
            for i=1:length(fn)
                field=fn{i};
                child=docNode.createElement(field);
                child.appendChild(docNode.createTextNode(num2str(self.children.(field))));
                tag.appendChild(child);                
            end
        end
        function obj=change_position(self,p_offset)
            self.start_timestamp=self.start_timestamp-p_offset;
            self.end_timestamp=self.start_timestamp+str2double(self.length);
            self.position=num2str(self.start_timestamp);
            obj=self;
        end
        function res=eq(self,tag)
            res=strcmp(self.name,tag.name) && self.start_timestamp==tag.start_timetamp;
        end
    end
    methods (Static)
        function filter=make_filter_function(p_tag_type,p_from,p_len,p_func)
            if nargin<4; p_func=@(x) true;end
            if nargin<3; p_len=inf;end
            if nargin<2; p_from=0;end
            if nargin<1; p_tag_type=[];end
            if p_from>=0                            
                p_func=@(t) t.start_timestamp>p_from &&  p_func(t);
                if p_len~=inf
                    end_time=p_from+p_len;
                    p_func=@(t) t.start_timestamp<=end_time && p_func(t);
                end
            end
            if ~isempty(p_tag_type)
                p_func=@(t) strcmp(t.name,p_tag_type) && p_func(t);
            end
            filter=p_func;
        end
    end
end

