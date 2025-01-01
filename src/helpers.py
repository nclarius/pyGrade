#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Helper functions
"""

import grading
import os, getpass, random, atexit


###################
# interaction
###################

def debug_mode():
    """
    Whether to print debug information.
    :return: whether to enable debug mode specific statements
    :rtype: bool
    """
    return grading.debug and get_grader() == "Natalie"


def print_help():
    """
    Print help information for the available actions.
    :return: None
    """
    print("\n"
          "Available options:\n"
          "------------------\n"
          "- h/help:\t\t\t\thelp for next action\n"
          "Accessing students:\n"
          "- n/next/next student:\tgo to next student\n"
          "- prev/previous:\t\tgo to previous student\n"
          "- g/go to:\t\t\t\tgo to student by index\n"
          "- reload:\t\t\t\treload current student\n"
          "- graded:\t\t\t\tprint list of submissions marked as graded\n"
          "- pending/ungraded:\t\tprint list of submissions marked as yet to be graded\n"
          "Operations on students:\n"
          "- t/tests/run tests:\trun tests on current student\n"
          "- p/points/edit points:\tmanually edit the points achieved\n"
          "- c/comment:\t\t\topen the comment file\n"
          "- f/feedback:\t\t\tshow the feedback string\n"
          "- note:\t\t\t\t\tshow note for graders\n"
          "- status:\t\t\t\tshow and edit grading status\n"
          "Handling student data in local memory:\n"
          "- student:\t\t\t\tprint data of current student object\n"
          "- students:\t\t\t\tprint dict of all students\n"
          "- id:\t\t\t\t\tprint data of student by id\n"
          "- backup:\t\t\t\tcreate a backup of current student object\n"
          "- reset:\t\t\t\treset student object to backup\n"
          "- delete:\t\t\t\tdelete current student object\n"
          "Data import and export:\n"
          "- s/save/export:\t\tsave current student data into results.tsv\n"
          "- reimport:\t\t\t\tre-import results.tsv and external files\n"
          "- moodle:\t\t\t\texport results into moodle.csv\n"
          "- passed:\t\t\t\texport passed students into passed.tsv\n"
          "Viewing data:\n"
          "- main file:\t\t\topen the main file\n"
          "- results:\t\t\t\topen results.tsv\n"
          "- studentlist:\t\t\topen studentlist.tsv\n"
          "- notes:\t\t\t\topen notes.txt\n"
          "- crashes:\t\t\t\topen crashes.txt\n"
          "- plagiarism:\t\t\topen plagiarism.txt\n"
          "- avg/average:\t\t\tprint average points achieved in tasks\n"
          "Grading process:\n"
          "- restart:\t\t\t\tre-initialize exercise to reload files\n"
          "- e/end/end grading:\tend grading\n"
          "\n")


def get_grader():
    """
    Get the name of the current grader from the system username
    :return: name of the grader
    :rtype: str
    """
    match getpass.getuser():
        case "natalie":
            return "Natalie"
        case "maxim":
            return "Maxim"
        case "johannes" | "jdellert":
            return "Johannes"
        case _:
            print_error("Username not found")


def open_by_grader_preference(filepath):
    """
    Open a file with the application of the grader's preference.
    :param filepath: path of the file to open
    :return: None
    """
    match get_grader():
        case "Natalie":
            os.system("code " + filepath + "&")
        case "Maxim":
            if filepath.endswith(".py"):
                os.system("gedit " + filepath + "&")
            else:
                os.system("gedit " + filepath + "&")
        case "Johannes":
            if filepath.endswith(".py"):
                os.system("mate.open " + filepath)
            else:
                os.system("gedit " + filepath + "&")


###################
# AI module
###################
greetings = ["Hi", "Hej", "Ahoy", "Moin", "Hey", "Howdy", "Sup,", "Hiya", "Yo", "привіт", "Long time no see,",
         "Hey there,", "Howdy", "Soooo good to see you,", "Cheerio,", "Qapla',", "Welcome back,",
         "Welcome aboard,", "Hail to thee,"]
farewells = ["Bye", "See ya,", "Hej då", "до побачення,", "I'll miss you so much,", "Noooooooo please don't leave me,",
         "So long and thanks for all the fish,",
         "Have a nice day, and don't forget your lunchbox,",
         "Fine, you graded your homework, you can go. But be back before dawn,",
         "Drive carefully, and call me when you're back home safe,"]
inspirations = ["Keep going!", "Hang in there!", "Keep fighting!", "Keep it up!", "Keep rollin'!", "Stay strong!"]


def greeting():
    print(random.choice(greetings) + " " + get_grader() + "!")

farewelled = True
@atexit.register
def farewell():
    global farewelled
    if not farewelled:
        print("\n" + random.choice(farewells) + " " + get_grader() + "!")
        farewelled = True


###################
# color printing
###################

def color(col, str):
    """
    Format a string in the specified color
    :param col: the color to format the string in
    :type col: col
    :param str: the string to format
    :type str: str
    :return: str formatted in col
    :rtype: str
    """
    # begin sequence
    match col:
        case "bf":
            pfx = '\33[1m'
        case "ul":
            pfx = '\033[4m'
        case "it":
            pfx = '\33[3m'
        # colors
        case "green":
            pfx = '\033[32m'
        case "yellow":
            pfx = '\033[93m'
        case "orange":
            pfx = '\033[33m'
        case "red":
            pfx = '\033[31m'

        case _:
            print_error("Color " + col + " does not exist")
            return

    # end sequence
    sfx = '\033[0m'
    return pfx + str + sfx


def print_color(col, str):
    print(color(col, str))


def input_color(col, str):
    return input(color(col, str))

def print_success(str):
    print_color("green", "SUCCESS: " + str)

def print_info(str):
    print_color("yellow", "INFO: " + str)

def print_warning(str):
    print_color("orange", "WARNING: " + str)

def print_error(str):
    print_color("red", "ERROR: " + str)



###################
# string operations
###################

def ascii(name):
    """
    Replace any special characters by ASCII characters.
    :param name: the name ot normalize
    :type name: str
    :return: the normalized version of name
    :rtype: str
    """
    return name.replace("'", "")


def inflect(num, word):
    """
    Concatenate a number and a word in singular or plural form depending on the number.
    :param word: the number to base the inflection on
    :type num: int
    :param word: the word in plural form
    :type word: str
    :return: word if num==1, else the singular form of the word
    :rtype: str
    """
    res = str(num) + " "
    if float(num) == 1.0 and "s" in word:
        s_pos = word.rfind("s")
        if word[s_pos - 2:s_pos] != "ie":
            res += word[:s_pos] + word[s_pos + 1:]
        else:
            res += word[:s_pos - 2] + "y" + word[s_pos + 1:]
    else:
        res += word
    return res


def conjoin(lst):
    """
    Conjoin a list of words with commas and 'and'.
    Example: conjoin(['apple', 'banana', 'tomato']) == 'apple, banana and tomato'
    :param lst: the list of words to be conjoined
    :type lst: list[str]
    :return: the string of conjoined words
    :rtype: str
    """
    return ((", ".join(lst[:-1])) + " and " if len(lst) > 1 else "") + lst[-1]


def extract_infix(fullstr, start, end):
    """
    Extract a substring of fullstr that occurs between start and end.
    Example: extract_infix('abcdef', 'b', 'ef') = 'cd'
    :param fullstr: the string to take the substring from
    :type fullstr: str
    :param start: the substring preceding the substring to be extracted
    :type start: str
    :param end: the substring succeeding the substring to be extracted
    :type end: str
    :return: the substring of fullstr between start and end
    :rtype: str
    """
    return fullstr[(fullstr.index(start) + len(start)):(fullstr[fullstr.index(start):].index(end) - 1)]


def extract_prefix(fullstr, end, length=None):
    """
    Extract a substring of str that occurs before substr and is of length lenth.
    Example: extract_prefix('abcdef', 'ef', 2) = 'cd'
    :param fullstr: the string to take the substring from
    :type fuullstr: str
    :param start: the substring succeeding the substring to be extracted
    :type start: str
    :param length: the length of the substring to be extracted
    :type length: int
    :return: the substring of length len before substr
    :rtype: str
    """
    if length is None:
        return fullstr[:fullstr.index(end)]
    else:
        return fullstr[(fullstr.index(end) - length):fullstr.index(end)]


def extract_suffix(fullstr, start, length=None):
    """
    Extract a substring of str that occurs after substr and is of length lenth.
    Example: extract_suffix('abcdef', 'ab', 2) = 'cd'
    :param fullstr: the string to take the substring from
    :type fuullstr: str
    :param start: the substring preceding the substring to be extracted
    :type start: str
    :param length: the length of the substring to be extracted
    :type length: int
    :return: the substring of length len after substr
    :rtype: str
    """
    if length is None:
        return fullstr[(fullstr.index(start) + len(start)):]
    else:
        return fullstr[(fullstr.index(start) + len(start)):(fullstr.index(start) + len(start) + length)]


###################
# convert to string
###################

def tasks2str(tasks, tasks_count, tasks_total):
    res = "Tasks:\n" \
          "------\n"
    max_len_label = max([len(tasks[nr][0]) for nr in tasks])
    total_regular = tasks_total[0]
    total_bonus = tasks_total[1]
    for task_nr in tasks:
        if not task_nr == 0:
            task_name = tasks[task_nr][0]
            task_pnts = tasks[task_nr][1]
            task_is_bonus = tasks[task_nr][2]
            buffer = max_len_label - len(tasks[task_nr][0])
            res += "Task " + str(task_nr)
            if task_name:
                res += " (" + tasks[task_nr][0] + ")" + buffer * " "
            res += ":"
            if task_is_bonus:
                res += "+"
            else:
                res += " "
            res += str(task_pnts) + " points\n"
    res += "-------\n"
    res += "Total: "
    res += str(total_regular)
    if total_bonus > 0:
        res += "+" + str(total_bonus)
    res += " points\n"
    return res


def points2str(st, tasks, tasks_total):
    # global tasks, tasks_total
    # global s

    # print(st.points)
    res = "Points achieved:\n" \
          "----------------\n"
    max_len_label = max([len(tasks[nr][0]) for nr in tasks])
    total_regular = tasks_total[0]
    total_bonus = tasks_total[1]
    for task_nr in st.points:
        pnts = st.points[task_nr]
        task_name = tasks[task_nr][0]
        max_pnts = tasks[task_nr][1]
        is_bonus = tasks[task_nr][2]
        buffer = max_len_label - len(task_name)
        if task_nr == 0:
            buffer = max_len_label
            res += "Overall  " + buffer * " " + ":  "
            if pnts > 0:
                res += "  +"
            elif pnts == 0:
                res += "+/-"
            elif pnts < 0:
                res += "  "
            res += str(pnts) + " points"
            res += " (" + "{0:.0%}".format(pnts / total_regular) + ")"
            res += "\n"
        else:
            res += "Task " + str(task_nr)
            if task_name:
                res += " (" + task_name + ")" + buffer * " "
            res += ": "
            res += str(pnts) + "/"
            if is_bonus:
                res += "+"
            res += str(max_pnts) + " points"
            res += " (" + "{0:.0%}".format(pnts / max_pnts) + ")"
            res += "\n"
    res += "-------\n"
    res += "Total: "
    res += str(st.total_points) + "/"
    res += str(total_regular)
    if total_bonus > 0:
        res += "+" + str(total_bonus)
    res += " points"
    res += " (" + "{0:.0%}".format(st.total_points / total_regular) + ")"
    res += "\n"
    # res += "Total: " + (str(st.total_points) if st.total_points else "-") + "/" + str(tasks_total) + " points\n"
    return res


def points2html(st, tasks, tasks_total):
    # todo (medium prio): nicer formatting (alignment etc.)
    # global tasks, tasks_total
    # global s

    res = "<table>"
    total_regular = tasks_total[0]
    total_bonus = tasks_total[1]
    for task_nr in st.points:
        res += "<tr>"
        pnts = st.points[task_nr]
        task_name = tasks[task_nr][0]
        max_pnts = tasks[task_nr][1]
        is_bonus = tasks[task_nr][2]
        if task_nr == 0:
            res += "<td>Overall:&nbsp;</td><td>"
            if pnts > 0:
                res += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+"
            elif pnts == 0:
                res += "&nbsp;&nbsp;&nbsp;+/-"
            elif pnts < 0:
                res += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            res += str(pnts) + " points&nbsp;</td>"
            res += "<td>|" + abs(round(pnts / total_regular * 100 / 5)) * "#"
            res += " (" + "{0:.0%}".format(pnts / total_regular) + ")</td>"
        else:
            task_perc = pnts / max_pnts
            res += "<td>Task " + str(task_nr)
            if task_name:
                res += " (" + task_name + ")"
            res += ":&nbsp;</td>"
            res += "<td>&nbsp;" + str(pnts) + "/"
            if is_bonus:
                res += "+"
            res += "&nbsp;" + str(max_pnts) + " points&nbsp;</td>"
            res += "<td>|" + round(task_perc * 100 / 5) * "#"
            res += " (" + "{0:.0%}".format(task_perc) + ")</td>"
        res += "</tr>"
    res += "<tr><td>-------&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>"
    res += "<tr><td>Total:&nbsp;</td><td>"
    res += str(st.total_points) + "/"
    res += str(total_regular)
    if total_bonus > 0:
        res += "+" + str(total_bonus)
    res += " points&nbsp;</td>"
    res += "<td>|" + round(st.total_points / total_regular * 100 / 5) * "#"
    res += " (" + "{0:.0%}".format(st.total_points / total_regular) + ")</td>"
    res += "</tr>"
    res += "</table>"
    return res


def average2str(avg, avg_total, students, tasks, tasks_total):
    applicable = {st for st in students if students[st].done_grading}
    if len(applicable) == 0:
        return "(No students on the current assignment graded yet)"
    max_len_label = max([len(tasks[nr][0]) for nr in tasks])
    total_regular = tasks_total[0]
    total_bonus = tasks_total[1]
    res = color("ul", "Average points") + " for the current assignment " \
                                          "(based on " + inflect(len(applicable), "submissions") + "):\n"
    for task_nr in tasks:
        pnts = avg[task_nr]
        task_name = tasks[task_nr][0]
        max_pnts = tasks[task_nr][1]
        is_bonus = tasks[task_nr][2]
        buffer = max_len_label - len(task_name)
        if task_nr == 0:
            max_pnts = total_regular
        perc = pnts / max_pnts
        perc_x = round(perc * 25)
        if perc_x < 0:
            perc_x *= -1
        if task_nr == 0:
            buffer = max_len_label
            res += "Overall" + 3 * " " + buffer * " "
        else:
            res += "Task " + str(task_nr)
            if task_name:
                res += " (" + tasks[task_nr][0] + ") " + buffer * " "
        res += "|" + perc_x * "#" + " "
        res += "{0:.0%}".format(perc) + " ("
        if task_nr == 0:
            if pnts > 0:
                res += "+"
            elif pnts == 0:
                res += "+/-"
            elif pnts < 0:
                res += ""
            res += str(pnts)
        else:
            res += format(pnts, ".1f") + "/"
            if is_bonus:
                res += "+"
            res += str(max_pnts)
        res += " points)\n"
    res += "-------\n"
    res += "Total     " + max_len_label * " "
    res += "|" + round((avg_total / total_regular) * 25) * "#" + " "
    res += "{0:.0%}".format(avg_total / total_regular) + " ("
    res += format(avg_total, ".1f") + "/"
    res += str(total_regular)
    if total_bonus > 0:
        res += "+" + str(total_bonus)
    res += " points)"
    #     if task_nr == 0:
    #         res += "Overall: " +\
    #                ("  +" if pnts > 0 else "") + ("+/-" if pnts == 0 else "") + ("  " if pnts < 0 else "") +\
    #                str(pnts) + " points " + \
    #                (round((pnts/tasks_total)*500) * "#" + " (" + "{0:.0%}".format(pnts/tasks_total) + ")"\
    #                 if tasks_total > 0 else "") + "\n"
    #     else:
    #         res += "Task " + str(task_nr) + ": " + format(pnts, ".1f") + "/" \
    #            + str(max_pnts) + " points " +\
    #                (round((pnts/tasks_total)*500) * "#" + " (" + "{0:.0%}".format(pnts/max_pnts) + ")" \
    #                 if tasks_total > 0 else "") + "\n"
    # res += "-------\n"
    # res += "Total:  " + format(avg_total, ".1f") + "/" + str(tasks_total) + " points " +\
    #        (round((pnts/tasks_total)*500) * "#" + " (" + "{0:.0%}".format(avg_total/tasks_total) + ")"\
    #         if tasks_total > 0 else "") + "\n"
    return res


def points2md(s, tasks, tasks_total):
    # todo (low prio): no longer needed?
    # global s, tasks, tasks_total
    res = "#### Points achieved:\n"
    res += "Task nr | points achieved | out of max. points\n"
    res += "--- | --- | ---\n"
    for task_nr in s.points:
        res += "Task " + str(task_nr) + "|" + str(s.points[task_nr]) + "|" + str(tasks[task_nr]) + "<br/>\n"
    res += "--- | --- | --- \n"
    res += "Total |" + str(s.total_points) + "|" + str(tasks_total)
    return res


def string2html(string):
    # todo (low prio): no longer needed?
    return string.replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("\t", "&nbsp;") \
        .replace("&lt;code&gt;", "<code>").replace("&lt;/code&gt;", "</code>") \
        .replace("\r\n", "<br/>").replace("\n", "<br/>").replace("\r", "<br/>")


def print_feedback(feedback, s):
    # todo (low prio): not particularly nice ...
    fb = s.feedback.replace("<h4>", "\n<h4>").replace("</h4>", "</h4>\n\n").replace("</p>", "</p>\n\n") \
        .replace("<li>", "\n<li>").replace("</ul>", "\n</ul>\n") \
        .replace("<pre>", "\n<pre>").replace("</pre>", "</pre>\n") \
        .replace("<table>", "<table>\n").replace("</table>", "</table>\n").replace("</tr>", "</tr>\n") \
        .replace("<span style='color:Green'>", '\033[32m').replace("<span style='color:Orange'>", '\033[33m') \
        .replace("<span style='color:Grey'>", '\33[37m').replace("</span>", '\33[0m') \
        .replace("<code style='color:black'>", "`").replace("</code>", "`")
    for line in fb.split("<br/>"):
        print(line)


###################
# unit test checks
###################

def test_points(test):
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


def test_runonly(test):
    test_doc = test._testMethodDoc
    if test_doc is None:
        test_doc = ""
    if ":run-only: " in test_doc:
        test_doc_runonly_start = test_doc.index(":run-only: ") + 11
        test_doc_runonly_end = test_doc_runonly_start + \
                               (test_doc[test_doc_runonly_start:].index("\n") \
                                    if "\n" in test_doc[test_doc_runonly_start:] \
                                    else len(test_doc[test_doc_runonly_start:]))
        return bool(test_doc[test_doc_runonly_start:test_doc_runonly_end])
    else:
        return False
