import sys
from mainMenu import MainMenu
from databaseController import DatabaseController
from PyQt6.QtWidgets import QApplication, QMainWindow

#fact memorisation assistant class needs to initialise the database and present the user 
#with the main menu screen

class FactMemorisationAssistant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(400, 40, 800, 600)#set dimensions of the window x, y(of top left courner) width height
        self.setCentralWidget(MainMenu(self))#make the main menu visible
        self.database = DatabaseController()   
    #this will be run when the user closes the app
    def closeEvent(self, event):
        self.database.closeDatabase()
        print("Goodbye")
def main():
    #instansiate and display the application
    app = QApplication(sys.argv)
    mainWindow = FactMemorisationAssistant()
    mainWindow.show()
    sys.exit(app.exec())
    
if __name__ == '__main__':
   main()