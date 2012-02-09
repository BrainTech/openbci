from Rovio import Rovio;
import time;
from threading import Timer;
from Util import Queue;
from Util import Task;


one = Rovio('192.168.0.40','one', 'rovio1', 'rovio1');

taskQ = Queue();

task1 = Task(one.forward3,1);
task2 = Task(one.forward3,1);
taskQ.push(Task(one.turn,0));
taskQ.push(task1);
taskQ.push(Task(one.turn,0));
taskQ.push(task2);
# main loop keeps tracka og the queue and executing tasks
while True:
    # get the next task
    currentTask = taskQ.peek();
    time.sleep(.25);
    # if there's no task
    if(currentTask == None):
           time.sleep(.25); # sleep for 1/4 second
    else:
        print "NEXT TASK: " + currentTask.toString();

        # if the task has a positive duration, 
        if(currentTask.duration > 0):
            # start a timer that will pop that task after <duration> seconds
            t = Timer(currentTask.duration, taskQ.pop);
            t.start();
        
        # if the task has a non-positive duration
        if(currentTask.duration == 0):
            # perform the task, and pop it out of the queue
            currentTask.actfn();
            taskQ.pop();

        else: # positive duration
            # as along as this task is on top of the queue, 
            while(taskQ.peek() == currentTask):
                print "NT: " + currentTask.toString() + " " + "\n Peek: " + taskQ.peek().toString();
                # keep doing it
                currentTask.actfn();
            # this loop will end when the timer has popped the task off the queue