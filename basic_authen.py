from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
from wsgiref.simple_server import make_server
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
engine = create_engine("sqlite:///basic_authen.sqlite")
Session = sessionmaker(bind=engine)
metadata = MetaData()

user_table = Table("user", metadata,
  Column("id", Integer(), primary_key=True),
  Column("username", String(100), unique=True),
  Column("password", String(100)) 
)


Base = declarative_base()

class User(object):
  def __init__(self, username, password):
    self.username = username
    self.password = password
mapper(User, user_table)


metadata.create_all(engine)

#Put some data to db
try:
  session = Session()
  user = User(username="maidiep", password="maivandiep")
  session.add(user)
  session.commit()
except IntegrityError:
  session.rollback()
#===============================================
#MY APP
#===============================================
def application(environ, start_response):
  response_headers = [("content-type", "text/plain")]
  status = "200 OK"
  start_response(status, response_headers)
  try:
    username = environ["tacke"]
    return ["logined with name {}".format(username)]
  except KeyError:
    return ["Login Please"]

#=====================================================
#AUTHENTICATION MIDDLEWARE
#=====================================================
from base64 import b64decode
class Middleware():
  def __init__(self, app):
    self.wrapped_app = app

  def __call__(self, environ, start_response):
    try:
      auth = b64decode(environ["HTTP_AUTHORIZATION"].split()[1]).split(":")
      username = auth[0]
      password = auth[1]
      try:
        user = session.query(User).filter_by(username=username, password=password).one()
        environ["tacke"] = username
      except NoResultFound:
        pass
    except KeyError:
      pass
    return self.wrapped_app(environ, start_response)





#======================================================
#SERVER
#======================================================

httpd = make_server("", 8080, Middleware(application))
print("Starting server on port 8080")
httpd.serve_forever()
