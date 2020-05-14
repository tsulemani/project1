from wtforms import Form, BooleanField, StringField, PasswordField, validators, HiddenField



class LoginForm(Form):

    username = StringField('Username')
    review = StringField('Review')
    book = HiddenField()

    password = PasswordField('Password')
