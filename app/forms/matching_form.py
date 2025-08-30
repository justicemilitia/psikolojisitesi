# app/forms/matching_form.py
from flask_wtf import FlaskForm
from wtforms import RadioField, SelectMultipleField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import Optional, Length, DataRequired, NumberRange

class TherapistMatchingForm(FlaskForm):
    previous_support = RadioField(
        'Have you received psychological support before?', 
        choices=[('Yes','Yes'), ('No','No')], 
        validators=[Optional()]
    )
    previous_support_type = RadioField(
        'What kind of psychological support did you receive?', 
        choices=[('Psychotherapy','Psychotherapy'), ('Medication treatment','Medication treatment')], 
        validators=[Optional()]
    )
    psychotherapy_approach = RadioField(
        'What approach-based psychotherapy support did you receive?', 
        choices=[
            ('Schema Therapy','Schema Therapy'), 
            ('Cognitive Behavioral Therapy','Cognitive Behavioral Therapy'), 
            ('Psychodynamic/Psychoanalytic Therapy','Psychodynamic/Psychoanalytic Therapy'), 
            ('Systemic Therapy','Systemic Therapy'), 
            ('Other','Other')
        ], 
        validators=[Optional()]
    )
    session_frequency = RadioField(
        'What is the frequency/number of sessions per month?', 
        choices=[('1-3','1-3'), ('4-6','4-6'), ('6-8','6-8')], 
        validators=[Optional()]
    )
    reason = TextAreaField(
        'Could you briefly explain your reason for seeking therapy?', 
        validators=[Optional(), Length(max=200)]
    )
    support_type = RadioField(
        'What kind of psychological support are you looking for?', 
        choices=[
            ('Individual Therapy','Individual Therapy'), 
            ('Child & Adolescent Therapy','Child & Adolescent Therapy'), 
            ('Couples Therapy','Couples Therapy')
        ], 
        validators=[Optional()]
    )
    improvement_areas = SelectMultipleField(
        'Which of the following would you like to see improvement in through psychological support?', 
        choices=[
            ('Negative thoughts','Negative thoughts'),
            ('Depressive feelings','Depressive feelings'),
            ('Anxiety/Panic/Worry','Anxiety/Panic/Worry'),
            ('Sleep/Appetite problems','Sleep/Appetite problems'),
            ('Anger management','Anger management'),
            ('Romantic relationships','Romantic relationships'),
            ('Family relationships','Family relationships'),
            ('Socialization/Friendship relationships','Socialization/Friendship relationships'),
            ('Work performance/Work relationships','Work performance/Work relationships'),
            ('Feeling of loneliness','Feeling of loneliness'),
            ('Lack of belonging','Lack of belonging')
        ], 
        validators=[Optional()]
    )
    medication_info = TextAreaField(
        'Would you like to provide information about the type of medications and duration of use?', 
        validators=[Optional(), Length(max=200)]
    )
    medication_continues = RadioField(
        'Are you currently on medication?', 
        choices=[('Yes','Yes'), ('No','No')], 
        validators=[Optional()]
    )
    sleep_appetite = RadioField(
        'Do you have sleep/appetite problems?', 
        choices=[('Yes','Yes'), ('No','No')], 
        validators=[Optional()]
    )
    been_together_years = RadioField(
        'How long have you been together?', 
        choices=[('0-1','0-1'), ('1-3','1-3'), ('3+','3+')], 
        validators=[Optional()]
    )
    togetherness_improvement_areas = SelectMultipleField(
        'Which of the following would you like to see improvement in regarding your relationship by seeking support?', 
        choices=[
            ('Communication problems','Communication problems'),
            ('Extended family problems','Extended family problems'),
            ('Financial problems','Financial problems'),
            ('Lack of social sharing/activity','Lack of social sharing/activity'),
            ('Lack of romantic interest/affection','Lack of romantic interest/affection'),
            ('Cheating/Infidelity','Cheating/Infidelity'),
            ('Lack of sexual desire','Lack of sexual desire'),
            ('Differences in future expectations','Differences in future expectations'),
            ('Disagreements in child/pet care','Disagreements in child/pet care')
        ], 
        validators=[Optional()]
    )
    number_of_children = IntegerField(
        'Number of children?',
        validators=[
            DataRequired(message="Please enter the number of children."),
            NumberRange(min=0, max=100, message="Number of children must be between 0 and 100.")
        ]
    )
    age_of_children = IntegerField(
        "Child's age?",
        validators=[
            DataRequired(message="Please enter the child's age."),
            NumberRange(min=0, max=18, message="Child's age must be between 0 and 18.")
        ]
    )
    children_improvement_areas = SelectMultipleField(
        'Which of the following would you like to see improvement in for your child?', 
        choices=[
            ('Emotion regulation','Emotion regulation'),
            ('Social anxiety/withdrawal','Social anxiety/withdrawal'),
            ('School/Exam anxiety','School/Exam anxiety'),
            ('Peer bullying (perpetrating, being exposed)','Peer bullying (perpetrating, being exposed)'),
            ('Adolescent emotional ups and downs','Adolescent emotional ups and downs'),
            ('Difficulty in relationship with authority','Difficulty in relationship with authority'),
            ('Boundary violations','Boundary violations')
        ], 
        validators=[Optional()]
    )

    submit = SubmitField('Find Suitable Therapists')
