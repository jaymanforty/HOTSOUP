from re import I
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

    ### HOTSOUP! POINTS ###

    def hs_update_lotto_jackpot(self, amount) -> int:
        """ Updates the current HS! points lottery. Returns the amount that was updated to """
        self.cursor.execute(""" UPDATE HSLottery SET TotalPoints = ? """, (amount,))
        self.connection.commit()
        return amount

    def hs_get_lotto_jackpot(self) -> int:
        """ Gets the current jackpot for lottery """
        jackpot = self.cursor.execute(""" SELECT TotalPoints FROM HSLottery """).fetchone()
        return jackpot[0] if jackpot else None

    def hs_get_all(self) -> list:
        """ Get all users with HS! points """
        users = self.cursor.execute(""" SELECT * FROM HSPoints""").fetchall()
        return users if users else None
        
    def hs_get_points(self, user_id) -> int:
        """ Gets the points of specified user """
        self.hs_init_points(user_id)
        points = self.cursor.execute(""" SELECT Points FROM HSPoints WHERE UserId = ? """,(user_id,)).fetchone()
        return points[0] if points else 0

    def hs_get_total_points_won(self, user_id) -> int:
        self.hs_init_points(user_id)
        points = self.cursor.execute(""" SELECT TotalPointsWon FROM HSPoints WHERE UserId = ? """,(user_id,)).fetchone()
        return points[0] if points else 0

    def hs_get_total_points_lost(self, user_id) -> int:
        self.hs_init_points(user_id)
        points = self.cursor.execute(""" SELECT TotalPointsLost FROM HSPoints WHERE UserId = ? """,(user_id,)).fetchone()
        return points[0] if points else 0

    def hs_add_points(self, user_id, points) -> int:
        """ Add X amount of points to specified user_id """
        self.hs_init_points(user_id)
        points += self.hs_get_points(user_id)
        self.cursor.execute(""" UPDATE HSPoints SET Points = ? WHERE UserId = ?""", (points, user_id))
        self.connection.commit()
        return points

    def hs_add_total_points_won(self, user_id, points) -> int:
        """ Add X amount of points to total points won """
        self.hs_init_points(user_id)
        points += self.hs_get_total_points_won(user_id)
        self.cursor.execute(""" UPDATE HSPoints SET TotalPointsWon = ? WHERE UserId = ?""",(points,user_id))
        return points

    def hs_add_total_points_lost(self,user_id,points) -> int:
        """ Add X amount of points to total points lost """
        self.hs_init_points(user_id)
        points += self.hs_get_total_points_lost(user_id)
        self.cursor.execute(""" UPDATE HSPoints SET TotalPointsLost = ? WHERE UserId = ?""",(points,user_id))
        return points

    def hs_sub_points(self, user_id, points) -> int:
        """ Add X amount of points to specified user_id """
        self.hs_init_points(user_id)
        points = self.hs_get_points(user_id) - points
        if points < 0: points = 0
        self.cursor.execute(""" UPDATE HSPoints SET Points = ? WHERE UserId = ?""",(points,user_id))
        self.connection.commit()
        return points
    
    def hs_init_points(self, user_id):
        self.cursor.execute(""" INSERT OR IGNORE INTO HSPoints VALUES (?,?,?,?) """, (user_id, 50, 0 ,0))
        self.connection.commit()

    ### Role guessing ###
    def update_fan_role(self, num_fan, user_id):
        """ Updates owner of the roles """
        self.cursor.execute(""" UPDATE FanRoles SET UserId = ? WHERE FanNumber = ?""",(user_id,num_fan))
        self.connection.commit()
        return
        
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


    ### HS! Tag ###
    def hs_add_tag_count(self, user_id, count) -> int:
        self.hs_init_tag_count(user_id)
        count += self.hs_get_tag_count(user_id)
        self.cursor.execute(""" UPDATE HSTag SET TagCount = ? WHERE UserId = ?""", (count, user_id))
        self.connection.commit()
        return count

    def hs_get_tag_count(self, user_id) -> int:
        self.hs_init_tag_count(user_id)
        points = self.cursor.execute(""" SELECT TagCount FROM HSTag WHERE UserId = ? """,(user_id,)).fetchone()
        return points[0] if points else 0

    def hs_init_tag_count(self, user_id):
        self.cursor.execute(""" INSERT OR IGNORE INTO HSTag VALUES (?,?) """, (user_id, 0))
        self.connection.commit()