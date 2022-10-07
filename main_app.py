from ast import Pass
from flask import Flask, render_template, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField, TextAreaField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt



# --------------------------------------------------------------------------------
class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    email = EmailField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class UpdateForm(FlaskForm):
    email = EmailField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Email"})
    first_name = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "FirstName"})
    last_name = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "LastName"})
    mobile_no = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Mobile No"})
    gender = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Gender"})
    age = IntegerField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "age"})
    about = TextAreaField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "about"})
    
    submit = SubmitField('Update')



class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

# --------------------------------------------------------------------------------
app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '6d3f0e7a2a7153828ee4345053d07164'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# --------------------------------------------------------------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique=True)  
    email = db.Column(db.String(200))
    password = db.Column(db.String(10))
    profile = db.relationship("Profile", backref="app_user", cascade="all, delete", lazy="select", uselist=False) # One-To-One Relationship
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __str__(self) -> str:
        return f"{self.username}"


class Profile(db.Model):
    id = db.Column('profile_id', db.Integer, primary_key = True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    mobile_no = db.Column(db.String(13))
    Gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    about = db.Column(db.String(100))
    user = db.Column(db.Integer, db.ForeignKey("user.id"))

# --------------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template("login.html", form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        print("------->", new_user.id)
        db.session.add(new_user)
        db.session.commit()
        new_profile = Profile(first_name="", last_name="", mobile_no="", Gender="", age=0,about="", user=new_user.id)
        db.session.add(new_profile)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    form = UpdateForm()
    user_to_update = User.query.get_or_404(id)
    print(user_to_update.profile.user)
    profile_to_update = Profile.query.filter_by(user=user_to_update.profile.user)[0]
    if request.method == "POST":
        user_to_update.email = request.form['email']
        profile_to_update.first_name = request.form['first_name']
        profile_to_update.last_name = request.form['last_name']
        profile_to_update.mobile_no = request.form['mobile_no']
        profile_to_update.Gender = request.form['gender']
        profile_to_update.age = request.form['age']
        profile_to_update.about = request.form['about']
        try:
            db.session.commit()
            return redirect(url_for('dashboard'))
            # return render_template("update_user.html", form=form, user_to_update = user_to_update, profile_to_update=profile_to_update)
        except:
            return render_template("update_user.html", form=form, user_to_update = user_to_update, profile_to_update=profile_to_update)
    else:
        return render_template("update_user.html", form=form, user_to_update = user_to_update, profile_to_update=profile_to_update)

@app.route('/delete/<int:id>')
@login_required
def delete_login_user(id):
    user_to_delete = "iiiii"
    if id == current_user.id:
        user_to_delete = User.query.get_or_404(id)
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            print("user deleted successfuly")
            return redirect(url_for('register'))
        except:
            print("error!! ")
            return redirect(url_for('dashboard'))
    print("Something went wrong, look for cause")
    return redirect(url_for('dashboard'))


if __name__ == "__main__":
    app.run()