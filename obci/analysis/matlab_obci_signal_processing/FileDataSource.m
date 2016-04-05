classdef FileDataSource < DataSource
    %FileDataSource Reads data from give file    
    
    properties
        file_name        
    end
    properties (SetAccess=private,GetAccess=private)
        channel_count
        fileID
        sample_size=8;
        sample_type= 'double'
    end
    
    methods
         function self=FileDataSource(p_file_name,p_nr_channels,sample_type)
            default('sample_type','double')
            self.file_name=p_file_name;
            self.channel_count=p_nr_channels;
            [self.fileID,msg]=fopen(p_file_name,'r');
            if self.fileID<0
                throw(MException('SignalExceptions:FileOpenError',[msg ,':',p_file_name]));
            end
            self.sample_type=lower(sample_type);         
            if strcmp(self.sample_type, 'float')               
               self.sample_size=4;
            end
         end        
        function seek_samples(self,p_from)
            fseek(self.fileID,p_from*self.channel_count*self.sample_size,-1);
        end
        function samples=read_samples(self,p_len)            
            [samples,len]=fread(self.fileID,[self.channel_count,p_len],self.sample_type,0,'l');
            if p_len~=inf && len<p_len
                throw(MException('SignalExceptions:NoNextValue','Not enough samples!'))
            end
        end
        function delete(self)
            fclose(self.fileID);
        end        
    end
    
end

