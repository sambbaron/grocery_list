""" Add Test Data """

from werkzeug.security import generate_password_hash

from shopping_list.models import *
from shopping_list.database import session


def add_all():
    """ Add all test data """
    add_user()
    add_store()
    add_user_store()
    add_route()
    add_item_group()
    add_route_group()
    add_list()
    add_item_measurement()
    add_list_item()


def add_user():
    """ Add Test User """
    user1 = User(name="Testy",
                 email="testy@test.com",
                 password=generate_password_hash("test"))
    user2 = User(name="Testy2",
                 email="testy2@test.com",
                 password=generate_password_hash("test"))
    session.add_all([user1, user2])
    session.commit()


def add_store():
    """ Add Test Store

    Associated with test User from setUp
    """
    store1 = Store(name="Test Store")
    store2 = Store(name="Other Store")

    session.add_all([store1, store2])
    session.commit()


def add_user_store():
    """ Add Test UserStore association

    Associated with test User and Store
    """
    # Check for test User and Store
    if session.query(User).get(1) is None:
        add_user()
    if session.query(Store).get(1) is None:
        add_store()

    user_store1 = UserStore(user_id=1,
                            store_id=1,
                            nickname="My Test Store",
                            default=True)
    user_store2 = UserStore(user_id=1,
                            store_id=2,
                            nickname="My Other Store",
                            default=False)

    session.add_all([user_store1, user_store2])
    session.commit()


def add_route():
    """ Add Test Route

    Associated with test User and Store
    """
    # Check for test User and Store
    if session.query(User).get(1) is None:
        add_user()
    if session.query(Store).get(1) is None:
        add_store()

    # Set related store
    store1 = session.query(Store).filter(Store.id == 1).all()

    route1 = Route(name="Default",
                   default=True)
    session.add(route1)
    route2 = Route(name="Full Shop",
                   default=False,
                   user_id=1,
                   store=store1)
    session.add(route2)
    route3 = Route(name="Quick Shop",
                   default=False,
                   user_id=1,
                   store=store1)
    session.add(route3)

    session.commit()


def add_item_group():
    """ Add Test Item Groups """

    item_groups = ["vegetables", "fruits", "herbs", "dairy/eggs", "meat", "sundry", "international",
                   "frozen", "bulk", "baking", "spices", "prepared foods", "gourmet", "alcohol",
                   "paper/kitchen", "cleaning", "toiletries"]

    for item_group in item_groups:
        session.add(ItemGroup(name=item_group))

    session.commit()


def add_route_group():
    """ Add Test Route Group

    With Item Groups
    """
    # Check for test Route
    if session.query(Route).get(1) is None:
        add_route()
    if session.query(ItemGroup).get(1) is None:
        add_item_group()

    # Add first six Item Groups ascending to first test Route
    for n in range(1, 7):
        session.add(RouteGroup(route_id=2, item_group_id=n, route_order=n))

    # Add first six Item Groups descending to second test Route
    r = 1
    for n in range(6, 0, -1):
        session.add(RouteGroup(route_id=3, item_group_id=n, route_order=r))
        r += 1

    session.commit()


def add_list():
    """ Add Test List

    Associated with test User and Route
    """
    # Check for test User and Store
    if session.query(User).get(1) is None:
        add_user()
    if session.query(Store).get(1) is None:
        add_store()
    if session.query(Route).get(1) is None:
        add_route()

    list1 = List(shop_date=datetime.date.today(),
                 user_id=1,
                 store_id=1,
                 route_id=2)
    list2 = List(shop_date=datetime.date.today() + datetime.timedelta(days=7),
                 user_id=1,
                 store_id=1,
                 route_id=3)

    session.add_all([list1, list2])
    session.commit()


def add_item_measurement():
    """ Add Test Item Measurements """

    measurement_name_list = ["pounds", "ounces", "each", "pack", "cans", "dozen"]
    measurement_abbrev_list = ["lbs", "oz", "ea", "pack", "can", "doz"]
    for measurement in measurement_name_list:
        i = measurement_name_list.index(measurement)
        item_measurement = ItemMeasurements(name=measurement,
                                            abbreviation=measurement_abbrev_list[i])
        session.add(item_measurement)

    session.commit()


def add_list_item():
    """ Add Test List Items

    Associated with test List
    """
    if session.query(List).get(1) is None:
        add_list()
    if session.query(ItemMeasurements).get(1) is None:
        add_item_measurement()
    if session.query(ItemGroup).get(1) is None:
        add_item_group()

    item1 = ListItem(item_name="Steak",
                     item_notes="Organic",
                     item_quantity=1,
                     list_id=2,
                     item_measurement_id=1,
                     item_group_id=5)
    item2 = ListItem(item_name="Eggs",
                     item_notes="Large",
                     item_quantity=1,
                     list_id=2,
                     item_measurement_id=6,
                     item_group_id=4)
    item3 = ListItem(item_name="Tomato Sauce",
                     item_notes="Muir Glen",
                     item_quantity=28,
                     list_id=2,
                     item_measurement_id=2,
                     item_group_id=6)
    item4 = ListItem(item_name="Onion",
                     item_notes="Yellow",
                     item_quantity=3,
                     list_id=2,
                     item_measurement_id=3,
                     item_group_id=1)

    session.add_all([item1, item2, item3, item4])
    session.commit()