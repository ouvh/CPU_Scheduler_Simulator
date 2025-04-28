the project consist of simulating the work of a scheduler


project structure:


a web app which is a dashboard   ||||  backend to communicate between the web app ad the scheduler  |||| the actual scheduler


task:
-- create the model class which will represent the process( the process will have a run function that will ecexture one instruction it should include also blocking IO instruction) 
process id,arrival time burst time(number of instruction with the proportion of I\O) and of course priorities,
for course higher number means higher priorities

--create a class responsible of managing processes and saving them into file and reading the file
it is responsible of managing processes and creating them. it acts like the process table  

-- create the  scheduling algorithm

-- wrap all this inside a scheduler class   



now for the frontend :


-- the user can create processes with all the parameter. {use the feature to include a random generator}
-- enable the user to simulate the start of the machine and choose the scheduling algorithm and run the scheduling algorithm.

after that visualize all metrics (for each process and the average for all processes).

since the system is dynamic , we must figure out a way to visualize those metrics online dynamically


ok now for the metrics:
general metrics:
-- number of ready start processes 
-- number of blocked processes
-- number of ready state processes.
-- running time of the cpu
-- the current running process
 in case priorites algorithm:
 display a like a table with processes in a queue that is updated


specific metrics:
running time
turnaround time
waiting time ( for this , we will inplement like a timestamp algorithm to track times accurately)

another things the scheduler should simulate also the arrival time for the process.


at the end save a report of the execution of the scheduler

the platform should a good UI and animations for good description.




