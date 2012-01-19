classdef TagsSource < handle
    %TagsSource Object which can read and write tags from file
    %   It is used by ReadManager and SmarTags
    %   are returned in a form of array of objects of class Tag
    
    properties
        file_name=[];        
    end
    properties (SetAccess=private,GetAccess=private)
        iter_pos=0;
        iter_filter;
        dom
        tags
    end   
    methods    
        function self=TagsSource(p_file_name)
            self.tags=[];
            if nargin==1
                self.file_name=p_file_name;
                self.dom=xmlread(p_file_name);
                self.read_tags();          
            end
        end
                
        function tags=get_tags(self,p_tag_type,p_from,p_len,p_func)
            %GET_TAGS(p_tag_type=[], p_from=[], p_len=[], p_func=@(x)true)
            % get_tags('name') get tags with given name
            % get_tags([],10) get tags which position is greater then 10
            % get_tags([], 10,20) get_tags which position is between 10 and
            % 20
            % get_tags([],[],[],@(t) t.start_timestamp==5) get tags for
            % which function returns true   
            % get_tags() - no filtering is done
            if nargin==1; tags=self.tags; return; end;
            if nargin<5; p_func=@(x) true;end
            if nargin<4; p_len=inf;end
            if nargin<3; p_from=0;end
            if nargin<2; p_tag_type=[];end
            filter = Tag.make_filter_function(p_tag_type,p_from,p_len,p_func);            
            tags=self.tags(arrayfun(filter,self.tags));
        end
        function iter_tags(self,p_tag_type,p_from,p_len,p_func)
            %ITER_TAGS(p_tag_type,p_from,p_len,p_func) - sets filter for
            % tags similar to get_tags. Used for lazy iterator.
            if nargin==1; return; end;
            if nargin<5; p_func=@(x) true;end
            if nargin<4; p_len=-1;end
            if nargin<3; p_from=-1;end
            if nargin<2; p_tag_type=-1;end
            self.iter_filter=Tag.make_filter_function(p_tag_type,p_from,p_len,p_func);
            
        end
        function set_tags(self,p_tags,p_first_ts)
            %SET_TAGS(p_tags,p_first_ts=0.0)  sets tags for this object
            %p_tags = array of objects of class Tag
            %p_first_ts = value which is subtracted from each tags position            
            if isempty(p_tags)
                self.tags=[];
                return
            end
            default('p_first_ts',0.0)
            tags(1,length(p_tags))=Tag();            
            for i=1:length(p_tags)
                tags(i)=p_tags(i).change_position(p_first_ts);
            end
            self.tags=tags;
        end
        function tag=next_tag(self)
            %NEXT_TAG() get next tag using filter set by iter_tags()
            st=size(self.tags);
            while self.iter_pos<st(2)
                self.iter_pos=self.iter_pos+1;
                tag=self.tags(self.iter_pos);
                if self.iter_filter(tag)
                    return
                end
            end
            tag=[];
        end
        function save_to_file(self,p_file_name)
            %SAVE_TO_FILE save tags to p_file_name
            docNode=com.mathworks.xml.XMLUtils.createDocument('tagFile');
            docRootNode=docNode.getDocumentElement;
            docRootNode.setAttribute('formatVersion','1.0');
            docRootNode.appendChild(self.get_default_tags(docNode));
            tagData=docNode.createElement('tagData');
            docRootNode.appendChild(tagData);
            tags=docNode.createElement('tags');
            for tag=self.tags
                tags.appendChild(tag.get_xml_element(docNode));
            end
            tagData.appendChild(tags);
            xmlwrite(p_file_name,docNode);            
        end        
    end
    methods (Access=private)
        function read_tags(self)
            %READ_TAGS oidfsdoijf idsojf 
            %   sdkflmsdlkf msdlk;m f
            ttags=self.dom.getElementsByTagName('tag');
            tgs(1,ttags.getLength)=Tag();
            for i=0:ttags.getLength-1
                tgs(i+1)=Tag(ttags.item(i));
            end
            self.tags=tgs;
        end
        function paging=get_default_tags(self,docNode)
            paging=docNode.createElement('paging');
            paging.setAttribute('page_size','20.0');
            paging.setAttribute('blocks_per_page','5');            
        end
    end
end
