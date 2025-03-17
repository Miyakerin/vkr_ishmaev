from datetime import datetime
from typing import Annotated

from pydantic import EmailStr
from sqlalchemy import MetaData, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, Mapped, mapped_column


def todict(obj):
    """ Return the object's dict excluding private attributes,
    sqlalchemy state and relationship attributes.
    """
    excl = ('_sa_adapter', '_sa_instance_state')
    return {k: v for k, v in vars(obj).items() if not k.startswith('_') and
            not any(hasattr(v, a) for a in excl)}


metadata_obj = MetaData()
Base = declarative_base()


class MyBase(Base):
    __abstract__ = True

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}

    def __repr__(self):
        params = ', '.join(f'{k}={v}' for k, v in todict(self).items())
        return f"{self.__class__.__name__}({params})"


class User(MyBase):
    __tablename__ = 'users'
    user_id: Mapped[int] = mapped_column("user_id", Integer, primary_key=True, nullable=False)
    username: Mapped[Annotated[str, 64]] = mapped_column("username", String(64), nullable=False)
    email: Mapped[EmailStr] = mapped_column("email", String(64), nullable=False)
    password: Mapped[Annotated[str, 256]] = mapped_column("password", String(256), nullable=False)
    create_timestamp: Mapped[datetime] = mapped_column("create_timestamp", DateTime(timezone=False), nullable=False, default=datetime.now())
    delete_timestamp: Mapped[datetime] = mapped_column("delete_timestamp", DateTime(timezone=False), nullable=True, default=None)
