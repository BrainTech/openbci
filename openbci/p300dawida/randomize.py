import numpy as np

class SequenceCreater():
    def __init__(self,numOfRows, numOfCols, repeat):
        
        self.numOfRows = numOfRows
        self.numOfCols = numOfCols
        self.repeat = repeat
                
        self.createSequence()
        self.randomizeSequence()
        
        print self.sequence 
    
    def createSequence(self):
        "Creates sequence list"
        self.sequence = list()
        
        # Adds row* tuple(r,num) and col*tuple(c,num)
        # where r- is row, and c - is column
        for i in range(self.numOfRows):
            self.sequence.append( ("r", i) )
        for j in range(self.numOfCols):
            self.sequence.append( ("c", j) )
         
        # Repeats the same list 'repeat' times
        self.sequence = self.sequence*self.repeat
    
    def randomizeSequence(self):
        "Shuffles sequence"
        
        np.random.shuffle(self.sequence)
        for i in range(len(self.sequence)-1):
            
            # Check if any tuple is same as next one.
            # If not, shuffle list again.
            if self.sequence[i]==self.sequence[i+1]:
                self.randomizeSequence()
        

if __name__ == "__main__":
    
    numOfRows = 4
    numOfCols = 4
    repeat = 2
    
    SequenceCreater(numOfRows, numOfCols, repeat)