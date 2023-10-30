from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

import listSelector
from questionViewer import *

#This is the fist screen that the user sees and it will be a label of what the program is 
#above a vertical list of buttons to access the functionality
#memorise facts button
#add facts button
#time travel button
#move list button
#split list button
class MainMenu(QWidget):
    def __init__(self, app):
        QWidget.__init__(self)
        self.app = app
        self.app.setWindowTitle("Main Menu")
        layout = QVBoxLayout()
        #top fact memorisation label
        welcomeLabel = QLabel(self)
        welcomeLabel.setFont(QFont('Arial', 40))
        welcomeLabel.setText("Fact Memorisation Assistant") 
        welcomeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcomeLabel) 
        #memorise facts button
        memoriseFactsButton = QPushButton("Memorise Facts", self)
        memoriseFactsButton.setFont(QFont('Arial', 20))
        memoriseFactsButton.clicked.connect(self.memoriseFactsButtonClick)
        memoriseFactsButton.setStyleSheet("background-color:LawnGreen;")
        layout.addWidget(memoriseFactsButton)
        #add facts button
        addFactsButton = QPushButton("Add facts", self)
        addFactsButton.setFont(QFont('Arial', 20))
        addFactsButton.clicked.connect(self.addFactsButtonClick)
        addFactsButton.setStyleSheet("background-color:DeepSkyBlue;")
        layout.addWidget(addFactsButton)
        #time travel button
        timeTravelButton = QPushButton("Time Travel", self)
        timeTravelButton.setFont(QFont('Arial', 20))
        timeTravelButton.clicked.connect(self.timeTravelButtonClick)
        layout.addWidget(timeTravelButton)
        #move list button
        moveListButton = QPushButton("Move List", self)
        moveListButton.setFont(QFont('Arial', 20))
        moveListButton.clicked.connect(self.moveListButtonClick)
        layout.addWidget(moveListButton)
        #split list button    
        splitListButton = QPushButton("Split List", self)
        splitListButton.setFont(QFont('Arial', 20))
        splitListButton.clicked.connect(self.splitListButtonClick)
        layout.addWidget(splitListButton)    
        #delete list button
        deleteListButton = QPushButton("Delete List", self)
        deleteListButton.setFont(QFont('Arial', 20))
        deleteListButton.clicked.connect(self.deleteListButtonClick)
        deleteListButton.setStyleSheet("background-color : red;")
        layout.addWidget(deleteListButton)          

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)#make the stuff in the layout move to the top of the page
        self.setLayout(layout)
    
    def memoriseFactsButtonClick(self):
        self.app.setCentralWidget(listSelector.ListSelectorMemorise(self.app))
    def addFactsButtonClick(self):
        self.app.setCentralWidget(listSelector.ListSelectorAddFacts(self.app))
    def timeTravelButtonClick(self):
        pass

    def moveListButtonClick(self):
        pass

    def splitListButtonClick(self):
        self.app.setCentralWidget(QuestionViewer(self.app))
    def deleteListButtonClick(self):
        self.app.setCentralWidget(listSelector.ListSelectorDeleteLists(self.app))