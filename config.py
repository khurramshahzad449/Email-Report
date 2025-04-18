import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

# Gong API Configuration
GONG_ACCESS_KEY = os.getenv('GONG_ACCESS_KEY')
GONG_SECRET_KEY = os.getenv('GONG_SECRET_KEY')
GONG_BASE_URL = os.getenv('GONG_BASE_URL')

# Ideal Pitch Template
IDEAL_PITCH_TEMPLATE = """
Key Components of an Ideal Sales Pitch:

Seamless Integration – The CRM integrates easily with existing tools like email, ERP, and marketing automation systems.

AI-Driven Insights – Advanced AI provides predictive analytics, lead scoring, and automated follow-ups.

Customization & Scalability – The platform is highly configurable to match company workflows and can scale as the business grows.

User-Friendly Interface – Intuitive design ensures quick adoption with minimal training.

Robust Security & Compliance – Enterprise-grade security features meet industry regulations like GDPR and SOC 2.
"""

# Analysis Parameters
ANALYSIS_PARAMETERS = {
    'min_confidence_threshold': 0.7,
    'max_missing_points': 3,
    'required_sections': [
        'introduction',
        'value_proposition',
        'solution_overview',
        'social_proof',
        'pricing',
        'call_to_action'
    ]
}

# Email Template
EMAIL_TEMPLATE = """
* What You Did Well: 
{{ didWell }}

* What Needs Improvement: 
{{ improvements }}  

* Final Score: {{ finalScore }}

* Coaching Tip:
{{ coachingTips }}

""" 