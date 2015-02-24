""" Add Test Data """

from werkzeug.security import generate_password_hash

from grocery_list.models import *
from grocery_list.database import session


def add_all():
    """ Add all test data """
    add_user()
    add_store()
    add_user_store()
    add_route()
    add_item_group()
    add_route_group()
    add_list()

def add_user():
    """ Add Test User """
    user = User(name="Testy",
                email="testy@test.com",
                password=generate_password_hash("test")
    )
    session.add(user)
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
                           default=True
    )
    user_store2 = UserStore(user_id=1,
                           store_id=2,
                           nickname="My Other Store",
                           default=False
    )

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

    route1 = Route(name="Full Shop",
                  default=True,
                  user_id=1,
                  store=store1
    )
    route2 = Route(name="Quick Shop",
                  default=False,
                  user_id=1,
                  store=store1
    )

    session.add_all([route1, route2])
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

    # Add first five Item Groups to test Route
    for n in range(1, 6):
        session.add(RouteGroup(route_id=1, item_group_id=n, route_order=n))

    session.commit()

def add_list():
    """ Add Test List

    Associated with test User and Route
    """
    # Check for test User and Store
    if session.query(User).get(1) is None:
        add_user()
    if session.query(Route).get(1) is None:
        add_route()

    list1 = List(shop_date=datetime.date.today(),
                user_id=1,
                route_id=1
    )
    list2 = List(shop_date=datetime.date.today() + datetime.timedelta(days=7),
                user_id=1,
                route_id=1
    )

    session.add_all([list1, list2])
    session.commit()
