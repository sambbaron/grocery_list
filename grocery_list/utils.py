""" Custom Utility Functions """

from .database import session
from . import models


def update_form_data(data, **new_primary_keys):
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

        # Set key parameters per Form input name schema
        param = str(key).split(".", 2)
        # SQLAlchemy model table name
        key_model = param[0]
        # Primary Key - return from new_primary_keys if not provided
        if not param[1] or param[1].isspace():
            key_primary_key = new_primary_keys[key_model]
        else:
            key_primary_key = tuple(int(i) for i in param[1].split(" "))
        # Column name
        key_column = param[2]

        try:
            # Set SQLAlchemy model class
            model = getattr(models, key_model)
            # Set row to update
            row = session.query(model).get(key_primary_key)
            # Perform record update with dict value
            setattr(row, key_column, value)
            session.commit()
        except Exception as e:
            print("ERROR = {}".format(e))
            print("Model = {}".format(param[0]))
            print("Key = {}".format(param[1]))
            print("Value = {}".format(param[2]))
            return False

    return True