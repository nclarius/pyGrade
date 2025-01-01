"""
Definition of a student
"""

import os
from os.path import *


class Student(object):

    def __init__(self, a):
        # student metadata
        self.a = a
        self.index = "(no index)"
        self.id = "(no ID)"
        self.last_name = "(no last name)"
        self.first_name = "(no first name)"
        self.matr_nr = "(no matr nr)"
        self.moodle_id = "(no moodle ID)"
        # self.path_feedback = ""
        # results
        self.points = {}
        self.total_points = 0.0
        self.feedback = "(no feedback)"
        self.grader = "(no grader)"
        self.notes = "(no notes)"
        self.crashes = "(no crash)"
        self.plagiarism = "(no plagiarism)"
        # state of grading process
        self.done_tests = False
        self.done_comment = False
        self.done_grading = False
        # paths
        self.dirname_raw = ""
        self.dirname_graded = ""
        self.path_raw = ""
        self.path_graded = ""
        self.path_comment = ""

    def __repr__(self):
        return "student: " + self.first_name + " " + self.last_name

    # def full_name(self):
    #     return self.first_name + " " + self.last_name

    # def dirname_raw(self):
    #     return grading.normalize(self.full_name()) + "_" + self.moodle_id + "_assignsubmission_file_"
    #
    # def dirname_graded(self):
    #     return self.id + "_" + self.last_name + "_" + self.first_name
    #
    # def path_raw(self):
    #     global path_subm_raw
    #     return os.path.abspath(os.path.join(path_subm_raw, self.dirname_raw))
    #
    # def path_graded(self):
    #     global path_subm_graded
    #     return os.path.abspath(os.path.join(path_subm_graded, self.dirname_graded))
    #
    # def path_comment(self):
    #     return os.path.abspath(os.path.join(self.path_graded, "comment.md"))

    def print_data(self):
        for (var_name, var_value) in self.__dict__.items():
            if not var_name.startswith("path") and not var_name.startswith("dirname") and var_name != "feedback":
                print(str(var_name) + ": " + str(var_value))

    def print_data_full(self):
        for (var_name, var_value) in self.__dict__.items():
            print(str(var_name) + ": " + str(var_value))
        # for key, value in {"dirname_raw: ": self.dirname_raw, "dirname_graded: ": self.dirname_graded,
        #                    "path_raw: ": self.path_raw, "path_graded: ": self.path_graded,
        #                    "path_comment: ": self.path_comment}.items():
        #     print(key + value)

    def update_data(self, notes, crashes, plagiarism, tasks, tasks_total):

        # update total points
        # todo (medium prio): identical to function "total_points()"
        self.total_points = sum(self.points.values())

        # # update comment file
        # if self.path_comment != "":
        #     # todo (medium prio): identical to function "feedback()"
        #     # todo (medium prio): markdown: when newline? first replace "\n" with "<br/>", later with ""?
        #     res = ""
        #     res += "<h5>Points achieved:</h5>"
        #     res += grading.markdown.markdown(grading.points2str(self, tasks, tasks_total))\
        #         .replace("Points achieved:\n", "")\
        #         .replace("\r\n", "<br/>").replace("\n", "<br/>").replace("\r", "<br/>")
        #
        #     res += "<h5Comments:</h5>"
        #     if os.path.isfile(self.path_comment):
        #         with open(self.path_comment, "r") as comment_file:
        #             cmt = comment_file.read()
        #             if cmt == "":
        #                 cmt = "-"
        #                 self.done_comment = False
        #             else:
        #                 self.done_comment = True
        #             res += grading.markdown.markdown(cmt)\
        #                 .replace("\r\n", "<br/>").replace("\n", "<br/>").replace("\r", "<br/>")
        #     res += "<p>Your submission was graded by " + self.grader + ".</p>"
        #
        #     res = res.replace("</li><br/>", "</li>").replace("<ul><br/>", "<ul>")
        #     self.feedback = res
        
        # update notes
        for note in notes:
            id = note[0]
            note = note[1] if note[1] != "" else "(no comment about the note)"
            if id == self.id:
                if note not in self.notes:
                    if self.notes == "(no notes)":
                        self.notes = [note]
                    else:
                        self.notes.append(note)

        # update crash notes
        for crash in crashes:
            id = crash[0]
            note = crash[1] if crash[1] != "" else "(no comment about the crash)"
            if id == self.id:
                if note not in self.crashes:
                    if self.crashes == "(no crash)":
                        self.crashes = [note]
                    else:
                        self.crashes.append(note)

        # update plagiarism notes
        for plag in plagiarism:
            student_cluster = plag[0]
            note = plag[1] if plag[1] != "" else "(no comment about the plagiarism)"
            for st_tuple in student_cluster:
                name = st_tuple[0]
                moodle_id = st_tuple[1]
                if moodle_id == self.moodle_id:
                    names = []
                    for st_tuple in student_cluster:
                        if st_tuple[1] == "solution":
                            name = "the exemplary solution from " + st_tuple[2]
                            moodle_id = ""
                        else:
                            name = st_tuple[0]
                            moodle_id = st_tuple[1]
                        if moodle_id != self.moodle_id:
                            names.append(name)
                    self.plagiarism = (names, note)
                    break
