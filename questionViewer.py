import random
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QMessageBox, QProgressBar, QPushButton, QSizePolicy, QTextEdit, QVBoxLayout, QWidget
from PyQt6.QtGui import QFont
import mainMenu
# parent class for defining questionViewer UI


class QuestionViewer(QWidget):
    def __init__(self, app):
        QWidget.__init__(self)
        self.app = app
        #popup to boss the user about
        self.popup = QMessageBox()
        self.popup.setIcon(QMessageBox.Icon.Information)
        self.popup.setStandardButtons(QMessageBox.StandardButton.Ok)
        mainLayout = QVBoxLayout()
        #label to indecate the list in use
        self.listLabel = QLabel()
        self.listLabel.setFont(QFont('Arial', 15))
        mainLayout.addWidget(self.listLabel)
        #labels and progress bar for showing statistics about progress
        topRowLayout = QHBoxLayout()
        self.answersGivenLabel = QLabel()
        self.answersGivenLabel.setFont(QFont('Arial', 15))
        self.topRowWidget = QWidget()
        topRowLayout.addWidget(self.answersGivenLabel)
        self.questionsCorrectLabel = QLabel()
        self.questionsCorrectLabel.setFont(QFont('Arial', 15))
        topRowLayout.addWidget(self.questionsCorrectLabel)
        self.questionsLeftLabel = QLabel()
        self.questionsLeftLabel.setFont(QFont('Arial', 15))
        topRowLayout.addWidget(self.questionsLeftLabel)
        self.progressBar = QProgressBar(self)
        self.topRowWidget.setLayout(topRowLayout)
        mainLayout.addWidget(self.topRowWidget)
        mainLayout.addWidget(self.progressBar)
        #display single line edit for the source
        self.sourceDisplay = QLineEdit(self)
        self.sourceDisplay.setFont(QFont('Arial', 20))
        mainLayout.addWidget(self.sourceDisplay)
        #display multiline text as the question
        self.questionDisplay = QTextEdit(self)
        self.questionDisplay.setFont(QFont('Arial', 40))
        mainLayout.addWidget(self.questionDisplay, 100)
        #single line text input for the answer
        self.answerDisplay = QLineEdit(self)
        self.answerDisplay.setFont(QFont('Arial', 20))
        mainLayout.addWidget(self.answerDisplay)
        #multipline text to give correct answer if necessary
        self.correctAnswerDisplay = QTextEdit(self)        
        self.correctAnswerDisplay.setFont(QFont('Arial', 40))
        mainLayout.addWidget(self.correctAnswerDisplay, 50)
        #Horrizontal layout to hold the bottom three buttons
        bottomRowLayout = QHBoxLayout()
        #left button ... this is configured as the home button on all pages
        self.leftButton = QPushButton()
        self.leftButton.setFont(QFont('Arial', 20))
        self.leftButton.setText("Home")
        self.leftButton.clicked.connect(self.homeButtonClick)
        bottomRowLayout.addWidget(self.leftButton)
        #middle button
        self.middleButton = QPushButton()
        self.middleButton.setFont(QFont('Arial', 20))
        bottomRowLayout.addWidget(self.middleButton)
        #right button
        self.rightButton = QPushButton()
        self.rightButton.setFont(QFont('Arial', 20))
        bottomRowLayout.addWidget(self.rightButton)
        #add bottom row layout to main layout
        mainLayout.addLayout(bottomRowLayout)

        self.setLayout(mainLayout)
    def homeButtonClick(self):
        self.app.setCentralWidget(mainMenu.MainMenu(self.app))

#child classes for defining specific questionViewer functionality
class AddQuestionsQuestionViewer(QuestionViewer):
    def __init__(self, app, listToAddTo): #listToAddTo = ('listName2', listID2)
        super().__init__(app)
        self.listToAddTo = listToAddTo
        self.topRowWidget.setVisible(False)
        self.progressBar.setVisible(False)
        #display the list the user is adding questions to
        self.listLabel.setText(self.listToAddTo[0])
        #configure source input
        self.sourceDisplay.setReadOnly(False)
        self.sourceDisplay.textChanged.connect(self.sourceChanged)
        self.sourceDisplay.setToolTip("Enter the question's source")
        #configure question input
        self.questionDisplay.setReadOnly(False)
        self.questionDisplay.setToolTip("Enter a question")
        #configure answer input
        self.answerDisplay.setReadOnly(False)
        self.answerDisplay.setToolTip("Enter the answers separated by ` ")
        #hide correct answer display 
        self.correctAnswerDisplay.setVisible(False)
        #configure middle button as reuse source button
        self.lastSourceID = ""
        self.lastSourceName = ""
        self.sameLastSource = False
        self.middleButton.clicked.connect(self.reuseSourceButtonClick)
        self.middleButton.setText("reuse source")
        self.middleButton.setToolTip("enters the source used for the last question")
        #configure right button as add question button
        self.rightButton.clicked.connect(self.addQuestionButtonClick)
        self.rightButton.setText("Add Question")
        self.rightButton.setStyleSheet("background-color:DeepSkyBlue;")
    def sourceChanged(self):
        self.sameLastSource = False
    def addQuestionButtonClick(self):
        #hold the inputted data
        question = self.questionDisplay.toPlainText() 
        answerInput = self.answerDisplay.text()#answer input formatting is delt with in the database controller
        sourceName = self.sourceDisplay.text()
        #display a popup if any field is empty
        if sourceName == "":
            self.popup.setText("You need to add a source")
            self.popup.show()
            return
        if question == "":
            self.popup.setText("You need to add a question")
            self.popup.show()
            return
        if answerInput == "":
            self.popup.setText("You need to add answers")
            return        
        #clear the input fields
        self.sourceDisplay.clear()
        self.questionDisplay.clear()
        self.answerDisplay.clear()
        #if the source hasn't changed then use the old sourceID
        if self.sameLastSource == True:
            sourceID = self.lastSourceID
        else:#get the new sourceID and change the last source attribute
            sourceID = self.app.database.getSourceID(sourceName)
            #if sourceID is false then this is a new source entry so it must be added to the database
            if sourceID == False:
                sourceID = self.app.database.addSource(sourceName)
            self.lastSourceID = sourceID
            self.lastSourceName = sourceName
        #put the question into the database with the correct listID
        self.app.database.addQuestion(question, answerInput, self.listToAddTo[1], sourceID)
        self.sameLastSource = False#this will become true if the user presses the reuse source button and false if the user edits the source

    def reuseSourceButtonClick(self):
        if self.lastSourceID != "":
            self.sourceDisplay.setText(self.lastSourceName)
            self.sameLastSource = True
class FactMemoriserQuestionViewer(QuestionViewer):
    def __init__(self, app, selectedLists):#selectedLists = [(listName, listID)]
        super().__init__(app)
        self.answerEntered = False
        uniqueSelectedListIDs = []
        #get a list of all listIDs that are selected with no duplicates
        for list in selectedLists:#each list may be at a totally different point in the list tree
            sublists = self.app.database.getAllSublists(list[1], [list[1]])#adding the parent to the starter list ensures it will also be in the result
            #add each sublist to the list of unique listIDs. If a user selected a list and then it's parent there could be duplicats so checking is needed
            for listID in sublists:
                if listID not in uniqueSelectedListIDs:
                    uniqueSelectedListIDs.append(listID)
        #get a list of all the questionIDs from the selected lists
        self.questionIDs = self.app.database.getQuestionIDsOfLists(uniqueSelectedListIDs)#each entry = (questionID, listNam)
        self.totalQuestionsSelected = len(self.questionIDs)
        self.questionsCorrect = 0
        self.answersGiven = 0
        #configure labels
        self.progressBar.setValue(0)
        self.questionsLeftLabel.setText("Questions Left: " + str(len(self.questionIDs)))
        self.questionsCorrectLabel.setText("Questions Correct: 0")
        self.answersGivenLabel.setText("Answers given: 0")
        #disable editability
        self.sourceDisplay.setReadOnly(True)
        self.questionDisplay.setReadOnly(True)
        self.correctAnswerDisplay.setReadOnly(True)
        self.askQuestion()
        #configure enter button
        self.rightButton.setStyleSheet("background-color:LawnGreen;")
        self.rightButton.setText("Enter")
        self.rightButton.clicked.connect(self.enterButtonClick)
        #make the answer line edit control if the enter button does anything to prevent accidental skipping of questions
        self.answerDisplay.textChanged.connect(self.answerChanged)
    #this is called if the user enters text into the answer box
    def answerChanged(self):
        if self.answerDisplay.text() != "":#user must enter at least one character to enter an answer
            self.answerEntered = True
    #ask the user a question
    def askQuestion(self):
        if len(self.questionIDs) > 0:
            #choose a random questionID and select that question
            self.questionID = random.choice(self.questionIDs)
            self.questionDisplay.setText(self.app.database.getQuestion(self.questionID))
            self.sourceDisplay.setText(self.app.database.getQuestionSource(self.questionID))
            self.listLabel.setText(self.app.database.getListContaining(self.questionID))
        else:
            self.popup.setText("You have completed all of the selected questions!")
            self.popup.show()
            self.popup.buttonClicked.connect(self.homeButtonClick)

    #this connects the enter key on the keyboard with the enter button 
    def keyPressEvent(self, e):
        if e.key() == 16777220:
            self.enterButtonClick()
    #this method is called when the user enters their answer
    def enterButtonClick(self):
        if self.answerEntered == True:
            self.answersGiven = self.answersGiven + 1
            self.answersGivenLabel.setText("Answers given: " + str(self.answersGiven))
            self.answerEntered = False#make sure questions can't be accidentally skipped
            userAnswer = self.answerDisplay.text()
            userAnswer = userAnswer.replace(" ", "")
            self.answerDisplay.clear()
            correctAnswers = self.app.database.getQuestionAnswers(self.questionID)
            correctAnswersString = ""
            for correctAnswer in correctAnswers:
                correctAnswersString = correctAnswersString + correctAnswer + " "
                if userAnswer == correctAnswer:#process the correct answer and ask another question before returning
                    self.app.database.incrementStreak(self.questionID)
                    self.app.database.addStreakSquaredDaysToAskDate(self.questionID)
                    self.correctAnswerDisplay.setStyleSheet("background-color: LawnGreen;")
                    self.correctAnswerDisplay.setText("CORRECT!")
                    self.questionIDs.remove(self.questionID)
                    self.questionsLeftLabel.setText("Questions Left: " + str(len(self.questionIDs)))
                    self.questionsCorrect = self.questionsCorrect + 1
                    self.questionsCorrectLabel.setText("Questions Correct: " + str(self.questionsCorrect))
                    self.progressBar.setValue(int((self.questionsCorrect / self.totalQuestionsSelected) * 100))
                    self.askQuestion()
                    return
            #if the program gets to this point then the answer was wrong so process wrong answer
            self.app.database.zeroStreak(self.questionID)
            self.correctAnswerDisplay.setStyleSheet("background-color: RED;")
            self.correctAnswerDisplay.setText(correctAnswersString)
            self.askQuestion()





        
