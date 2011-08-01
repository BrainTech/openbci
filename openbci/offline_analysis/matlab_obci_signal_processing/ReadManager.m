classdef ReadManager < handle
    %READMANAGER Class for reading and writing channel data, tags and data
    %params
    properties
        info_source
        data_source
        tags_source        
    end
    methods
        function self=ReadManager(p_info_source,p_data_source,p_tags_source)
            %READMANAGER(p_info_source,p_data_source,p_tags_source=[])
            %   p_info_source - file_name or InfoSource
            %   p_data_source - file_name or DataSource
            %   p_tags_source - optional,file_name or TagsSource
            if ~isa(p_info_source,'InfoSource')
                p_info_source=InfoSource(p_info_source);            
            end
            self.info_source=p_info_source;
            if ~isa(p_data_source,'DataSource')
                p_data_source=FileDataSource(p_data_source,self.info_source.get_param('number_of_channels'));
            end
            self.data_source=p_data_source;
            if nargin==3 && ~isempty(p_tags_source)
                if ~isa(p_tags_source,'TagsSource')
                    p_tags_source=TagsSource(p_tags_source);
                end
                self.tags_source = p_tags_source;
            else
                self.tags_source=TagsSource();
            end
        end
        function param=get_param(self,p_param_name)
            %GET_PARAM get one param. see help InfoSource.get_param
            param=self.info_source.get_param(p_param_name);
        end

        function set_param(self,p_param_name, p_param_value)
            %SET_PARAM set one param. see help InfoSource.set_param
            self.info_source.set_param(p_param_name, p_param_value);
        end

        function start_ts=get_start_timestamp(self)
            %GET_START_TIMESTAMP gets start timestamp of this stream
            start_ts=0;
        end
        function params=get_params(self)
            %GET_PARAMS get all params. see help InfoSource.get_params
            params=self.info_source.get_params();
        end         
        function set_params(self,p_params)
            %SET_PARAMS(p_params) 
            %   p_params= struct
            %   Set params. see help InfoSource.set_params
            self.info_source.set_params(p_params)
        end
        function samples=get_samples(self,p_from,p_len)
            %GET_SAMPLES(p_from,p_len) get samples. 
            %   see help DataSource.get_samples
            %   when invoked without arguments, all samples are cached in
            %   memory, so it is faster in the future.
            if nargin==1
                samples=self.data_source.get_samples();
                if ~isa(self.data_source,'MemoryDataSource')
                    self.data_source=MemoryDataSource(samples);
                end
            end
            if nargin<3; p_len=inf; end
            if nargin<2; p_from=0; end                 
            samples=self.data_source.get_samples(p_from,p_len);
        end
        
        function iter_samples(self,p_from,p_len)
            %ITER_SAMPLES iter through samples
            %   see help DataSource.iter_samples
            if nargin<3; p_len=inf; end
            if nargin<2; p_from=0; end            
            self.data_source.iter_samples(p_from,p_len)          
        end
        function samples=next_samples(self)
            %NEXT_SAMPLES iter through samples
            %   see help DataSource.next_samples
            samples=self.data_source.next_samples();
        end
        function set_samples(self,p_samples,p_channel_names)
            %SET_SAMPLES(p_samples,p_channel_names)
            %   p_samples - matrix(num_channels,num_samples)
            %   p_channel_names - array of strings of length of
            %   num_channels
            %Usage:
            % set_samples([1,2,3;4,5,6],{'A','B'})
            s=size(p_samples);
            if s(1)>0 && (~exist('p_channel_names','var')||length(p_channel_names)~=s(1))
                throw(MException('ReadManager:WrongChannelNames','Wrong number of channel names'));
            end
            self.data_source=MemoryDataSource();
            self.data_source.set_samples(p_samples);
            self.info_source.set_param('channels_names',p_channel_names);
            self.info_source.set_param('number_of_channels',length(p_channel_names));
            self.info_source.set_param('number_of_samples',s(2))  ;          
        end
        function ch_samples=get_channel_samples(self,p_ch_name,p_from,p_len)
            %GET_CHANNEL_SAMPLES(p_ch_name, p_from=[],p_len=inf) - gets all
            %samples fron given channel
            %   p_ch_name - channel index or channel name as string
            %   p_from - from which sample to start
            %   p_len - how many samples
            if nargin<4; p_len=inf; end
            if nargin<3; p_from=0; end            
            samples=self.get_samples(p_from,p_len);
            if isinteger(p_ch_name)
                ch_ind=p_ch_name;
            else
                ch_ind=find(ismember(self.get_param('channels_names'),p_ch_name)==1);
            end
            ch_samples=samples(ch_ind,:);
        end
        function tags=get_tags(self,p_tag_type,p_from,p_len,p_func)
            %GET_TAGS(p_tag_type,p_from,p_len,p_func) get filtered tags.
            %   see help TagsSource.get_tags
           if nargin<5; p_func=@(x) true;end
            if nargin<4; p_len=inf;end
            if nargin<3; p_from=0;end
            if nargin<2; p_tag_type=[];end
            tags = self.tags_source.get_tags(p_tag_type,p_from,p_len,p_func);
        end
        
        function iter_tags(self,p_tag_type,p_from,p_len,p_func)
            %ITER_TAGS(p_tag_type,p_from,p_len,p_func) get filtered tags.
            %   see help TagsSource.iter_tags
            if nargin<4; p_func=@(x) true;end
            if nargin<3; p_len=inf;end
            if nargin<2; p_from=0;end
            if nargin<1; p_tag_type=[];end
            self.tags_source.iter_tags(p_tag_type,p_from,p_len,p_func);
        end
        function tag=next_tag(self)
            %NEXT_TAG() get filtered tags.
            %   see help TagsSource.next_tag
            tag=self.tags_source.next_tag();
        end
        function set_tags(self,p_tags,p_first_ts)
            %SET_TAGS(p_tags,p_first_timestamp) set tags.
            %   see help TagsSource.set_tags
            default('p_first_ts',0)
            self.tags_source.set_tags(p_tags,p_first_ts)
        end
        function save_to_file(self,p_dir,p_name)
            %SAVE_TO_FILE(p_dir,p_name) save date from this ReadManager to
            %   files 
            %   p_dir - directory path
            %   p_name - prefix for file names .obci.dat, .obci.info,
            %   .obci.tags
            
            if ~isa(self.data_source,'MemoryDataSource')
                [~]=self.get_samples();
            end
            path=[p_dir '/' p_name];
            self.data_source.save_to_file([path '.obci.dat']);
            self.info_source.save_to_file([path '.obci.info']);
            self.tags_source.save_to_file([path '.obci.tags']);            
        end
    end
end
