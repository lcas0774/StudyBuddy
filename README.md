```STUDY BUDDY```
Terminal conversational program that helps decide what to study depending on submission date, total grade weight, progression status and available time. 
Requires standard Python 3.9 or higher.

# Run

Open a terminal inside study_buddy folder and run:

```sh
python3 main.py
```

You need to add courses before adding assignments. 
Option 4 starts a study session. When you are done studying, record your progress and task status by choosing option 5. 
Data will be automatically saved on 'data.json', in the same study_buddy directory.
First run starts without data. No need to install extra special libraries or additional software. 

# Files included

1. `models.py`: Course y Assessment class design, parameters and validation checks.
2. `planner.py`: priority calculation and time organization.
3. `storage.py`: saving and recovering data. 
4. `main.py`: full program process. 

# Basic rules

- Priority calculation = urgency 60%, grade weight 30%, progress state 10%
- Urgency: 100 if deadline is today or already expired; 80 if its in 1-2 days; 60 in 3-5;
  30 in 5-10; 10 in >10.
- Total estimated time is expected in minutes and corresponds to expected time to complete the full task.
- Progress is expected as total current progress.
- Remaining time is estimated proporcionally to progress, and rounded up.
- Time is firstly assigned to the task with higher priority, and if theres a remainder, to the next one.
- A task can be partially worked on during a study session. It is not assumed as finished when the session ends.
- Completed and blocked tasks are not recommended. Expired pending tasks are.
- A completed task means 100% progress; stating 100% progress stablishes complete status.
- A blocked task becomes available by changing its status, a completed task can become re-opened by updating its progression percentage. 
- Recommending a task does not automatically change its status. 
- Cancel the process at any point by entering "CANCEL", process will not be saved. 
- Deleting a course will delete all its assessment. Deleting an assessment does not affect its course. 

Does not include task division or reminders. 
Assessment type is just descriptive. It does not affect calculations. 
Priority calculation could be modified in the code by the user to change weight of the factors, it can be found in `planner.py`.

