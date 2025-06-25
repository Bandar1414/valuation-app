# app/models/visitor_model.py

from app import db
from datetime import datetime

class Visitor(db.Model):
    __tablename__ = 'visitors'
    ip = db.Column(db.String(100), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
