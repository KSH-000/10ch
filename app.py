from flask import Flask, render_template, request, url_for, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import string, random

app = Flask(__name__)

db_uri = 'sqlite:///messages.db'
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)


def generate_id(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


class Article(db.Model):
    __tablename__ = 'articles'
    number = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    name = db.Column(db.Text())
    message = db.Column(db.Text())
    id = db.Column(db.String(8), nullable=False, 
                   default=lambda: generate_id(8))
    thread_id = db.Column(db.Integer, db.ForeignKey('threads.id'), 
                          nullable=False)


class Thread(db.Model):
    __tablename__ = "threads"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(), nullable=False)
    board_id = db.Column(db.Text(), nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.now)


# 板のカテゴライズ
categories = [
    {
        "name": "ニュース・時事",
        "boards": [
            {"id": "news", "name": "ニュース速報"},
            {"id": "politics", "name": "政治"},
            {"id": "economy", "name": "経済"},
        ]
    },
    {
        "name": "生活",
        "boards": [
            {"id": "chat", "name": "雑談"},
            {"id": "gourmet", "name": "料理・グルメ"},
            {"id": "health", "name": "健康・医療"},
        ]
    },
    {
        "name": "趣味・娯楽",
        "boards": [
            {"id": "anime", "name": "アニメ"},
            {"id": "games", "name": "ゲーム"},
            {"id": "movies", "name": "映画"},
        ]
    },
    {
        "name": "学問・技術",
        "boards": [
            {"id": "programming", "name": "プログラミング"},
            {"id": "science", "name": "科学"},
            {"id": "math", "name": "数学"},
        ]
    },
    {
        "name": "芸能・音楽",
        "boards": [
            {"id": "idols", "name": "アイドル"},
            {"id": "music", "name": "音楽"},
            {"id": "drama", "name": "ドラマ"},
        ]
    },
    {
        "name": "スポーツ",
        "boards": [
            {"id": "baseball", "name": "野球"},
            {"id": "soccer", "name": "サッカー"},
            {"id": "sports_gen", "name": "スポーツ全般"},
        ]
    },
    {
        "name": "旅行・地域",
        "boards": [
            {"id": "travel", "name": "旅行"},
            {"id": "local", "name": "地域情報"},
            {"id": "overseas", "name": "海外"},
        ]
    },
    {
        "name": "相談・その他",
        "boards": [
            {"id": "advice", "name": "人生相談"},
            {"id": "school", "name": "学校生活"},
            {"id": "tech_support", "name": "技術的な質問"},
        ]
    }
]


# ホームページ
@app.route("/", methods=['GET'])
def home():
    return render_template("home.html")


# スレッド個別ページ
@app.route('/thread/<int:thread_id>', methods=['GET', 'POST'])
def show_thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)

    if request.method == 'POST':
        name = request.form['name'] or "名無しさん"
        message = request.form['message']
        new_article = Article(name=name, message=message, thread_id=thread.id)
        db.session.add(new_article)
        db.session.commit()
        return redirect(url_for('show_thread', thread_id=thread.id))

    articles = Article.query.filter_by(thread_id=thread.id).all()
    return render_template('thread.html', thread=thread, articles=articles)


# 投稿削除フォーム
@app.route('/delete/<string:article_id>', methods=['POST'])
def delete_article(article_id):
    article = Article.query.filter_by(id=article_id).first()
    if article:
        db.session.delete(article)
        db.session.commit()
    return redirect(url_for('index'))


# 板一覧を表示
@app.route("/subback")
def subback():
    return render_template("/subback/subback.html", categories=categories)


# 板一覧からスレッド一覧へ移動
@app.route("/subback/<board_id>")
def show_subback(board_id):
    board_name = None
    for category in categories:
        for board in category["boards"]:
            if board["id"] == board_id:
                board_name = board["name"]
                break
    if not board_name:
        return "板が見つかりません", 404
            
    threads = Thread.query.filter_by(board_id=board_id).all()

    return render_template("/subback/thread_list.html", 
                           board_id=board_id, 
                           board={"id": board_id, "name": board_name}, 
                           threads=threads)


# 新規スレッド作成
@app.route("/subback/<board_id>/new_thread", methods=["GET", "POST"])
def make_thread(board_id):
    if request.method == 'POST':
        title = request.form['title']
        name = request.form['name']
        message = request.form['message']

        new_thread = Thread(title=title, board_id=board_id)
        db.session.add(new_thread)
        db.session.commit()

        new_article = Article(name=name, message=message, 
                              thread_id=new_thread.id)
        db.session.add(new_article)
        db.session.commit()
        return redirect(url_for('show_thread', thread_id=new_thread.id))


@app.route("/search")
def search():
    if request.method == "POST":
        pass
    return "仮"


@app.route("/topics/new")
def topics_new():
    return render_template("topics_new.html")


@app.route("/histories")
def histories():
    return render_template("histories.html")


@app.route("/topics/hot")
def topics_hot():
    return render_template("topics_hot.html")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)