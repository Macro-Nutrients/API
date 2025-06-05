# config.py

import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'BebekGorengH.Slamet')  # Akan override lewat --set-env-vars
    PROJECT_ID = 'macro-nutrient'
    DATABASE_ID = 'macronutrient'
    
