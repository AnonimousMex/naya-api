

from sqlmodel import Session


class UserController:
    def __init(self, session: Session):
        self.session = session