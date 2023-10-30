from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget

import mainMenu
import listDeletor
import questionViewer

#parent class for defining list selector UI
class ListSelector(QWidget):
    def __init__(self, app):
        QWidget.__init__(self)
        self.app = app
        mainLayout = QVBoxLayout()
        self.listRoute = []
        self.selectedLists = []
        # label at the top of the page
        topLabel = QLabel(self)
        topLabel.setFont(QFont('Arial', 30))
        topLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.topLabel = topLabel
        mainLayout.addWidget(self.topLabel)
        # scroll area to display lists options to select from
        listOptionsScrollArea = QScrollArea()
        listOptionsWidget = QWidget()
        self.listOptionsLayout = QVBoxLayout()
        self.listOptionsLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        listOptionsWidget.setLayout(self.listOptionsLayout)
        listOptionsScrollArea.setWidget(listOptionsWidget)
        listOptionsScrollArea.setWidgetResizable(True)#This is needed to make the widgets added visible
        mainLayout.addWidget(listOptionsScrollArea)
        # row to add a list
        self.middleRowWidget = QWidget()#needs to be a widget in order no set visibility
        middleRowLayout = QHBoxLayout()
        self.newListNameInput = QLineEdit()
        self.newListNameInput.setFont(QFont('Arial', 20))
        addListButton = QPushButton("Add List")
        addListButton.setFont(QFont('Arial', 20))
        addListButton.clicked.connect(self.addListButtonClick)
        middleRowLayout.addWidget(self.newListNameInput)
        middleRowLayout.addWidget(addListButton)
        self.middleRowWidget.setLayout(middleRowLayout)
        mainLayout.addWidget(self.middleRowWidget)
        # label to indecate to the user that below are the lists selected
        selectedLabel = QLabel(self)
        selectedLabel.setFont(QFont('Arial', 30))
        selectedLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selectedLabel = selectedLabel
        mainLayout.addWidget(self.selectedLabel)
        # scroll area to display lists that are selected
        listsSelectedScrollArea = QScrollArea()
        listsSelectedWidget = QWidget()
        self.listsSelectedVerticalLayout = QVBoxLayout()
        self.listsSelectedVerticalLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        listsSelectedWidget.setLayout(self.listsSelectedVerticalLayout)
        listsSelectedScrollArea.setWidget(listsSelectedWidget)
        listsSelectedScrollArea.setWidgetResizable(True)#This is needed to make the widgets added visible
        mainLayout.addWidget(listsSelectedScrollArea)
        #Horrizontal layout to hold the bottom three buttons
        bottomRowLayout = QHBoxLayout()
        #left button
        backHomeButton = QPushButton("Back")
        backHomeButton.setFont(QFont('Arial', 20))
        backHomeButton.clicked.connect(self.backHomeButtonClick)
        bottomRowLayout.addWidget(backHomeButton)
        #right button
        self.rightButton = QPushButton()
        self.rightButton.setFont(QFont('Arial', 20))
        bottomRowLayout.addWidget(self.rightButton)
        #add bottom row layout to main layout
        mainLayout.addLayout(bottomRowLayout)
        self.setLayout(mainLayout)
        #show a popup dialogue to tell the user they can only select one list
        self.popup = QMessageBox()
        self.popup.setIcon(QMessageBox.Icon.Information)
        self.popup.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.initialiseListOptionsDisplay()
    #adds a new sublist
    def addListButtonClick(self):
        parentListID = self.listRoute[len(self.listRoute) - 1]
        newListName = self.newListNameInput.text()
        self.newListNameInput.clear()
        self.app.database.addSublist(parentListID, newListName)
        self.populateOptionsDisplay(parentListID)#redraw the options available as one has been added
    #clear rows on options display
    def clearOptionsDisplay(self):
        while self.listOptionsLayout.count():
            self.listOptionsLayout.takeAt(0).widget().deleteLater()
    #set the options display to show universal root
    def initialiseListOptionsDisplay(self):
        self.middleRowWidget.setVisible(False)
        selectButton, searchButton = self.addListDisplayRow("UniversalRoot", 1, True)#UniversalRoot listID will always be 1
        #connect the buttons to their functionality
        searchButton.clicked.connect(self.searchButtonClick)
        selectButton.clicked.connect(self.selectButtonClick)
    #add back button to list options display
    def addBackButton(self):
        backButton = QPushButton("Back")
        backButton.setStyleSheet("background-color:DeepSkyBlue;")
        backButton.clicked.connect(self.backButtonClick)
        self.listOptionsLayout.addWidget(backButton)
    #functionality for the back button in the list options display
    def backButtonClick(self):
        self.clearOptionsDisplay()
        self.listRoute.pop()
        print(self.listRoute)
        if len(self.listRoute) == 0:
            self.initialiseListOptionsDisplay()
        else:
            self.populateOptionsDisplay(self.listRoute[len(self.listRoute) - 1])
    #go back a page button
    def backHomeButtonClick(self):
        self.app.setCentralWidget(mainMenu.MainMenu(self.app))
            
    #populate the options display with the child lists given a parent listID
    def populateOptionsDisplay(self, listID):
        self.clearOptionsDisplay()
        #if the parent is not the universal root then add a back button
        self.addBackButton()
        for sublist in self.app.database.getImmediateSublists(listID):#returns [('listName', listID), ('listName2', listID2)]
            #check that the new option isn't actually already selected
            if(sublist[0], sublist[1]) in self.selectedLists:
                print("aldready selected")
                continue
            selectButton, searchButton = self.addListDisplayRow(sublist[0], sublist[1], True)
            #connect buttons to their functionality
            searchButton.clicked.connect(self.searchButtonClick)
            selectButton.clicked.connect(self.selectButtonClick)
        
    #method to make rows in this list displays. Functionality of the buttons is not made here!
    def addListDisplayRow(self, listName, listID, isOptionRow):
        rowWidget = QWidget()
        rowLayout = QHBoxLayout()
        #make the label of the name of the list 
        rowLabel = QLabel(listName)
        rowLabel.setFont(QFont('Arial', 15))
        rowLayout.addWidget(rowLabel)
        if isOptionRow:
            #make the select button
            selectButton = QPushButton("Select")
            selectButton.listID = listID
            selectButton.listName = listName
            selectButton.setStyleSheet("background-color : PaleGreen;")
            rowLayout.addWidget(selectButton)
            #make the search button
            searchButton = QPushButton("Search")
            searchButton.listID = listID
            searchButton.setStyleSheet("background-color : #FFAE42;")#colour is yellow orange
            rowLayout.addWidget(searchButton)
            #add rowlayout to widget and add to the options display
            rowWidget.setLayout(rowLayout)
            self.listOptionsLayout.addWidget(rowWidget)
            #return references to buttons so the functionality can be added
            return selectButton, searchButton
        else:#this will be selected lists display
            #make the button to remove this selected option
            removeButton = QPushButton("Remove")
            removeButton.listID = listID
            removeButton.listName = listName
            removeButton.clicked.connect(self.removeButtonClick)
            removeButton.setStyleSheet("background-color : red;")
            rowLayout.addWidget(removeButton)
            #add row to selected options display
            rowWidget.setLayout(rowLayout)
            self.listsSelectedVerticalLayout.addWidget(rowWidget)
    #remove a row from the selected list display and add the removed entry to the options display
    def removeButtonClick(self):
        button = self.sender()
        self.selectedLists.remove((button.listName, button.listID))
        button.parent().deleteLater()#delete this selection from the selected lists display
        #check if this is the universal root that is being removed
        if len(self.listRoute) == 0:
            if button.listID == 1:
                selectButton, searchButton = self.addListDisplayRow(button.listName, button.listID, True)
                #connect buttons to their functionality
                searchButton.clicked.connect(self.searchButtonClick)
                selectButton.clicked.connect(self.selectButtonClick)               
        #check if this list is a sublist of the currently viewed list and if so add it back to the options display
        elif (button.listName, button.listID) in self.app.database.getImmediateSublists(self.listRoute[len(self.listRoute) - 1]):
            selectButton, searchButton = self.addListDisplayRow(button.listName, button.listID, True)
            #connect buttons to their functionality
            searchButton.clicked.connect(self.searchButtonClick)
            selectButton.clicked.connect(self.selectButtonClick)    
    #this method is abstract and it will be implemented in the child classes
    def selectButtonClick(self):
        raise NotImplementedError("Please Implement this method")
    #this method may be overridden in subclasses
    def searchButtonClick(self):  
        button = self.sender()
        self.listRoute.append(button.listID)
        print(self.listRoute)
        self.populateOptionsDisplay(button.listID)


#all subclasses will either be used to pick one or multiple lists so the select button functionalities is done in the below subclasses
class selectOneListSelector(ListSelector):
    def __init__(self, app):
        super().__init__(app)
    def selectButtonClick(self):
        if self.listsSelectedVerticalLayout.count() == 0:
            button = self.sender()
            self.selectedLists.append((button.listName, button.listID))
            self.addListDisplayRow(button.listName, button.listID, False)
            button.parent().deleteLater()#delete this options display row
        else:#already a list selected
            self.popup.setText("You can only select one list")
            self.popup.show()
#the below subclasses have specific names and will inherit from one of the above two parent classes
class ListSelectorMemorise(ListSelector):
    def __init__(self, mainWindow):
        super().__init__(mainWindow)
        self.topLabel.setText("Select Fact Lists to memorise")
        self.selectedLabel.setText("You will memorise:")

    def selectButtonClick(self):
        button = self.sender()
        self.selectedLists.append((button.listName, button.listID))
        self.addListDisplayRow(button.listName, button.listID, False)
        button.parent().deleteLater()#delete this options display row
        self.rightButton.setText("Memorise!")
        self.rightButton.setStyleSheet("background-color:LawnGreen;")
        self.rightButton.clicked.connect(self.memoriseButtonClick)
    def memoriseButtonClick(self):
        self.app.setCentralWidget(questionViewer.FactMemoriserQuestionViewer(self.app, self.selectedLists))

class ListSelectorAddFacts(selectOneListSelector):
    def __init__(self, app):
        super().__init__(app)
        self.topLabel.setText("Select your list to add to")
        self.selectedLabel.setText("You will add facts to:")
        self.rightButton.setText("Add Facts")
        self.rightButton.setStyleSheet("background-color : DeepSkyBlue;")
        self.rightButton.clicked.connect(self.addFactsButtonClick)
    def addFactsButtonClick(self):
        if len(self.selectedLists) == 0:
            self.popup.setText("You must select one list")
            self.popup.show()
        else:
            self.app.setCentralWidget(questionViewer.AddQuestionsQuestionViewer(self.app, self.selectedLists[0]))
    #this method overrides parent class implementation as also needs to show the add list entry when needed
    def searchButtonClick(self):  
        listID = self.sender().listID
        self.middleRowWidget.setVisible(True)
        self.listRoute.append(listID)
        print(self.listRoute)
        self.populateOptionsDisplay(listID)
class ListSelectorDeleteLists(ListSelector):
    def __init__(self, app):
        super().__init__(app)
        self.topLabel.setText("Select your list to delete")
        self.selectedLabel.setText("You will delete:")
        self.rightButton.setText("Delete")
        self.rightButton.setStyleSheet("background-color : red;")
        self.rightButton.clicked.connect(self.deleteButtonClick)
    def selectButtonClick(self):
        button = self.sender()
        if button.listID == 1:#if this is the universal root
            self.popup.setText("You cannot delete the UniversalRoot list")
            self.popup.show()
        elif self.listsSelectedVerticalLayout.count() == 0:
            button = self.sender()
            self.selectedLists.append((button.listName, button.listID))
            self.addListDisplayRow(button.listName, button.listID, False)
            button.parent().deleteLater()#delete this options display row
        else:#already a list selected
            self.popup.setText("You can only select one list")
            self.popup.show()
    def deleteButtonClick(self):
        if len(self.selectedLists) > 0:#if a list has been selected
            self.app.setCentralWidget(listDeletor.ListDeletor(self.app, self.selectedLists[0]))
        else:
            self.popup.setText("You must select a list")
            self.popup.show()            


    

