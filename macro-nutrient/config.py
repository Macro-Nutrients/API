import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'BebekGorengH.Slamet')  # Ganti dengan kunci rahasia yang kuat
    PROJECT_ID = 'macro-nutrient'  # ID proyek di Google Cloud
    DATABASE_ID = 'macronutrient'  # ID database (opsional, bisa disesuaikan dengan kebutuhan)
