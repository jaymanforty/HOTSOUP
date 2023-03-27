from sqlalchemy.future import select
from sqlalchemy.orm import Session

from db.config import async_session
from db.models.hs_points import HSPoints

from exc import CustomCommandError

class DB:

    def __init__(self, session: Session) -> None:
        self.db_session = session

    ############
    ### Util ###
    ############

    async def add(self, obj):
        """ Add ORM object to database """
        self.db_session.add(obj)
        await self.db_session.flush()

    async def delete(self, obj):
        await self.db_session.delete(obj)
        await self.db_session.flush()
    

    #################
    ### HS Points ###
    #################

    async def get_hs_points_obj(self, user_id: int) -> HSPoints:
        """ Get HSPoints model for given user """
        q = await self.db_session.execute(select(HSPoints).where(HSPoints.user_id == user_id))
        o = q.scalars().first()
        if not o: raise CustomCommandError("You have not collected any points!")
        return o if o else None