classdef DataSource < handle
    %DATASOURCE Provides sample data
    %   retuns sample in matrix. Rows are channels, columns are samples
    
    properties        
    end
    properties (SetAccess=private, GetAccess=private)
        iter_pos
        iter_limit
    end
    methods
        function self=DataSource()
        end
        function samples=get_samples(self,p_from,p_len)
            %GET_SAMPLES(p_from=0,p_len=inf) retuns samples
            %   when p_len is inf, maximum number of samples is returned
            %   samples are returned in a
            %   matrix(nr_of_channels,nr_of_samples)
            %   Raises Exceptions when p_len is not inf and is to big
            default('p_len',inf);
            default('p_from',0);
            self.seek_samples(p_from);
            samples=self.read_samples(p_len);
        end        
        function iter_samples(self,p_from,p_len)
            %ITER_SAMPLES(p_from=0,p_len=inf)
            %   starts iterator for getting samples       
            
            default('p_from',0)
            default('p_len',inf)
            self.iter_limit=p_len;
            self.seek_samples(p_from);
        end
        function samples=next_samples(self)
            %NEXT_SAMPLES() - gets one column of samples, all channels
            % Raises exception in the end
            self.iter_pos=self.iter_pos+1;
            if self.iter_pos>self.iter_limit
                samples=[];
                throw(MException('SignalExceptions:NoNextValue','There is no next value in the iterator'))
            end
            samples=self.read_samples(1);
        end
        function save_to_file(self,p_file_name)
            %SAVE_TO_FILE(p_filename) - dumps all samples to the file            
            file_id=fopen(p_file_name,'w');
            fwrite(file_id,self.get_samples(),'double',0,'l');
            fclose(file_id);            
        end
        function seek_samples(self,p_from)            
        end
        function samples=read_samples(self,p_len)
            throw(MException('SignalExceptions:NoNextValue','There is no more samples'))
        end
    end    
end

