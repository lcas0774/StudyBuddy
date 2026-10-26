"""Classes used during the program process"""

from datetime import date


ASSESSMENT_TYPES = ("assignment", "quiz", "test", "presentation", "exam")
STATUSES = ("not_started", "in_progress", "blocked", "done")
STATUS_LABELS = {
    "not_started": "Not started",
    "in_progress": "In progress",
    "blocked": "Blocked",
    "done": "Completed",
}



class Course:
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.validate_course()
    
    def validate_course(self):
        if self.code.strip() == "":
            raise ValueError("Course code cannot be empty.")
        if self.name.strip() == "":
            raise ValueError("Course name cannot be empty.")
        self.code = self.code.strip().upper()
        self.name = self.name.strip()



class Assessment:
    def __init__(self, id:int, course_code:str, name, type, due_date:str, weight:int, estimated_minutes, progress=0, status="not_started"):
        self.id = id
        self.course_code = course_code
        self.name = name
        self.type = type
        self.due_date = due_date # Formatted YYYY-MM-DD, for easier storage
        self.weight = weight
        self.estimated_minutes = estimated_minutes
        self.progress = progress
        self.status = status
        self.validate_assessment()

    def validate_assessment(self):
        if type(self.id) is not int or self.id < 1:
            raise ValueError("ID has to be a positive integer.")
        if self.course_code.strip() == "":
            raise ValueError("Course code is missing.")
        if self.name.strip() == "":
            raise ValueError("Name cannot be empty.")
        self.course_code = self.course_code.strip().upper()
        self.name = self.name.strip()
        
        if self.type not in ASSESSMENT_TYPES:
            raise ValueError("Invalid assessment type. " 
                             "Assessment types: assignment, quiz, test, presentation, exam")
        if not isinstance(self.due_date, str):
            raise ValueError("Wrong date format." 
                             "Please use YYYY-MM-DD format.")
        parsed_date = date.fromisoformat(self.due_date)
        if parsed_date.isoformat() != self.due_date:
            raise ValueError("Please use YYYY-MM-DD format.")
        if type(self.weight) is not int or not 0 <= self.weight <= 100:
            raise ValueError("Grade weight must be an integer between 0 - 100.")
        if type(self.estimated_minutes) is not int or self.estimated_minutes <= 0:
            raise ValueError("Estimated time must be an integer > 0")
        
        self.update_progress(self.progress, self.status)

    def update_progress(self, progress, status):
        #Keeps progress and status coherent.
        if type(progress) is not int or not 0 <= progress <= 100:
            raise ValueError("Progress must be between 0 - 100.")
        if status not in STATUSES:
            raise ValueError("Invalid status."
                             "Select status: Not started, In progress, Blocked, Completed")
        if status == "done" or progress == 100:
            progress, status = 100, "done"
        elif status != "blocked":
            status = "in_progress" if progress > 0 else "not_started"
        self.progress = progress
        self.status = status

class CancelOperation(Exception):
    pass
    