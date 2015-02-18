""" Database Models using SQLAlchemy """

import datetime

from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from flask.ext.login import UserMixin

from .database import Base, engine


class User(Base, UserMixin):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(50), unique=True)
    password = Column(String(50))

    store = relationship("UserStore", backref="user")
    route = relationship("Route", backref="user")
    list = relationship("List", backref="user")

class Store(Base):
    """ Global list of stores

    Populated as users select/input stores

    Attributes:
        name (str, required): Store name
        address (str): Store address

    Example:
        Whole Foods 123 Main St New York, NY 12345
    """
    __tablename__ = "store"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    street_address = Column(String(100))
    city = Column(String(50))
    postal_code = Column(String(10))
    country = Column(String(50))

    user = relationship("UserStore", backref="store")
    route = relationship("StoreRoute", backref="store")


class UserStore(Base):
    """ Association of Users and Stores

    Allow users to assign "My Stores"
    """
    __tablename__ = "user_store"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    store_id = Column(Integer, ForeignKey("store.id"), primary_key=True)
    nickname = Column(String(50))


class Route(Base):
    """ Route - sorted collection of item groups by store

    Support multiple routes through store
    depending on use case

    Attributes:
        name (str, required): Route name
        default (bool): Default route for creating lists
        user (fk): User
        store (fk): Store

    Examples:
        Full Shop - route used to shop in entire store
        Quick Shop - route that might only hit the certain
            sections, like prepared foods, etc.
    """
    __tablename__ = "route"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    default = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    store_id = Column(Integer, ForeignKey("store.id"), index=True)
    list = relationship("List", backref="route")


class ItemGroup(Base):
    """ Defined groups of items (section/department)

    Predefined groups for use in Store Routes

    Attributes:
        name (str, required): Group name
        description (str): Group description, item types

    Examples:
        Vegetables
        Fruits
        Meat
        International
    """
    __tablename__ = "item_group"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(100))

    stores = relationship("ItemGroup",
                          secondary="item_group_store",
                          backref="item_group"
    )

    routes = relationship("ItemGroup",
                          secondary="item_group_route",
                          backref="item_group"
    )

    list_items = relationship("ListItem", backref="item_group")

# Item Groups assigned to Stores
itemGroup_store_table = Table("item_group_store", Base.metadata,
                         Column("item_group_id", Integer, ForeignKey("item_group.id"), nullable=False, index=True),
                         Column("store_id", Integer, ForeignKey("store.id"), nullable=False, index=True)
)

# Item Groups assigned to Routes
itemGroup_route_table = Table("item_group_route", Base.metadata,
                         Column("item_group_id", Integer, ForeignKey("item_group.id"), nullable=False, index=True),
                         Column("route_id", Integer, ForeignKey("route.id"), nullable=False, index=True)
)


class List(Base):
    """ Shopping List header

    Attributes:
        shop_date (date, required): Shopping date
        name (str): List name
        user (fk): User
        route (fk): Route (with related Store)

    Example:
        2/17/05, Full Shop, Whole Foods Downtown
    """
    __tablename__ = "list"

    id = Column(Integer, primary_key=True)
    shop_date = Column(DateTime, nullable=False)
    name = Column(String(50))

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    route_id = Column(Integer, ForeignKey("route.id"), index=True)


class ItemMeasurements(Base):
    """ Predefined measurements

    Attributes:
        name(str, required): Measurement name
        abbreviation(str, required): Measurement abbreviation

    Examples:
        pounds - lbs
        each - ea
        pack - pk
        can - cn
    """
    __tablename__ = "item_measurement"

    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False)
    abbreviation = Column(String(10), nullable=False)

    list_items = relationship("ListItem", backref="item_measurement")


class ListItem(Base):
    """ Items in List

    Assigned an Item Group
    Uses Item Group and Route to set sort order

    Attributes:
        item_name (str, required): Item name
        item_notes (str): Additional information on item, such as
            type, brand, or variety
        item_quantity (decimal): How much of item to be purchased
        item_measurement (fk): Measurement corresponding to quantity
        item_group (fk, required): Item group for routing

    Examples:
        Onion, Yellow, 5, each, Vegetables
        Flank Steak, Organic, 2, lbs, Meat
        Ketchup, Heinz, 16, oz, Sundry
    """
    __tablename__ = "list_item"

    id = Column(Integer, primary_key=True)
    item_name = Column(String(50), nullable=False)
    item_notes = Column(String(100))
    item_quantity = Column(Numeric)

    item_measurement_id = Column(Integer, ForeignKey("item_measurement.id"))
    item_group_id = Column(Integer, ForeignKey("item_group.id"), nullable=False, index=True)



if __name__ == "__main__":
    Base.metadata.create_all(engine)