"""Basic rules to prioritize and organize study time."""

from datetime import date
from math import ceil


def days_remaining(assessment, today=None):
    if today is None:
        today = date.today()
    return (date.fromisoformat(assessment.due_date) - today).days


def calculate_priority(assessment, today=None):
    days = days_remaining(assessment, today)
    if days <= 0:
        urgency = 100
    elif days <= 2:
        urgency = 80
    elif days <= 5:
        urgency = 60
    elif days <= 10:
        urgency = 30
    else:
        urgency = 10
    priority = urgency * 0.6 + assessment.weight * 0.3 + (100 - assessment.progress) * 0.1
    return priority

def remaining_minutes(assessment):
    #Calculate remaining time by rounding up
    remaining_minutes = assessment.estimated_minutes * (100 - assessment.progress) / 100
    return ceil(remaining_minutes)


def explain(assessment, today=None):
    days = days_remaining(assessment, today)
    if days < 0:
        deadline = f"Submission date was {abs(days)} day(s) ago."
    elif days == 0:
        deadline = "Submission date is today."
    else:
        deadline = f"Submission date is in {days} day(s)."
    return (f"{deadline}, it is worth {assessment.weight}% of your final mark. "
            f"Your current progress is {assessment.progress}%.")


def recommend_session(assessments, available_minutes, today=None):
    #Recommends different (assessment,time) options
    if type(available_minutes) is not int or available_minutes <= 0:
        raise ValueError("Available time must be an integer > 0.")
    if today is None:
        today = date.today()
    eligible = [a for a in assessments
                if a.status not in ("blocked", "done") and a.progress < 100]

    #Sort assessments by priority, highest first.
    def get_priority(assessment):
        return calculate_priority(assessment, today)
    
    eligible.sort(key=get_priority, reverse=True)
    plan = []
    for assessment in eligible:
        minutes = min(remaining_minutes(assessment), available_minutes)
        plan.append((assessment, minutes))
        available_minutes -= minutes
        if available_minutes == 0:
            break
    return plan

