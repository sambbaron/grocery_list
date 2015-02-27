""" Custom Utility Functions """

from .database import session
from . import models


def update_from_form(data, **new_primary_keys):
    """ Create/Update SQLAlchemy model data with HTML form data

    If primary_key not provided in dictionary key, then assume
        new record and use new_primary_keys object

    Arguments:
        data (dict): Dictionary of html form data
            key: Form input name in schema ModelClass.ID.ColumnName
                ModelClass: SQLAlchemy model class name defined in models.py
                ID: Primary Key ID, multiple keys comma separated
                ColumnName: Column name
            value: Form input value
        new_primary_keys (dict): Dictionary of new primary keys for post
            key: Model class name
            value: Primary key

    Return:
        Boolean indicating success
    """

    # Loop through sorted dictionary
    for key, value in sorted(data.items()):
        try:
            # Set key parameters per Form input name schema
            param = str(key).split(".", 2)
            # SQLAlchemy model table name
            key_model = param[0]
            # Primary Key - return from new_primary_keys if not provided
            if not param[1] or param[1].isspace():
                key_primary_key = new_primary_keys[key_model]
            else:
                key_primary_key = param[1]
            # Convert Primary Keys to tuple
            key_primary_key = tuple(int(i) for i in str(key_primary_key).split(" "))
            # Column name
            key_column = param[2]

            # Set SQLAlchemy model class
            model = getattr(models, key_model)
            # Set row to update
            row = session.query(model).get(key_primary_key)

            # For empty value, set to null if column type is integer
            if value == "" and str(model.__table__.columns[key_column].type) == "INTEGER":
                value = None

            # Perform record update with dict value
            setattr(row, key_column, value)
            session.commit()

        except Exception as e:
            print("ERROR = {}".format(e))
            print("Submitted Key = {}".format(key))
            print("Model = {}".format(param[0]))
            print("Primary_Key = {}".format(param[1]))
            print("Column = {}".format(param[2]))
            print("Value = {}".format(value))
            return False

    return True
