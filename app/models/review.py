from datetime import datetime
from app import db

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # 5 üzerinden puan
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    psychologist_id = db.Column(db.Integer, db.ForeignKey('psychologists.id'), nullable=False)

    def __repr__(self):
        return f"Review(psychologist='{self.psychologist.full_name}', user='{self.user.email}', rating={self.rating})"