
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import mainMenu
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget


class ListDeletor(QWidget):
    def __init__(self, app, listToDelete):#listToDelete = (listName, listID)
        QWidget.__init__(self)
        self.listToDelete = listToDelete
        self.app = app
        self.app.setWindowTitle("List Deletor")
        mainLayout = QVBoxLayout()
        mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)#make the stuff in the layout move to the top of the page
        titleLabel = QLabel("You are deleting: " + listToDelete[0])
        titleLabel.setFont(QFont('Arial', 30))
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainLayout.addWidget(titleLabel)
        #dialogue to tell the user to select options
        self.popup = QMessageBox()
        self.popup.setIcon(QMessageBox.Icon.Information)
        self.popup.setStandardButtons(QMessageBox.StandardButton.Ok)
        #radio pushButton to select weather to delete sublists or move them to the parent of the deleted list
        subtitle1 = QLabel("What should be done with the sublists?")
        subtitle1.setFont(QFont('Arial', 30))
        subtitle1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainLayout.addWidget(subtitle1)
        radioOneLayout = QHBoxLayout()
        self.deleteSublistsButton = QPushButton("Delete sublists")
        self.deleteSublistsButton.setFont(QFont('Arial', 30))
        self.deleteSublistsButton.setCheckable(True)
        self.deleteSublistsButton.clicked.connect(self.deleteSublistsButtonClick)
        radioOneLayout.addWidget(self.deleteSublistsButton)
        self.migrateSublistsButton = QPushButton("Migrate sublists")
        self.migrateSublistsButton.setFont(QFont('Arial', 30))
        self.migrateSublistsButton.setCheckable(True)
        self.migrateSublistsButton.clicked.connect(self.migrateSublistsButtonClick)
        radioOneLayout.addWidget(self.migrateSublistsButton)
        mainLayout.addLayout(radioOneLayout)
        #radio pushButton to select weather to delete the questions in the deleted lists or split them into other lists
        subtitle2 = QLabel("What should be done with the questions?")
        subtitle2.setFont(QFont('Arial', 30))
        subtitle2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainLayout.addWidget(subtitle2)
        radioTwoLayout = QHBoxLayout()
        self.deleteQuestionsButton = QPushButton("Delete questions")
        self.deleteQuestionsButton.setFont(QFont('Arial', 30))
        self.deleteQuestionsButton.setCheckable(True)
        self.deleteQuestionsButton.clicked.connect(self.deleteQuestionsButtonClick)
        radioTwoLayout.addWidget(self.deleteQuestionsButton)
        self.migrateQuestionsButton = QPushButton("Migrate questions")
        self.migrateQuestionsButton.setFont(QFont('Arial', 30))
        self.migrateQuestionsButton.setCheckable(True)
        self.migrateQuestionsButton.clicked.connect(self.migrateQuestionsButtonClick)
        radioTwoLayout.addWidget(self.migrateQuestionsButton)
        mainLayout.addLayout(radioTwoLayout)
        #delete button
        deleteButton = QPushButton("DELETE!")
        deleteButton.setFont(QFont('Arial', 100))
        deleteButton.setStyleSheet("background-color:red;")
        deleteButton.clicked.connect(self.deleteButtonClick)
        mainLayout.addWidget(deleteButton)
        #go home and do nothing button
        homeButton = QPushButton("GO HOME\n AND\n DO NOTHING")
        homeButton.setFont(QFont('Arial', 100))
        homeButton.setStyleSheet("background-color:MediumSeaGreen;")
        homeButton.clicked.connect(self.homeButtonClick)
        mainLayout.addWidget(homeButton)
        self.setLayout(mainLayout)
    def homeButtonClick(self):
        self.app.setCentralWidget(mainMenu.MainMenu(self.app))
    def deleteWithSublistsAndQuestions(self, listToDelete):#listToDelete = (listName, listID)
        sublists = self.app.database.getImmediateSublists(listToDelete[1])
        for list in sublists:
            self.deleteWithSublistsAndQuestions(list)
        self.app.database.deleteQuestionsByListID(listToDelete[1])

    def deleteButtonClick(self):
        if self.deleteQuestionsButton.isChecked() and self.deleteQuestionsButton.isChecked():

            self.deleteWithSublistsAndQuestions(self.listToDelete)#this value must be passed in as it it a recursive method

        elif self.migrateQuestionsButton.isChecked() or self.deleteQuestionsButton.isChecked():
            shouldDeleteQuestions = self.deleteQuestionsButton.isChecked()
            if shouldDeleteQuestions:
                print("delete Questions")
            else:#migrate Questions
                print("migrate Questions")
        else:
            self.popup.setText("You must select what to do with the Questions")
            self.popup.show()

        if self.migrateSublistsButton.isChecked() or self.deleteSublistsButton.isChecked():
            shouldDeleteSublists = self.deleteSublistsButton.isChecked()
            if shouldDeleteSublists:
                print("delete sublists")
            else:#migrate sublists
                print("migrate sublists")
        else:
            self.popup.setText("You must select what to do with the sublists")
            self.popup.show()
    def deleteSublistsButtonClick(self):
        self.migrateSublistsButton.setChecked(False)

    def migrateSublistsButtonClick(self):
        self.deleteSublistsButton.setChecked(False)

    def deleteQuestionsButtonClick(self):
        self.migrateQuestionsButton.setChecked(False)

    def migrateQuestionsButtonClick(self):
        self.deleteQuestionsButton.setChecked(False)