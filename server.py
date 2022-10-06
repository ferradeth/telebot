from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
database = SQLAlchemy(app)


class Users(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    login = database.Column(database.String(64))

    def __repr__(self):
        return "<Users %r>" % self.id


class Categories(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(64))

    def __repr__(self):
        return "<Categories %r>" % self.id


class Subs(database.Model):
    user_id = database.Column(database.Integer, primary_key=True)
    category_id = database.Column(database.String(64))

    def __repr__(self):
        return "<Categories %r>" % self.id


# if len(database.session.execute(database.select(Categories)).scalars()) < len(config.categories):
#     for cat in config.categories:
#         database.session.add(Categories(name=cat))
#         database.session.commit()


@app.route("/start", methods=["POST", "GET"])
def reg_user():
    if request.method == 'POST':
        print(request.json['login'])
        # print(database.session.execute(database.select(Users).filter_by(login=request.json['login'])).one())
        if database.session.execute(database.select(Users).filter_by(login=request.json['login'])).first() is None:
            database.session.add(Users(login=request.json['login']))
            database.session.commit()
            print('пользователь зарегистрировался')
    return {'ok': True}


# @app.route("/sub/info", methods=["POST", "GET"])
# def add_sub():
#     if request.method == 'POST':
#         return database.session.execute(database.select(Categories)).scalars()


if __name__ == "__main__":
    app.run()
