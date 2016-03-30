class Queue:
    q = [];
    def __init__(self):
        self.q = [];

    def length(self):
        return len(self.q);
    
    def push(self,item):
        self.q.append(item);
        
    def pop(self):
        topop = self.q.pop();
        print "Pop! " + topop.toString();
#        return self.q.pop();
        return topop;
        
    def peek(self):
#        print "len is: ", len(self.q);
        if(len(self.q) > 0):
            return self.q[len(self.q)-1];
        else:
            return None;
        
    def toString(self):
        retval = "<";
        for i in self.q:
            print i.toString();
            reval = retval + " " + i.toString();
        return retval;
    
# Function/Duration Pair    
class Task:
    actfn = None;
    duration = 0;
    
    def __init__(self, actfn, duration):
        self.actfn = actfn;
        self.duration = duration;
        
    def toString(self):
        return "<" + self.actfn.__name__ + ", " + str(self.duration) + ">";
    
     
