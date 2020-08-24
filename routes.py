from flask_login import login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, flash, url_for, make_response, session
import datetime

from sqlalchemy import and_
from werkzeug import Response
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import redirect, secure_filename

from app import db, app, User, Post, msg, save_img

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
@app.route('/help')
def helper():
    return render_template('pod.html')
@app.route('/')
def hello_world():
    q=request.args.get('q')
    if q:
        posts=Post.query.filter(Post.name.contains(q),)
    else:
        posts=Post.query.order_by(Post.timestamp.desc())
    return render_template('index.html',posts=posts)


@app.route('/user<int:id>/lic',methods=['GET','POST'])
@login_required
def lk(id):
    user=User.query.get(id)
    if current_user.is_authenticated==False:
        return redirect(url_for('hello_world'))
    else:
        return render_template('lk.html',user=user)


@app.route('/post<int:id>/delete',methods=['GET','POST'])
def delete_post(id):
    ed_post=Post.query.get(id)
    try:
        ed_post.active = False
        db.session.commit()
        return redirect('/lic/actualpost')
    except:
        return print(f"у вас серьезные траблы {current_user.name}")

@app.route('/post<int:id>/restore',methods=['GET','POST'])
def restore_post(id):
    ed_post=Post.query.get(id)
    try:
        ed_post.active = True
        db.session.commit()
        return redirect('/lic/notactualpost')
    except:
        return print(f"у вас серьезные траблы {current_user.name}")


@app.route('/post<int:id>/edit',methods=['GET','POST'])
def edit_post(id):
    post = Post.query.get(id)
    if request.method == 'POST':
        post.name = request.form.get('name')
        post.category = request.form.get('category')
        post.description = request.form.get('description')
        post.hostel = request.form.get('hostel')
        post.cost = request.form.get('cost')
        post.urlon = request.form.get('urlon')
        post.user_id = current_user.id
        post.img_0 = save_img(request.files['photo0'])
        post.img_1 = save_img(request.files['photo1'])
        post.img_2 = save_img(request.files['photo2'])
        post.img_3 = save_img(request.files['photo3'])
        try:
            db.session.commit()
            return redirect('/lic/actualpost')
        except:
            return print(f"у вас серьезные траблы {current_user.name}")
    else:
        return render_template('editpost.html',post=post)




@app.route('/post<int:id>')
def show_post(id):
    post =Post.query.get(id)
    p=post.user_id
    user=User.query.get(p)
    datnow = datetime.datetime.now()
    datpost = post.timestamp
    delta = datnow - datpost
    if delta.days > 30 & post.active==True:
        try:
            post.active = False
            db.session.commit()
            return "Объявление слишком долго находилоась активным, войдите в личный кабинет для повторной активации объявления"
        except:
            return print(f"у вас серьезные траблы {current_user.name}")
    #if delta.days >60 & post.active==False:
     #   try:
      #      db.session.delete(post)
       #     db.session.commit()
        #    return "Объявление слишком долго находилоась неактивным и к сожалению оно было удалено"
        #except:
         #   return print(f"у вас серьезные траблы {current_user.name}")
    #'post.html', post = post, user = user
    return render_template('post.html',post=post,user=user)
  #  return render_template('тест.html',user=user)
#@app.route('/photo<int:id>')
#def show_photo(id):
#    post = Post.query.get(id)
#    if not post:
#        return "not img with that id"
#    return Response(post.img)

@app.route('/user<int:id>/lic/editdata', methods=['GET','POST'])
@login_required
def editdata(id):
    user=User.query.get(id)
    now_User=current_user
    if request.method =="POST":
        now_User.mail = request.form['mail']
        now_User.name = request.form['name']
        now_User.id_vk = request.form['id_vk']
        now_User.hostel = request.form['hostel']
        password1=request.form['password1']
        password2=request.form['password2']
        try:
            if password2 != password1:
                flash('ВАШИ ПАРОЛИ НЕ ИДЕНТИЧНЫ')
            else:
                hash_pwd = generate_password_hash(password1)
                now_User.password=hash_pwd
                db.session.commit()
                return redirect('/lic')

        except:

            return print(f"у вас серьезные траблы {current_user.name}")
    return render_template('editdata.html')

@app.route('/user<int:id>/lic/actualpost')
@login_required
def actualpost(id):
    user=User.query.get(id)
    posts = Post.query.filter_by(user_id=current_user.id, active = 1).all()
    return render_template('actualpost.html',posts=posts)

@app.route('/user<int:id>/lic/notactualpost')
@login_required
def notactualpost(id):
    user=User.query.get(id)
    posts = Post.query.filter_by(user_id=current_user.id, active=0).all()
    return render_template('notactualpost.html', posts=posts)


@app.route('/lic/toppost')
@login_required

def toppost():
    return render_template('toppost.html')


@app.route('/main')

def main():
    return render_template('main.html')


@app.route('/login', methods=['GET','POST'])
def loginging():
    if request.method =='POST':
        mail = request.form.get('mail')
        password = request.form.get('password')

        if mail and password:
            user = User.query.filter_by(mail=mail).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(url_for('hello_world'))
            else:
                flash('НЕ СОВПАДАЮТ ПАРОЛИ')

        else:
            flash('ВВЕДИТЕ ПАРОЛЬ И ЛОГИН')

    return render_template('login_page.html')

@app.route('/registration', methods=['GET','POST'])
def regist():
    mail = request.form.get('mail')
    name = request.form.get('name')
    id_vk = request.form.get('id_vk')
    hostel = request.form.get('hostel')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    if request.method=='POST':
        if not (mail or name or id_vk or hostel or password or password2):
            flash('ВВЕДИТЕ ВСЕ ДАННЫЕ')
        elif password2!=password:
            flash('ВАШИ ПАРОЛИ НЕ ИДЕНТИЧНЫ')
        else:
            hash_pwd=generate_password_hash(password)

            new_User=User(mail=mail, name=name, id_vk=id_vk, hostel=hostel, password=hash_pwd)

            db.session.add(new_User)
            db.session.commit()
            return redirect(url_for('loginging'))

    return render_template('registration_page.html')





@app.route('/newpost', methods=['GET','POST'])
@login_required
#def allowed_file(filename):
#    return '.' in filename and \
#           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def reg_post():
    if request.method == 'POST' :
        name = request.form.get('name')
        category = request.form.get('category')
        description = request.form.get('description')
        hostel = request.form.get('hostel')
        cost = request.form.get('cost')
        urlon = request.form.get('urlon')
        user_id=current_user.id
        photo0 = save_img(request.files['photo0'])
        photo1 = save_img(request.files['photo1'])
        photo2 = save_img(request.files['photo2'])
        photo3 = save_img(request.files['photo3'])
        active=True

        if  name==None or category==None or description==None or hostel==None or cost==None or urlon==None or photo0==None:
             flash("Необходимо заполнить поля:Название объявления,Категория,Описание,Цена,Общежитие и выбрать хотя бы 1 фото")
        else:
            new_post = Post(category=category, name=name, description=description, hostel=hostel,
                                cost=cost, urlon=urlon, timestamp=datetime.datetime.now(), user_id=user_id,
                                active=active,img_0=photo0,img_1=photo1,img_2=photo2,img_3=photo3)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('hello_world'))
    return render_template('registration_post_page.html')

@app.route('/upload')
def up():
    return 'Success'


@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return  redirect(url_for('hello_world'))


@app.after_request
def redirect_to_sign(responce):
    if responce.status_code==401:
        return redirect(url_for('loginging')+'?next='+request.url)
    return responce



@app.route('/chatik',methods=['GET','POST'])
@login_required
def chat():
    if request.method == 'POST':

        #post=Post.query.filter(Post.id==id).first()
        message = request.form.get('msg')
        current_id=current_user.id
        post_id=current_user.id
        if not message:
            return flash('Введите сообщение')
        else:
            message= msg(current_id=current_id,post_id=post_id,msg=message,msgDate=datetime.datetime.now())
            db.session.add(message)
            db.session.commit()
            return redirect(url_for('hello_world'))

    return render_template('chat.html')
@app.route('/messages')
def messages():
    m = msg.query.all()

    return render_template('message.html',msg=m)







