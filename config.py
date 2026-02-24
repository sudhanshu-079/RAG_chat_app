import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "AIzaSyBKtSaueym_fLGetCS48iLoUYa8jA8hjEE"
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:XXXX@localhost:5432/ai_knowledge_vault"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")