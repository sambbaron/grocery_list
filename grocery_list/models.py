""" Database Models using SQLAlchemy """

import datetime

from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from flask.ext.login import UserMixin

from .database import Base, engine


class User(Base, UserMixin):
    """ Application Users

    Attributes:
        name (str): User name
        email (str): User email address
        password (str): User password (hashed)
    """

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), default="Guest")
    email = Column(String(50), unique=True)
    password = Column(String(128))

    store = relationship("UserStore", backref="user")
    route = relationship("Route", backref="user")
    list = relationship("List", backref="user")


class Store(Base):
    """ Global list of stores

    Populated as users select/input stores

    Attributes:
        name (str, required): Store name
        street_address (str): Store address
        city (str): City
        state (str): 2-character state code
        postal_code (str): 10-character postal code
        country (str): Country code (undefined)
        default (bool): Default store in selection

    Example:
        Whole Foods 123 Main St New York, NY 12345
    """
    __tablename__ = "store"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    street_address = Column(String(100))
    city = Column(String(50))
    state = Column(String(2))
    postal_code = Column(String(10))
    country = Column(String(50))

    user = relationship("UserStore", backref="store")


class UserStore(Base):
    """ Association of Users and Stores

    Allow users to assign "My Stores"

    Attributes:
        user_id (fk, primary key): User
        store_id (fk, primary key): Store
        nickname (str): User defined store name different from place name
    """
    __tablename__ = "user_store"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    store_id = Column(Integer, ForeignKey("store.id"), primary_key=True)
    nickname = Column(String(50))
    default = Column(Boolean, default=False)


class Route(Base):
    """ Route - sorted collection of item groups by store

    Support multiple routes through store
    depending on use case

    Attributes:
        name (str, required): Route name
        default (bool): Default route for creating lists
        user_id (fk): User
        store_id (fk): Store

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

    store = relationship("Store",
                         secondary="route_store",
                         backref="route")
    list = relationship("List", backref="route")


# Routes assigned to Stores
# Allow users to use routes without stores
# Create default route
route_store_table = Table("route_store", Base.metadata,
                         Column("route_id", Integer, ForeignKey("route.id"), nullable=False, index=True),
                         Column("store_id", Integer, ForeignKey("store.id"), nullable=False, index=True)
)



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

    store = relationship("Store",
                          secondary="store_item_group",
                          backref="item_group"
    )
    route = relationship("RouteGroup", backref="item_group")
    list_item = relationship("ListItem", backref="item_group")


# Item Groups assigned to Stores
store_itemGroup_table = Table("store_item_group", Base.metadata,
                         Column("item_group_id", Integer, ForeignKey("item_group.id"), nullable=False, index=True),
                         Column("store_id", Integer, ForeignKey("store.id"), nullable=False, index=True)
)


class RouteGroup(Base):
    """ Item Groups assigned to Routes

    Sort order for use in Lists

    Attributes:
        route_id (fk, required): Route
        item_group_Id (fk, required): Item Group
        route_order (int, default=0): Sort order for Item Groups in Route

    Examples:
        Route: Full Shop
        Item Groups:
            Vegetables - 1
            Fruits - 2
            International - 3
            Meat - 4
    """
    __tablename__ = "route_item_group"

    id = Column(Integer, primary_key=True)
    route_id = Column(Integer, ForeignKey("route.id"), index=True)
    item_group_id = Column(Integer, ForeignKey("item_group.id"), index=True)
    route_order = Column(Integer, default=0)


class List(Base):
    """ Shopping List header

    Attributes:
        shop_date (date, required): Shopping date
        name (str): List name
        user_id (fk): User
        route_id (fk): Route (with related Store)

    Example:
        2/17/05, Full Shop, Whole Foods Downtown
    """
    __tablename__ = "list"

    id = Column(Integer, primary_key=True)
    shop_date = Column(DateTime, nullable=False)
    name = Column(String(50))

    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    route_id = Column(Integer, ForeignKey("route.id"), index=True)

    list_item = relationship("ListItem", backref="list")


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

    list_item = relationship("ListItem", backref="item_measurement")


class ListItem(Base):
    """ Items in List

    Assigned an Item Group
    Uses Item Group and Route to set sort order

    Attributes:
        item_name (str, required): Item name
        item_notes (str): Additional information on item, such as
            type, brand, or variety
        item_quantity (decimal): How much of item to be purchased
        list_id (fk, required): List header
        item_measurement_id (fk): Measurement corresponding to quantity
        route_item_group_id (fk, required): Item Group assigned to Route used for sorting

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

    list_id = Column(Integer, ForeignKey("list.id"), nullable=False, index=True)
    item_measurement_id = Column(Integer, ForeignKey("item_measurement.id"))
    item_group_id = Column(Integer, ForeignKey("item_group.id"), nullable=False, index=True)
