from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean

engine = create_engine('sqlite:///user_database.db',echo=True)

meta = MetaData()

Users= Table(
    "Users",
    meta,
    Column('id', Integer, primary_key=True),
    Column('email', String, nullable=False, unique=True),
    Column('hashed_password', String, nullable=False),
    Column('disabled', Boolean, default=False),
)

meta.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)