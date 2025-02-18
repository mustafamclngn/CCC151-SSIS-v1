import re
import os
import sys
import csv
from PyQt5 import QtWidgets
from Window_design import Ui_MainBox

#CSV FILES AS DATABASE
STUDENTS_CSV_FILE = "students.csv"
PROGRAMS_CSV_FILE = "programs.csv"
COLLEGES_CSV_FILE = "colleges.csv"

class MainApp(QtWidgets.QMainWindow, Ui_MainBox):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #SET BUTTON CONNECTIONS
        self.addStudent_button.clicked.connect(self.add_student)
        self.delete_button.clicked.connect(self.delete_selected_item)
        self.addProgram_button.clicked.connect(self.add_program)
        self.addCollege_button.clicked.connect(self.add_college)

        self.students = []
        self.programs = []
        self.colleges = []

        #CLEAR TABLE SELECTED ITEM EVERY AFTER CHANGE OF SELECTION
        self.studentTable_widget.itemSelectionChanged.connect(self.clear_other_selections)
        self.programTable_widget.itemSelectionChanged.connect(self.clear_other_selections)
        self.collegeTable_widget.itemSelectionChanged.connect(self.clear_other_selections)

        #CHECK IF DATABASES EXIST
        if os.path.exists(STUDENTS_CSV_FILE):
            self.load_student()
        else:
            QtWidgets.QMessageBox.information(self, "File Error", "students.csv file not found")
        if os.path.exists(PROGRAMS_CSV_FILE):
            self.load_program()
            self.populate_program_code()
        else:
            QtWidgets.QMessageBox.information(self, "File Error", "programs.csv file not found")
        if os.path.exists(COLLEGES_CSV_FILE):
            self.load_college()
            self.populate_college_code()
        else:
            QtWidgets.QMessageBox.information(self, "File Error", "colleges.csv file not found")

    #CLEAR TABLE SELECTED ITEM EVERY AFTER CHANGE OF SELECTION
    def clear_other_selections(self):
        sender_table = self.sender()

        if sender_table is not self.studentTable_widget:
            self.studentTable_widget.clearSelection()
        if sender_table is not self.programTable_widget:
            self.programTable_widget.clearSelection()
        if sender_table is not self.collegeTable_widget:
            self.collegeTable_widget.clearSelection()

    #DELETE SELECTED ROWS
    def delete_selected_item(self):
        if self.studentTable_widget.currentRow() >= 0:
            self.delete_student_confirmation()
            return
    
        if self.programTable_widget.currentRow() >= 0:
            self.delete_program_confirmation()
            return
    
        if self.collegeTable_widget.currentRow() >= 0:
            self.delete_college_confirmation()
            return

#=================================================================================================ADD STUDENTS=========================================================================================================

    #VALIDATE IF STUDENT ID IS VALID (ONLY ACCEPTS YEAR STARTING FROM 2-XXX)
    def validate_student_id_format(self, student_id, edit_state=False):
        if not edit_state:
            valid_id_number = re.match(r'^2[0-9]{3}-[0-9]{4}$', student_id)
        else:
            valid_id_number = re.match(r'^2[0-9]{3}-[0-9]{4}$|^$', student_id)
        return True if valid_id_number else False
    
    #UPDATE STUDENT TABLE INFORMATION
    def update_student_table(self):
        self.studentTable_widget.setRowCount(len(self.students))
        for row, student in enumerate(self.students):
            for col, data in enumerate(student):
                self.studentTable_widget.setItem(row, col, QtWidgets.QTableWidgetItem(data))

    #ADD STUDENT BUTTON
    def add_student(self):
        student_id = self.lineEdit_2.text().strip()
        student_first_name = self.lineEdit_3.text().strip().title()
        student_last_name = self.lineEdit_4.text().strip().title()
        student_gender = self.comboBox_2.currentText()
        student_year_level = self.comboBox.currentText()
        student_program_code = self.comboBox_5.currentText().upper()
        
        #VALIDATE IF INPUTS ARE VALID
        if not self.validate_student_id_format(student_id):
            QtWidgets.QMessageBox.warning(self, 'Input Error', 'Please input a valid Student ID')
            return
        
        #ALLOW SPACE INPUT (DOUBLE NAME EX: JOHN DOE)
        if not all(char.isalpha() or char.isspace() for char in student_first_name):
            QtWidgets.QMessageBox.warning(self, 'Input Error', 'Invalid first name')
            return
        
        if not (student_last_name.isalpha()):
            QtWidgets.QMessageBox.warning(self, 'Input Error', 'Invalid last name')
            return
        
        #CHECK FOR EXISTING INPUTS
        if any(student[0] == student_id for student in self.students):
            QtWidgets.QMessageBox.warning(self, 'Input Error', 'Student ID already exists.')
            return

        if student_id and student_first_name and student_last_name and student_year_level and student_gender and student_program_code:
            student_data = [student_id, student_first_name, student_last_name, student_year_level, student_gender, student_program_code]

            self.students.append(student_data)
            self.save_students_csv()
            self.update_student_table()
            self.clear_student_input()
            QtWidgets.QMessageBox.information(self, "Success", "Student added successfully.")
        else:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please input for all the fields")

    #CLEAR STUDENT LINE BOXES EVERY AFTER SUCCESFUL ADD
    def clear_student_input(self):
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        self.lineEdit_4.clear()
        self.comboBox_2.setCurrentIndex(0)
        self.comboBox.setCurrentIndex(0)
        self.comboBox_5.setCurrentIndex(0)
        
    #DELETE STUDENT CONFIRMATION PROMPT
    def delete_student_confirmation(self):
        confirmation = QtWidgets.QMessageBox(self)
        confirmation.setWindowTitle("Confirm Deletion")
        confirmation.setText(f"Are you sure you want to delete this student?")
        confirmation.setIcon(QtWidgets.QMessageBox.Warning)
        confirmation.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        confirmation.setDefaultButton(QtWidgets.QMessageBox.No)
        
        result = confirmation.exec_()
        
        #IF DELETE == YES
        if result == QtWidgets.QMessageBox.Yes:
            self.delete_student()
            self.save_students_csv()
            self.update_student_table()

    #DELETE STUDENT
    def delete_student(self):
        selected_student_row = self.studentTable_widget.currentRow()
        if selected_student_row >= 0:
            del self.students[selected_student_row]
            self.save_students_csv()
            self.update_student_table()
    
    #SAVE INPUT TO STUDENTS CSV   
    def save_students_csv(self):
        with open(STUDENTS_CSV_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Student ID", "First Name", "Last Name", "Year Level", "Gender", "Program Code"])
            writer.writerows(self.students)

    #LOAD STUDENTS DATABASE
    def load_student(self):
        with open(STUDENTS_CSV_FILE, mode="r") as file:
            reader = csv.reader(file)
            next(reader)
            self.students = [row for row in reader]
            self.update_student_table()

#======================================================================================================================================================================================================================

#=================================================================================================ADD PROGRAMS=========================================================================================================
    
    #UPDATE PROGRAM TABLE INFORMATION
    def update_program_table(self):
        self.programTable_widget.setRowCount(len(self.programs))
        for row, program in enumerate(self.programs):
            for col, data in enumerate(program):
                self.programTable_widget.setItem(row, col, QtWidgets.QTableWidgetItem(data))

    #POPULATE COMBOBOX_5 (STUDENTS' PROGRAM CODES FROM )
    def populate_program_code(self):
        with open(PROGRAMS_CSV_FILE, "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            program_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

            self.comboBox_5.clear()
            self.comboBox_5.addItem("")
            self.comboBox_5.addItems(program_codes)

    #ADD PROGRAM BUTTON
    def add_program(self):
        pr_program_code = self.lineEdit_6.text().strip().upper()
        pr_program_name = self.lineEdit.text().strip().title()
        program_college_code = self.comboBox_4.currentText().upper()

        #VALIDATE IF INPUTS ARE VALID
        if not (pr_program_code.isalpha()):
            QtWidgets.QMessageBox.warning(self, 'Input Error', 'Invalid Program Code')
            return
        
        #ALLOW SPACE INPUT (BACHELOR OF ...)
        if not all(char.isalpha() or char.isspace() for char in pr_program_name):
            QtWidgets.QMessageBox.warning(self, 'Input Error', 'Invalid Program Name')
            return

        if not pr_program_code or not pr_program_name or not program_college_code:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return
        
        #CHECK IF THERE ARE EXISTING CODES
        existing_program_codes = set()
        if os.path.exists(PROGRAMS_CSV_FILE):
            with open(PROGRAMS_CSV_FILE, "r", newline='') as file:
                reader = csv.reader(file)
                existing_program_codes = {row[0] for row in reader if len(row) > 0}

        #CHECK IF THERE ARE EXISTING INPUTS
        if pr_program_code in existing_program_codes:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Program Code already exists.")
            return
        
        if pr_program_code and pr_program_name and program_college_code:
            program_data = [pr_program_code, pr_program_name, program_college_code]

            self.programs.append(program_data)
            self.save_programs_csv()
            self.update_program_table()
            self.populate_program_code()
            self.clear_program_input()
            QtWidgets.QMessageBox.information(self, "Success", "Program added successfully.")
        else:
            QtWidgets.QMessageBox.information(self, "Input Error", "Please input for all fields")

    #CLEAR PROGRAM LINE BOXES EVERY AFTER SUCCESFUL ADD
    def clear_program_input(self):
        self.lineEdit_6.clear()
        self.lineEdit.clear()
        self.comboBox_4.setCurrentIndex(0)

    #DELETE PROGRAM CONFIRMATION PROMPT
    def delete_program_confirmation(self):
        confirmation = QtWidgets.QMessageBox(self)
        confirmation.setWindowTitle("Confirm Deletion")
        confirmation.setText(f"Are you sure you want to delete this program?")
        confirmation.setInformativeText("All affected students in this program will be marked as unenrolled")
        confirmation.setIcon(QtWidgets.QMessageBox.Warning)
        confirmation.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        confirmation.setDefaultButton(QtWidgets.QMessageBox.No)  # Make "No" the default for safety

        result = confirmation.exec_()
        
        #IF DELETE == YES
        if result == QtWidgets.QMessageBox.Yes:
            self.delete_program()
            self.save_students_csv()
            self.update_student_table()

    #DELETE PROGRAM
    def delete_program(self):
        selected_program_row = self.programTable_widget.currentRow()
        if selected_program_row >= 0:
            deleted_program_code = self.programs[selected_program_row][0]
            del self.programs[selected_program_row]

            #SET AFFECTED STUDENTS UNDER DELETED PROGRAM CODE TO UNENROLLED
            for student in self.students:
                if student[5] == deleted_program_code:
                    student[5] = "UNENROLLED"

            #UPDATE CSV,TABLE,COMBOBOX
            self.save_students_csv()
            self.save_programs_csv()
            self.update_student_table()
            self.update_program_table()
            self.populate_program_code()

    #SAVE INPUT TO PROGRAM CSV
    def save_programs_csv(self):
        with open(PROGRAMS_CSV_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Program Code", "Program Name", "College Code"])
            writer.writerows(self.programs)

    #LOAD PROGRAM DATABASE
    def load_program(self):
        if os.path.exists(PROGRAMS_CSV_FILE):
            with open(PROGRAMS_CSV_FILE, mode="r") as file:
                reader = csv.reader(file)
                next(reader)
                self.programs = [row for row in reader]
                self.update_program_table()
                
#=======================================================================================================================================================================================================================

#=================================================================================================ADD COLLEGES==========================================================================================================

    #POPULATE COMBOBOX_4 (PROGRAMS' COLLEGE CODE)
    def populate_college_code(self):
        with open(COLLEGES_CSV_FILE, "r", newline='') as file:
            reader = csv.reader(file)
            next(reader, None)
            college_codes = sorted(set(row[0] for row in reader if len(row) > 0 and row[0].strip()))

        self.comboBox_4.clear()
        self.comboBox_4.addItem("")
        self.comboBox_4.addItems(college_codes)

    #ADD COLLEGE BUTTON
    def add_college(self):
        co_college_code = self.lineEdit_8.text().strip().upper()
        co_college_name = self.lineEdit_9.text().strip().title()

        #VALIDATE IF INPUTS ARE VALID
        if not co_college_code.isalpha():
            QtWidgets.QMessageBox.warning(self, "Input Error", "Invalid College Code")
            return
        
        if not all(char.isalpha() or char.isspace() for char in co_college_name):
            QtWidgets.QMessageBox.warning(self, "Input Error", "Invalid College Name")
            return
        
        #CHECK IF THERE ARE EXISTING CODES
        existing_college_codes = set()
        if os.path.exists(COLLEGES_CSV_FILE):
            with open(COLLEGES_CSV_FILE, "r", newline='') as file:
                reader = csv.reader(file)
                existing_college_codes = {row[0] for row in reader if len(row) > 0}

        if co_college_code in existing_college_codes:
            QtWidgets.QMessageBox.warning(self, "Input Error", "College Code already exists.")
            return

        if co_college_code and co_college_name:
            college_data = [co_college_code, co_college_name]
            self.colleges.append(college_data)
            self.save_colleges_csv()
            self.update_college_table()
            self.populate_college_code()
            self.clear_college_inputs()
            QtWidgets.QMessageBox.information(self, "Success", "College added successfully.")
        else:
            QtWidgets.QMessageBox.information(self, "Input Error", "Please input for all fields")

    #CLEAR COLLEGE LINE BOXES EVERY AFTER SUCCESFUL ADD
    def clear_college_inputs(self):
        self.lineEdit_8.clear()
        self.lineEdit_9.clear()

    #DELETE COLLEGE CONFIRMATION
    def delete_college_confirmation(self):
            confirmation = QtWidgets.QMessageBox(self)
            confirmation.setWindowTitle("Confirm Deletion")
            confirmation.setText(f"Are you sure you want to delete this college?")
            confirmation.setInformativeText("All affected affected programs in this college will be deleted and all affected students in this programs will be marked as unenrolled")
            confirmation.setIcon(QtWidgets.QMessageBox.Warning)
            confirmation.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            confirmation.setDefaultButton(QtWidgets.QMessageBox.No)
            
            result = confirmation.exec_()
            
            #IF DELETE == YES
            if result == QtWidgets.QMessageBox.Yes:
                self.delete_college()
                self.save_colleges_csv()
                self.update_college_table()

    #DELETE COLLEGE
    def delete_college(self):
            selected_college_row = self.collegeTable_widget.currentRow()
            if selected_college_row >= 0:
                deleted_college_code = self.colleges[selected_college_row][0]
                
                #PROGRAMS AFFECTED UNDER DELETED COLLEGE
                program_in_college = [program[0] for program in self.programs if program[2] == deleted_college_code]
                
                #REMOVE MATCHING PROGRAMS IN COLLEGE CODE
                self.programs = [program for program in self.programs if program[2] != deleted_college_code]
                
                #SET AFFECTED STUDENTS UNDER PROGRAMS AFFECTED UNDER DELETED COLLEGE TO UNENROLLED
                for student in self.students:
                    if student[5] in program_in_college:
                        student[5] = "UNENROLLED"
                
                del self.colleges[selected_college_row]
                
                #UPDATE CSV,TABLE,COMBOBOX
                self.save_colleges_csv()
                self.save_programs_csv()
                self.save_students_csv()
                self.update_college_table()
                self.update_program_table()
                self.update_student_table()
                self.populate_college_code()
                self.populate_program_code()

    #UPDATE COLLEGE TABLE INFORMATION
    def update_college_table(self):
        self.collegeTable_widget.setRowCount(len(self.colleges))
        for row, college in enumerate(self.colleges):
            for col, data in enumerate(college):
                self.collegeTable_widget.setItem(row, col, QtWidgets.QTableWidgetItem(data))

    #SAVE INPUT TO COLLEGES CSV
    def save_colleges_csv(self):
        with open(COLLEGES_CSV_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["College Code", "College Name"])
            writer.writerows(self.colleges)

    #LOAD PROGRAM DATABASE
    def load_college(self):
        if os.path.exists(COLLEGES_CSV_FILE):
            with open(COLLEGES_CSV_FILE, mode="r") as file:
                reader = csv.reader(file)
                next(reader)
                self.colleges = [row for row in reader]
                self.update_college_table()

#========================================================================================================================================================================================================================

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainApp()
    mainWindow.show()
    sys.exit(app.exec_())