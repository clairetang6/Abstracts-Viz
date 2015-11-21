from sqlalchemy import create_engine
engine = create_engine('sqlite:///database/app.db')

from . import models
models.Base.metadata.create_all(engine)