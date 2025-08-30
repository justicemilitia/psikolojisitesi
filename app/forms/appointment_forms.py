from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, HiddenField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from datetime import datetime

class AppointmentForm(FlaskForm):
    """Form for creating an appointment"""
    psychologist_id = SelectField('Psychologist', validators=[
        DataRequired()
    ], coerce=int)
    date = StringField('Date', validators=[
        DataRequired()
    ])
    time = StringField('Time', validators=[
        DataRequired()
    ])
    submit = SubmitField('Book Appointment')
    
    def validate_date(self, date):
        """Validate that date is in the future"""
        try:
            appointment_date = datetime.strptime(date.data, '%Y-%m-%d').date()
            today = datetime.today().date()
            if appointment_date < today:
                raise ValidationError('Appointment date must be in the future.')
        except ValueError:
            raise ValidationError('Invalid date format. Please use YYYY-MM-DD.')
    
    def validate_time(self, time):
        """Validate time format"""
        try:
            datetime.strptime(time.data, '%H:%M')
        except ValueError:
            raise ValidationError('Invalid time format. Please use HH:MM.')

class AppointmentCancellationForm(FlaskForm):
    """Form for cancelling an appointment"""
    submit = SubmitField('Cancel Appointment')