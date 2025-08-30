# app/models/company.py

from app import db
from datetime import datetime

class Company(db.Model):
    __tablename__ = 'companies'
    company_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Şirketin kullanıcılarını temsil eden ilişki
    users = db.relationship('User', backref='company', lazy=True)

    def __repr__(self):
        return f'<Company {self.company_name}>'