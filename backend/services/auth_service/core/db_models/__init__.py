from datetime import datetime
from typing import Annotated

from pydantic import EmailStr
from sqlalchemy import MetaData, Column, Integer, String, Boolean, DateTime, ForeignKey
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
    is_admin: Mapped[bool] = mapped_column("is_admin", Boolean, nullable=False, default=False)
    create_timestamp: Mapped[datetime] = mapped_column("create_timestamp", DateTime(timezone=False), nullable=False, default=datetime.now())
    delete_timestamp: Mapped[datetime] = mapped_column("delete_timestamp", DateTime(timezone=False), nullable=True, default=None)


class UserXProfilePicture(MyBase):
    __tablename__ = 'user_x_profile_picture'
    user_x_profile_picture_id: Mapped[int] = mapped_column("user_x_profile_picture_id", Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column("user_id", ForeignKey(User.user_id), nullable=False)
    s3_key: Mapped[str] = mapped_column("s3_key", String(256), nullable=False)
    bucket_name: Mapped[str] = mapped_column("bucket_name", String(256), nullable=False)
    is_main: Mapped[bool] = mapped_column("is_main", Boolean, nullable=False, default=True)
    create_timestamp: Mapped[datetime] = mapped_column("create_timestamp", DateTime(timezone=False), nullable=False,
                                                       default=datetime.now())
    delete_timestamp: Mapped[datetime] = mapped_column("delete_timestamp", DateTime(timezone=False), nullable=True,
                                                       default=None)


class UserCode(MyBase):
    __tablename__ = 'user_code'
    user_code_id: Mapped[int] = mapped_column("user_code_id", Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column("user_id", ForeignKey(User.user_id), nullable=False)
    code: Mapped[Annotated[str, 16]] = mapped_column("code", String(1024), nullable=False)
    attempt_number: Mapped[int] = mapped_column("attempt_number", Integer, nullable=False)
    create_timestamp: Mapped[datetime] = mapped_column("create_timestamp", DateTime(timezone=False), nullable=False,
                                                       default=datetime.now())
    delete_timestamp: Mapped[datetime] = mapped_column("delete_timestamp", DateTime(timezone=False), nullable=True, default=None)
