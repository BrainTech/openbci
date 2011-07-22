classdef MemoryDataSource < DataSource
    %UNTITLED12 Summary of this class goes here
    %   Detailed explanation goes here
    
    properties (SetAccess=private,GetAccess=private)
        samples
        samp_pos=0
    end    
    methods
        function self=MemoryDataSource(p_samples)
            default('p_samples',[])
            self.set_samples(p_samples)
        end
        function set_samples(self,samples)
            self.samples=samples;
            self.samp_pos=0;
        end
        function seek_samples(self,p_from)
            self.samp_pos=max(p_from-1,0);
        end
        function samples=read_samples(self,p_len)
            if p_len==inf
                p_len=length(self.samples)-self.samp_posp;
            end
            to=self.samp_pos+p_len;
            if to>length(self.samples)
                throw(MException('SignalExceptions:NoNextValue','Not enough samples!'))
            else
                samples=self.samples(:,self.samp_pos+1:to);
            end
            self.samp_pos=to;                
        end
    end
    
end

