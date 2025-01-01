#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is pyGrade, a tool for semi-automated grading of Python programming assignments.
Author: Natalie Clarius <natalie.clarius@student.uni-tuebingen.de>

This tool provides a command-line interface to let you
- step through submissions
- visually inspect the student's code
- run unit tests (the unit tests themselves will have to be written by you)
- automatically assign points based on the test results
- manually adjust these points
- write comments
- automatically generate a pretty feedback summary in HTML format
- store the results in a Moodle-compatible format.
All you will have to do by hand outside of the tool is downloading and uploading the necessary files.

The script requires a particular set-up of the file structure and some generic background files in order to work.
If you would like to use the script for your own course, please contact me for the details.

The tool was originally designed for the course "Programming and Data Analysis for Linguists" (responsible: Johannes
Dellert), University of Tübingen, summer semester 2018.
It was written under limited time resources and contains many ugly pieces of code and fragile workarounds.
A cleaned up, more robust and thoroughly documented version 2.0 is in planning.
Until then, please feel free to e-mail me any bug reports and improvement suggestions you may have.

Workflow for each assignment:
-----------------------------

1. pull

2. set up the files
2.1. download submissions from Moodle and unzip into <exercise folder>/submissions_raw
2.2. download grading table from Moodle into <exercise folder>/results/results_moodle_raw.csv

3. check for plagiarism
3.1. run jplag (information on how to use in /scripts/jplag/readme.txt)
3.2. inspect
3.3. write results into <exercise folder>/results/plagiarism.txt

4. initialize the script
4.1. start this script, type in exercise number, wait for everything to be initlaized

5. grade the submissions
5.1. go to student (by next or by go to); verify everything is loaded correctly
5.2. inspect submission visually
5.3. if necessary, fix crucial mistakes and reload
5.4. run tests
5.5. possibly edit points
5.6. write comment!
5.7. rinse and repeat...

6. when done with all submissions:
6.1. make sure that everyone has been graded
6.1. run 'moodle' to generate the filled-in Moodle results table
6.2. upload the generated results_moodle.csv to Moodle (make sure to check the box that forces overwrite)

7. push!

Please note:
1. Before running the script, ALWAYS pull and after running the script, ALWAYS push the exercises folder.
Otherwise changes to the grading results are lost!
2. All changes to the reults are to be made locally (by editing the results.tsv or, better, via the grading script)
and kept in sync with Moodle by uploading a new version of the results_moodle.csv.
If you decide to make changes in the Moodle data online or in the results_moodle.csv,
please make sure that you also have these changes in the results.tsv.
"""

from helpers import *
from assignment import Assignment
import copy
from os.path import *

# debug mode
debug = True

# Loop variables
action = None
end_grading = False
idx = 0
graders = []
thresholds = []


def main():
    global end_grading

    # show greeting message
    greeting()

    # obtain exercise number from user
    ex_nr = ask_ex_nr() if not debug else str(10)

    # initialize grading session
    print("Initializing...\n")
    a = Assignment(ex_nr)

    # main loop
    while not end_grading:
        next_action()


def next_action():
    global a, s, backup, action, raw, idx, reload, end_grading

    match input("\nNext action (type 'h' for help): "):

        case "h" | "help":
            print_help()
    
        # accessing students
    
        case "n" | "next" | "next student":
            print("Going on to next student...")
            idx += 1
            a.next_student(idx)
    
        case "prev" | "previous":
            print("Going on to previous student...")
            idx -= 1
            a.next_student(idx)
    
        case "g" | "go to" | "go to student" | "raw":
            a.print_raw()
            a.goto_student()
    
        case "reload":
            print("Reloading current student...")
            reload = True
            # todo (low prio): don't ask to mark student as graded on reload
            a.next_student(idx)
    
        case "graded":
            a.print_graded()
            a.goto_student()
    
        case "pending", "ungraded":
            a.print_pending()
            a.goto_student()
    
        # Operations on students
    
        case "t" | "tests" | "run tests":
            print("Initializing tests...")
            a.run_tests()
    
        case "p" | "points" | "edit points":
            a.edit_points()
    
        case "c" | "comment":
            a.comment()
    
        case "f" | "feedback":
            print("Feedback for current student:\n"
                  "-----------------------------")
            a.print_feedback(a.feedback(), s)
    
        case "note":
            a.note()
    
        case "status" | "grading status":
            a.edit_grading_status()
    
        case "avg" | "average":
            print()
            print(average2str(a.average(), a.average_total(), a.students, a.tasks, a.tasks_total))
    
        case "stats" | "statistics":
            a.stats()
    
        # handling student data
    
        case "student":
            a.print_student()
    
        case "students":
            a.print_students()
    
        case "id":
            id = input("Enter the id: ")
            a.students[id].print_data()
            a.next_student(idx)
    
        case "update":
            # todo (low prio): does this work? no longer needed?
            a.update_student_data()
            print("Updated data for " + str(len(a.students)) + " students")
    
        case "backup":
            backup = copy.copy(s)
            print("Created backup for student object " + raw[idx-1])
    
        case "reset":
            if s is None:
                print("No current student")
                return
            s = copy.copy(backup)
            print("Resent student object for " + raw[idx-1] + " to backup")
    
        case "delete":
            if s is None or not a.verify_overwrite():
                return
            match input("This deletes all data of the current student object (" + str(s) + ") from local memory.\n"
                           "Files (such as the comment.md) will remain.\n"
                           "Are you sure you want to proceed? ('y'/'n') "):
                case "y" | "yes":
                    pass
                case _:
                    return
            del a.students[s.id]
            s = None
            print("Deleted student object for " + raw[idx-1])
    
        # data import and export
    
        # todo (low prio): update
        case "s" | "save" | "save results":
            a.verify_done()
            a.export_results(False)
    
        case "reimport" | "re-import":
            # if not verify_done():
            #     return
            print("Re-importing results...")
            a.import_results(False)
    
        case "moodle":
            a.export_results_moodle()
    
        case "passed":
            a.export_passed()
    
        # opening files
    
        case "main file":
            open_by_grader_preference(join(s.path_graded, a.main_file_name+".py"))
    
        case "notes":
            open_by_grader_preference(a.path_notes_file)
    
        case "crashes":
            open_by_grader_preference(a.path_crashes_file)
    
        case "plagiarism":
            open_by_grader_preference(a.path_plagiarism_file)
    
        case "results":
            open_by_grader_preference(a.path_results_file)
    
        case "studentlist":
            open_by_grader_preference(a.path_studentlist_file)
    
        # grading process
    
        case "restart" | "reinitialize":
            if not a.verify_done():
                return
            print("Re-initializing...\n")
            a = Assignment(a.ex_nr)
    
        case "e" | "end" | "end grading":
            if not a.verify_done():
                return
            a.export_results(False)
            a.stats()
            end_grading = True
            # sys.exit()
    
        # not specified
        case _:
            print_color("red", "ERROR: Action not specified")

def ask_ex_nr():
    while True:
        if (ex_nr := input("Enter the two-digit number of the exercise (example: '00'): ")).isdigit():
            return ex_nr
        else:
            print_color("red", "ERROR: Not a valid exercise number")

if __name__ == '__main__':
    main()

# todo (medium prio): config file
# todo (high prio): documentation
