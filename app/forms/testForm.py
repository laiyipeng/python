# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import BooleanField, SubmitField, StringField, PasswordField, validators, widgets, SelectMultipleField, SelectField, RadioField

class testForm(Form):
    id = StringField('id')
    name = StringField('name')
    value = StringField('value', validators=[validators.required('xxx')])
    hidden_tag = StringField('hidden_tag')
    submit = SubmitField('提交')