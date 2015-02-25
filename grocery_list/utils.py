""" Custom Utility Functions """

from . import app
from .database import session
from . import models


def update_form_data(data):
    """ Update SQLAlchemy model data with HTML form data

    Arguments:
        data (dict): Dictionary of html form data
            key: Form input name in schema ModelClass.ID.ColumnName
                ModelClass: SQLAlchemy model class defined in models.py
                ID: Primary Key ID, multiple keys comma separated
                ColumnName: Column name
            value: Form input value

    Return:
        Boolean indicating success
    """

    # Loop through sorted dictionary
    for key, value in sorted(data.items()):

        # Set key parameters per Form input name schema
        param = str(key).split(".", 2)
        key_model = param[0]
        key_primary_key = tuple(int(i) for i in param[1].split(","))
        key_column = param[2]

        try:
            # Set SQLAlchemy model class
            model = getattr(models, key_model)
            # Set row to update
            row = session.query(model).get(key_primary_key)
            # Perform column update with dict value
            setattr(row, key_column, value)
            session.commit()
        except Exception as e:
            print("ERROR = {}".format(e))
            print("Model = {}".format(param[0]))
            print("Key = {}".format(param[1]))
            print("Value = {}".format(param[2]))
            return False

    return True
