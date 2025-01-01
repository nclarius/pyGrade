# This is just a temporary script that is needed to set up the student list at the beginning of the course.

from os.path import *

path_exercises = join(dirname(dirname(dirname(abspath(__file__)))), "exercises")

# make sure moodle file is sorted by last name, tab-separated and has "Teilnehmer/in" removed
# remove doublequotes in files first

with open(join(path_exercises, "studentlist_prelim.tsv"), "r", encoding="utf-8") as slp:
    next(slp)
    with open(join(path_exercises, "studentlist.tsv"), "w", encoding="utf-8") as sl:
        sl.write("\t".join(("Moodle-ID","Last name","First name","MatrNr")) + "\n")
        for line_sl in slp.readlines():
            first_name, last_name, matr_nr, e_mail, last_loaded = line_sl.split("\t")
            full_name = first_name + " " + last_name
            print(full_name)
            print("check")
            with open(join(path_exercises, "studentlist_moodle.tsv"), "r", encoding="utf-8") as ml:
                next(ml)
                for line_ml in ml.readlines():
                    if line_ml.split("\t")[1] == full_name:
                        moodle_id = line_ml.split("\t")[0]
                        sl.write("\t".join((str(moodle_id),last_name, first_name, matr_nr))+"\n")
                        print("found")
                        break
