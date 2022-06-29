from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date 
from io import StringIO
import csv,os
import pandas as pd

from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy.model import Model

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aroma.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
data=[]

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User1.query.get(int(user_id))


class OilData(db.Model):
    __tablename__ = 'oil'
    oil_id = db.Column(db.Integer, primary_key=True)
    oil_name = db.Column(db.String(30), nullable=False)#名前
    oil_category = db.Column(db.String(100), nullable=False)#分類
    oil_note= db.Column(db.Integer)#topnote
    oil_smell=db.Column(db.String(100))#香りの種類
    oil_due = db.Column(db.Integer, nullable=False)#開封日からの使用期限

class UserData(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    oil_id = db.Column(db.Integer)
    user_volume_ml = db.Column(db.Integer, nullable=False)#所持量
    user_open = db.Column(db.DateTime, nullable=False)#開封日
    user_due = db.Column(db.DateTime, nullable=False)#使用期限

class RecipeData(db.Model):
    __tablename__ = 'recipe'
    recipe_id = db.Column(db.Integer, primary_key=True)
    recipe_oil_id0 = db.Column(db.Integer)
    recipe_oil_id1 = db.Column(db.Integer)
    recipe_oil_id2 = db.Column(db.Integer)
    recipe_oil_id3 = db.Column(db.Integer)
    recipe_oil_id0_volume = db.Column(db.Integer)
    recipe_oil_id1_volume  = db.Column(db.Integer)
    recipe_oil_id2_volume  = db.Column(db.Integer)
    recipe_oil_id3_volume  = db.Column(db.Integer)
    recipe_efficacy = db.Column(db.String(100))

class User1(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), nullable=False, unique=True)
	password = db.Column(db.String(25))

###############メイン画面###############################
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        #posts = UserData.query.order_by(UserData.user_due).all()
        posts = UserData.query.all()

        #posts = UserData.query.join(OilData, UserData.oil_id == OilData.oil_id).all()
        #print(posts.user_name)

        #for post in posts:
            #print(vars(post))
        #    print(post.id.name)

        return render_template('index.html', posts=posts, today=date.today(),min=int(50))

    else:
        user_id = request.form.get('user_id')
        oil_id = request.form.get('oil_id')
        user_volume_ml= request.form.get('user_volume_ml')
        user_open = request.form.get('user_open')
        user_due = request.form.get('user_due')
        print(user_id,oil_id,user_volume_ml,user_open,user_due)
        user_open = datetime.strptime(user_due, '%Y-%m-%d')
        user_due = datetime.strptime(user_due, '%Y-%m-%d')
        new_post = UserData(user_id=user_id,oil_id=oil_id,user_volume_ml=user_volume_ml,user_open=user_open, user_due=user_due)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        # Userのインスタンスを作成
        user1 = User1(username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(user1)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        # Userテーブルからusernameに一致するユーザを取得
        user = User1.query.filter_by(username=username).first()
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect('/')
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/create')
def create():
    oildatas = db.session.query(OilData).all()
    print(oildatas)
    return render_template('create.html',oildatas=oildatas)

##############TODOアプリ###############################
@app.route('/detail/<int:id>')
def read(id):
    post = UserData.query.get(id)
    print(post)
    return render_template('detail.html', post=post)

@app.route('/detail_test/<int:id>')
def read_test(id):
    ergames = ergamethema.query.get(id)
    print(ergames)
    return render_template('detail_test.html', ergames=ergames)

@app.route('/delete/<int:id>')
def delete(id):
    post = UserData.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect('/')

@app.route('/add')
def add():
    example = Post()
    #example.id = 1
    example.title = 'auto title'
    example.detail = 'auto detail'
    example.due = datetime.strptime('2021-09-20', '%Y-%m-%d')
    print(example)

    db.session.add(example)
    db.session.commit()
    return redirect('/')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.title = request.form.get('title')
        post.detail = request.form.get('detail')
        post.due = datetime.strptime(request.form.get('due'), '%Y-%m-%d')
        print(post.due)

        db.session.commit()
        return redirect('/')

# フォーム表示
@app.route('/upload', methods=['GET'])
def home():
    return render_template("upload.html")

# オイルデータベース管理
@app.route('/oildatabase', methods=['GET', 'POST'])
def oildatabase():
    if request.method == 'GET':
        posts = OilData.query.all()
        print(posts)
        print("oildb")
        return render_template("oildatabase.html" ,posts=posts )


@app.route('/add_oildata_test')
def add_oildata_test():
    print("add_oil")
    example = OilData()
    #example.id = 1
    example.oil_name= 'auto title'
    example.oil_category = 'auto category'
    example.oil_note = 'auto note'
    example.oil_smell = 'auto smell'
    example.oil_due = datetime.strptime('2021-09-20', '%Y-%m-%d')
    print(example)

    db.session.add(example)
    db.session.commit()
    return redirect('/oildatabase')

@app.route('/add_oildata')
def add_oildata():
    print("add_oil")
    example = OilData()
    #example.id = 1
    example.oil_name= 'auto title'
    example.oil_category = 'auto category'
    example.oil_note = 'auto note'
    example.oil_smell = 'auto smell'
    example.oil_due = datetime.strptime('2021-09-20', '%Y-%m-%d')
    print(example)

    db.session.add(example)
    db.session.commit()
    return redirect('/oildatabase')

@app.route('/delete_oildata/<int:oil_id>')
def delete_oildata(oil_id):
    post = OilData.query.get(oil_id)
    print(post)

    db.session.delete(post)
    db.session.commit()
    return redirect('/oildatabase')


# アップロード機能
@app.route('/upload', methods=['POST'])
def upload():
    try:
        print(request.files)
        print("2------")

        #fileの取得（FileStorage型で取れる）
        # https://tedboy.github.io/flask/generated/generated/werkzeug.FileStorage.html
        fs = request.files['file']
        print("3------")

        # 下記のような情報がFileStorageからは取れる
        app.logger.info('file_name={}'.format(fs.filename))
        app.logger.info('content_type={} content_length={}, mimetype={}, mimetype_params={}'.format(
            fs.content_type, fs.content_length, fs.mimetype, fs.mimetype_params))
        print("4------")

        # ファイルを保存
        fs.save(fs.filename)
        print("5------")

        # アップしたファイルをインサートする
        data=reading_csv(fs.filename)
        insert_sql(data)
        print(data)

        return render_template("uploaded.html", data = data)
    except:
        print("except")
        return "ファイルがありません"

# CSVファイルを読み込む関数
def reading_csv(filename):
    data = []
    with open(filename, encoding='utf-8') as f:#windowsとmacで文字コードが異なる。OSに依存しない対応を要検討。
        print(f)
        reader = csv.reader(f)
        print(reader)

        header_ = next(csv.reader(f))
        for row in reader:
            tuples=(row[0], row[1], row[2])
            print(tuples)
            data.append(tuples,)
    print(data)
    return data

# CSVファイルを書き込む関数
def insert_sql(data):
    for temp in data:
        print(temp)
        example = Post()
        #example.id = 1
        example.title = temp[0]
        example.detail = temp[1]
        example.due = datetime.strptime(temp[2], '%Y-%m-%d')
        print(example)

        db.session.add(example)
        db.session.commit()
        #return redirect('/')

@app.route('/test')
def csv_display(): 
    date_fruit_list = pd.read_csv("./testdata.csv").values.tolist()
    #df= pd.DataFrame(date_fruit_list)
    df= pd.DataFrame(date_fruit_list)

    df.to_csv("./testdata2.csv")#ファイルがあったら、上書きしてる
    print(date_fruit_list)
    return render_template('date_fruits.html', title='食べた果物記録', date_fruit_list=date_fruit_list)


@app.route("/export")
def export_action():
    # 現在のディレクトリを取得
    paths = os.path.abspath(__file__)[:-7]
    print(paths)
    return send_from_directory(
        directory=paths + '/input',
        path='testdata.csv',
        as_attachment=True,
        attachment_filename='testdata.csv',
    )

#################ライン返信ゲーム##################################
@app.route('/vote/<int:id2>', methods=['GET', 'POST'])
def vote(id):
    post = ergamethema.query.get(id)
    if request.method == 'GET':
        return render_template('wait.html', post=post)
    else:
        post.title2 = request.form.get('title2')
        post.detail2 = request.form.get('detail2')
        post.due2 = datetime.strptime(request.form.get('due2'), '%Y-%m-%d')
        print(post.due2)

        db.session.commit()
        return redirect('/')

@app.route('/erhome', methods=['GET'])
def erhome():
    posts = er_room.query.all()
    print(posts)
    return render_template('erhome.html', posts=posts)

@app.route('/er_enter_room', methods=['GET'])
def er_enter_room():
    posts = er_room.query.all()
    print(posts)
    return render_template('erhome.html', posts=posts)

@app.route('/ercreate')
def ercreate():
    return render_template('ercreate.html')

@app.route('/er_thema_create')
def er_thema_create():
    return render_template('er_thema_create.html')

@app.route('/er_thema_create_process', methods=['GET', 'POST'])
def er_thema_create_prosecc():
    if request.method == 'GET':
        posts = ergamethema.query.all()
        print(posts)
        return render_template('erhome.html', posts=posts)

    else:
        id = request.form.get('id')
        thema= request.form.get('thema')
        print(id,thema)
        
        new_post = ergamethema(id=id, thema=thema)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/erhome')

@app.route('/er_create_room')
def er_create_room():
    return render_template('er_create_room.html')

@app.route('/er_room_enter/<int:id>')
def er_room_enter(id):
    post = er_room.query.get(id)
    print(post)
    return render_template('er_room_enter.html', post=post)

@app.route('/er_create_room_process', methods=['POST'])
def er_create_room_prosecc():
    
    id = request.form.get('id')
    room_name = request.form.get('room_name')
    room_pass = request.form.get('room_pass')
    thema_id = 0
    player_num = 0
    room_status = 0

    print(id,room_name,room_pass,thema_id,player_num,room_status)        
    new_post = er_room(id=id, room_name=room_name,room_pass=room_pass,thema_id=thema_id,player_num=player_num,room_status=room_status)
    db.session.add(new_post)
    db.session.commit()
    return redirect('/erhome')

@app.route('/er_delete/<int:id>')
def er_delete(id):
    post = ergamethema.query.get(id)

    db.session.delete(post)
    db.session.commit()
    return redirect('/erhome')

#@app.route('/er_create_room', methods=['GET', 'POST'])
#def er_create_room():
#    if request.method == 'GET':
#        ergames = ergamethema.query.all()
#        print(ergames)
#        return render_template('er_create_room.html', ergames=ergames)
#    else:
#        return redirect('/erhome')

@app.route('/er_room_enter/<int:id>', methods=['GET'])
def er_thema_get(id):
	return render_template('er_room_enter.html', \
		title = 'Form Sample(get)', \
		message = '何のお肉が好きですか？')

@app.route('/er_room_enter/<int:id>', methods=['POST'])
def er_thema_post(id):
    post = er_room.query.get(id)
    print(post)
    name = request.form.get('sel')

    return render_template('er_room_enter.html', \
		title = 'Form Sample(post)', \
		message = '{}の肉がお好きなんですね！'.format(name), post=post)

if __name__ == "__main__":
    app.run(debug=True)#debug環境
    #app.run() # 本番環境