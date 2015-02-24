""" Database Connection using SQLAlchemy """

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from . import app


class Base(object):
    """ Extend SQLAlchemy Base object """

    def as_dict_base(self, excluded_columns = []):
        """ Convert model data into dictionary

        Args:
            excluded_columns (list[str]): List of columns to exclude from dictionary

        Return:
            SQLAlchemy model as dictionary
        """
        data_dict = {}
        for column in self.__table__.columns:
            if column.name not in excluded_columns:
                data_dict.update({column.name: getattr(self,column.name)})

        return data_dict


# Database URI from config.py
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
Base = declarative_base(cls=Base)
Session = sessionmaker(bind=engine)
session = Session()