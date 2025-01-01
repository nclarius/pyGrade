#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of an assignment grading session
"""

import helpers
from student import *
import os, sys, shutil, traceback, unittest, csv, math, random, markdown, copy, itertools
import importlib
import importlib.util
from importlib import import_module
from os.path import *

debug = True


class Assignment(object):

    def __init__(self, ex_nr):
        # paths and files
        self.path_script = abspath(__file__)
        self.path_exercises = join(dirname(dirname(self.path_script)), "demo")
        # self.path_exercises = join(dirname(dirname(dirname(self.path_script))), "exercises")
        self.ex_nr = ex_nr
        self.path_ex = ""
        self.path_solution = ""
        self.path_handout = ""
        self.path_resources = ""
        self.path_results = ""
        self.path_subm_raw = ""
        self.path_subm_graded = ""
        self.raw = []
        self.names = []
        self.main_file_name = ""
        self.main_file = None
        self.test_files = []
        self.path_results_file = ""
        self.path_moodle_file = ""
        self.path_moodle_file_raw = ""
        self.path_studentlist_file = ""
        self.path_notes_file = ""
        self.path_crashes_file = ""
        self.path_plagiarism_file = ""
        self.path_templates_file = ""
        self.filenames_dont_open = tuple(["__pycache__", ".idea", ".gitkeep", "comment.md", ".pickle"])

        # student data
        self.studentlist = {}  # dictionary of student data from Modle
        self.students = {}  # dictionary of student objects with moodle id (str) as key
        self.s = None  # current student object
        self.backup = None  # backup for student object
        self.view_only = False
        self.reload = False
        # field_names_results = vars(Student(self)).keys()  # field names for results file
        field_names_results = ["id", "last_name", "first_name", "matr_nr", "moodle_id",
                                    "points", "total_points", "crashes", "plagiarism", "notes", "grader",
                                    "done_tests", "done_comment", "done_grading", "feedback"]
        #                           "path_raw_dirname", "path_raw", "path_graded_dirname", "path_graded", "path_comment", "feedback"]
        field_names = []

        # tasks and points
        self.tasks = {}  # tasks with total points; format {task_nr: ("task_name", pnts, is_bonus), ...}
        self.tasks_total = (0.0, 0.0)  # total sum of points in tasksk# avg_points = {}
        self.tasks_count = 0  # number of tasks
        self.assignments = {}  # assignments with total points; format {1: 0.5, 2: 2.0, 3: 3.5}
        self.assignments_total = 0.0  # total sum of points to be gained in assignments
        self.assignments_count = 0  # number of assignments

        # internal lists
        self.notes = []  # notes about self.students
        self.crashes = []  # submissions that crash - list of tuples of tuples of tuples and strings
        self.plagiarism = []  # plagiarism clusters - list of tuples of lists of tuples of strings and strings
        self.default_comments = {}  # default comments for crashes, plagiarism etc.

        # set up
        self.obtain_paths()
        self.obtain_tasks()
        self.import_results(False, True)


    def obtain_paths(self):
        print("Obtaining paths...")
        paths_found = False

        # exercise
        self.path_ex = join(self.path_exercises,
                  [dirname for dirname in os.listdir(self.path_exercises) if dirname.startswith("ex" + self.ex_nr)][0])

        # solution
        self.path_solution = join(self.path_ex, "code_solution")
        sys.path.insert(0, self.path_solution)
        # if not debug:
        #     for filename in os.listdir(path_solution):
        #         if not filename.endswith(filenames_dont_open):
        #             print("opening " + filename)
        #             helpers.open_by_grader_preference(join(path_solution, filename))

        # handout
        self.path_handout = join(self.path_ex, "code_handout")
        sys.path.insert(1, self.path_handout)
        # if not debug:
        #     for filename in os.listdir(path_handout):
        #         if not filename.endswith(filenames_dont_open):
        #             print("opening " + filename)
        #             helpers.open_by_grader_preference(join(self.path_handout, filename))

        # resources
        self.path_resources = join(self.path_ex, "resources")
        sys.path.insert(2, self.path_resources)

        # raw
        self.path_subm_raw = join(self.path_ex, "submissions_raw")
        raw = [dirname[:dirname.index("_")] for dirname in sorted(os.listdir(self.path_subm_raw))
               if os.path.isdir(join(self.path_subm_raw, dirname)) and not dirname.startswith("_solution")]

        # graded
        self.path_subm_graded = join(self.path_ex, "submissions_graded")
        if not exists(self.path_subm_graded): os.makedirs(self.path_subm_graded)

        # results
        self.path_results = join(self.path_ex, "results")
        self.path_results_file = join(self.path_results, "results.tsv")
        self.path_moodle_file = join(self.path_results, "results_moodle.csv")
        self.path_moodle_file_raw = join(self.path_results, "results_moodle_raw.csv")

        # find main file and test files
        self.main_file_name = "ex_" + self.ex_nr
        self.test_files = [filename[:-3] for filename in os.listdir(self.path_solution)
                      if filename.startswith("test_") and filename.endswith(".py")]
        if not self.test_files:
            helpers.print_warning("No test files found in '" + self.path_solution + "'")
            paths_found = False

        # open files
        if not debug:
            files_to_open = [join(self.path_handout, "test_" + self.main_file_name + ".py"),
                             join(self.path_handout, self.main_file_name + ".py"),
                             join(self.path_solution, "test_full_" + self.main_file_name + ".py"),
                             join(self.path_solution, "solution_" + self.main_file_name + ".py")]
            for filename in files_to_open:
                print("opening " + basename(filename))
                helpers.open_by_grader_preference(filename)

        # self.studentlist/scores
        self.path_studentlist_file = join(self.path_exercises, "studentlist.tsv")

        # notes/crashes/plagiarism/default comments
        self.path_notes_file = join(self.path_results, "notes.txt")
        self.path_crashes_file = join(self.path_results, "crashes.txt")
        self.path_plagiarism_file = join(self.path_results, "plagiarism.txt")
        self.path_templates_file = join(self.path_exercises, "templates/default_comments.txt")

        paths = [self.path_exercises, self.path_ex,
                 self.path_solution, self.path_handout, self.path_resources, self.path_results,
                 self.path_subm_raw, self.path_subm_graded,
                 self.path_results_file, self.path_moodle_file, self.path_moodle_file_raw,
                 self.path_notes_file, self.path_crashes_file, self.path_plagiarism_file]
        not_found = [pathname.__name__ for pathname in paths if pathname == ""]
        if not not_found:
            paths_found = True
            helpers.print_success("All paths found\n")
        else:
            for pathname in not_found:
                paths_found = False
                helpers.print_error("Path " + pathname + " not found")


    def obtain_files(self, silent=False):
        # todo (low prio): unify format of notes files

        if not silent:
            print("Obtaining files...")

        if not isfile(self.path_studentlist_file):
            helpers.print_error("self.studentlist.tsv not found")
            return

        # obtain notes
        # todo (low prio) still working?
        if not isfile(self.path_notes_file):
            f = open(self.path_notes_file, "w+", encoding="utf-8")
            f.close()
        else:
            with open(self.path_notes_file, "r", encoding="utf-8") as f:
                notes = []
                for line in f.readlines():
                    if not line.startswith("#"):
                        moodle_name = line.split("\t")[0]
                        st = self.lookup_student(moodle_name)
                        comment = line.split("\t")[1].replace("\n", "")
                        notes.append((st["ID"], comment))
                        # todo (low prio) include full name, not only id

        # obtain crashes
        if not isfile(self.path_crashes_file):
            f = open(self.path_crashes_file, "w+", encoding="utf-8")
            f.close()
        else:
            with open(self.path_crashes_file, "r", encoding="utf-8") as f:
                crashes = []
                for line in f.readlines():
                    if not line.startswith("#"):
                        moodle_name = line.split("\t")[0]
                        st = self.lookup_student(moodle_name)
                        comment = line.split("\t")[1].replace("\n", "")
                        crashes.append((st["ID"], comment))

        # obtain plagiarism
        # todo (medium prio): overwrite existing fields
        # todo (low prio): plagiarism entry in student object sometimes disappears?
        if not isfile(self.path_plagiarism_file):
                f = open(self.path_plagiarism_file, "w+", encoding="utf-8")
                f.close()
        else:
            with open(self.path_plagiarism_file, "r", encoding="utf-8") as f:
                plagiarism = []
                for line in f.readlines():
                    if not line.startswith("#"):
                        student_cluster = [tuple(st_tuple.split("_"))\
                                           for st_tuple in line.split(": ")[0].split(" + ")]
                        note = line.split(": ")[1].strip("\n") if len(line.split(": ")) > 1 else ""
                        plagiarism.append((student_cluster, note))

        # obtain default comments
        if not isfile(self.path_templates_file):
            f = open(self.path_templates_file, "w+", encoding="utf-8")
            f.close()
        else:
            with open(self.path_templates_file, "r", encoding="utf-8") as f:
                default_comments = {}
                # todo (low prio): fails on linebreaks in default comment
                for line in f.readlines():
                    if not line.strip() == "":
                        default_comments.update({(line.split("\t"))[0]: (line.split("\t"))[1]})

        # re-sort raw
        raw_prelim = []
        for raw_name in self.raw:
            st = self.lookup_student(raw_name)
            if st is not None:
                raw_prelim.append(st)
        self.raw = sorted(raw_prelim, key=lambda st: st["Last name"])
        # self.raw = sorted(raw_prelim, key=lambda st: st["First name"])
        self.raw = [st["First name"] + " " + st["Last name"] for st in self.raw]
        # self.raw = [st["Last name"] + ", " + st["First name"] for st in self.raw]
        names = list(itertools.chain(*[[name, self.lookup_student(name)["First name"], self.lookup_student(name)["Last name"]] \
                                 for name in self.raw]))

        if not silent:
            helpers.print_success("All files found\n")


    def obtain_tasks(self):
        # todo (medium prio): account for bonus tasks
        # todo (low prio): include name of task
        try:
            print("Obtaining tasks...")
            tasks_warning = False
            tasks_test = {}

            for test_file_name in self.test_files:
                spec = importlib.util.spec_from_file_location(test_file_name, join(self.path_solution, test_file_name + ".py"))
                test_file = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(test_file)
                # test_file = importlib.abc.Loader.create_module(spec)
                # sys.modules[spec.name] = test_file
                suite = unittest.defaultTestLoader.loadTestsFromName(test_file_name)

                # todo (low prio): current setup incompatible with more than one test file
                # todo (low prio): make tasks specification nicer (tasks class? task name optional? bonus points spec?)
                test_file_tasks = getattr(test_file, "tasks")
                test_file_total_points = getattr(test_file, "total_points")
                self.tasks[0] = ("Overall", 0.0, False)
                for nr in test_file_tasks:
                    task_name = ""
                    task_pnts = 0
                    task_is_bonus = False
                    if type(test_file_tasks[nr]) == tuple:
                        for el in test_file_tasks[nr]:
                            if type(el) == str:
                                task_name = el
                            elif type(el) == float or type(el) == int:
                                task_pnts = float(el)
                            elif type(el) == bool:
                                task_is_bonus = el
                    elif type(test_file_tasks[nr]) in [float, int]:
                        task_pnts = float(test_file_tasks[nr])
                    self.tasks[nr] = (task_name, task_pnts, task_is_bonus)
                if type(test_file_total_points) == tuple:
                    self.tasks_total = (float(test_file_total_points[0]), float(test_file_total_points[1]))
                else:
                    self.tasks_total = (float(test_file_total_points), 0.0)
                tasks_count = len(self.tasks)-1

                self.tasks_total_tests = float(sum([points for points in [val[1] for val in self.tasks.values() if not val[2]]]))
                self.tasks_total_tests_bonus =  float(sum([points for points in [val[1] for val in self.tasks.values() if val[2]]]))
                if self.tasks_total[0] != self.tasks_total_tests:
                    tasks_warning = True
                    helpers.print_warning("Total points are specified as " + helpers.inflect(self.tasks_total, "points, ") +
                                "but points specified in task dict sum up to " + helpers.inflect(self.tasks_total_tests, "points"))
                if self.tasks_total[1] != self.tasks_total_tests_bonus:
                    tasks_warning = True
                    helpers.print_warning("Total bonus points are specified as " + helpers.inflect(self.tasks_total, "points, ") +
                                "but bonus points specified in task dict sum up to " + helpers.inflect(self.tasks_total_tests, "points"))


                for i, case in enumerate(suite._tests):
                    case_name = \
                        (case._tests[0].id())[(case._tests[0].id().index("Test")):case._tests[0].id().index(".test_")]
                    tasks_test[i+1] = 0.0
                    for j, test in enumerate(case._tests):
                        # test_name = test._testMethodName
                        # test_doc = test._testMethodDoc
                        # if not case_name.startswith("TestRun"):
                        tasks_test[i+1] += float(self.points_test(test))
                    tasks_test[i+1] = round(tasks_test[i+1], 3)

                if len(self.tasks)-1 != len(tasks_test):
                    tasks_warning = True
                    helpers.print_warning("" + \
                                "Points are set up for " + helpers.inflect(len(self.tasks), "tasks, ") +
                                "but test file containts unit tests for " + helpers.inflect(len(tasks_test), "tasks"))
                for i, case in enumerate(suite._tests):
                    case_name = \
                        (case._tests[0].id())[(case._tests[0].id().index("Test")):case._tests[0].id().index(".test_")]
                    if not case_name.startswith("TestRun"):
                        if tasks_test[i+1] != self.tasks[i+1][1]:
                            tasks_warning = True
                            helpers.print_warning("" +
                                        "Points for Task " + str(i+1) + " (" + self.tasks[i+1][0] + ") " + \
                                        "are specified as " + helpers.inflect(self.tasks[i+1][1], "points, ") +\
                                        "but unit tests sum up to " + helpers.inflect(tasks_test[i+1], "points"))

                if tasks_warning:
                    helpers.print_color("orange", "If you have run-only tests or bonus tasks, you can ignore this warning.\n" +
                                "Otherwise, you might want to edit the test file and re-initialize the exercise by typing " +
                                "'restart'.")

            # destroy data
            sys.path.remove(self.path_handout)
            for test_file in self.test_files:
                if test_file in sys.modules: del sys.modules[test_file]
            if self.main_file_name in sys.modules: del sys.modules[self.main_file_name]
            sys.path_importer_cache[self.main_file_name] = None
            importlib.invalidate_caches()

            helpers.print_success("Tasks initialized")
            print(helpers.tasks2str(self.tasks, tasks_count, self.tasks_total))
        except Exception as err:
            print(traceback.print_exc(err))


    def next_student(self, n):
        # todo (low prio): index no longer needed, use ID instead
        # verify that previous student is done
        if not reload:
            if not self.verify_done():
                return

        # destroy data of previous student
        if self.s is not None:
            if self.s.path_raw in sys.path: sys.path.remove(self.s.path_raw)
            if self.s.path_graded in sys.path: sys.path.remove(s.path_graded)
            for test_file in self.test_files:
                if test_file in sys.modules: del sys.modules[test_file]
            if self.main_file_name in sys.modules: del sys.modules[self.main_file_name]
            if main_file in globals(): del main_file
            sys.path_importer_cache[self.main_file_name] = None
            importlib.invalidate_caches()

        # print("\n------------\nbegin next student")
        # modulenames = set(sys.modules) & set(globals())
        # allmodules = [sys.modules[name] for name in modulenames]
        # print("currently loaded modules: " + str(allmodules))
        # print("sys.path: " + str(sys.path))
        # print("sys.modules: " + str(sys.modules))
        # print("globals: " + str(globals()))
        # print("self.students: " + str(self.students))
        # print("s: " + str(s))
        # print("--------------\n")

        # if n-1 in thresholds:
        #     assigned_grader = graders[thresholds.index(n-1)]
        #     if assigned_grader == helpers.get_grader():
        #         print()
        #         helpers.print_color("orange", "End of your part reached.")
        #         answer = input(helpers.color("orange", "Return? "))
        #         if answer in ["y", "yes", "r", "return"]:
        #             return

        # end of list
        if n > len(self.raw):
            print()
            print("End of raw directory reached")
            return

        # pos = 0
        # thresholds_ = [0] + thresholds + [len(self.raw)]
        # for i in range(len(thresholds)+1):
        #     if (thresholds_[i])+1 <= n <= thresholds_[i+1]:
        #         pos = i
        #         break
        # assigned_grader = graders[pos]
        # if not assigned_grader == helpers.get_grader():
        #     helpers.print_warning("This is not your student.")
        #     answer = input(helpers.color("orange", "Are you sure you want to continue? "))
        #     if answer in ["n", "no", "r", "return"]:
        #         return

        # create new student object
        s = Student(self)
        view_only = False
        raw_name = self.raw[n-1].replace("'", "")
        for dirname in os.listdir(self.path_subm_raw):
            if dirname.startswith(self.raw_name):
                self.s.dirname_raw = dirname
                self.s.path_raw = os.path.join(self.path_subm_raw, self.s.dirname_raw)
                break
        print("\nRaw directory: " + self.s.dirname_raw)
        self.s.moodle_id = self.s.dirname_raw[self.s.dirname_raw.index("_") + 1:self.s.dirname_raw.index("_assign")]
        self.s.index = "#{:02d}".format(idx)
        found = False
        for id in self.studentlist:
            if helpers.ascii(self.studentlist[id]["First name"] + " " + self.studentlist[id]["Last name"]) == helpers.ascii(self.raw_name):
                self.s.id = id
                found = True
                break
        if not found:
            helpers.print_error("Student " + raw_name + " was not found in self.studentlist")
            return

        # change to raw directory
        os.chdir(s.path_raw)
        sys.path.insert(0, self.s.path_raw)
        print("Contents:")
        for filename in os.listdir(self.s.path_raw):
            print("- " + filename)
        print()

        # select action in case data for student already exists
        merge = False
        if self.s.id in self.students:
            print("Data for this student already exists:")
            self.students[self.s.id].print_data()
            print()
            valid_answer = False
            while not valid_answer:
                match input("Available options:\n"
                               "'s': skip this student and go on to next one\n"
                               "'m': merge data\n"
                               "'o': overwrite existing data with new entry\n"
                               "'v': view-only mode - take over existing data and warn before making modifications\n"
                               "'r': return and select next action\n"
                               "How do you want to proceed? "):
                    case "s" | "skip":
                        # todo (medium prio): make this safer (generating feedback fails with wrong absolute paths)
                        print("Going on to next student...\n")
                        valid_answer = True
                        # s = self.students[self.s.moodle_id]
                        s = None
                        backup = None
                        idx += 1
                        self.next_student(idx)
                        return
                    case "m" | "merge":
                        print("Merging data...\n")
                        valid_answer = True
                        merge = True
                        continue
                    case "o" | "overwrite":
                        print("Overwriting data...\n")
                        valid_answer = True
                        continue
                    case "v" | "view" | "view-only":
                        print("View-only mode activated\n")
                        valid_answer = True
                        view_only = True
                        merge = True
                        continue
                    case "r" | "return":
                        print()
                        valid_answer = True
                        s = None
                        return
                    case _:
                        helpers.print_error("Not a valid option")

        # set remaining variables
        if merge:  # take over data from existing entry
            for field in ["last_name", "first_name", "matr_nr",
                          "points", "total_points", "feedback", "grader", "done_tests", "done_comment", "done_grading"]:
                setattr(s, field, getattr(self.students[self.s.id], field))
        else:  # initialize student
            self.s.last_name = self.studentlist[self.s.id]["Last name"]
            self.s.first_name = self.studentlist[self.s.id]["First name"]
            self.s.matr_nr = self.studentlist[self.s.id]["MatrNr"]
            self.s.points = {task_nr: 0.0 for task_nr in self.tasks}
            self.s.total_points = 0.0
            self.students[self.s.id] = s
        if not view_only:
            self.s.grader = helpers.get_grader()

        # update student data
        crash = False
        if not view_only:
            self.obtain_files(True)
            self.s.update_data(self.notes, self.crashes, self.plagiarism, self.tasks, self.tasks_total)

        import_main_file = True
        if self.s.crashes != "(no crash)":
            crash = True
            import_main_file = False
            match helpers.input_color("orange", "WARNING: This student's code crashes.\nNotes: " + str(self.s.crashes) +
                                 "\nDo you want to try to import the main file? ('y'/'n') "):
                case "y" | "yes":
                    import_main_file = True
                case _:
                    pass
            print()

        # get student data and create main folder
        # if import_main_file:
        #     # todo (high prio): find a better fix for encoding issue than this
        #    self.s.last_name = main_file.family_name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        #    self.s.first_name = main_file.first_name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
        #     self.s.matr_nr = main_file.student_id
        #     self.s.dirname_graded = self.s.last_name.replace(" ", "-") +\
        #                        "_" + self.s.first_name.replace(" ", "-") +\
        #                        "_" + self.s.matr_nr
        # else:
        #     # todo (low prio): this folder remains after having re-loaded the student with the data fixed
        #     self.s.dirname_graded = "(crashed)_" + self.s.dirname_raw.replace(" ", "-")
        # self.s.path_graded = join(self.path_subm_graded, self.s.dirname_graded)

        # get student data and create main folder
        self.s.dirname_graded = str(self.s.id) +\
                                "_" + helpers.ascii(self.s.last_name).replace(" ", "-") +\
                                "_" + helpers.ascii(self.s.first_name).replace(" ", "-")
        self.s.path_graded = join(self.path_subm_graded, self.s.dirname_graded)
        if not exists(self.s.path_graded): os.makedirs(self.s.path_graded)
        sys.path.insert(0, self.s.path_graded)
        # copy all raw and resource files into graded folder
        if len(os.listdir(self.s.path_graded)) == 0:
            for filename in os.listdir(s.path_raw):
                if not filename.endswith(self.filenames_dont_open) and not exists(join(self.s.path_graded, filename)):
                    shutil.copyfile(join(self.s.path_raw, filename), join(self.s.path_graded, filename))
        # for filename in os.listdir(path_resources):
        #     if not filename.endswith(filenames_dont_open) and not exists(join(s.path_graded, filename)):
        #         shutil.copyfile(join(path_resources, filename), join(s.path_graded, filename))

        # create comment file
        self.s.path_comment = join(self.s.path_graded, "comment.md")
        if not exists(self.s.path_comment):
            with open(self.s.path_comment, "w", encoding="utf-8") as f: pass

        # make sure configuration doesn't work on raw path
        if self.s.path_raw in sys.path: sys.path.remove(self.s.path_raw)
        if self.main_file_name in sys.modules: del sys.modules[self.main_file_name]
        sys.path_importer_cache[self.main_file_name] = None

        # cd into the graded folder and open all source files in editor
        os.chdir(self.s.path_graded)

        if not debug:
            for filename in os.listdir(self.s.path_graded):
                if not filename.endswith(self.filenames_dont_open):
                    print("opening " + filename)
                    helpers.open_by_grader_preference(filename)

        # read in main file
        # todo (medium prio): on reload/merge, take file from graded, not from raw
        if import_main_file:
            # # https://docs.python.org/3/reference/import.html:
            # If sys.meta_path processing reaches the end of its list without returning a spec, then a ModuleNotFoundError
            # is raised. Any other exceptions raised are simply propagated up, aborting the import process."""
            # # https://docs.python.org/3/library/exceptions.html:
            # exception Exception
            # All built-in, non-system-exiting exceptions are derived from this class. All user-defined exceptions should
            # also be derived from this class.
            # --> instead: BaseException?

            import traceback
            try:
                main_file = import_module(self.main_file_name)
            # except ImportError as e:
            # except SystemExit as e:
            except Exception as e:
                import_main_file = False
                crash = True
                helpers.print_error("Exception - failed to import module " + self.main_file_name)
                crash_note = traceback.format_exc().splitlines()[-1]
                helpers.print_color("red", crash_note)
                print()
                with open(self.path_crashes_file, "a+", encoding="utf-8") as f:
                    f.seek(0)
                    if self.raw[idx-1] + "\t" + crash_note not in f.read():
                        if self.s.crashes == "(no crash)":
                            self.s.crashes = [crash_note]
                        else:
                            if not crash_note in self.s.crashes:
                                self.s.crashes.append(crash_note)
                        f.write(self.raw[idx-1] + "\t" + crash_note + "\n")
            # except BaseException as e:
            # except:
            #     # other errors: SyntaxError, NameError, TypeError
            else:
                main_file = importlib.reload(main_file)
                print(helpers.color("green", "SUCCESS: Imported module " + self.main_file_name))
                print()
        reload = False

        # todo (low prio): part of it must come before importing file in order to detect crashes
        # update student data
        if not view_only:
            self.obtain_files(True)
            self.s.update_data(self.notes, self.crashes, self.plagiarism, self.tasks, self.tasks_total)
            if not self.s.done_comment:
                # todo (low prio): open file in append mode to include both comments?
                self.comment_crashes()
                self.comment_plagiarism()

                # write bullet points for tasks in comment file
                if self.s.crashes == "(no crash)" and self.s.plagiarism == "(no plagiarism)":
                    with open(self.s.path_comment, "w", encoding="utf-8") as f:
                        for task_nr in self.tasks:
                            if not task_nr == 0:
                                f.write("- Task " + str(task_nr) + " (" + self.tasks[task_nr][0] + "): \n")
                        f.write("")

        # print and save student data
        # todo (low prio): "access denied" message appearing sometimes
        self.print_student(self)
        if crash:
            helpers.print_color("orange", "\nWARNING: This student's code crashed while attempting to import the main file. "
                        "Scroll up for information on the error.")
        if self.s.notes != "(no notes)":
            print()
            for cmnt in self.s.notes:
                helpers.print_color("orange", "NOTE: " + cmnt)  # todo (low prio) doesn't work on reload
        if self.s.plagiarism != "(no plagiarism)":
            helpers.print_color("orange", "\nWARNING: This student plagiarized their code with " +
                                 helpers.conjoin(self.s.plagiarism[0]) +
                                 ".\nNotes: " + self.s.plagiarism[1])
        self.students[self.s.id] = s
        backup = copy.copy(s)


    def run_tests(self):
        # todo (low prio): possibility to abort execution
        # todo (low prio): better handling of test structuring (test suites?)
        import re

        if self.s is None or not self.verify_overwrite():
            return

        # todo (low prio): exception catching needed?
        try:
            if self.s.crashes != "(no crash)":
                match helpers.input_color("orange", "WARNING: This student's code crashes.\nNotes: " + str(self.s.crashes) +
                                     "\nAre you sure you want to attempt to run tests on them? ('y'/'n') "):
                    case "y" | "yes":
                        pass
                    case _:
                        return

            if self.s.plagiarism != "(no plagiarism)":
                match helpers.input_color("orange", "WARNING: This student plagiarized their code with " +
                                     helpers.conjoin(self.s.plagiarism[0]) +
                                     ".\nNotes: " + self.s.plagiarism[1] +
                                     "\nAre you sure you want to run tests on them? ('y'/'n') "):
                    case "y" | "yes":
                        pass
                    case _:
                        return

            # for tests that come as a main file (like for ex00)
            # for test_file in self.test_files:
            #     # print("sys path: " + str(sys.path))
            #     # print("Running test file " + test_file)
            #     runpy.run_module(test_file, {}, "__main__")
            #     # print("Done running test file")

            test_summary = "Summary of test results:\n" \
                           "------------------------\n"
            failure_summary = ""
            failures = {}

            for test_file_name in self.test_files:

                # print("sys.path: " + str(sys.path))
                # print("sys.modules: " + str(sys.modules))
                # print("globals: " + str(globals()))
                # print("sys.argv: " + str(sys.argv))

                # todo (low prio): extract file path of module that test file is run on, to ensure correct configuration
                print("Running tests in " + test_file_name + " on " + os.path.abspath(self.main_file.__file__))
                print()
                # for name, obj in inspect.getmembers(sys.modules[__name__]):
                #     if inspect.isclass(obj):
                #         print(obj)

                suite = unittest.defaultTestLoader.loadTestsFromName(test_file_name)

                # print("\n------------\nbegin run_tests()")
                # modulenames = set(sys.modules) & set(globals())
                # allmodules = [sys.modules[name] for name in modulenames]
                # print("currently loaded modules: " + str(allmodules))
                # print("sys.path: " + str(sys.path))
                # print("sys.modules: " + str(sys.modules))
                # print("globals: " + str(globals()))
                # print("self.students: " + str(self.students))
                # print("s: " + str(s))
                # print("begin run_tests()\n--------------\n")

                # print(suite)
                # print(suite._tests)
                # todo (medium prio): print details of test failures
                for i, case in enumerate(suite._tests):
                    # print("case: " + str(case))
                    # todo (low prio): use built-in functions to extract names:
                    # - unittest.defaultTestLoader.getTestCaseNames()
                    # - unittest.defaultTestLoader.sortTestMethodsUsing
                    # case_name = unittest.defaultTestLoader.getTestCaseNames(case)
                    case_name = \
                         (case._tests[0].id())[(case._tests[0].id().index("Test")):case._tests[0].id().index(".test_")]
                    test_summary += "• " + case_name + " (" + self.tasks[i+1][0] + ") (" + str(self.tasks[i+1][1]) + " pnts):\n"
                    failures[case_name] = {}
                    if not self.s.done_tests:
                        self.s.points[i+1] = 0.0
                    # print(case._tests)
                    for j, test in enumerate(case._tests):
                        # test_name = test._testMethodName
                        # test_doc = test._testMethodDoc
                        test_name = test.id()[test.id().index(".test_")+1:]
                        test_pnts = self.points_test(test)
                        failures[case_name][test_name] = []
                        if self.test_runonly(test):
                            # todo (medium prio): better handling of runonly tests (expected/actual output)
                            print("Running " + case_name + "/" + test_name)
                            # print("--------------\nBegin program output\n--------------")
                        result = test.run()
                        if self.test_runonly(test):
                            print("Done running " + case_name + "/" + test_name + "\n")
                            # print("--------------\nEnd program output\n--------------\n")
                        if result:
                            len_failures = len(result.failures) if result.failures is not None else 0
                            len_errors = len(result.errors) if result.errors is not None else 0
                            # print(str(len_failures) + " failures: " + str(result.failures))
                            # print(str(len_errors) + " errors: " + str(result.errors))
                            if len_failures + len_errors == 0:
                                test_summary += "  - " + test_name + ": "
                                test_summary += helpers.color("green", "succeeded")\
                                    if not self.test_runonly(test) else helpers.color("orange", "visual inspection required")
                                test_summary += " (" + str(test_pnts) + "/" + str(test_pnts) + " pts)\n"
                                if not self.s.done_tests:
                                    self.s.points[i+1] += test_pnts
                            else:
                                test_summary += "  - " + test_name + ": "
                                test_summary += helpers.color("red", "failed")\
                                    if not self.test_runonly(test) else helpers.color("orange", "visual inspection required")
                                test_summary += " (" + str(0.0) + "/" + str(test_pnts) + " pts)\n"
                                for error in result.errors:
                                    # error = str(error)
                                    # start_err_1 = error.index("in " + test_name) + len("in " + test_name)
                                    # end_err_1 = error[start_err_1:].index("File")
                                    # err_1 = error[start_err_1:end_err_1]
                                    # err_1 = err_1.
                                    # replace("\\n    self", "self").replace("\\n", "\n      ").replace("\n')", "")
                                    # # err_1 = extract_infix(str(error), "in " + test_name, "File ")\
                                    # #    .replace("\\n    self", "self").replace("\\n", "\n      ").replace("\n')", "")
                                    # start_err_2 = error[end_err_1:].index(", line")-len(" line")
                                    # err_2 = error[start_err_2:].replace("\\n    self", "self")\
                                    #     .replace("\\n", "\n      ").replace("\n      ')", "")
                                    # # err_2 = extract_suffix(str(error), ", ").
                                    # replace("\\n", "\n      ").replace("\n')", "")
                                    # # failures[case_name][test_name].append(err_1 + "\n" + err_2)
                                    # failures[case_name][test_name].append(err_1 + "\n" + err_2)
                                    # todo (low prio): make this printout nicer (see Task 2, Nicole Breuninger)
                                    # err = extract_infix(str(error), "in " + test_name+"\\n", "\\n  File") + "\\n" +\
                                    #       extract_infix(str(error)[str(error).index("in " + test_name):], ", ", "\\n')")\
                                    #       .replace("\\n", "\n    ")
                                    err = str(error)
                                    failures[case_name][test_name].append(err)
                                    # test_summary += err + "\n"
                                for failure in result.failures:
                                    # fail = extract_infix(str(failure), "in " + test_name, "\\n')") \
                                    #     .replace("\\n", "\n    ")
                                    fail = str(failure)
                                    # ass_stment = re.findall("(self\.assert(.*))\\n.AssertionError", fail)[0][0]
                                    # ass_err = re.search("(AssertionError.*)\\n", fail).group(0)
                                    # failures[case_name][test_name].
                                    # append("    - " + ass_stment + "\n" + "      " + ass_err + "\n")
                                    # test_summary += fail + "    - " + ass_stment + "\n" + "      " + ass_err + "\n"
                                    # test_summary += fail + "\n"

            # fill in failures string
            fails = False
            fails_task = False
            fails_test = False
            for task_name in failures:
                for test_name in failures[task_name]:
                    for fail_name in failures[task_name][test_name]:
                        if not fails:
                            fails = True
                            failure_summary += "Failures:\n" \
                                               "---------"
                        if not fails_task:
                            fails_task = True
                            failure_summary += "\n- " + task_name + ":\n"
                        if not fails_test:
                            fails_test = True
                            failure_summary += "\n  - " + test_name + ":\n\n"
                        failure_summary += "    - " + fail_name + "\n"
                    fails_test = False
                fails_task = False
            failure_summary = failure_summary.replace("\n      \n", "")

            # print summaries
            # print(failure_summary + "\n")
            print(test_summary)
            self.points_total(self.s)
            helpers.print_success("All tests done\n")
            print(helpers.points2str(self.s, self.tasks, self.tasks_total))
            self.s.done_tests = True
            self.export_results()
        except Exception as err:
            print(traceback.print_exc(err))


    def edit_points(self):
        if self.s is None or not self.verify_overwrite():
            return

        print("\nCurrent points:\n" + helpers.points2str(self.s, self.tasks, self.tasks_total))
        task_nr = input("Enter the number of the task you want to change the points for ('0' for overall; 'r' to return): ")
        if task_nr in ["r", "return"]:
            return
        if task_nr in ["overall", "Overall"]:
            task_nr = 0
        else:
            task_nr = int(task_nr)
        max_points = self.tasks[task_nr][1]
        points_valid = False
        while not points_valid:
            new_points = float(input("Enter the new points: "))
            if new_points > max_points and not task_nr == 0:
                helpers.print_color("orange",
                            "WARNNING: The points you entered exceed the maximum number of poihts for the task (" +\
                            str(max_points) + "). Are you sure you want to set the points to the this value?")
            self.s.points[task_nr] = float(new_points)
            points_valid = True
        self.points_total(self.s)
        helpers.print_color("green", "\nSUCCESS: New points:")
        print(helpers.points2str(self.s, self.tasks, self.tasks_total))
        self.export_results()


    def comment(self):
        if self.s is None or not self.verify_overwrite():
            return

        helpers.open_by_grader_preference(self.s.path_comment)
        self.s.done_comment = True  # todo (low prio): gets lost after editing points?
        print("Opened comment file")


    def note(self):

        print("Notes:")
        print(self.s.notes)
    #     s.notes = input("Enter new notes string:\n")
    #     export_results()


    def edit_grading_status(self):
        if self.s is None or not self.verify_overwrite():
            return

        print("\nCurrent grading status for this student: " + ("graded" if self.s.done_grading else "pending"))
        valid_answer = False
        while not valid_answer:
            match input("What would you like to set the grading status to? ('graded'/'pending') "):
                case "graded":
                    self.s.done_grading = True
                    print("Grading status set to 'graded'")
                    break
                case "pending":
                    self.s.done_grading = False
                    print("Grading status set to 'pending'")
                    break
        self.export_results()

    def points_test(self, test):
        test_doc = test._testMethodDoc
        if test_doc is None:
            test_doc = ""
        if ":points: " in test_doc:
            test_doc_points_start = test_doc.index(":points: ") + len(":points: ")
            test_doc_points_end = test_doc_points_start + \
                                (test_doc[test_doc_points_start:].index("\n") \
                                    if "\n" in test_doc[test_doc_points_start:] \
                                    else len(test_doc[test_doc_points_start:]))
            return float(test_doc[test_doc_points_start:test_doc_points_end])
        else:
            return 0.5


    def points_total(self, st):
        # if s is None or not verify_overwrite():
        if st is None:
            return

        st.points = {key: round(val, 3) for key, val in st.points.items()}
        st.total_points = sum(st.points.values())

        # todo (low prio): only trigger on save?
        if st.done_grading:
            if self.tasks_total[0] > 0:
                self.studentlist[st.id]["ex_" + self.ex_nr + "_points"] = st.total_points
                self.studentlist[st.id]["ex_" + self.ex_nr + "_perc"] = round((st.total_points/self.tasks_total[0]), 2)
        applicable = [ass for ass in self.assignments if self.studentlist[st.id][ass + "_points"] not in ["", "-"]]
        if len(applicable) > 0:
            self.studentlist[st.id]["Points total"] =\
                sum([self.studentlist[st.id][ass + "_points"] for ass in applicable])
            self.studentlist[st.id]["Perc average"] =\
                round((sum([self.studentlist[st.id][ass + "_perc"] for ass in applicable])/len(applicable)), 3)
            self.studentlist[st.id]["Perc total"] = \
                round((self.studentlist[st.id]["Points total"]/self.studentlist["Total"]["Points total"]), 3)
            self.studentlist[st.id]["Remaining"] = \
                round(((0.6 * self.studentlist["Total"]["Points total"]) - self.studentlist[st.id]["Points total"]), 3)
            self.studentlist[st.id]["Status"] = \
                (1 if self.studentlist[st.id]["Remaining"] <= 0 else
                    (0 if self.studentlist[st.id]["Remaining"] <= self.studentlist["Total"]["Remaining"] else
                         (-1 if self.studentlist[st.id]["Remaining"] > self.studentlist["Total"]["Remaining"] else
                          "unclear")))


    # todo (low prio): command to update feedback string for all self.students
    def feedback(self, st, silent=True):
        # if s is None or not verify_overwrite():
        if st is None:
            return

        self.points_total(st)

        # todo (medium prio): markdown: when newline? first replace "\n" with "<br/>", later with ""?
        res = ""

        res += "<h4>Comments:</h4>"
        res += "<p>"
        if os.path.getsize(st.path_comment) == 0:
            cmt = "-"
            st.done_comment = False
        else:
            with open(st.path_comment, "r", encoding="utf-8") as comment_file:
                cmt = comment_file.read()
                st.done_comment = True
        res += markdown.markdown(cmt)\
            .replace("\r\n", "<br/>").replace("\n", "<br/>").replace("\r", "<br/>")\
            .replace("</code><br/>", "</code></pre>").replace("<br/><code>", "<pre><code>")
        res += "</p>"
        res = res.replace("<p><p>", "<p>").replace("</p></p>", "</p>")
        res += "<p></p>"

        if self.tasks_total[0] > 0:
            res += "<h4>Points achieved:</h4>"
            # todo (low prio): remove redundant whitespace in tasks overview (current fix doesn't work)
            # res += markdown.markdown(points2str(st, tasks, self.tasks_total).replace("  ", "").replace(": ", ":"))\
            #     .replace("<h2>Points achieved:</h2>", "").replace("</p>\n<hr />\n<p>", "<br/>-------<br/>")\
            #     .replace("\r\n", "<br/>").replace("\n", "<br/>").replace("\r", "<br/>")
            res += helpers.points2html(st, self.tasks, self.tasks_total)
        res += "<p></p><p>Your submission was graded by " + st.grader + ".</p>"
        res += "<p></p>"

        if self.ex_nr != "00":
            res += "<h4>Current score:</h4>"
            assmnts_sofar = [ass_nr for ass_nr in self.assignments if int(ass_nr[3:]) <= int(self.ex_nr)]
            submitted_sofar = [ass_nr for ass_nr in self.assignments if int(ass_nr[3:]) <= int(self.ex_nr) and \
                     self.studentlist[st.id][ass_nr + "_points"] not in ["", "-"]]
            total_total = float(self.studentlist["Total"]["Points total"])
            avg_sofar_perc = sum([self.studentlist[st.id][ass_nr + "_perc"] for ass_nr in submitted_sofar])/len(submitted_sofar) if submitted_sofar else 0
            achieved_sofar = sum([self.studentlist[st.id][ass_nr + "_points"] for ass_nr in submitted_sofar])
            total_sofar = sum([self.studentlist["Total"][ass_nr + "_points"] for ass_nr in assmnts_sofar])
            achieved_sofar_sofar_perc = achieved_sofar/total_sofar if total_sofar else 0
            achieved_sofar_perc = achieved_sofar/total_total
            needed_sofar = round(total_total * 0.6) - achieved_sofar
            needed_sofar_perc = needed_sofar/total_total
            remaining_sofar = total_total - total_sofar
            passed_sofar = achieved_sofar >= 0.6 * total_total
            passable_sofar = needed_sofar <= remaining_sofar

            # todo (medium prio): turn this into ass2str
            res += "<table>"
            for ass in assmnts_sofar:
                res += "<tr><td>Assignment " + ass[3:] + ":&nbsp;</td>"
                achievable = self.studentlist["Total"][ass + "_points"]
                if ass in submitted_sofar:
                    achieved = self.studentlist[st.id][ass + "_points"]
                    achieved_perc = self.studentlist[st.id][ass + "_perc"]
                    res += "<td>" + "{0:05.2f}".format(achieved) + "/" + \
                           "{0:04.1f}".format(achievable) + " points&nbsp;</td>"
                    res += "<td>|" + round(achieved_perc*100/5) * "#"
                    res += " (" + "{0:.0%}".format(self.studentlist[st.id][ass + "_perc"]) + ")" + "</td>"
                else:
                    res += "<td>" + "&nbsp;&nbsp;---&nbsp;&nbsp;" + "/" + \
                           "{0:04.1f}".format(achievable) + " points&nbsp;</td>"
                    res += "<td>(not submitted)</td>"
                res += "</tr>"
            res += "<tr><td>-----------</td><td>&nbsp;</td><td>&nbsp;</td></tr>"
            res += "<tr><td>Average so far:&nbsp;</td>"
            res += "<td></td>"
            res += "<td>|" + round(avg_sofar_perc*100/5) * "#"
            res += " (" + "{0:.1%}".format(avg_sofar_perc) + ")</td></tr>"
            res += "<tr><td>Total so far:&nbsp;</td>"
            res += "<td>" + "{0:05.2f}".format(achieved_sofar) + "/" + str(total_sofar) + " points&nbsp;</td>"
            res += "<td>|" + round(achieved_sofar_sofar_perc*100/5) * "#"
            res += " (" + "{0:.1%}".format(achieved_sofar_sofar_perc) + ")</td></tr>"
            res += "</table>"
            res += "<p></p><p>"

            res += "Out of " + str(total_total) + " points to be gained in this course, "
            res += "you need a minimum of 60% (=" + str(total_total * 0.6) + " points) to pass the class.</p>"
            res += "<table>"
            res += "<tr><td>Overall percentage achieved so far:&nbsp;</td>"
            res += "<td><span style='color:Green'>" + "{0:.1%}".format(achieved_sofar_perc) + "</span></td></tr>"
            res += "<tr><td>Points still needed to pass the course:&nbsp;</td>"
            res += ("<td><span style='color:Orange'>" if needed_sofar > 0.0 else "<td><span style='color:Green'>") + \
                   str(round(needed_sofar, 3)) + " points</span></td></tr>"
            res += "</table>"
            res += "<p></p>"

            # res += "<p>Average score on your assignments submitted so far: " + \
            #        "{0:.1%}".format(avg_sofar) + "<br/>"
            # res += "<p>Average score on your assignments submitted so far: " +\
            #        ("{0:.1%}".format(self.studentlist[st.id]["Perc average"]) if self.studentlist[st.id]["Perc average"] != "-"\
            #         else "-") + "<br/>"
            # res += "Total points achieved so far: " + str(achieved_sofar) + "<br/>"
            # res += "Total points achieved so far: " + str(self.studentlist[st.id]["Points total"]) + "<br/>"
            # res += "Overall percentage achieved so far (= green): " +\
            #       "{0:.1%}".format(achieved_sofar_perc) + "<br/>"
            # res += "Total percentage achieved so far: " +\
            #        ("{0:.1%}".format(self.studentlist[st.id]["Perc total"]) if self.studentlist[st.id]["Perc average"] != "-"\
            #         else "-") + "<br/>"
            # res += "Points still needed to pass this course (= orange)*: " + str(needed_sofar) + "<br/>"
            # res += "Points still needed to pass this course*: " + str(self.studentlist[st.id]["Remaining"]) + "</p>"
            # res += "* (= min. 60% = " + str(float(0.6 * self.studentlist["Total"]["Points total"])) + " points out of " + \
            #       str(float(self.studentlist["Total"]["Points total"])) + " points to be gained in in this course)" + "</p>"

            scale = 5
            achieved_x = math.floor(achieved_sofar_perc*100/scale)
            needed_x = round(math.ceil(needed_sofar_perc*100/scale), 3) if achieved_sofar_perc < 0.6 else 0
            rest_x = round(total_total/scale - (achieved_x + needed_x)) if achieved_sofar_perc < 1 else 0
            res += "<p>"
            res += "<span style='color:Green'>" + achieved_x * "#" + "|" + "</span>"
            res += "<span style='color:Orange'>" + needed_x * "#" + "|" + "</span>"
            res += "<span style='color:Grey'>" + rest_x * "#" + "</span>"
            res += "</p>"

            # todo (medium prio) generates a new result table everytime
            res += ("<p>Congratulations, you passed the course!</p>"
                        if passed_sofar else "") + \
                   ("<p>" + random.choice(helpers.inspirations) + "</p>"
                        if not passed_sofar and passable_sofar else "") + \
                   ("<p>Unfortunately, it currently looks like it won't be possible for you to reach the minimum "
                    "percentage required for passing this course in this term anymore!</p>"
                        if not passable_sofar else "")
            # res += ("<p>Congratulations, you have already passed the course!</p>"
            #         if self.studentlist[st.id]["Status"] == 1 else "") + \
            #        ("<p>Keep going!</p>"
            #         if self.studentlist[st.id]["Status"] == 0 else "") + \
            #        ("<p>Unfortunately, it currently looks like it won't be possible for you to reach the minimum "
            #         "percentage required for passing this course in this semester anymore!</p>"
            #         if self.studentlist[st.id]["Status"] == -1 else "")

        res = res.replace("</li><br/>", "</li>").replace("<ul><br/>", "<ul>").replace("</ul><br/>", "</ul>")\
            .replace("</h4><br/>", "</h4>").replace("<>", "").replace("<code>", "<code style='color:black'>")
        st.feedback = res
        if not silent:
            print(helpers.points2str(st, self.tasks, self.tasks_total))
            helpers.print_feedback(self.feedback(), st)

        if not silent:
            helpers.print_success("Generated feedback string")


    def comment_crashes(self):
        # todo (medium prio): check if comment already in file
        if self.s.crashes != "(no crash)" and not self.view_only:
            with open(self.s.path_comment, "a+", encoding="utf-8") as f:

                # # check if comment file already contains default comment
                # for def_comment in default_comments:
                #     if def_comment.startswith("Crash"):
                #         f.seek(0)
                #         if default_comments[def_comment][:default_comments[def_comment].index(".")]\
                #                 in f.read():
                #             # s.done_tests = True
                #             # s.done_comment = True
                #             return

                # else: append default comment
                # if not s.done_comment:
                cmnt = self.default_comments["Crash"]
                f.write(cmnt)
                for crash_note in self.s.crashes:
                    f.write("- " + crash_note.replace(" (automatically caught by exception handler)", "") + "\n")
                print("Wrote default comment for crashed submissions\n")
                self.s.done_tests = True
                self.s.done_comment = True


    def comment_plagiarism(self):
        # todo (medium prio): check if comment already in file
        if self.s.plagiarism != "(no plagiarism)" and not self.view_only:
            with open(self.s.path_comment, "a+", encoding="utf-8") as f:

                # # check if comment file already contains default comment
                # for def_comment in default_comments:
                #     if def_comment.startswith("Plagiarism"):
                #         f.seek(0)
                #         if default_comments[def_comment][:default_comments[def_comment].index(".")+1]\
                #                 in f.read():
                #             # self.s.done_tests = True
                #             # self.s.done_comment = True
                #             return

                # else: append default comment
                # if not self.s.done_comment:
                cmnt = ""
                if self.s.plagiarism[1] == "to discuss":
                    return
                elif self.s.plagiarism[1] == "uncertain":
                    cmnt = self.default_comments["Plagiarism uncertain"]
                else:
                    cmnt = self.default_comments["Plagiarism"]
                cmnt = cmnt.replace("(names of the other self.students)",
                            helpers.conjoin(self.s.plagiarism[0]))
                if len(self.s.plagiarism[0]) == 1 and "solution" in self.s.plagiarism[0][0]:
                    cmnt.replace("each of you", "you")
                f.write(cmnt)
                print("Wrote default comment for plagiarized submissions\n")
                self.s.done_tests = True
                self.s.done_comment = True


    def average(self):
        # maxim = [self.students[st].total_points for st in self.students if self.students[st].grader == "Maxim"]
        # natalie = [self.students[st].total_points for st in self.students if self.students[st].grader == "Natalie"]
        # print("Maxim: " + str(round(sum(maxim)/len(maxim), 2)))
        # print("Natalie: " + str(round(sum(natalie)/len(natalie), 2)))
        applicable = {st for st in self.students if self.students[st].done_grading}
        return {task_nr: round((sum([self.students[st].points[task_nr] for st in applicable])/len(applicable)), 1)
                for task_nr in self.tasks}


    def average_total(self):
        return sum(self.average().values())


    def compute_scores(self):
        # todo (medium prio): student table not filled in correctly

        # student-wise average and totals
        self.studentlist_ = [sid for sid in self.studentlist if sid not in ["Average", "Total"]]
        for sid in self.studentlist_:
            applicable = [ass for ass in self.assignments if self.studentlist[sid][ass + "_points"] not in ["", "-"]]
            if len(applicable) > 0:
                self.studentlist[sid]["Points total"] =\
                    sum([self.studentlist[sid][ass + "_points"] for ass in applicable])
                self.studentlist[sid]["Perc average"] =\
                    round((sum([self.studentlist[sid][ass + "_perc"] for ass in applicable])/len(applicable)), 3)
                self.studentlist[sid]["Perc total"] = \
                    round((self.studentlist[sid]["Points total"]/self.studentlist["Total"]["Points total"]), 3)
                self.studentlist[sid]["Remaining"] = \
                    round(((0.6 * self.studentlist["Total"]["Points total"]) - self.studentlist[sid]["Points total"]), 3)
                self.studentlist[sid]["Status"] = \
                    (1 if self.studentlist[sid]["Remaining"] <= 0.0 else
                        (0 if self.studentlist[sid]["Remaining"] <= self.studentlist["Total"]["Remaining"] else
                             (-1 if self.studentlist[sid]["Remaining"] > self.studentlist["Total"]["Remaining"] else
                              "unclear")))

        # assignment-wise average and totals
        self.studentlist_ = [sid for sid in self.studentlist if sid != "Total" and sid != "Average"]
        for ass in self.assignments:
            applicable = [sid for sid in self.studentlist_\
                          if self.studentlist[sid][ass + "_points"] not in ["", "-"]]
            if len(applicable) > 0:
                self.studentlist["Average"][ass + "_points"] =\
                round((sum([self.studentlist[sid][ass + "_points"] for sid in applicable])/len(applicable)), 2)
                self.studentlist["Average"][ass + "_perc"] =\
                round((sum([self.studentlist[sid][ass + "_perc"] for sid in applicable])/len(applicable)), 2)
                self.studentlist["Total"][ass + "_points"] = self.assignments[ass]
                self.studentlist["Total"][ass + "_perc"] = len(applicable)

        # overall average
        for field_name in ["Points total", "Perc average", "Perc total", "Remaining", "Status"]:
            applicable = [sid for sid in self.studentlist_
                          if self.studentlist[sid][field_name] not in ["", "-"]]
            if len(applicable) > 0:
                self.studentlist["Average"][field_name] =\
                    round((sum([self.studentlist[sid][field_name] for sid in applicable])/len(applicable)), 2)

        # overall totals
        applicable = [sid for sid in self.studentlist_
                      if self.studentlist[sid]["Points total"] not in ["", "-"]]
        self.studentlist["Total"]["Perc average"] = len(applicable)
        self.studentlist["Total"]["Perc total"] = round((self.assignments_total/self.studentlist["Total"]["Points total"]), 2)
        self.studentlist["Total"]["Remaining"] = self.studentlist["Total"]["Points total"] - self.assignments_total
        passed = [sid for sid in self.studentlist_ if self.studentlist[sid]["Status"] == 1]
        pending = [sid for sid in self.studentlist_ if self.studentlist[sid]["Status"] == 0]
        failed = [sid for sid in self.studentlist_ if self.studentlist[sid]["Status"] == -1]
        ghosts = len(self.studentlist_)-len(applicable)
        self.studentlist["Total"]["Status"] = \
            str(len(passed)) + ":" + str(len(pending)) + ":" + str(len(failed)) + ":" + str(ghosts)


    def stats(self):
        # todo (low prio): student-specific stats
        # todo (low prio): names for assignments

        header = "Statistics\n" \
                 "=========="

        scale = (self.studentlist["Total"]["Points total"]/100)/2
        applicable = [sid for sid in self.studentlist\
                      if sid not in ["Total", "Average"] and self.studentlist[sid]["Points total"] not in ["", "-"]]
        applicable_ = [sid for sid in self.studentlist if sid not in ["Total", "Average"]]
        points_total = float(self.studentlist["Total"]["Points total"])
        passing_threshold = points_total * 0.6
        total_achieved = round(self.studentlist["Total"]["Perc total"] * points_total, 2)
        total_achieved_perc = round(total_achieved/points_total, 2)
        total_remaining = round(points_total-total_achieved, 2)
        total_remaining_perc = round(total_remaining/points_total, 2)
        avg_achieved = self.studentlist["Average"]["Points total"]
        avg_achieved_perc = self.studentlist["Average"]["Perc total"]
        avg_remaining = self.studentlist["Average"]["Remaining"]

        # todo (low prio): average for current assignment with bars

        progress = helpers.color("ul", "Course progress:") + " "
        progress += helpers.color("green", round(scale * total_achieved) * "#")
        progress += helpers.color("orange", round(scale * (points_total-total_achieved)) * "#")
        # progress += "\n" + len("Course progress:") * "-" + " "
        progress += "\n" + len("Course progress:") * " " + " "
        progress += str(total_achieved) + " points to be gained so far, "
        progress += str(points_total) + " points to be gained in total"

        # timeline += "pend." + "|" + int(pending) * helpers.color("orange", "#") + " "  + "(" + str(pending) + ")\n"
        # timeline += "fail." + "|" + int(failed) * helpers.color("red", "#") + " " + "(" + str(failed) + ")"

        achieved = helpers.color("ul", "Average number of points achieved:") + " "
        achieved += helpers.color("green", round(scale * avg_achieved) * "#")
        achieved += helpers.color("orange", round(scale * avg_remaining) * "#")
        achieved += round(scale * points_total * 0.4) * "#"
        # remaining += "\n" + len("Average number of points achieved:") * "-" + " "
        achieved += "\n" + len("Average number of points achieved:") * " " + " "
        achieved += str(round(avg_achieved, 1)) + " achieved so far, "
        achieved += str(round(avg_remaining, 1)) + " remaining to pass, "
        achieved += str(round(points_total, 1)) + " to be gained in total"

        # todo (low prio): average mark is off by one depending on diff
        assmnts = helpers.color("ul", "Average scores on assignments:") + "\n"
        ass_applicable = [ass for ass in self.assignments if self.studentlist["Average"][ass + "_points"] not in ["", "-"]]
        # assmnts += len("Scores on assignments:") * "-" + "\n"
        avg_avg_pnts = sum([self.studentlist["Average"][ass + "_points"] for ass in ass_applicable])/len(ass_applicable)
        avg_avg_perc = sum([self.studentlist["Average"][ass + "_perc"] for ass in ass_applicable])/len(ass_applicable)
        avg_avg_perc_scaled = round(avg_avg_perc*50)
        for ass in ass_applicable:
            max_pnts = self.studentlist["Total"][ass + "_points"]
            avg_pnts = self.studentlist["Average"][ass + "_points"]
            avg_perc = self.studentlist["Average"][ass + "_perc"]
            avg_perc_scaled = round(avg_perc*50)
            if avg_pnts not in ["", "-"]:
                diff_avg = avg_perc - avg_avg_perc
                diff_avg_scaled = round(diff_avg*50)
                assmnts += ass + " |"
                label = " " + "{0:.1%}".format(avg_pnts/max_pnts) + " (" + str(avg_pnts) + "/" + str(max_pnts) + " points)"
                if diff_avg >= 0:  # larger than or equal to avg, put avg in middle
                    assmnts += (round(avg_avg_perc_scaled)-1) * "#" + helpers.color("orange", "X") + round(diff_avg_scaled+1) * "#"
                    assmnts += label
                else:  # smaller than average, put avg after spaces
                    diff_avg *= -1
                    diff_avg_scaled *= -1
                    assmnts += round(avg_perc_scaled) * "#"
                    if len(label)+2 < diff_avg:  # label fits, put avg afterwards
                        assmnts += label + ((round(diff_avg_scaled) - len(label)) * " ") + helpers.color("orange", "X")
                    else:  # label doesn't fit, put avg before
                        assmnts += (diff_avg_scaled-1) * " " + helpers.color("orange", "X") + label
                assmnts += "\n"
        assmnts += (len("ex_00")+1) * "-" + "\n"
        assmnts += "Average: " + "{0:.1%}".format(avg_avg_perc) + "\n"
        assmnts += "Total: " + str(total_achieved) + " points"

        submissions = helpers.color("ul", "Number of submissions on assignments:") + "\n"
        # submissions += len("Number of submissions:") * "-" + "\n"
        ass_applicable = [ass for ass in self.assignments if self.studentlist["Total"][ass + "_perc"] not in ["", "."]]
        avg_num_subm = sum([self.studentlist["Total"][ass + "_perc"] for ass in ass_applicable])/len(ass_applicable)
        for ass in self.assignments:
            num_subm = self.studentlist["Total"][ass + "_perc"]
            if num_subm not in ["", "-"]:
                diff_avg = num_subm - avg_num_subm
                submissions += ass + " |"
                label = " " + str(num_subm) + " subm."
                if diff_avg >= 0:  # larger than or equal to avg, put avg in middle
                    submissions += (round(avg_num_subm)-1) * "#" + helpers.color("orange", "X") + (round(diff_avg)+1) * "#"
                    submissions += label
                else:  # smaller than average, put avg after spaces
                    diff_avg *= -1
                    submissions += round(num_subm) * "#"
                    if len(label)+2 < diff_avg:  # label fits, put avg afterwards
                        submissions += label + ((round(diff_avg) - len(label)) * " ") + helpers.color("orange", "X")
                    else:  # label doesn't fit, put avg before
                        submissions += (round(diff_avg)-1) * " " + helpers.color("orange", "X") + label
                submissions += "\n"
        subm_total = sum([int(self.studentlist["Total"][ass + "_perc"]) for ass in self.assignments\
                          if self.studentlist["Total"][ass + "_perc"] not in ["", "-"]])
        submissions += (len("ex_00")+1) * "-" + "\n"
        submissions += "Average: " + str(round(avg_num_subm, 1)) + " submissions\n"
        submissions += "Total: " + str(subm_total) + " submissions"

        timeline = helpers.color("ul", "Timeline of threshold passing") + " (passed:pending:failed:inactive)" + helpers.color("ul", ":\n")
        for ass_nr in self.assignments:
            ass_sofar = [ass for ass in self.assignments if int(ass[3:]) <= int(ass_nr[3:])]
            remaining_here = points_total - sum([self.studentlist["Total"][ass + "_points"] for ass in ass_sofar])
            # inactive_here = [sid for sid in applicable_
            #                  if self.studentlist[sid][ass_nr + "_points"] == "-"]
            # passed_here = len([sid for sid in applicable_ if sid not in inactive_here and
            #                    sum([self.studentlist[sid][ass + "_points"]
            #                         for ass in ass_sofar if self.studentlist[sid][ass + "_points"] != "-"])
            #                    >= passing_threshold
            #                    ])
            # pending_here = len([sid for sid in applicable_ if sid not in inactive_here and
            #                     sum([self.studentlist[sid][ass + "_points"]
            #                         for ass in ass_sofar if self.studentlist[sid][ass + "_points"] != "-"])
            #                     < passing_threshold and
            #                     (passing_threshold -
            #                      sum([self.studentlist[sid][ass + "_points"]
            #                          for ass in ass_sofar if self.studentlist[sid][ass + "_points"] != "-"]))
            #                     <= remaining_here
            #                     ])
            # failed_here = len([sid for sid in applicable_ if sid not in inactive_here and
            #                    (passing_threshold -
            #                     sum([self.studentlist[sid][ass + "_points"]
            #                          for ass in ass_sofar if self.studentlist[sid][ass + "_points"] != "-"]))
            #                    > remaining_here
            #                    ])
            inactive_here = [sid for sid in applicable_ if sid not in applicable]
            passed_here = len([sid for sid in applicable if
                               sum([self.studentlist[sid][ass + "_points"]
                                    for ass in ass_sofar if self.studentlist[sid][ass + "_points"] != "-"])
                               >= passing_threshold
                               ])
            pending_here = len([sid for sid in applicable if
                                sum([self.studentlist[sid][ass + "_points"]
                                    for ass in ass_sofar if self.studentlist[sid][ass + "_points"] != "-"])
                                < passing_threshold and
                                (passing_threshold -
                                 sum([self.studentlist[sid][ass + "_points"]
                                     for ass in ass_sofar if self.studentlist[sid][ass + "_points"] != "-"]))
                                <= remaining_here
                                ])
            failed_here = len([sid for sid in applicable if
                               (passing_threshold -
                                sum([self.studentlist[sid][ass + "_points"]
                                     for ass in ass_sofar if self.studentlist[sid][ass + "_points"] != "-"]))
                               > remaining_here
                               ])
            timeline += ass_nr + " |" + \
                        passed_here * helpers.color("green", "#") + \
                        pending_here * helpers.color("orange", "#") + \
                        failed_here * helpers.color("red", "#") + \
                        len(inactive_here) * "#" + \
                        " " + "(" + \
                        helpers.color("green", "{:02d}".format(passed_here)) + ":" + \
                        helpers.color("orange", "{:02d}".format(pending_here)) + ":" + \
                        helpers.color("red", "{:02d}".format(failed_here)) + ":" + \
                        "{:2d}".format(len(inactive_here)) + \
                        ")\n"
        timeline += "------"

        status = helpers.color("ul", "Status:") + " "
        passed, pending, failed, ghosts = self.studentlist["Total"]["Status"].split(":")
        themes = [["self.students registered", "passed", "pending", "failed", "inactive"],
                  ["players in the game", "winners", "still fighting", "losers", "slackers"]
                  # ["kids on the boat", "on the save side of the river", "still paddling", "drowned", "river ghosts"],
                  # ["kids in the woods", "made it home", "still wandering around", "lost forever", "forest spirits"],
                  # ["little monkeys jumping on a bed", "jumped high enough to save their a**", \
                  # "still jumping bumping their head", "jumped too low and fell out of the bed",,\
                  # "of the monkeys are long dead"]
                  ]
        theme = random.choice(themes)
        status += helpers.color("green", (int(passed) * "#")) if int(passed) > 0 else ""
        status += helpers.color("orange", (int(pending) * "#")) if int(pending) > 0 else ""
        status += helpers.color("red", (int(failed) * "#")) if int(failed) > 0 else ""
        status += (int(ghosts) * "#") if int(ghosts) > 0 else ""
        # status += "\n" + len("Status:") * "-" + " "
        status += "\n" + len("Status:") * " " + " "
        status += helpers.inflect(len(self.studentlist)-2, theme[0]) + ", "
        status += helpers.inflect(passed, theme[1]) + ", "
        status += helpers.inflect(pending, theme[2]) + ", "
        status += helpers.inflect(failed, theme[3]) + ", "
        status += helpers.inflect(ghosts, theme[4])

        # todo (low prio): average doesn't show when noone has average points
        # todo (low prio): if ub is in last range, ub is still shown as additional entry
        # todo (low prio): use percentages instead of points?
        freqdist = helpers.color("ul", "Frequency distribution of points achieved:\n")
        # scores = {sid: self.studentlist[sid]["Points total"] for sid in applicable}
        scores = {sid: self.studentlist[sid]["Perc total"] for sid in applicable}
        fd = {val: list(scores.values()).count(val) for val in scores.values()}
        # ub = math.ceil(max([total_achieved] + [self.studentlist[sid]["Points total"] for sid in applicable]))
        ub = math.ceil((max([self.studentlist["Total"]["Perc total"]] +\
                                [self.studentlist[sid]["Perc total"] for sid in applicable]))*100)/100
        # steps = math.ceil(ub/10)
        # steps = math.ceil((ub/10)*100)/100
        steps = round(.05 * round(float(ub/10)/.05), 2)
        # ranges = reversed([(i, i + steps) for i in range(0, ub, steps)])
        ranges = reversed([(i/100, i/100 + steps) for i in range(0, round(ub*100), round(steps*100))])
        for rng in ranges:
            num_vals = sum([fd[val] for val in fd if rng[0] <= val < rng[1]])
            passed = rng[0] >= 0.6
            passable = rng[1] - 1/100 + total_remaining_perc >= 0.6
            avg_here = rng[0] <= avg_achieved_perc < rng[1]
            # freqdist += "{:05.1%}".format(rng[0]) + " <= p < " + "{:05.1%}".format(rng[1])
            freqdist += "{:4.0%}".format(rng[0]) + " <= p < " + "{:4.0%}".format(rng[1])
            # if rng != ub:
            #     freqdist += "{:04.1f}".format(rng[0]) + " <= p < " + "{:04.1f}".format(rng[1])
            #     num_vals = sum([fd[val] for val in fd if rng[0] <= val < rng[1]])
            #     passed = rng[1] >= 0.6 * points_total
            #     passable = rng[0] + total_remaining >= 0.6 * points_val
            #     avg_here = rng[0] <= avg_achieved < rng[1]
            # else:
            #     if rng < max(fd):
            #         freqdist += str(float(rng)) + " <= p < " + str(float(max(fd)))
            #     else:
            #         freqdist += len(str(float(rng))) * " " + "    p = " + str(float(rng))
            #     num_vals = sum([fd[val] for val in fd if val >= rng])
            #     passed = rng >= 0.6 * points_total
            #     passable = rng + total_remaining >= 0.6
            #     avg_here = avg_achieved == rng
            col = "orange"
            if passed and passable:
                col = "green"
            elif not passed and passable:
                col = "orange"
            elif not passed and not passable:
                col = "red"
            if avg_here:
                freqdist += " " + helpers.color("orange", "X") + (num_vals * helpers.color(col, "#"))
            else:
                freqdist += " |" + (num_vals * helpers.color(col, "#"))
            # freqdist += helpers.color("orange", "X") + (num_vals * helpers.color(col, ("#" if not avg_here else "X")))
            freqdist += " " + str(num_vals)
            freqdist += " (" + "{0:.0%}".format(num_vals/len(scores)) + ")"
            freqdist += "\n"

        highscores = helpers.color("ul", "Highscore:\n")
        # highscores += len("High scores:") * "-" + "\n"
        ranks = sorted({self.studentlist[sid]["Points total"] for sid in applicable}, reverse=True)
        scores = sorted(applicable, key=lambda x: self.studentlist[x]["Points total"], reverse=True)
        max_len_label = max([len(self.studentlist[sid]["First name"] + " " + self.studentlist[sid]["Last name"])
                             for sid in applicable])
        best = {ass: sorted([(sid, self.studentlist[sid]["Points total"])
                             for sid in applicable if sum([self.studentlist[sid][ass_nr + "_points"]
                             for ass_nr in self.assignments if
                             int(ass_nr[3:]) <= int(ass[3:]) and
                             self.studentlist[sid][ass_nr + "_points"] not in ["", "-"]]) >= passing_threshold],
                             key=lambda kv: kv[1], reverse=True)
                             for ass in self.assignments}
        rank = 0
        for ass in sorted(best, key=lambda kv: kv[0]):
            for sid, score in best[ass]:
                if rank <= 10 or True:
                    name = self.studentlist[sid]["First name"] + " " + self.studentlist[sid]["Last name"]
                    if name not in highscores:
                        buffer = max_len_label - len(name)
                        if str(score) + "/" not in highscores or True:
                            rank += 1
                        highscores += "{: >2}".format(rank) + ". " +\
                            name + buffer * " " + ": " + \
                            "{0:04.1f}".format(score) + "/" + str(total_achieved) + \
                            " points (" + "{:4.0%}".format(score/total_achieved) + ")" +\
                            "; passed with " + ass + "\n"
        for sid in scores:
            if rank <= 10 or True:
                # if sid not in [[b[0] for b in b] for b in best.values()]:
                score = self.studentlist[sid]["Points total"]
                name = self.studentlist[sid]["First name"] + " " + self.studentlist[sid]["Last name"]
                if name not in highscores:
                    buffer = max_len_label - len(name)
                    if str(score) + "/" not in highscores or True:
                        rank += 1
                    highscores += "{: >2}".format(rank) + ". " +\
                                  name + buffer * " " + ": " +\
                                  "{0:04.1f}".format(score) + "/" + str(total_achieved) +\
                                  " points (" + "{:4.0%}".format(score/total_achieved) + ")" +\
                                  "; failed\n"
        # for sid in scores[:10]:
        #     score = self.studentlist[sid]["Points total"]
        #     name = self.studentlist[sid]["First name"] + " " + self.studentlist[sid]["Last name"]
        #     buffer = max_len_label - len(name)
        #     highscores += "{: >2}".format(ranks.index(score)+1) + ". " +\
        #                   name + buffer * " " + ": " +\
        #                   "{0:04.1f}".format(score) + "/" + str(total_achieved) +\
        #                   " points (" + "{:4.0%}".format(score/total_achieved) + ")\n"
        # highscores += "...\n"
        # for sid in scores[-5:]:
        #     score = self.studentlist[sid]["Points total"]
        #     name = self.studentlist[sid]["First name"] + " " + self.studentlist[sid]["Last name"]
        #     buffer = max_len_label - len(name)
        #     highscores += "{: >2}".format(ranks.index(score)+1) + ". " +\
        #                   name + buffer * " " + ": " +\
        #                   "{0:04.1f}".format(score) + "/" + str(total_achieved) +\
        #                   " points (" + "{:4.0%}".format(score/total_achieved) + ")\n"

        print()
        print(header)
        print()
        print(helpers.average2str(self.average(), self.average_total(), self.students, self.tasks, self.tasks_total))
        # print(points)
        print()
        print(progress)
        print()
        print(assmnts)
        print()
        print(submissions)
        print()
        print(timeline)
        print(status)
        print()
        print(achieved)
        print()
        print(freqdist)
        print(highscores)

        # print(helpers.color("ul", "self.students who could pass with a bonus assignment worth 16 points:"))
        # bonus = [sid for sid in applicable if 44.0 <= float(self.studentlist[sid]["Points total"]) < 60.0]
        # for sid in bonus:
        #     print(self.studentlist[sid]["First name"] + " " + self.studentlist[sid]["Last name"] + ": " +
        #     str(self.studentlist[sid]["Remaining"]))


    def update_student_data(self):
        # todo (medium prio): doesn't work, since student.update_data() requires arguments

        for st in self.students:
            self.students[st].update_data()


    def verify_overwrite(self):
        # todo (low prio): instead of verify overwrite, just don't apply changes in view-only mode

        if self.view_only:
            match helpers.input_color("orange", "WARNING: You selected to process this student in view-only mode. \n"
                                 "Are you sure you want to overwrite the existing data? ('y'/'n') "):
                case "y" | "yes":
                    pass
                case _:
                    return False
        return True


    def verify_done(self):
        # todo (medium prio): check in the very end that everyone has undergone tests and comment?

        if self.s is None:
            return True

        if not self.s.done_grading:
            match input("Would you like to mark the previous student (" + self.s.first_name + " " + self.s.last_name +
                           ") as graded? ('y'/'n'/'r' to return) "):

                case "y" | "yes":
                    confirm_done = True
                    if confirm_done and not self.s.done_tests:
                        match helpers.input_color("orange",
                                             "WARNING: You didn't run the tests. "
                                             "Are you sure you want to mark this student as graded? ('y'/'n'/'r' to return) "):
                            case "y" | "yes":
                                confirm_done = True
                            case "n" | "no":
                                confirm_done = False
                            case _:
                                return False
                    if confirm_done and not self.s.done_comment:
                        match helpers.input_color("orange",
                                             "WARNING: You didn't write a comment. "
                                             "Are you sure you want to mark this student as graded? ('y'/'n'/'r' to return) "):
                            case "y" | "yes":
                                confirm_done = True
                            case "n" | "no":
                                confirm_done = False
                            case _:
                                return False
                    if confirm_done:
                        self.s.done_grading = True
                        self.compute_scores()
                        self.export_results(False)
                    return True  # student graded (or not), continue
    
                case "n" | "no":  # student not graded, but continue
                    return True
    
                case _:  # return
                    return False

        else:
            self.export_results(False)
            return True


    def import_results(self, silent=True, initial=False):
        return
        if initial:
            print("Importing results...")

        if not exists(self.path_results_file):  # create results.tsv
            with open(self.path_results_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=field_names_results, delimiter="\t")
                writer.writeheader()
            if not silent:
                print("Created results.tsv")

        else:  # import results.tsv data into student dict
            with open(self.path_results_file, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f, delimiter="\t")
                for row in reader:
                    st = Student(self)
                    for field in ["id", "last_name", "first_name", "matr_nr", "moodle_id",
                                  "feedback", "grader", "notes", "crashes"]:
                        setattr(st, field, row[field])
                    for field in ["points", "total_points", "plagiarism", "done_tests", "done_comment", "done_grading"]:
                        if not row[field] == "(no plagiarism)": setattr(st, field, eval(row[field]))
                    # for field in ["path_raw_dirname", "path_raw", "path_graded_dirname", "path_graded", "path_comment"]:
                    #     setattr(st, field, row[field])
                    st.dirname_graded = str(st.id) + \
                                       "_" + helpers.ascii(st.last_name).replace(" ", "-") + \
                                       "_" + helpers.ascii(st.first_name).replace(" ", "-")
                    st.path_graded = join(self.path_subm_graded, st.dirname_graded)
                    if not exists(st.path_graded): os.makedirs(st.path_graded)
                    st.path_comment = join(st.path_graded, "comment.md")
                    if not exists(st.path_comment):
                        with open(st.path_comment, "w", encoding="utf-8") as f: pass
                    self.students[st.id] = st
            if not silent:
                helpers.print_color("green",
                            "SUCCESS: Imported " + helpers.inflect(reader.line_num-1, "entries ") +
                            "from results.tsv into self.students dict")

        # import self.studentlist.tsv data into self.studentlist dict
        with open(self.path_studentlist_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")

            # append missing field names
            field_names = reader.fieldnames
            for field_name in ["Points total", "Perc average", "Perc total", "Remaining", "Status"]:
                if field_name not in field_names:
                    field_names.append(field_name)
            if self.tasks_total[0] > 0:
                if "ex_" + self.ex_nr + "_points" not in field_names:
                    field_names.append("ex_" +self.ex_nr + "_points")
                if "ex_" + self.ex_nr + "_perc" not in field_names:
                    field_names.append("ex_" +self.ex_nr + "_perc")

            # fill self.studentlist with data from reader
            for row in reader:
                sid = row["ID"]
                if sid not in self.studentlist:
                    self.studentlist[sid] = {"ID": sid}
                if not row["ex_" +self.ex_nr + "_points"]:
                    row["ex_" +self.ex_nr + "_points"] = "-"
                if not row["ex_" +self.ex_nr + "_perc"]:
                    row["ex_" +self.ex_nr + "_perc"] = "-"
                if sid == "Total":
                    row["ex_" +self.ex_nr + "_points"] = self.tasks_total[0]
                    row["ex_" +self.ex_nr + "_perc"] = len(self.raw)
                    if field_name not in row:
                        row.append((field_name, "-"))
                    entry = row[field_name] if row[field_name] != "" else "-"
                    self.studentlist[sid].update({field_name: entry})
                for field_name in field_names[4:]:
                    if field_name not in self.studentlist[sid]:
                        self.studentlist[sid][field_name] = "-"
                    entry = self.studentlist[sid][field_name]
                    if entry != "-" and isinstance(entry, str) and not (sid == "Total" and field_name == "Status"):
                        self.studentlist[sid][field_name] = eval(entry)
            for row in self.studentlist:
                print(self.studentlist[row])

            # compute assignments
            assignments = {field_name[:5]: self.studentlist["Total"][field_name]\
                           for field_name in field_names\
                           if field_name.startswith("ex_") and field_name.endswith("_points")\
                           and self.studentlist["Total"][field_name] != "" and self.studentlist["Total"][field_name] != "-"}
            if self.tasks_total[0] > 0:
                assignments["ex_" +self.ex_nr] = self.tasks_total[0]
            assignments_total = sum([assignments[ass] for ass in assignments])
            assignments_count = len(assignments)

            # compute scores
            self.compute_scores()

        if not silent:
            helpers.print_color("green",
                        "SUCCESS: Imported " + helpers.inflect(reader.line_num - 1, "entries ") +
                        "from self.studentlist.tsv into self.studentlist dict\n")

        # update student data and save again
        if self.s is not None:
            curr_student = self.s.id
        self.obtain_files(silent)
        print("Updating student data...")
        # todo (low prior): get this back, but without absolute paths (causes conflict)
        for st in self.students.values():
            st.update_data(self.notes, self.crashes, self.plagiarism, self.tasks, self.tasks_total)
        if initial:
            for st in self.students.values():
                self.points_total(st)
                self.feedback(st)
            self.compute_scores()
        if not silent:
            helpers.print_color("green",
                        "SUCCESS: Updated data for " + helpers.inflect(len(self.students), "self.students"))
        self.export_results()
        if s is not None:
            s = self.students[curr_student]

        if initial:
            print()
            print(str(len(self.raw)) + " raw submissions - " +
                  str(len(self.graded())) + " graded, " + str(len(self.pending())) + " pending")


    def export_results(self, silent=True):
        # todo (medium prio): update self.studentlist only when saving results
        # todo (high prio): encoding issue fixed?
        # todo (low prio): prints message twice when hitting 'save'

        if self.s is not None:
            self.points_total(self.s)
            self.feedback(self.s)
        if not silent:
            for st in self.students.values():
                self.points_total(st)
                self.feedback(st)
            self.compute_scores()
        if not silent:
            helpers.print_success("Saved changes in current student")
            self.compute_scores()

        # results.tsv
        with open(self.path_results_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=field_names_results, delimiter="\t")
            writer.writeheader()
            for st in self.students.values():
                row = {}
                for field in field_names_results:
                    row[field] = getattr(st, field)
                writer.writerow(row)
        if not silent:
            helpers.print_success("Exported " + helpers.inflect(len(self.students), "entries ") +
                        "from self.students dict into results.tsv")

        # self.studentlist.tsv
        # for id in self.studentlist:
        #     print(str(self.studentlist[id]))
        with open(self.path_studentlist_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=field_names, delimiter="\t")
            writer.writeheader()
            # header rows
            for id in ["Total", "Average"]:
                row = {"ID": id}
                for key, value in self.studentlist[id].items():
                    row[key] = self.studentlis[id][key]
                writer.writerow(row)
            # student rows
            for id in sorted(self.studentlis)[:-2]:
                row = {"ID": id}
                for key, value in self.studentlis[id].items():
                    row[key] = self.studentlis[id][key]
                writer.writerow(row)
        if not silent:
            helpers.print_success("Exported " + helpers.inflect(len(self.studentlis), "entries ") +
                        "from self.studentlist dict into self.studentlist.tsv")


    def export_results_moodle(self):
        if self.tasks_total[0] > 0:
            self.assignmentscompute_scores()
        self.export_results()

        if self.pending():
            helpers.print_warning("" + str(len(self.pending())) + " self.students are marked as not yet graded.")
            match input("Are you sure you want to proceed? ('y'/'n') "):
                case "y" | "yes":
                    pass
                case _:
                    return

        if not exists(self.path_moodle_file_raw):
            helpers.print_error("results_moodle_raw.csv not found")
            return

        with open(self.path_moodle_file_raw, "r", encoding="utf-8-sig", newline="") as raw:
            reader = csv.DictReader(self.raw, delimiter=",")
            # print(reader.fieldnames)
            with open(self.path_moodle_file, "w", encoding="utf-8-sig", newline="") as filled:
                writer = csv.DictWriter(filled, fieldnames=reader.fieldnames, delimiter=",")
                writer.writeheader()
                for row in reader:
                    if "Keine Abgabe" in row["Status"]:
                        writer.writerow(row)
                        continue
                    moodle_id = row['ID'][row['ID'].index("/in")+3:]
                    full_name = row["Vollständiger Name"]
                    moodle_ids = [self.students[id].moodle_id for id in self.students]
                    if moodle_id not in moodle_ids:
                        helpers.print_warning("" + full_name + " (moodle id " + moodle_id + ") "
                                    "submitted but was not found in self.students dict")
                        continue
                    st = self.students[self.lookup_student(full_name)["ID"]]
                    if st is not None:
                        row["Bewertung"] = str(st.total_points).replace(".", ",")
                        row["Feedback als Kommentar"] = st.feedback
                        writer.writerow(row)

        helpers.print_color("green",
                    "SUCCESS: Exported " + helpers.inflect(len(self.students), "entries ") + "from self.students dict into results_moodle.csv\n")


    def export_passed(self):
        filename = join(self.path_exercises, "passed.tsv")
        with open(filename, "w") as f:
            f.write("Last name\tFirst name\tMatrNr\n")
            applicable = [sid for sid in self.studentlist
                          if sid not in ["Total", "Average"] and self.studentlist[sid]["Perc total"] != "-"]
            passed = [sid for sid in applicable if self.studentlist[sid]["Status"] == 1]
            for sid in passed:
                f.write(self.studentlist[sid]["Last name"] + "\t" +
                        self.studentlist[sid]["First name"] + "\t" +
                        self.studentlist[sid]["MatrNr"] + "\n")
        helpers.print_success("Wrote passing self.students (" +
                    str(len(passed)) + " passed/" + str(len(applicable)) + " applicable" +
                    ") to " + filename)

    def graded(self):
        return [name for name in self.raw
                if self.lookup_student(name) is not None and self.lookup_student(name)["ID"] in self.students \
                and self.students[self.lookup_student(name)["ID"]].done_grading]

    def pending(self):
        return [name for name in self.raw
                if self.lookup_student(name) is not None and not self.lookup_student(name)["ID"] in self.students \
                or not self.students[self.lookup_student(name)["ID"]].done_grading]

    def print_raw(self):
        list_graded = self.graded()
        list_pending = self.pending()

        if int(self.ex_nr) % 2 == 0:
            graders = ["Natalie", "Maxim"]
        else:
            graders = ["Maxim", "Natalie"]
        thresholds = [i * round(len(self.raw) / len(graders)) for i in range(1, len(graders))]

        print()
        print(str(len(self.raw)) + " raw submissions - " +
                str(len(list_graded)) + " graded ('X'), " + str(len(list_pending)) + " pending ('O')")
        for idx, subm in enumerate(self.raw):
            print("[" + str(idx + 1).zfill(2) + "]" + \
                    (helpers.color("green", " (X) ") if subm in list_graded else helpers.color("orange", " (O) ")) + subm)
            if idx + 1 in thresholds:
                pos = self.thresholds.index(idx + 1)
                print("-------" + \
                        (" ↑ " + graders[pos] if 0 <= pos < len(graders) else "") + \
                        (" ↓ " + graders[pos + 1] if 0 <= pos + 1 < len(graders) else "") + \
                        " -------")
            # id = subm.split("_")[1]
            # st = self.students[id]
            # print("[" + str(idx + 1).zfill(2) + "]" + " (" +
            #       ("x" if st is not None and st.done_tests else "o") +
            #       ("x" if st is not None and st.done_comment else "o") +
            #       ("X" if st is not None and st.done_grading else "O") +
            #       ") " + subm)
        print()

    def print_graded(self):
        print()
        print(str(len(self.graded())) + " submissions marked as graded ('X'):")
        for subm in self.graded():
            idx = self.raw.index(subm)
            print("[" + str(idx + 1).zfill(2) + "]" + helpers.color("green", " (X) ") + subm[:subm.index("_")])
        print()

    def print_pending(self):
        print(str(len(self.pending())) + " submissions marked as not yet graded ('O'):")
        for subm in self.pending():
            idx = self.raw.index(subm)
            print("[" + str(idx + 1).zfill(2) + "]" + helpers.color("orange", " (O) ") + subm[:subm.index("_")])
        print()


    def lookup_student(self, raw_name):
        for id in self.studentlist:
            first_name = self.studentlist[id]["First name"]
            last_name = self.studentlist[id]["Last name"]
            full_name = first_name + " " + last_name
            for name in [full_name, first_name, last_name]:
                if helpers.ascii(raw_name.lower()) == helpers.ascii(name.lower()):
                    return self.studentlist[id]
        helpers.print_error("name " + raw_name + " was not found in self.studentlist")


    def print_student(self):
        if self.s is None:
            print("No current student")
            return

        print("Current student:\n"
            "----------------")
        self.s.print_data()
        # s.print_data_full()


    def print_students(self):
        print("Student objects in local memory:\n")
        # print(self.students)
        for id in self.students:
            self.students[id].print_data()
            print()


    def goto_student(self):
        valid_input = False
        while not valid_input:
            answer = input("Number or name of student ('r' to return): ")
            match answer:
                case "r" | "return":
                    return
                case answer if answer.isdigit() and 0 < int(answer) <= len(self.raw):
                    idx = int(answer)
                    valid_input = True
                case answer if helpers.ascii(answer.lower()) in [helpers.ascii(name.lower()) for name in self.names]:
                    if self.names.count("answer") > 1:
                        helpers.print_error("There is more than one student of this name - "
                                        "please specify the full name or the number")
                        continue
                    else:
                        full_name = self.lookup_student(answer)["First name"] + " " + self.lookup_student(answer)["Last name"]
                        idx = self.raw.index(full_name) + 1
                        valid_input = True
                case _:
                    helpers.print_error("Not a valid name or number")
        print("Going on to student #" + str("{0:02d}".format(idx)) + " (" + self.raw[idx - 1] + ")...")
        self.next_student(idx)
