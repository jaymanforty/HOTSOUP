from sqlalchemy import Column, Integer


from db.config import Base



class HSPoints(Base):
    __tablename__="hs_points"

    user_id = Column(Integer, primary_key=True)
    points = Column(Integer)
    points_won = Column(Integer)
    points_lost = Column(Integer)
    double_wins = Column(Integer)
    double_losses = Column(Integer)

    @property
    def mention(self):
        return f"<@{self.user_id}>"