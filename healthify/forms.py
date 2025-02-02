from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import healthify.databasefile as db
from flask import flash


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        regTblName = "StudentRecords.dbo.healthifyRegistration"
        result = db.checkdata(f"select username from {regTblName} where username = '{username.data}'")
        if result>0:
            raise ValidationError('Username already exists, please chose a different username')

    def validate_email(self, email):
        regTblName = "StudentRecords.dbo.healthifyRegistration"
        result = db.checkdata(f"select email from {regTblName} where email = '{email.data}'")
        if result>0:
            raise ValidationError('Username already exists, please chose a different username')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')




class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        regTblName = "StudentRecords.dbo.healthifyRegistration"
        result = db.checkdata(f"select username from {regTblName} where username = '{username.data}'")
        if result > 0:
            raise ValidationError('Username already exists, please chose a different username')

    def validate_email(self, email):
        regTblName = "StudentRecords.dbo.healthifyRegistration"
        result = db.checkdata(f"select email from {regTblName} where email = '{email.data}'")
        if result > 0:
            raise ValidationError('Username already exists, please chose a different username')


class PostForm(FlaskForm):
    title = StringField('Title', validators = [DataRequired()])
    content = TextAreaField('Content', validators = [DataRequired()])
    submit = SubmitField('Post')