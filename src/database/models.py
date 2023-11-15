import enum
from sqlalchemy import Column, Integer, String, Boolean, func, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Date, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=False)
    roles = Column("roles", Enum(Role), default=Role.user)


note_m2m_tag = Table(
    "note_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE")),
)


class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    created_at = Column("created_at", DateTime, default=func.now())
    description = Column(String(150), nullable=False)
    done = Column(Boolean, default=False)
    tags = relationship("Tag", secondary=note_m2m_tag, backref="notes")


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    e_mail = Column(String(50), nullable=False)
    phone_number = Column(String(17), nullable=False)
    born_date = Column(Date, nullable=False)
    description = Column(String(150), nullable=False)
    created_at = Column("created_at", DateTime, default=func.now())


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False, unique=True)
