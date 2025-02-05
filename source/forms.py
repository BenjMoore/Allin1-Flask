from flask_wtf import FlaskForm
from wtforms import FileField, StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired

class UploadForm(FlaskForm):
    file = FileField("File", validators=[DataRequired()])
    folder = StringField("Folder (optional)")
    submit = SubmitField("Upload")

class DeleteForm(FlaskForm):
    path = HiddenField("Path", validators=[DataRequired()])
    submit = SubmitField("Delete")

class CreateFolderForm(FlaskForm):
    folder = StringField('Folder Name', validators=[DataRequired()])
    submit = SubmitField('Create Folder')