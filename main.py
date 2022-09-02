from mainWindow import Ui_MainWindow
from subjectWindow import Ui_SubjectWindow
from answerDialog import Ui_AnswerDialog
from addWindow import Ui_AddWindow
from PyQt5 import QtWidgets as qtw, QtCore as qtc, QtGui as qtg
from clickable_label import ClickableLabel
import style
import sqlite3

""" *********************** M A I N    W I N D O W *********************** """

class MainWindow(qtw.QWidget):
    def __init__(self):
        """ Main Window for the application. """
        super().__init__()

        # Main Window init
        self.ui_main = Ui_MainWindow()
        self.ui_main.setupUi(self)
        self.subject_name = None
        self.subj_list = []

        # Label Error
        self.ui_main.label_error.hide()

        # Button Events
        self.ui_main.btn_add.clicked.connect(self.add_subj)
        self.ui_main.btn_load.clicked.connect(self.goto_load)
        self.ui_main.btn_delete.clicked.connect(self.delete_subj)

        # Cursor
        self.ui_main.btn_add.setCursor(qtc.Qt.PointingHandCursor)
        self.ui_main.btn_load.setCursor(qtc.Qt.PointingHandCursor)
        self.ui_main.btn_delete.setCursor(qtc.Qt.PointingHandCursor)

        # Method Calls
        self.get_subj()

    def get_id(self, subj):
        """ Gets the ID of the subject from the database. """
        conn = sqlite3.connect("reviewer.db")
        c = conn.cursor()
        c.execute(
            f"""
                SELECT subject_id FROM subjects WHERE subject_name = '{subj}'
            """
        )
        id = c.fetchone()[0]
        return id

    def add_subj(self):
        """ Gets the text value in the Line Edit object. """
        subj_name = self.ui_main.txt_subj.text()

        if not subj_name:
            self.ui_main.label_error.setText("Please enter text field")
            self.ui_main.label_error.setStyleSheet(style.label_red)
            self.ui_main.label_error.show()
            return

        if self.save_to_db(subj_name):
            self.ui_main.txt_subj.clear()
            self.ui_main.label_error.setText(f"{subj_name} has been saved!")
            self.ui_main.label_error.setStyleSheet(style.label_green)
            self.ui_main.combobox_subj.addItem(subj_name)

    def delete_subj(self):
        """ Deletes the subject chosen. """
        self.subject_name = self.ui_main.combobox_subj.currentText()

        if not self.ui_main.combobox_subj.currentText():
            warning_box = qtw.QMessageBox.about(self, "Error", "There is nothing to delete")
            return

        message_box = qtw.QMessageBox()
        message_box.setStyleSheet("background-color: #2b5b84; color: white;")
        confirm = message_box.question(self, "Delete Subject",
                                      f"Are you sure you want to delete {self.subject_name}?",
                                      message_box.Yes | message_box.No)

        if confirm == message_box.Yes:
            conn = sqlite3.connect("reviewer.db")
            c = conn.cursor()
            c.execute("PRAGMA foreign_keys = ON")
            c.execute(f"DELETE FROM subjects WHERE subject_name = '{self.subject_name}'")
            conn.commit()
            conn.close()

            self.ui_main.combobox_subj.clear()
            self.subj_list = self.get_subj()
            self.update_combobox()
            self.ui_main.label_error.hide()

    def save_to_db(self, subject):
        """ Inserts a main subject in the database. """

        try:
            conn = sqlite3.connect("reviewer.db")
            c = conn.cursor()
            c.execute(f"INSERT INTO subjects(subject_name) VALUES (?)", (subject,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            self.ui_main.label_error.setText("That subject already exists")
            self.ui_main.label_error.setStyleSheet(style.label_red)
            self.ui_main.label_error.show()
            return False

    def goto_load(self):
        """ Loads the subject chosen in the combobox """
        self.subject_name = self.ui_main.combobox_subj.currentText()

        if self.ui_main.combobox_subj.count() == 0:
            self.ui_main.label_error.show()
            self.ui_main.label_error.setStyleSheet(style.label_red)
            self.ui_main.label_error.setText("Please Add a subject")
            return
        else:
            self.subject_window = SubjectWindow(self.subject_name,
                                                self.get_id(self.subject_name))
            stack_widget.addWidget(self.subject_window)
            stack_widget.setCurrentIndex(stack_widget.currentIndex() + 1)

    def get_subj(self):
        """ Fetches the subjects in the database. """
        conn = sqlite3.connect("reviewer.db")
        c = conn.cursor()
        c.execute("SELECT * FROM subjects")

        self.subj_list = c.fetchall()
        self.update_combobox()

    def get_subj_id(self):
        conn = sqlite3.connect("reviewer.db")
        c = conn.cursor()
        c.execute("SELECT * FROM subjects")

        self.update_combobox()

    def update_combobox(self):
        """ Inserts the subjects into the combobox. """
        if not self.list_empty():
            for subj in self.subj_list:
                self.ui_main.combobox_subj.addItem(subj[1])

    def list_empty(self):
        """ Returns a boolean value that checks if the subject list is empty or not. """
        return True if not self.subj_list else False

""" *********************** S U B J E C T    W I N D O W *********************** """

class SubjectWindow(qtw.QWidget):
    def __init__(self, subject_name, id):
        """ GUI for the questions and answers """
        super().__init__()
        self.subj_window = Ui_SubjectWindow()
        self.subj_window.setupUi(self)
        self.id = id

        # Questions and answers
        self.qa_list = self.get_qa()

        # Attribute
        self.subj_name = subject_name

        # Form Layout
        self.form_layout = qtw.QFormLayout()

        # Hbox
        self.vbox = []

        # Group Box
        self.group_box = qtw.QGroupBox()
        self.group_box.setLayout(self.form_layout)

        # Scroll Area
        self.subj_window.scroll_qa.setWidget(self.group_box)
        self.subj_window.scroll_qa.setWidgetResizable(True)

        # Label
        self.subj_window.label_subject.setText(f"{self.subj_name}")

        # Button Events
        self.subj_window.btn_back.clicked.connect(self.back_to_main)
        self.subj_window.btn_add.clicked.connect(self.goto_add)

        # Cursor
        self.subj_window.btn_back.setCursor(qtc.Qt.PointingHandCursor)
        self.subj_window.btn_add.setCursor(qtc.Qt.PointingHandCursor)

        # Default Event
        self.show_questions()

    def back_to_main(self):
        """ Goes back to the main UI """
        qtw.QStackedWidget.removeWidget(stack_widget, self)
        stack_widget.setCurrentIndex(0)

    def goto_add(self):
        """ Goes to the add questions window. """
        self.ui_add = AddWindow(self.subj_name, self)
        stack_widget.addWidget(self.ui_add)
        stack_widget.setCurrentIndex(stack_widget.currentIndex() + 1)

    def get_qa(self):
        """ Retrieves the questions and answers in the database and save it to the lists. """
        conn = sqlite3.connect("reviewer.db")
        c = conn.cursor()
        c.execute("SELECT * FROM flashcard WHERE flashcard_id = (?)", (self.id,))

        qa_list = c.fetchall()

        return qa_list

    def show_questions(self):
        """ Shows the questions in the scroll area. """
        for i, aq in enumerate(self.qa_list):

            # Label
            question = ClickableLabel()
            question.setWordWrap(True)
            question.setText(f"{i + 1}.) {aq[1]}")
            question.setStyleSheet(style.entries_text)
            question.setFixedWidth(510)
            question.setFixedHeight(100)
            question.clicked.connect(lambda i=i: self.show_answer(self.qa_list[i], i))

            # Delete Button
            btn_del = qtw.QPushButton()
            btn_del.setFixedWidth(75)
            btn_del.setFixedHeight(100)
            btn_del.setText("X")
            btn_del.clicked.connect(lambda checked, i = i: self.delete_question(self.qa_list[i]))
            btn_del.setStyleSheet(style.btn_red_del)

            # Cursor
            question.setCursor(qtc.Qt.PointingHandCursor)
            btn_del.setCursor(qtc.Qt.PointingHandCursor)

            self.form_layout.addRow(question, btn_del)

    def delete_rows(self):
        """ Deletes the entire rows of entries. """
        for i in reversed(range(self.form_layout.count())):
            self.form_layout.itemAt(i).widget().setParent(None)

    def show_answer(self, index, num):
        """ Shows the answer in a dialog format. """
        self.dialog_box = AnswerDialog(f"[{num+1}]  {index[2]}")
        self.dialog_box.show()

    def delete_question(self, entry):
        """ Deletes the particular question chosen. """
        message_box = qtw.QMessageBox()
        message_box.setStyleSheet("background-color: #2b5b84; color: white;")
        answer = message_box.question(self, "Delete Entry",
                                      f"Are you sure you want to delete this question?",
                                      message_box.Yes | message_box.No)

        if answer == message_box.Yes:
            conn = sqlite3.connect("reviewer.db")
            c = conn.cursor()
            c.execute(
                f""" 
                    DELETE FROM flashcard WHERE question = '{entry[1]}' AND answer = '{entry[2]}'
                """
            )

            conn.commit()
            conn.close()
            self.refresh_entries()
        else:
            return

    def refresh_entries(self):
        self.delete_rows()
        self.qa_list = self.get_qa()
        self.show_questions()

""" *********************** A N S W E R    D I A L O G *********************** """

class AnswerDialog(qtw.QWidget):
    def __init__(self, answer):
        super().__init__()
        self.ui_ans_dialog = Ui_AnswerDialog()
        self.ui_ans_dialog.setupUi(self)
        self.setWindowTitle("Reviewer")

        self.answer = answer

        self.ui_ans_dialog.label_answer.setText(answer)

        # Button Event
        self.ui_ans_dialog.btn_ok.clicked.connect(self.close)

        # Cursor
        self.ui_ans_dialog.btn_ok.setCursor(qtc.Qt.PointingHandCursor)

""" *********************** A D D    W I N D O W *********************** """

class AddWindow(qtw.QWidget):
    def __init__(self, subject_name, subj_ui):
        super().__init__()
        self.ui_add = Ui_AddWindow()
        self.ui_add.setupUi(self)
        self.subject_name = subject_name
        self.subj_ui = subj_ui

        # Label
        self.ui_add.label_subject.setText(f"{subject_name}")
        self.ui_add.label_error.hide()

        # Button Events
        self.ui_add.btn_back.clicked.connect(self.goto_subj)
        self.ui_add.btn_add.clicked.connect(self.check_field)

        # Cursor
        self.ui_add.btn_back.setCursor(qtc.Qt.PointingHandCursor)
        self.ui_add.btn_add.setCursor(qtc.Qt.PointingHandCursor)

    def goto_subj(self):
        """ Goes back to the subject UI. """
        qtw.QStackedWidget.removeWidget(stack_widget, self)
        stack_widget.setCurrentIndex(1)
        self.subj_ui.refresh_entries()

    def check_field(self):
        question = self.ui_add.txt_question.toPlainText()
        answer = self.ui_add.txt_answer.toPlainText()

        if not question or not answer:
            self.ui_add.label_error.setText("Please enter fields")
            self.ui_add.label_error.show()
            self.ui_add.label_error.setStyleSheet(style.label_red)
            return
        else:
            self.ui_add.label_error.setText("The question has been added!")
            self.ui_add.label_error.show()
            self.ui_add.label_error.setStyleSheet(style.label_green)
            self.add_to_db(question, answer)

        self.ui_add.txt_question.clear()
        self.ui_add.txt_answer.clear()

    def add_to_db(self, question, answer):
        conn = sqlite3.connect("reviewer.db")
        c = conn.cursor()


        c.execute(
            f"""
                SELECT subject_id FROM subjects 
                WHERE subject_name = '{self.subject_name}'
            """
        )

        id = c.fetchone()

        c.execute(
            """
                INSERT INTO flashcard (flashcard_id, question, answer) 
                VALUES (?,?,?)
            """,(id[0], question, answer)
        )

        conn.commit()
        conn.close()

""" *********************** M A I N    B L O C K *********************** """

if __name__ == "__main__":
    app = qtw.QApplication([])
    app.setWindowIcon(qtg.QIcon(qtg.QPixmap("./images/icon.png")))

    conn = sqlite3.connect("reviewer.db")
    c = conn.cursor()

    # PARENT TABLE
    c.execute(
        """
            CREATE TABLE IF NOT EXISTS subjects(
                subject_id INTEGER PRIMARY KEY,
                subject_name TEXT UNIQUE
            )
        """
    )

    # CHILD TABLE
    c.execute(
        """
            CREATE TABLE IF NOT EXISTS flashcard(
                flashcard_id INTEGER,
                question TEXT,
                answer TEXT,
                FOREIGN KEY (flashcard_id)
                    REFERENCES subjects(subject_id)
                    ON DELETE CASCADE
            )
        """
    )

    conn.commit()
    conn.close()

    # Main Window
    main_widget = MainWindow()

    # Stack Widgets
    stack_widget = qtw.QStackedWidget()
    stack_widget.setWindowTitle("Reviewer")
    stack_widget.setFixedWidth(626)
    stack_widget.setFixedHeight(764)
    stack_widget.setStyleSheet(style.widget_css)
    stack_widget.addWidget(main_widget)
    stack_widget.show()

    app.exec_()
