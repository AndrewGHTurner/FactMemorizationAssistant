import sqlite3


class DatabaseController():
    def __init__(self):
        self.connection = sqlite3.connect("facts.db")#connect to the database
        self.cursor = self.connection.cursor()#hold a reference to the cursor in the application object
        #check is foreign keys are supported
        self.cursor.execute("PRAGMA foreign_keys = ON")
        if (self.cursor.execute("PRAGMA foreign_keys").fetchall()[0][0] == 1):
            print("foreign keys are available")
        else:
            print("foreign keys are not available")
        #table containing questions
        self.cursor.execute("CREATE TABLE IF NOT EXISTS questions("
                   "questionID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                   "question VARCHAR NOT NULL,"
                   "streak INTEGER DEFAULT 0,"
                   "askDate DATE DEFAULT (date('now')),"
                   "listID INTEGER NOT NULL,"
                   "sourceID INTEGER,"
                   "FOREIGN KEY (listID) REFERENCES lists (listID),"
                   "FOREIGN KEY (sourceID) REFERENCES sources(sourceID)"
                   ")")
        #index to allow for quick selection of questions within a particular list
        self.cursor.execute("CREATE INDEX IF NOT EXISTS listIDIndex "
                   "ON questions(listID)")
        #table contaning the answers to the questions
        self.cursor.execute("CREATE TABLE IF NOT EXISTS answers("
                    "questionID INTEGER NOT NULL,"
                    "answer VARCHAR NOT NULL,"
                    "FOREIGN KEY (questionID) REFERENCES questions(questionID)"
                    ")")
        #table containing the sources of the questions
        self.cursor.execute("CREATE TABLE IF NOT EXISTS sources("
                            "sourceID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                            "sourceName VARCHAR UNIQUE NOT NULL,"
                            "timesReferenced INTEGER DEFAULT 0"
                            ")")
        #index to allow for quick selection of sources by ID
        self.cursor.execute("CREATE INDEX IF NOT EXISTS sourcesIDINDEX "
                            "ON sources(sourceID)")
        #index to allow for searching of source IDs by name
        self.cursor.execute("CREATE INDEX IF NOT EXISTS sourcesNameINDEX "
                            "ON sources(sourceName)")
        #idnex to allow for quick selection of answers to a particular question
        self.cursor.execute("CREATE INDEX IF NOT EXISTS "
                    "questionIndexA ON answers(questionID)")
        #table containing the human readable names of the question lists
        self.cursor.execute("CREATE TABLE IF NOT EXISTS lists("
                    "listID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,"
                    "listName VARCHAR UNIQUE NOT NULL"
                    ")")
        #index to allow for quick selection of a list name given its ID
        self.cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS listIDIndexMain ON lists(listID)")
        #add empty list that will be the root node of the system ... this list will encompas all others lists 
        self.cursor.execute("INSERT OR IGNORE INTO lists (listName) "
                    "VALUES ('UniversalRoot')")
        self.connection.commit()
        #table containing parent and sublist relationships between lists
        self.cursor.execute("CREATE TABLE IF NOT EXISTS sublists("
                    "parentID INTEGER NOT NULL,"
                    "childID INTEGER NOT NULL,"
                    "FOREIGN KEY (parentID) REFERENCES lists(listID)"
                    "FOREIGN KEY (childID) REFERENCES lists(listID)"
                    ")")
        #index to allow for quick selection of sublists given a parent ID
        self.cursor.execute("CREATE INDEX IF NOT EXISTS "
                    "parentIndex ON sublists(parentID)")
        #index to allow for quick selection of superlists given a child ID
        self.cursor.execute("CREATE INDEX IF NOT EXISTS "
                    "childIndex ON sublists(childID)")
    #given a listID returns a list of the immediate sublists
    def getImmediateSublists(self, listID):
        print("SELECT listName, listID FROM lists INNER JOIN sublists ON lists.listID = sublists.childID WHERE sublists.parentID = " + str(listID))
        self.cursor.execute("SELECT listName, listID FROM lists INNER JOIN sublists ON lists.listID = sublists.childID WHERE sublists.parentID = " + str(listID))
        return self.cursor.fetchall()
    #return a list of all lists that are below the given list in the list tree. The result will NOT include the given listID
    def getAllSublists(self, listID, sublists):
        #for each sublist of the given list get its sublists
        print(listID)
        print(self.getImmediateSublists(listID))
        for sublist in self.getImmediateSublists(listID):
            print("K")
            print(sublist)
            sublists.append(sublist[1])#add the sublist to the sublists list
            self.getAllSublists(sublist[1], sublists)#repeat for each sublist
        return sublists    
    #given a parent listID and a new list name enter the new sublist into the database. The result will NOT include the given listID
    def addSublist(self, parentListID, newListName):
        self.cursor.execute("INSERT INTO lists (listName) VALUES ('" + newListName + "') RETURNING listID")
        #get new list's ID
        newListID = self.cursor.lastrowid#seems to return the auto incremented primary key value which is good
        #make relation in the sublists table
        self.cursor.execute("INSERT INTO sublists (parentID, childID) VALUES (" + str(parentListID) + ", " + str(newListID) + ")")
        self.connection.commit()
    #get the name of the list that a question belongs to given the questionID
    def getListContaining(self, questionID):
        self.cursor.execute("SELECT listName FROM lists INNER JOIN questions ON questions.listID = lists.listID WHERE questions.questionID = " + str(questionID))
        return self.cursor.fetchall()[0][0]
    #delete all questions and answers given a listID
    def deleteQuestionsByListID(self, listID):
        #first delete the answers and then the questions
        self.cursor.execute("SELECT questionID, sourceID FROM questions WHERE listID = " + str(listID))
        questionIDs = self.cursor.fetchall()
        for questionID, sourceID in questionIDs:
            #delete the questions and answers
            self.cursor.execute("DELETE FROM answers WHERE questionID = " + str(questionID))
            self.cursor.execute("DELETE FROM questions WHERE questionID = " + str(questionID))
            self.connection.commit()
            #decrement the timesReferenced for the source of the question and delete the source if the timesReferenced reaches zero
            self.cursor.execute("UPDATE sources SET timesReferenced = ((SELECT timesReferenced FROM sources WHERE sourceID = " + str(sourceID) + ") - 1) WHERE sourceID = " + str(sourceID))
            self.connection.commit()
            self.cursor.execute("SELECT timesReferenced FROM sources WHERE sourceID = " + str(sourceID))
            timesReferenced = self.cursor.fetchall()[0][0]
            if timesReferenced < 1:#delete the source
                self.cursor.execute("DELETE FROM sources WHERE sourceID = " + str(sourceID))
        #then delete all sublist entrys
        self.cursor.execute("DELETE FROM sublists WHERE childID = " + str(listID)) #rows where listID is the parent will be deleted when child lists are deleted
        self.connection.commit()
        self.cursor.execute("DELETE FROM sublists WHERE parentID = " + str(listID)) #rows where listID is the parent will be deleted when child lists are deleted
        self.connection.commit()
        #then delete the list name entry
        self.cursor.execute("DELETE FROM lists WHERE listID = " + str(listID))	
        self.connection.commit()	
    #get all questionIDs from a list
    def getQuestionIDsOfLists(self, listIDs):
        conditions = ""
        for listID in listIDs:
            conditions = conditions + "listID = " + str(listID) + " OR "
        conditions = conditions[:-3]
        self.cursor.execute("SELECT questionID FROM questions WHERE (" + conditions + ") AND askDate <= DATE('now')")
        questionIDs = []
        for tuple in self.cursor.fetchall():
            questionIDs.append(tuple[0])
        return questionIDs

    #get sourceID given source name
    def getSourceID(self, sourceName):
        self.cursor.execute("SELECT sourceID FROM sources WHERE sourceName = '" + sourceName + "'")
        result = self.cursor.fetchall()
        if len(result) == 0:
            return False
        else:
            print("KKKK")
            print( result[0][0])
            return result[0][0]
    #add a new source to the database and return the sourceID of the new source
    def addSource(self, sourceName):
        self.cursor.execute("INSERT INTO sources (sourceName) VALUES ( '" + sourceName + "')")
        self.connection.commit()
        return self.cursor.lastrowid#seems to return the auto incremented primary key value which is good
    #add a new question to the database ... the sourceID given will definitly exist in the database
    def addQuestion(self, question, answerInput, listID, sourceID):
        #format the question so that it is suitable for the database
        question = question.replace("'","''")
        question = question.replace(">", "&gt;")
        question = question.replace("<", "&lt;")
        #put the question in the database
        self.cursor.execute("INSERT INTO questions (question, listID, sourceID) VALUES ('" + question + "', " + str(listID) + ", " + str(sourceID) + ")")
        #increment the source's timesReferenced number
        self.cursor.execute("UPDATE sources SET timesReferenced = ((SELECT timesReferenced FROM sources WHERE sourceID = " + str(sourceID) + ") + 1) WHERE sourceID = " + str(sourceID))
        #put the answers in the database
        questionID = self.cursor.lastrowid
        #format user input so it is suitable for the database
        answerInput = answerInput.replace(" ", "")
        answerInput = answerInput.replace("'","''")
        answerInput = answerInput.replace(">", "&gt;")
        answerInput = answerInput.replace("<", "&lt;")
        answers = answerInput.split("`")
        for answer in answers:
            self.cursor.execute("INSERT INTO answers (questionID, answer) VALUES (" + str(questionID) + ", '" + answer + "' )")
        self.connection.commit()
    def countQuestions(self, lists):
        conditions = ""
        for listID in self.selectedLists:
            conditions = conditions + "listID = " + str(listID) + " OR "
        pass
    #return the list of answers for a question given a questionID
    def getQuestionAnswers(self, questionID):
        self.cursor.execute("SELECT answer FROM answers WHERE questionID = " + str(questionID))
        correctAnswers = []
        for tuple in self.cursor.fetchall():
            answer = tuple[0].lower()
            answer = answer.replace("''", "'")
            correctAnswers.append(answer)
        return correctAnswers
    #increment the streak of a question given the questionID
    def incrementStreak(self, questionID):
        self.cursor.execute("UPDATE questions SET streak = ((SELECT streak FROM questions WHERE questionID = " + str(questionID) + ") + 1) WHERE questionID = " + str(questionID))
        self.connection.commit()
    #changes the ask date to exponentially further into the future based on the size of the streak given a questionID
    def addStreakSquaredDaysToAskDate(self, questionID):
        self.cursor.execute("SELECT streak FROM questions WHERE questionID = " + str(questionID))
        streak = self.cursor.fetchall()[0][0]
        self.cursor.execute("UPDATE questions SET askDate = DATE(DATE('now'), '+" + str(streak * streak) + " day') WHERE questionID = " + str(questionID))
        self.connection.commit()
    #set the streak to zero given a questionID
    def zeroStreak(self, questionID):
        self.cursor.execute("UPDATE questions SET streak = 0 WHERE questionID = " + str(questionID))
        self.connection.commit()
    #return a question given a questionID
    def getQuestion(self, questionID):
        self.cursor.execute("SELECT question FROM questions WHERE questionID = " + str(questionID))
        return self.cursor.fetchall()[0][0]
    #return the source of a question given the questionID
    def getQuestionSource(self, questionID):
        self.cursor.execute("SELECT sourceName FROM sources INNER JOIN questions ON questions.sourceID = sources.sourceID WHERE questions.questionID = " + str(questionID))
        return self.cursor.fetchall()[0][0]
    #to be called when the program terminates
    def closeDatabase(self):
        self.connection.close()