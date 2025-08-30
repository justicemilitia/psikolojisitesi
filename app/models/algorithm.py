from app import db

class Psychologist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # 'male', 'female' gibi değerler tutar
    gender = db.Column(db.String(10), nullable=False)
    # Dilleri virgülle ayrılmış şekilde tutabiliriz: "tr,en"
    languages = db.Column(db.String(50), nullable=False)
    # Uzmanlık alanları: "Anksiyete,Depresyon,İlişki"
    specialties = db.Column(db.String(200), nullable=False)
    # Diğer bilgiler...
    profile_image_url = db.Column(db.String(200))
    bio = db.Column(db.Text)
    age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Psychologist {self.name}>'