from flask_wtf import (FlaskForm, RecaptchaField)
from wtforms import (StringField, TextAreaField, PasswordField, BooleanField,SubmitField)
from wtforms.validators import (DataRequired, Length, EqualTo)
from flask_wtf.file import (FileField, FileAllowed, FileRequired)

from app.models import User
from app.extensions import file_result


class LoginForm(FlaskForm):
    username = StringField('用户名', [DataRequired(), Length(max=255)])
    password = PasswordField('密码', [DataRequired()])
    remember = BooleanField('记住我')

    def validata(self):
        check_validate = super(LoginForm, self).validata()
        if not check_validate:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append('账户或密码错误')
            return False
        if not self.user.check_password(self.password.data):
            self.username.errors.append('账户或密码错误')
            return False
        return True


class RegisterForm(FlaskForm):
    username = StringField('用户名', [DataRequired(), Length(max=255)])
    password = PasswordField('密码', [DataRequired(), Length(min=8)])
    confirm = PasswordField('确认密码', [DataRequired(), EqualTo('password')])
    recaptcha = RecaptchaField()

    def validate(self):
        check_validate = super(RegisterForm, self).validate()
        if check_validate:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append('该用户名已存在，请换一个')
            return False
        return True


class ResultUpForm(FlaskForm):
    file = FileField('结果上传', validators=[FileRequired(),FileAllowed(file_result)])


class CountReForm(FlaskForm):
    submit = SubmitField('更新')


class StartCheck(FlaskForm):
    submit = SubmitField('开始审核')