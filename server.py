from dataclasses import dataclass
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
database = SQLAlchemy(app)


@dataclass
class Users(database.Model):
    id: int
    login: str

    id = database.Column(database.Integer, primary_key=True)
    login = database.Column(database.String(64))


@dataclass
class Categories(database.Model):
    id: int
    name: str

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(64))


@dataclass
class Subs(database.Model):
    user_id: int
    category_id: int

    user_id = database.Column(database.Integer, primary_key=True)
    category_id = database.Column(database.Integer, primary_key=True)


if len(database.session.execute(database.select(Categories)).all()) < len(config.categories):
    for cat in config.categories:
        database.session.add(Categories(name=cat))
        database.session.commit()


@app.route("/start", methods=["POST", "GET"])
def reg_user():
    if request.method == 'POST':
        print(request.json['login'])
        # print(database.session.execute(database.select(Users).filter_by(login=request.json['login'])).one())
        if Users.query.filter_by(login=request.json['login']).first() is None:
            database.session.add(Users(login=request.json['login']))
            database.session.commit()
            print('пользователь зарегистрировался')
    return {'ok': True}


@app.route("/sub/info", methods=["POST", "GET"])
def add_sub():
    if request.method == 'POST':
        categories = Categories.query.all()
        return jsonify(categories)


@app.route("/sub/sub", methods=["POST", "GET"])
def sub_sub():
    if request.method == 'POST':
        res_cat = database.session.execute(database.select(Categories.id).filter_by(name=request.json['category'])).first()
        print(res_cat)
        if res_cat is not None:
            signup = database.session.execute(database.select(Users.id).filter_by(login=request.json['login'])).first()
            print(signup)
            check_ex = Subs.query.filter_by(user_id=signup[0], category_id=res_cat[0]).first()
            if check_ex is None:
                database.session.add(Subs(user_id=signup[0], category_id=res_cat[0]))
                result = {'answer': 'Вы успешно подписались на категорию'}
                database.session.commit()
            else:
                result = {'answer': 'Вы уже подписаны на эту категорию'}
        else:
            result = {'answer': 'Проверьте ввод, возможно такой категории не существует'}
        return result


@app.route("/unsub/cats", methods=["POST", "GET"])
def info_subs():
    if request.method == "POST":
        signup = database.session.execute(database.select(Users.id).filter_by(login=request.json['login'])).first()
        user_cats = database.session.execute(database.select(Subs.category_id).filter_by(user_id=signup[0])).all()
        print(user_cats)
        subs = []
        for s_id in user_cats:
            category = Categories.query.filter_by(id=s_id[0]).first()
            subs.append(category)
        print(jsonify(subs))
        return jsonify(subs)


@app.route("/unsub/del", methods=["POST", "GET"])
def del_sub():
    result = {}
    if request.method == "POST":
        signup = database.session.execute(database.select(Users.id).filter_by(login=request.json['login'])).first()
        print(f"айди пользователя: {signup[0]}")
        cat_sub = database.session.execute(database.select(Categories.id).filter_by(name=request.json['name'])).first()
        print(f"айди категории: {cat_sub[0]}")
        if cat_sub is not None:
            Subs.query.filter_by(user_id=signup[0], category_id=cat_sub[0]).delete(synchronize_session=False)
            database.session.commit()
            result = {'answer': 'Вы успешно отписались от категории'}
        else:
            result = {'answer': 'Вы не подписаны на эту категорию'}
    return result


@app.route("/news", methods=["POST", "GET"])
def send_news():
    user_id = database.session.execute(database.select(Users.id).filter_by(login=request.json["login"])).first()
    categories = database.session.execute(database.select(Subs.category_id).filter_by(user_id=user_id[0])).all()
    user_subs = []

    for category in categories:
        sub_categories = Categories.query.filter_by(id=category[0]).first()
        user_subs.append(sub_categories)

    return jsonify(user_subs)

if __name__ == "__main__":
    app.run()
