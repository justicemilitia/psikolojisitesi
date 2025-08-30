from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, NumberRange

class ReviewForm(FlaskForm):
    rating = RadioField(
        'Puanınız',
        choices=[(i, str(i)) for i in range(5, 0, -1)], # 5'ten 1'e yıldızlar
        validators=[DataRequired(message="Lütfen bir puan seçin.")],
        coerce=int
    )
    comment = TextAreaField(
        'Yorumunuz',
        validators=[Length(max=1000, message="Yorumunuz en fazla 1000 karakter olabilir.")],
        render_kw={"placeholder": "Deneyimlerinizi paylaşın..."}
    )
    submit = SubmitField('Değerlendirmeyi Gönder')