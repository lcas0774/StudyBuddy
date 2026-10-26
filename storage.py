"""Uploads and stores courses and assessments in a JSON file."""

import json
import pathlib
from models import Assessment, Course


# stores data alongside this python file
DATA_FILE = pathlib.Path(__file__).resolve().parent / "data.json"


def load_data(path=DATA_FILE):
    path = pathlib.Path(path)
    if not path.exists():
        return [], []
    try:
        with open(path, "r") as file:
            data = json.load(file)
        
        courses = []
        for item in data["courses"]:
            course = Course(
                code=item["code"],
                name=item["name"]
            )
            courses.append(course)

        assessments = []
        for item in data["assessments"]:
            assessment = Assessment(
                id=item["id"],
                course_code=item["course_code"],
                name=item["name"],
                type=item["type"],
                due_date=item["due_date"],
                weight=item["weight"],
                estimated_minutes=item["estimated_minutes"],
                progress=item["progress"],
                status=item["status"]
            )
            assessments.append(assessment)

        codes = []
        for course in courses:
            if course.code in codes:
                raise ValueError("Duplicate course code.")
            codes.append(course.code)

        ids = []
        for assessment in assessments:
            if assessment.id in ids:
                raise ValueError("Duplicate assessment ID.")
            ids.append(assessment.id)
            if assessment.course_code not in codes:
                raise ValueError("An assessment belongs to a non-existing course.")
        return courses, assessments
    except (ValueError, TypeError, KeyError) as error:
        raise ValueError(f"The file {path.name} contains invalid data: {error}")


def save_data(courses, assessments, path=DATA_FILE):
    path = pathlib.Path(path)
    
    courses_data = []
    for course in courses:
        course_data = {
            "code": course.code,
            "name": course.name
        }
        courses_data.append(course_data)


    assessments_data = []
    for assessment in assessments:
        assessment_data = {
            "id": assessment.id,
            "course_code": assessment.course_code,
            "name": assessment.name,
            "type": assessment.type,
            "due_date": assessment.due_date,
            "weight": assessment.weight,
            "estimated_minutes": assessment.estimated_minutes,
            "progress": assessment.progress,
            "status": assessment.status
        }
        assessments_data.append(assessment_data)
    
    data = {
        "courses": courses_data,
        "assessments": assessments_data
    }
    with open(path, "w") as file:
        json.dump(data, file, indent=4)