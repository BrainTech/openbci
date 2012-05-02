classdef InfoSource < handle
    %INFOSOURCE Class for reading and writing data params
    %   Detailed explanation goes here
    
    properties
        file_name        
    end
    properties (SetAccess=private, GetAccess=private)
        params
        dom
        tag_definitions=struct('channels_names',{'channelLabels', 'label'} ,...
			'channels_numbers',{'channelNumbers', 'number'} ,...
			'channels_gains',{'calibrationGain', 'calibrationParam'} ,...
			'channels_offsets',{'calibrationOffset', 'calibrationParam'} ,...
			'number_of_samples',{'sampleCount',[]} ,...
			'number_of_channels',{'channelCount',[]} ,...
			'sampling_frequency',{'samplingFrequency',[]} ,...
			'first_sample_timestamp',{'firstSampleTimestamp',[]} ,...
			'file',{'sourceFileName',[]} ,...
			'file_format',{'sourceFileFormat', 'rawSignalInfo'} ,...
			'calibration',{'calibration',[]} ,...
			'sample_type',{'sampleType',[]} ,...
			'byte_order',{'byteOrder',[]} ,...
			'page_size',{'pageSize',[]} ,...
			'blocks_per_page',{'blocksPerPage',[]} ,...
			'export_file_name',{'exportFileName',[]} ,...
			'export_date',{'exportDate',[]});
    end
    methods
        function self=InfoSource(p_file_name)
            %InfoSource(p_filename=[]) Reads params from xml p_filename
            self.params=struct();
            if nargin==1
                self.file_name=p_file_name;
                self.dom=xmlread(p_file_name);
                self.params=self.get_dom_params();
            end
        end
        function params=get_params(self)
            %GET_PARAMS returns struct where each field name is param name,
            %   and field value is param value- string or array of string
            params=self.params;
        end
        
        function param=get_param(self,p_param_name)
            %GET_PARAM(p_param_name) get single param with name
            %p_param_name. Raises an exception when there is no such param
            try
                param=self.params.(p_param_name);                
            catch
                throw(MException('SignalExceptions:NoParameter','There is no parameter like "%s"',p_param_name));
            end
        end
        function set_params(self,p_params)
           %SET_PARAMS(p_params) Replaces current params with params from
           %struct p_params. 
           %    Only params in p_params are replaced, the rest
           %    stays the same. Use reset_params() to clear all the params.
           %    Raises exception when param names are invalid.
           fn=fieldnames(p_params);
           for i=1:length(fn)
               self.set_param(fn{i},p_params.(fn{i}));
           end
        end
        function set_param(self,p_param_name,p_value)
            %SET_PARAM(p_param_name,p_value) Sets single param
            %   Raises exception when param name is invalid.
            try
                [~]=self.tag_definitions.(p_param_name);
            catch Ex
                throw(MException('SignalExceptions:NoParameter','There is no parameter like "%s"',p_param_name))
            end
            self.params.(p_param_name)=p_value;
        end
        function reset_params(self)
            %RESET_PARAMS clears all of the params
            self.params=struct();
        end
        function save_to_file(self,p_file_name)
            %SAVE_TO_FILE(p_file_name) - saves all the params to xml file
            docNode=com.mathworks.xml.XMLUtils.createDocument('rs:rawSignal');
            docRootNode=docNode.getDocumentElement;
            docRootNode.setAttribute('xmlns:rs','http://signalml.org/rawsignal');
            fn=fieldnames(self.params);
            for i=1:length(fn)
                field=fn{i};
                [name,subname]=self.get_param_names(field);
                child=docNode.createElement(name);
                if isempty(subname)                    
                    child.appendChild(docNode.createTextNode(num2str(self.params.(field))));
                else
                    elems=self.params.(field);
                    for elem=elems
                        subchild=docNode.createElement(subname);
                        subchild.appendChild(docNode.createTextNode(elem)   );
                        child.appendChild(subchild);
                    end                    
                end
                docRootNode.appendChild(child);
            end
            xmlwrite(p_file_name,docNode);
        end
    end
    methods (Static, Access=private)
        function param=get_param_name(p_param)
            param=strcat('rs:',p_param);
        end
    end
    methods (Access=private)
        function params=get_param_list(self,p_name,p_subname)
            try
                list=self.dom.getElementsByTagName(p_name).item(0).getElementsByTagName(p_subname);
                params=cell(1,list.getLength);
                for i=0:list.getLength-1
                    try
                        params(i+1)={char(list.item(i).getFirstChild.getData)};
                    catch Ex
                        params(i+1)={''};
                    end
                end                    
            catch ex
                params=[];
            end
        end
        
        function [name,subname]=get_param_names(self,p_name)
            subname=[];
            name=self.get_param_name(p_name);
            try
               names={self.tag_definitions.(p_name)};
               name=self.get_param_name(names{1});
               if ischar(names{2})
                    subname=self.get_param_name(names{2});
               end               
            catch ex
            end
        end
        
        function param=get_dom_param(self,p_param_name)
            [name,subname]=self.get_param_names(p_param_name);
            param=[];
            if ischar(subname)
                param=self.get_param_list(name,subname);
                return
            end
            try
                child=self.dom.getElementsByTagName(name).item(0).getFirstChild;
                try
                    t_param=char(child.getData);
                catch
                    t_param='';
                end
                param=str2num(t_param);
                if isnan(param)
                    param=t_param;
                end                    
            catch ex
                throw(MException('SignalExceptions:NoParameter','There is no parameter like "%s"',name))                
            end
        end
        function params=get_dom_params(self)
            params=struct();
            fn=fieldnames(self.tag_definitions);
            for i=1:length(fn)
                try
                    params.(fn{i})=self.get_dom_param(fn{i});
                catch ex
                end
            end
        end

    end
end

