import sqlite3

class Database:

    connection = None
    cursor = None

    def __init__(self):

        if Database.connection is None:
            try:
                Database.connection = sqlite3.connect("db.db")
                Database.cursor = Database.connection.cursor()
            except Exception as error:
                print("Error: DB connection not established {}".format(error))
            else:
                print("connection established")
        
        self.connection = Database.connection
        self.cursor = Database.cursor



    ### Role guessing ###
    def update_user_guesses(self, user_id, num_guesses):
        self.cursor.execute(""" UPDATE Guesses SET NumGuesses = ? WHERE UserId = ? """, (num_guesses, user_id))
        self.connection.commit()
        return

    def init_user_guesses(self, user_id):
        """ Initializes user id into database """
        self.cursor.execute(""" INSERT OR IGNORE INTO Guesses VALUES (?,?) """, (user_id,0))
        self.connection.commit()
        return

    def get_fan_role_user(self, num_fan) -> int:
        """ Returns the user_id for who currently holds num_fan spot"""
        user_id = self.cursor.execute(""" SELECT UserId FROM FanRoles WHERE FanNumber = ? """,(num_fan,)).fetchone()
        return user_id[0] if user_id else None
    
    def get_num_guesses(self, user_id) -> int:
        """ Returns the number of guesses for user_id supplied """
        guesses = self.cursor.execute(""" SELECT NumGuesses FROM Guesses WHERE UserId = ?""",(user_id,)).fetchone()
        return guesses[0] if guesses else None