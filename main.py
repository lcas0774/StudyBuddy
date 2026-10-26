"""Run this file to start Study Buddy."""

from datetime import date

from models import Assessment, Course, CancelOperation, ASSESSMENT_TYPES, STATUSES, STATUS_LABELS
from planner import recommend_session, calculate_priority, explain
from storage import DATA_FILE, load_data, save_data

def ask_input(prompt):
        value = input(prompt).strip()
        if value.lower() == "cancel":
            raise CancelOperation()
        return value

def ask_text(prompt):
    while True:
        value = ask_input(prompt).strip()
        if value:
            return value
        print("Input cannot be empty.")

def ask_integer(prompt, minimum=0, maximum=None):
    while True:
        try:
            value = int(ask_input(prompt))
            if value < minimum or (maximum is not None and value > maximum):
                raise ValueError
            return value
        except ValueError:
            if maximum is not None:
                print(f"Enter an integer between {minimum} and {maximum}.")
            else:
                print(f"Enter an integer >= {minimum}.")

def ask_date():
    while True:
        value = ask_input("Submission date (YYYY-MM-DD): ").strip()
        try:
            if date.fromisoformat(value).isoformat() == value:
                return value
        except ValueError:
            pass
        print("Please enter a valid date using the format YYYY-MM-DD.")

def choose_option(options, labels=None):
    for number, option in enumerate(options, start=1):
        print(f"{number}. {labels[option] if labels is not None else option}")
    selection = ask_integer("Choose an option: ", 1, len(options))
    return options[selection - 1]

def add_course(courses):
    code = ask_text("Course code: ").upper()
    if any(course.code == code for course in courses):
        print("This course already exists.")
        return False
    if code == '0':
        return False
    while len(code) != 8:
        print("Course code must be 8 characters long.")
        code = ask_text("Course code: ").upper()
    else:
        name = ask_text("Course name: ")
        if name == '0':
            return False
        while len(name) < 4:
            print("A valid name must contain at least 4 characters.")
            name = ask_text("Course name: ")
        courses.append(Course(code, name))
    return True

def add_assessment(courses, assessments):
    if not courses:
        print("Add a course first.")
        return False
    else:
        print("\nSelect course:")
    course_code = choose_option([course.code for course in courses],
                                {course.code: f"{course.code} — {course.name}" for course in courses})
    name = ask_text("Evaluation name: ")
    print("Type of evaluation: ")
    assessment_type = choose_option(ASSESSMENT_TYPES)
    due_date = ask_date()
    weight = ask_integer("Final grade weight (%): ", 0, 100)
    minutes = ask_integer("Total time estimated (minutes): ", 1)
    progress = ask_integer("Current progress (%): ", 0, 100)
    print("Current status: ")
    status = choose_option(STATUSES, STATUS_LABELS)
    next_id = max((a.id for a in assessments), default=0) + 1
    assessments.append(Assessment(next_id, course_code, name, assessment_type,
                                  due_date, weight, minutes, progress, status))
    return True

def show_assessments(assessments):
    if not assessments:
        print("There are no assessments saved.")
    for assessment in assessments:
        print(f"\n[{assessment.id}], {assessment.name}, ({assessment.course_code}) — {assessment.type}")
        print(f"  Submission date: {assessment.due_date} | Weight: {assessment.weight}%")
        print(f"  Progress: {assessment.progress}% | Status: {STATUS_LABELS[assessment.status]}")
        print(f"  Total estimated time: {assessment.estimated_minutes} minutes")

def show_courses(courses):
    if not courses:
        print("There are no courses saved.")
    for course in courses:
        print(f"\n{course.code} - {course.name}")

def update_assessment(assessments):
    if not assessments:
        print("There are no assessments to update.")
        return False
    show_assessments(assessments)
    assessment_id = ask_integer("Evaluation ID (0 to cancel): ", 0)

    if assessment_id == 0:
        print("Update cancelled.") 
        return False
    selected_assessment = None
    
    for assessment in assessments:
        if assessment.id == assessment_id:
            selected_assessment = assessment
            break
   
    if selected_assessment is None:
        print("Assessment ID does not exist.")
        return False
    progress = ask_integer("New progress total (%): ", 0, 100)
    status = choose_option(STATUSES, STATUS_LABELS)
    selected_assessment.update_progress(progress, status)
    print(f"Result: {assessment.progress}% - {STATUS_LABELS[assessment.status]}.")
    return True

def show_recommendation(assessments):
    if not assessments:
        print("Add an assessment first.")
        return
    available = ask_integer("How much time do you have? (in minutes)", 1)
    plan = recommend_session(assessments, available)
    if not plan:
        print("No available assessments: all completed or blocked.")
        return
    print("\nYour study session:")
    for number, (assessment, minutes) in enumerate(plan, start=1):
        print(f"{number}. {assessment.name} ({assessment.course_code}) — {minutes} minutes")
        print(f"   {explain(assessment)}")
        print(f"   Priority score: {calculate_priority(assessment):.1f}/100")
    used_minutes = 0
    for assessment, minutes in plan:
        used_minutes += minutes
    unused = available - used_minutes
    if unused:
        print(f"{unused} minutes were not allocated to any assessment.")
    print("When you are done, select option 6 to register progress.")

def delete_item(courses, assessments):
    print("\n1. Delete a course")
    print("2. Delete an assessment")
    print("0. Cancel")

    option = ask_integer("Choose an option: ", 0, 2)

    if option == 0:
        return False

    if option == 1:
        if not courses:
            print("There are no courses to delete.")
            return False

        for course in courses:
            print(f"{course.code} - {course.name}")

        code = ask_text("Course code to delete: ").upper()
        selected_course = None
        for course in courses:
            if course.code == code:
                selected_course = course
                break
        if selected_course is None:
            print("Course code does not exist.")
            return False
        print("This will also delete all assessments for this course.")
        confirmation = ask_text("Confirm deletion? (yes/no): ").lower()
        if confirmation != "yes":
            print("Deletion cancelled.")
            return False

        # delete assessments from the course
        assessments_to_delete = []

        for assessment in assessments:
            if assessment.course_code == code:
                assessments_to_delete.append(assessment)

        for assessment in assessments_to_delete:
            assessments.remove(assessment)

        courses.remove(selected_course)
        print("Course and its assessments deleted.")
        return True

    elif option == 2:
        if not assessments:
            print("There are no assessments to delete.")
            return False
        show_assessments(assessments)
        assessment_id = ask_integer("Assessment ID (0 to cancel): ", 0)
        if assessment_id == 0:
            return False
        selected_assessment = None
        for assessment in assessments:
            if assessment.id == assessment_id:
                selected_assessment = assessment
                break
        if selected_assessment is None:
            print("Assessment ID does not exist.")
            return False
        confirmation = ask_text("Confirm deletion? (yes/no): ").lower()
        if confirmation != "yes":
            print("Deletion cancelled.")
            return False
        assessments.remove(selected_assessment)
        print("Assessment deleted.")
        return True

def main():
    print("Welcome to Study Buddy!")
    try:
        courses, assessments = load_data()
    except (OSError, ValueError) as error:
        print(f"Data could not be loaded: {error}")
        print("Check the file before starting again. It was not overwritten.")
        return
    print(f"Data file: {DATA_FILE}")
    while True:
        try:
            print("\nWhat do you want to do?"
                  "\n1. Add course\n2. Add assessment\n3. View assessments"
                        "\n4. View courses \n5.Start a study session\n6. Update progress or status"
                        "\n7. Delete course or assessment\n0. Exit"
                        "\nEnter CANCEL at any point to cancel an operation.")
            option = ask_integer("\nChoose an option: ", 0, 7)
            changed = False
            if option == 0:
                try:
                    save_data(courses, assessments)
                except OSError as error:
                    print(f"Could not save data: {error}. "
                        "Your changes are still available, but will be lost if you close the program before saving.")
                    continue
                print("Changes saved.")
                break
            elif option == 1:
                changed = add_course(courses)
            elif option == 2:
                changed = add_assessment(courses, assessments)
            elif option == 3:
                show_assessments(assessments)
            elif option == 4:
                show_courses(courses)
            elif option == 5:
                show_recommendation(assessments)
            elif option == 6:
                changed = update_assessment(assessments)
            elif option == 7:
                changed = delete_item(courses, assessments)
            if changed:
                try:
                    save_data(courses, assessments)
                    print("Changes saved.")
                except OSError as error:
                    print(f"Could not save data: {error}. "
                        "Choose 0 to retry saving and exit.")
        except CancelOperation:
            print("Operation cancelled. Returning to the main menu.")
            continue

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram interrupted. Previously saved changes have been preserved.")
