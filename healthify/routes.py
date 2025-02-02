import os
import secrets
from PIL import Image
from flask import Flask, render_template, url_for, flash, redirect, jsonify, request, abort
import healthify.databasefile as db
from healthify.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from healthify import app, bcrypt
from flask_login import login_user, current_user, logout_user, login_required


hdata = []
#     [
#     {
#         'patientid':'A123',
#         'patientname':'John',
#         'payor':'BCBS',
#         'date_posted':'2023-10-21'
#     },
#     {
#         'patientid': 'A234',
#         'patientname': 'Scott',
#         'payor': 'BCBS',
#         'date_posted': '2023-10-21'
#     },
#     {
#         'patientid': 'A345',
#         'patientname': 'Kim',
#         'payor': 'BCBS',
#         'date_posted': '2023-10-21'
#     }
# ]
#

@app.route("/")
@app.route("/home")
def home():
    # srcSql = """  select Member_ID, Member_FirstName, Member_LastName, email_id, m.Plan_ID, hp.Plan_Name, hp.Payer_Name
    # from [StudentRecords].[dbo].[Member] m
    # join [dbo].[Health_Plan] hp
    # on m.Plan_ID = hp.Plan_ID """
    srcSql = """ select hr.username as author,hr.id ,hp.load_date as date_posted, coalesce(hr.picdetails,'default.png') as image_file, hp.title, hp.content 
     from  [dbo].[HealthPosts] hp
     join [StudentRecords].[dbo].[healthifyRegistration] hr
     on hp.userid = hr.id
     """
    hdata = db.getdata(srcSql)
    return render_template('home.html', posts = hdata)


@app.route("/register", methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.postdata(username=form.username.data, email=form.email.data, password=hashed_password)
        flash(f'Your Account has been created for {form.username.data}! you can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/about")
def about():
    return render_template('about.html', title='About')




@app.route("/login", methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        query = f"select id, username, picdetails, password from StudentRecords.dbo.healthifyRegistration where email='{form.email.data}'"
        users = db.getdata(query)
        for item in users:
            uname = item["username"]
            picdetails = item["picdetails"]
            pwd = item["password"]
            uid = item["id"]
            userobject = db.UserClass(uname,form.email.data, picdetails, uid, active=True)
            if userobject and bcrypt.check_password_hash(pwd, form.password.data):
                login_user(userobject, remember=form.remember.data)
                next_page = request.args.get('next')
            #if form.email.data == 'admin@blog.com' and form.password.data == 'password':
                flash('You have been logged in!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))



# @app.route("/account")
# @login_required
# def account():
#     return render_template('account.html', title='Account')


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn




@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    baseuser = current_user.username
    form = UpdateAccountForm()
    pic = "default.png"
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            print(picture_file)
            pic = picture_file
            current_user.username = form.username.data
            regTblName = "StudentRecords.dbo.healthifyRegistration"
            query = f"update {regTblName} set username = '{form.username.data}', email = '{form.email.data}', picdetails = '{picture_file}' where username = '{baseuser}'"
            row = db.checkdata(query)
            flash('Your account has been updated!', 'success')
            return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username

    image_file = url_for('static', filename='profile_pics/' + pic)
    return render_template('account.html', title='Account',
                            image_file=image_file, form=form)


@app.route("/post/new",  methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        flash("Your post has been created!","success")
        query = f"select id from StudentRecords.dbo.healthifyRegistration where username='{current_user.username}'"
        users = db.getdata(query)
        for item in users:
            uid = item["id"]
        query = f"insert into [dbo].[HealthPosts] (userid, title, content) values ({uid},'{form.title.data}','{form.content.data}')"
        row = db.checkdata(query)
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    srcSql = f""" select hp.id as id, hr.username as author, hp.load_date as date_posted, 
                    coalesce(hr.picdetails,'default.png') as image_file, hp.title, hp.content 
                     from  [dbo].[HealthPosts] hp
                     join [StudentRecords].[dbo].[healthifyRegistration] hr
                     on hp.userid = hr.id
                     where hp.id = {post_id}
                     """
    hdata = db.getdata(srcSql)
    return render_template('post.html', title = "update title_content", posts = hdata)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    print("entered for loop")
    srcSql = f""" select hr.id, hr.username as author, hp.load_date as date_posted,
                            coalesce(hr.picdetails,'default.png') as image_file, hp.title, hp.content
                             from  [dbo].[HealthPosts] hp
                             join [StudentRecords].[dbo].[healthifyRegistration] hr
                             on hp.id = hr.id
                             where hp.id = {post_id}
                             """
    posts = db.getdata(srcSql)
    for item in posts:
        title = item["title"]
        content = item["content"]
        uid = item["id"]
        author = item["author"]
        if author != current_user.username:
            abort(403)

        form = PostForm()
        if form.validate_on_submit():
            postTblName = "[dbo].[HealthPosts]"
            query = f"update {postTblName} set title = '{form.title.data}', content = '{form.content.data}' where id = {post_id}"
            row = db.checkdata(query)
            flash('Your post has been updated!', 'success')
            return redirect(url_for('post', post_id=uid))
        elif request.method == 'GET':
            form.title.data = title
            form.content.data = content
        return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    print(post_id)
    srcSql = f""" select hr.id, hr.username as author, hp.load_date as date_posted,
                                coalesce(hr.picdetails,'default.png') as image_file, hp.title, hp.content
                                 from  [dbo].[HealthPosts] hp
                                 join [StudentRecords].[dbo].[healthifyRegistration] hr
                                 on hp.id = hr.id
                                 where hp.id = {post_id}
                                 """
    posts = db.getdata(srcSql)
    for item in posts:
        uid = item["id"]
        author = item["author"]
        if author != current_user.username:
            abort(403)
        postTblName = "[dbo].[HealthPosts]"
        query = f"delete from {postTblName} where id = {post_id}"
        print(query)
        row = db.checkdata(query)
        flash('Your post has been deleted!', 'success')
        return redirect(url_for('home'))