from datetime import datetime

from sqlalchemy import MetaData, Integer, DateTime, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import declarative_base, mapped_column, Mapped


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


class Chat(MyBase):
    __tablename__ = 'chat'

    chat_id: Mapped[int] = mapped_column("chat_id", Integer, primary_key=True, nullable=False)
    language: Mapped[str] = mapped_column("language", String(16), nullable=False)
    user_id: Mapped[int] = mapped_column("user_id", Integer, nullable=False)
    create_timestamp: Mapped[datetime] = mapped_column("create_timestamp", DateTime(timezone=False), nullable=False,
                                                       default=datetime.now())
    delete_timestamp: Mapped[datetime] = mapped_column("delete_timestamp", DateTime(timezone=False), nullable=True,
                                                       default=None)


class Message(MyBase):
    __tablename__ = 'message'
    message_id: Mapped[int] = mapped_column("message_id", Integer, primary_key=True, nullable=False)
    company_name: Mapped[str] = mapped_column("company_name", String(128), nullable=True, default=None)
    sender: Mapped[str] = mapped_column("sender", String(256), nullable=False)
    chat_id: Mapped[int] = mapped_column("chat_id", ForeignKey(Chat.chat_id), nullable=False)
    create_timestamp: Mapped[datetime] = mapped_column("create_timestamp", DateTime(timezone=False), nullable=False,
                                                       default=datetime.now())
    delete_timestamp: Mapped[datetime] = mapped_column("delete_timestamp", DateTime(timezone=False), nullable=True,
                                                       default=None)


class MessageData(MyBase):
    __tablename__ = 'message_data'
    message_data_id: Mapped[int] = mapped_column("message_data_id", Integer, primary_key=True, nullable=False)
    message_id: Mapped[int] = mapped_column("message_id", ForeignKey(Message.message_id), nullable=False)
    text: Mapped[str] = mapped_column("text", Text, nullable=False)
    is_main: Mapped[bool] = mapped_column("is_main", Boolean, nullable=False, default=True)
    create_timestamp: Mapped[datetime] = mapped_column("create_timestamp", DateTime(timezone=False), nullable=False,
                                                       default=datetime.now())
    delete_timestamp: Mapped[datetime] = mapped_column("delete_timestamp", DateTime(timezone=False), nullable=True,
                                                       default=None)


class File(MyBase):
    __tablename__ = 'file'
    file_id: Mapped[int] = mapped_column("file_id", Integer, primary_key=True, nullable=False)
    filename: Mapped[str] = mapped_column("filename", String(256), nullable=False)
    s3_key: Mapped[str] = mapped_column("s3_key", String(256), nullable=False)
    bucket_name: Mapped[str] = mapped_column("bucket_name", String(256), nullable=False)
    file_size: Mapped[str] = mapped_column("file_size", Integer, nullable=False) # file size in bytes
    mimetype: Mapped[str] = mapped_column("mimetype", String(256), nullable=False)
    user_id: Mapped[int] = mapped_column("user_id", Integer, nullable=False)
    create_timestamp: Mapped[datetime] = mapped_column("create_timestamp", DateTime(timezone=False), nullable=False,
                                                       default=datetime.now())
    delete_timestamp: Mapped[datetime] = mapped_column("delete_timestamp", DateTime(timezone=False), nullable=True,
                                                       default=None)


class MessageDataXFile(MyBase):
    __tablename__ = 'message_data_x_file'
    message_data_x_file_id: Mapped[int] = mapped_column("message_data_x_file_id", Integer, primary_key=True, nullable=False)
    file_id: Mapped[int] = mapped_column("file_id", ForeignKey(File.file_id), nullable=False)
    message_data_id: Mapped[int] = mapped_column("message_data_id", ForeignKey(MessageData.message_data_id), nullable=False)
    create_timestamp: Mapped[datetime] = mapped_column("create_timestamp", DateTime(timezone=False), nullable=False,
                                                       default=datetime.now())
    delete_timestamp: Mapped[datetime] = mapped_column("delete_timestamp", DateTime(timezone=False), nullable=True,
                                                       default=None)


class FileXCompany(MyBase):
    __tablename__ = 'file_x_company'
    file_x_company_id: Mapped[int] = mapped_column("file_x_company_id", Integer, primary_key=True, nullable=False)
    file_id: Mapped[int] = mapped_column("file_id", ForeignKey(File.file_id), nullable=False)
    company_name: Mapped[str] = mapped_column("company_name", String(256), nullable=False)
    file_company_id: Mapped[str] = mapped_column("file_company_id", String(512), nullable=False)
    id_type: Mapped[str] = mapped_column("id_type", String(64), nullable=False)
    create_timestamp: Mapped[datetime] = mapped_column("create_timestamp", DateTime(timezone=False), nullable=False,
                                                       default=datetime.now())
    delete_timestamp: Mapped[datetime] = mapped_column("delete_timestamp", DateTime(timezone=False), nullable=True,
                                                       default=None)


class UserBalance(MyBase):
    __tablename__ = 'user_balance'
    user_balance_id: Mapped[int] = mapped_column("user_balance_id", Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column("user_id", Integer, nullable=False)
    balance: Mapped[int] = mapped_column("balance", Integer, nullable=False, default=0)
    create_timestamp: Mapped[datetime] = mapped_column("create_timestamp", DateTime(timezone=False), nullable=False,
                                                       default=datetime.now())
    delete_timestamp: Mapped[datetime] = mapped_column("delete_timestamp", DateTime(timezone=False), nullable=True,
                                                       default=None)