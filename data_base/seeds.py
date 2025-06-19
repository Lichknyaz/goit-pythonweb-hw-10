from faker import Faker

from connect import Session
from models import User

session = Session()
# fake = Faker()
#
# if __name__ == "__main__":
#
#     users = []
#     for _ in range(50):
#         user = User(
#             name=fake.name(),
#             email=fake.email(),
#             phone=fake.phone_number(),
#             birthday=fake.date_of_birth(),
#         )
#         session.add(user)
#         users.append(user)
#
#     session.commit()
#     session.close()
