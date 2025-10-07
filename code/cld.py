import streamlit as st
from PIL import Image
import requests
import numpy as np
from keras.preprocessing.image import load_img, img_to_array
from keras.models import load_model
import time
import os
from io import BytesIO
import pandas as pd
import base64
import re
from datetime import datetime

# Custom CSS for colorful, attractive UI with enhanced styles
st.markdown("""
    <style>
    :root {
        --primary-gradient: linear-gradient(135deg, #ff6f61 0%, #ffb347 30%, #98d98e 60%, #4fc3f7 100%);
        --secondary-gradient: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        --success-color: #28a745;
        --info-color: #0288d1;
        --warning-color: #f57c00;
        --error-color: #dc3545;
        --text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        --box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        --border-radius: 12px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .main {
        background: var(--primary-gradient);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        padding: 20px;
        border-radius: var(--border-radius);
        position: relative;
        overflow: hidden;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .main::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('https://www.transparenttextures.com/patterns/food.png') repeat;
        opacity: 0.1;
        z-index: -1;
        animation: textureFloat 20s linear infinite;
    }
    
    @keyframes textureFloat {
        0% { transform: translateX(0) translateY(0); }
        100% { transform: translateX(-100px) translateY(-50px); }
    }
    
    .title {
        color: #ff3d00;
        font-size: 3.5em;
        font-weight: bold;
        text-align: center;
        text-shadow: var(--text-shadow);
        margin-bottom: 10px;
        animation: titleGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes titleGlow {
        from { text-shadow: var(--text-shadow), 0 0 20px rgba(255, 61, 0, 0.5); }
        to { text-shadow: var(--text-shadow), 0 0 30px rgba(255, 61, 0, 0.8); }
    }
    
    .subheader {
        color: #26a69a;
        font-size: 2em;
        text-align: center;
        margin-bottom: 20px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
        font-style: italic;
    }
    
    .success-box {
        background: linear-gradient(135deg, rgba(212, 237, 218, 0.95), rgba(40, 167, 69, 0.1));
        padding: 20px;
        border-radius: var(--border-radius);
        border: 2px solid var(--success-color);
        color: #155724;
        box-shadow: var(--box-shadow);
        animation: fadeInUp 0.6s ease-out;
        margin: 10px 0;
    }
    
    .info-box {
        background: linear-gradient(135deg, rgba(225, 245, 254, 0.95), rgba(2, 136, 209, 0.1));
        padding: 20px;
        border-radius: var(--border-radius);
        border: 2px solid var(--info-color);
        color: #01579b;
        box-shadow: var(--box-shadow);
        animation: fadeInUp 0.6s ease-out 0.1s both;
        margin: 10px 0;
    }
    
    .warning-box {
        background: linear-gradient(135deg, rgba(255, 248, 225, 0.95), rgba(245, 124, 0, 0.1));
        padding: 20px;
        border-radius: var(--border-radius);
        border: 2px solid var(--warning-color);
        color: #4a2c00;
        box-shadow: var(--box-shadow);
        animation: fadeInUp 0.6s ease-out 0.2s both;
        margin: 10px 0;
    }
    
    .error-box {
        background: linear-gradient(135deg, rgba(248, 215, 218, 0.95), rgba(220, 53, 69, 0.1));
        padding: 20px;
        border-radius: var(--border-radius);
        border: 2px solid var(--error-color);
        color: #721c24;
        box-shadow: var(--box-shadow);
        animation: fadeInUp 0.6s ease-out 0.3s both;
        margin: 10px 0;
    }
    
    .chat-container {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(240, 240, 255, 0.9));
        border-radius: var(--border-radius);
        padding: 20px;
        margin: 20px 0;
        box-shadow: var(--box-shadow);
        border: 2px solid var(--info-color);
        max-height: 600px;
        overflow-y: auto;
    }
    
    .chat-message {
        padding: 12px 16px;
        margin: 10px 0;
        border-radius: 10px;
        animation: fadeInUp 0.3s ease-out;
    }
    
    .user-message {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border-left: 4px solid #2196f3;
        margin-left: 20px;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #f1f8e9, #dcedc8);
        border-left: 4px solid #8bc34a;
        margin-right: 20px;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stButton>button {
        background: linear-gradient(135deg, var(--success-color), #20c997);
        color: white;
        border-radius: var(--border-radius);
        font-weight: bold;
        padding: 12px 24px;
        transition: var(--transition);
        border: none;
        box-shadow: var(--box-shadow);
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #218838, #28a745);
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 8px 20px rgba(40, 167, 69, 0.3);
    }
    
    .stButton>button:hover::before {
        left: 100%;
    }
    
    .stFileUploader {
        background: var(--secondary-gradient);
        border-radius: var(--border-radius);
        padding: 20px;
        box-shadow: var(--box-shadow);
        transition: var(--transition);
    }
    
    .stFileUploader:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255, 154, 158, 0.3);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, rgba(178, 223, 219, 0.95), rgba(77, 208, 225, 0.2));
        border-radius: var(--border-radius);
        padding: 25px;
        box-shadow: var(--box-shadow);
        border-left: 4px solid var(--info-color);
    }
    
    .stExpander {
        background: linear-gradient(135deg, rgba(206, 147, 216, 0.95), rgba(156, 39, 176, 0.1));
        border-radius: var(--border-radius);
        border: 2px solid #9c27b0;
        margin: 10px 0;
        transition: var(--transition);
    }
    
    .stExpander:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 16px rgba(156, 39, 176, 0.2);
    }
    
    @media (max-width: 768px) {
        .title { font-size: 2.5em; }
        .subheader { font-size: 1.5em; }
        .main { padding: 10px; }
        .stButton>button { padding: 10px 20px; font-size: 0.9em; }
    }
    
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #28a745, #20c997);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #218838, #28a745);
    }
    </style>
""", unsafe_allow_html=True)

# Load model and labels
@st.cache_resource
def load_classification_model():
    try:
        # Load model using path relative to this script file so it works
        # even when Streamlit is started from a different working directory.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, 'FV.h5')
        return load_model(model_path)
    except Exception as e:
        st.error(f"Failed to load model: {str(e)}")
        return None

model = load_classification_model()
if model is None:
    st.stop()

labels = {0: 'apple', 1: 'banana', 2: 'beetroot', 3: 'bell pepper', 4: 'cabbage', 5: 'capsicum', 6: 'carrot',
          7: 'cauliflower', 8: 'chilli pepper', 9: 'corn', 10: 'cucumber', 11: 'eggplant', 12: 'garlic', 13: 'ginger',
          14: 'grapes', 15: 'jalapeno', 16: 'kiwi', 17: 'lemon', 18: 'lettuce',
          19: 'mango', 20: 'onion', 21: 'orange', 22: 'paprika', 23: 'pear', 24: 'peas', 25: 'pineapple',
          26: 'pomegranate', 27: 'potato', 28: 'radish', 29: 'soy beans', 30: 'spinach', 31: 'sweetcorn',
          32: 'sweetpotato', 33: 'tomato', 34: 'turnip', 35: 'watermelon'}

fruits = ['Apple', 'Banana', 'Bell Pepper', 'Chilli Pepper', 'Grapes', 'Jalapeno', 'Kiwi', 'Lemon', 'Mango', 'Orange',
          'Paprika', 'Pear', 'Pineapple', 'Pomegranate', 'Watermelon']
vegetables = ['Beetroot', 'Cabbage', 'Capsicum', 'Carrot', 'Cauliflower', 'Corn', 'Cucumber', 'Eggplant', 'Ginger',
              'Lettuce', 'Onion', 'Peas', 'Potato', 'Radish', 'Soy Beans', 'Spinach', 'Sweetcorn', 'Sweetpotato',
              'Tomato', 'Turnip']

# Knowledge base for chatbot
NUTRITION_FACTS = {
    'apple': {'calories': 52, 'protein': 0.3, 'carbs': 14, 'fiber': 2.4, 'vitamin_c': 'High', 'benefits': 'Good for heart health, rich in antioxidants'},
    'banana': {'calories': 89, 'protein': 1.1, 'carbs': 23, 'fiber': 2.6, 'potassium': 'High', 'benefits': 'Energy boost, good for digestion'},
    'beetroot': {'calories': 43, 'protein': 1.6, 'carbs': 10, 'fiber': 2.8, 'folate': 'High', 'benefits': 'Lowers blood pressure, improves exercise performance'},
    'bell pepper': {'calories': 31, 'protein': 1.0, 'carbs': 6, 'fiber': 2.1, 'vitamin_c': 'Very High', 'benefits': 'Immune system support, eye health'},
    'cabbage': {'calories': 25, 'protein': 1.3, 'carbs': 6, 'fiber': 2.5, 'vitamin_k': 'High', 'benefits': 'Anti-inflammatory, supports digestion'},
    'carrot': {'calories': 41, 'protein': 0.9, 'carbs': 10, 'fiber': 2.8, 'vitamin_a': 'Very High', 'benefits': 'Excellent for eye health, immune support'},
    'cauliflower': {'calories': 25, 'protein': 1.9, 'carbs': 5, 'fiber': 2.0, 'vitamin_c': 'High', 'benefits': 'Low-carb alternative, cancer prevention'},
    'corn': {'calories': 86, 'protein': 3.3, 'carbs': 19, 'fiber': 2.0, 'lutein': 'High', 'benefits': 'Eye health, energy source'},
    'cucumber': {'calories': 16, 'protein': 0.7, 'carbs': 4, 'fiber': 0.5, 'hydration': 'Excellent', 'benefits': 'Hydration, weight loss'},
    'eggplant': {'calories': 25, 'protein': 1.0, 'carbs': 6, 'fiber': 3.0, 'antioxidants': 'High', 'benefits': 'Heart health, blood sugar control'},
    'garlic': {'calories': 149, 'protein': 6.4, 'carbs': 33, 'fiber': 2.1, 'allicin': 'High', 'benefits': 'Immune boost, antibacterial properties'},
    'ginger': {'calories': 80, 'protein': 1.8, 'carbs': 18, 'fiber': 2.0, 'gingerol': 'High', 'benefits': 'Reduces nausea, anti-inflammatory'},
    'grapes': {'calories': 69, 'protein': 0.7, 'carbs': 18, 'fiber': 0.9, 'resveratrol': 'High', 'benefits': 'Heart health, antioxidant rich'},
    'kiwi': {'calories': 61, 'protein': 1.1, 'carbs': 15, 'fiber': 3.0, 'vitamin_c': 'Very High', 'benefits': 'Immune support, digestive health'},
    'lemon': {'calories': 29, 'protein': 1.1, 'carbs': 9, 'fiber': 2.8, 'vitamin_c': 'Very High', 'benefits': 'Alkalizing, detoxifying'},
    'lettuce': {'calories': 15, 'protein': 1.4, 'carbs': 3, 'fiber': 1.3, 'vitamin_k': 'High', 'benefits': 'Hydration, low calorie'},
    'mango': {'calories': 60, 'protein': 0.8, 'carbs': 15, 'fiber': 1.6, 'vitamin_a': 'High', 'benefits': 'Skin health, immune support'},
    'onion': {'calories': 40, 'protein': 1.1, 'carbs': 9, 'fiber': 1.7, 'quercetin': 'High', 'benefits': 'Anti-inflammatory, heart health'},
    'orange': {'calories': 47, 'protein': 0.9, 'carbs': 12, 'fiber': 2.4, 'vitamin_c': 'Very High', 'benefits': 'Immune boost, skin health'},
    'pear': {'calories': 57, 'protein': 0.4, 'carbs': 15, 'fiber': 3.1, 'copper': 'Good', 'benefits': 'Digestive health, weight management'},
    'pineapple': {'calories': 50, 'protein': 0.5, 'carbs': 13, 'fiber': 1.4, 'bromelain': 'High', 'benefits': 'Anti-inflammatory, digestion aid'},
    'pomegranate': {'calories': 83, 'protein': 1.7, 'carbs': 19, 'fiber': 4.0, 'antioxidants': 'Very High', 'benefits': 'Heart health, anti-aging'},
    'potato': {'calories': 77, 'protein': 2.0, 'carbs': 17, 'fiber': 2.1, 'potassium': 'High', 'benefits': 'Energy source, satisfying'},
    'spinach': {'calories': 23, 'protein': 2.9, 'carbs': 4, 'fiber': 2.2, 'iron': 'High', 'benefits': 'Muscle health, bone strength'},
    'tomato': {'calories': 18, 'protein': 0.9, 'carbs': 4, 'fiber': 1.2, 'lycopene': 'High', 'benefits': 'Heart health, cancer prevention'},
    'watermelon': {'calories': 30, 'protein': 0.6, 'carbs': 8, 'fiber': 0.4, 'hydration': 'Excellent', 'benefits': 'Hydration, muscle soreness relief'},
}

def fetch_nutrition(prediction):
    """Fetch nutritional information for the predicted item using Nutritionix API."""
    try:
        app_id = 'af090f89'
        app_key = '7efd4f2fdc1e1fa089916e68c19feac8'
        url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
        headers = {'x-app-id': app_id, 'x-app-key': app_key, 'Content-Type': 'application/json'}
        data = {'query': prediction, 'timezone': 'US/Eastern'}
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        if 'foods' in result and len(result['foods']) > 0:
            food = result['foods'][0]
            return {
                'calories': f"{food['nf_calories']:.1f} kcal",
                'protein': f"{food.get('nf_protein', 0):.1f} g",
                'fat': f"{food.get('nf_total_fat', 0):.1f} g",
                'carbs': f"{food.get('nf_total_carbohydrate', 0):.1f} g",
                'fiber': f"{food.get('nf_dietary_fiber', 0):.1f} g",
                'sugars': f"{food.get('nf_sugars', 0):.1f} g",
                'sodium': f"{food.get('nf_sodium', 0):.1f} mg",
                'serving_size': f"{food.get('serving_qty', 100)} {food.get('serving_unit', 'g')}"
            }
        return None
    except Exception as e:
        return None

def prepare_image(img_path, confidence_threshold):
    """Process the image and predict using the model, returning top-3 predictions if valid."""
    try:
        if not os.path.exists(img_path):
            return None, None, None
        if os.path.getsize(img_path) > 5 * 1024 * 1024:
            return None, None, None
        
        img = load_img(img_path, target_size=(224, 224))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        prediction = model.predict(img_array, verbose=0)[0]
        top_indices = np.argsort(prediction)[::-1][:3]
        top_confidences = prediction[top_indices] * 100
        top_labels = [labels[i].capitalize() for i in top_indices]
        
        max_confidence = top_confidences[0]
        if max_confidence < confidence_threshold:
            return "Not a fruit or vegetable", max_confidence, None
        return top_labels[0], max_confidence, list(zip(top_labels, top_confidences))
    except Exception as e:
        return None, None, None

def generate_report(prediction, category, nutrition, confidence, top3=None):
    """Generate a text report of the prediction and nutrition info."""
    report = f"# Fruit & Vegetable Classification Report\n\n"
    report += f"**Prediction**: {prediction}\n"
    report += f"**Category**: {category}\n"
    report += f"**Confidence**: {confidence:.2f}%\n"
    if top3:
        report += "\n**Top 3 Predictions**:\n"
        for label, conf in top3:
            report += f"- {label}: {conf:.2f}%\n"
    if nutrition:
        report += f"\n**Nutrition (per serving)**:\n"
        report += f"- Calories: {nutrition['calories']}\n"
        report += f"- Protein: {nutrition['protein']}\n"
        report += f"- Fat: {nutrition['fat']}\n"
        report += f"- Carbohydrates: {nutrition['carbs']}\n"
        report += f"- Fiber: {nutrition['fiber']}\n"
        report += f"- Sugars: {nutrition['sugars']}\n"
        report += f"- Sodium: {nutrition['sodium']}\n"
        report += f"- Serving Size: {nutrition['serving_size']}\n"
    else:
        report += "\n**Nutrition**: Not available\n"
    return report

# ===== FREE AI CHATBOT (Rule-Based with NLP) =====

class FruitVegChatbot:
    """Rule-based chatbot for fruit and vegetable classification system."""
    
    def __init__(self):
        self.context = {
            'last_classification': None,
            'conversation_count': 0
        }
    
    def classify_intent(self, user_input):
        """Classify user intent based on keywords."""
        user_input = user_input.lower()
        
        # Greeting intents
        if any(word in user_input for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'greetings']):
            return 'greeting'
        
        # Classification intents
        if any(word in user_input for word in ['classify', 'identify', 'what is', "what's", 'analyze', 'detect', 'recognize', 'latest', 'last image']):
            return 'classify_image'
        
        # Nutrition intents
        if any(word in user_input for word in ['calorie', 'nutrition', 'nutrient', 'protein', 'carb', 'fat', 'fiber', 'vitamin', 'healthy', 'health benefit']):
            return 'nutrition_query'
        
        # History intents
        if any(word in user_input for word in ['history', 'previous', 'past', 'show me', 'list', 'record']):
            return 'show_history'
        
        # Comparison intents
        if 'compare' in user_input or 'difference between' in user_input or 'vs' in user_input:
            return 'compare'
        
        # Help intents
        if any(word in user_input for word in ['help', 'what can you do', 'how to', 'guide', 'instructions']):
            return 'help'
        
        # Model/System info
        if any(word in user_input for word in ['model', 'accuracy', 'how does', 'how do you work', 'machine learning', 'ai']):
            return 'system_info'
        
        # Recommendation
        if any(word in user_input for word in ['recommend', 'suggest', 'best', 'healthiest', 'which fruit', 'which vegetable']):
            return 'recommendation'
        
        # Goodbye
        if any(word in user_input for word in ['bye', 'goodbye', 'see you', 'thanks', 'thank you']):
            return 'goodbye'
        
        return 'unknown'
    
    def extract_food_name(self, user_input):
        """Extract fruit or vegetable name from user input."""
        user_input = user_input.lower()
        all_foods = list(labels.values())
        
        for food in all_foods:
            if food in user_input:
                return food
        
        # Check for plural forms
        for food in all_foods:
            if food + 's' in user_input or food + 'es' in user_input:
                return food
        
        return None
    
    def get_response(self, user_input):
        """Generate response based on user intent."""
        intent = self.classify_intent(user_input)
        self.context['conversation_count'] += 1
        
        if intent == 'greeting':
            return self._greeting_response()
        
        elif intent == 'classify_image':
            return self._classify_response()
        
        elif intent == 'nutrition_query':
            food_name = self.extract_food_name(user_input)
            return self._nutrition_response(food_name)
        
        elif intent == 'show_history':
            return self._history_response()
        
        elif intent == 'compare':
            return self._compare_response(user_input)
        
        elif intent == 'help':
            return self._help_response()
        
        elif intent == 'system_info':
            return self._system_info_response()
        
        elif intent == 'recommendation':
            return self._recommendation_response(user_input)
        
        elif intent == 'goodbye':
            return self._goodbye_response()
        
        else:
            return self._unknown_response()
    
    def _greeting_response(self):
        greetings = [
            "Hello! 👋 I'm your Fruit & Vegetable AI Assistant. How can I help you today?",
            "Hi there! 🍎 Ready to explore the world of fruits and vegetables with me?",
            "Greetings! 🥕 I'm here to help you with image classification and nutrition info!"
        ]
        return greetings[self.context['conversation_count'] % len(greetings)]
    
    def _classify_response(self):
        if 'history' not in st.session_state or len(st.session_state.history) == 0:
            return "❌ No images have been classified yet. Please upload an image in the 'Image Classification' tab first, then I can tell you about it!"
        
        last_entry = st.session_state.history[-1]
        self.context['last_classification'] = last_entry['Prediction']
        
        response = f"🔍 **Latest Classification Results:**\n\n"
        response += f"📸 **Image**: {last_entry['Image']}\n"
        response += f"🎯 **Prediction**: {last_entry['Prediction']}\n"
        response += f"📊 **Confidence**: {last_entry['Confidence']}\n"
        response += f"🏷️ **Category**: {last_entry['Category']}\n\n"
        
        # Add interesting fact
        food_name = last_entry['Prediction'].lower()
        if food_name in NUTRITION_FACTS:
            info = NUTRITION_FACTS[food_name]
            response += f"💡 **Did you know?** {info['benefits']}"
        
        return response
    
    def _nutrition_response(self, food_name):
        if food_name is None:
            if self.context['last_classification']:
                food_name = self.context['last_classification'].lower()
            else:
                return "🤔 I couldn't identify which fruit or vegetable you're asking about. Please mention a specific name like 'apple' or 'carrot'."
        
        if food_name in NUTRITION_FACTS:
            info = NUTRITION_FACTS[food_name]
            response = f"🥗 **Nutritional Information for {food_name.title()}:**\n\n"
            response += f"🔥 **Calories**: {info['calories']} kcal per 100g\n"
            response += f"💪 **Protein**: {info['protein']}g\n"
            response += f"🍞 **Carbs**: {info['carbs']}g\n"
            response += f"🌾 **Fiber**: {info['fiber']}g\n\n"
            
            # Add special nutrients
            special = [k for k in info.keys() if k not in ['calories', 'protein', 'carbs', 'fiber', 'benefits']]
            if special:
                response += f"⭐ **Special Nutrients**: {', '.join([f'{k.title()}: {info[k]}' for k in special])}\n\n"
            
            response += f"✨ **Health Benefits**: {info['benefits']}"
            return response
        else:
            return f"Sorry, I don't have detailed nutrition information for {food_name} in my database yet. But you can try using the Nutrition API in the Image Classification tab!"
    
    def _history_response(self):
        if 'history' not in st.session_state or len(st.session_state.history) == 0:
            return "📋 No classification history available yet. Start by uploading and classifying some images!"
        
        history = st.session_state.history[-5:]  # Last 5 entries
        response = f"📊 **Your Recent Classifications** (Last {len(history)} entries):\n\n"
        
        for i, entry in enumerate(reversed(history), 1):
            response += f"**{i}.** {entry['Prediction']} ({entry['Confidence']}) - {entry['Category']}\n"
        
        # Add statistics
        total = len(st.session_state.history)
        fruit_count = sum(1 for e in st.session_state.history if 'Fruit' in e['Category'])
        veg_count = total - fruit_count
        
        response += f"\n📈 **Statistics**: Total: {total} | Fruits: {fruit_count} | Vegetables: {veg_count}"
        
        return response
    
    def _compare_response(self, user_input):
        # Extract two food names
        foods_in_input = [food for food in NUTRITION_FACTS.keys() if food in user_input.lower()]
        
        if len(foods_in_input) < 2:
            return "🔍 Please mention two fruits or vegetables to compare. Example: 'Compare apple and banana' or 'apple vs orange'"
        
        food1, food2 = foods_in_input[0], foods_in_input[1]
        info1, info2 = NUTRITION_FACTS[food1], NUTRITION_FACTS[food2]
        
        response = f"⚖️ **Comparison: {food1.title()} vs {food2.title()}**\n\n"
        response += f"| Nutrient | {food1.title()} | {food2.title()} |\n"
        response += f"|----------|---------|----------|\n"
        response += f"| Calories | {info1['calories']} | {info2['calories']} |\n"
        response += f"| Protein | {info1['protein']}g | {info2['protein']}g |\n"
        response += f"| Carbs | {info1['carbs']}g | {info2['carbs']}g |\n"
        response += f"| Fiber | {info1['fiber']}g | {info2['fiber']}g |\n\n"
        
        # Determine winner
        if info1['calories'] < info2['calories']:
            response += f"💡 **{food1.title()}** has fewer calories, making it better for weight management.\n"
        else:
            response += f"💡 **{food2.title()}** has fewer calories, making it better for weight management.\n"
        
        if info1['fiber'] > info2['fiber']:
            response += f"🌾 **{food1.title()}** has more fiber, excellent for digestion!"
        else:
            response += f"🌾 **{food2.title()}** has more fiber, excellent for digestion!"
        
        return response
    
    def _help_response(self):
        response = """🤖 **I'm Your Fruit & Vegetable AI Assistant!**

Here's what I can help you with:

**🔍 Image Classification:**
- "Classify the latest image"
- "What did I just upload?"
- "Analyze my last photo"

**🥗 Nutrition Information:**
- "How many calories in an apple?"
- "Tell me about carrot nutrition"
- "What are the benefits of spinach?"

**📊 History & Statistics:**
- "Show my classification history"
- "What have I classified?"
- "List my previous results"

**⚖️ Compare Foods:**
- "Compare apple and banana"
- "Difference between tomato and potato"
- "Apple vs orange nutrition"

**💡 Recommendations:**
- "What's the healthiest vegetable?"
- "Best fruit for vitamin C"
- "Recommend a low-calorie fruit"

**ℹ️ System Information:**
- "How does the AI work?"
- "What's your accuracy?"
- "Tell me about the model"

Just ask me anything! 😊"""
        return response
    
    def _system_info_response(self):
        response = """🤖 **About the AI Classification System:**

**📊 Model Details:**
- Type: Deep Learning CNN (Convolutional Neural Network)
- Architecture: Custom trained model for fruit & vegetable recognition
- Training: Trained on thousands of images across 36 classes
- Input Size: 224x224 pixels RGB images

**🎯 Capabilities:**
- Classifies 36 different fruits and vegetables
- Provides confidence scores for predictions
- Shows top-3 most likely predictions
- Real-time image analysis

**🔬 How It Works:**
1. You upload an image
2. Image is preprocessed (resized, normalized)
3. CNN extracts visual features
4. Model predicts the class with confidence score
5. Results displayed with nutrition information

**📈 Performance:**
- Confidence threshold: Adjustable (50-90%)
- Works best with: Clear, well-lit, centered images
- Supported formats: JPG, PNG (max 5MB)

**🌟 Features:**
- Real-time classification
- Nutrition API integration
- History tracking
- AI chatbot assistance (that's me!)

The system uses advanced computer vision to identify fruits and vegetables with high accuracy! 🚀"""
        return response
    
    def _recommendation_response(self, user_input):
        user_input = user_input.lower()
        
        if any(word in user_input for word in ['vitamin c', 'immune', 'cold']):
            return """🍊 **Best for Vitamin C & Immune Support:**

1. **Bell Pepper** - Highest vitamin C content!
2. **Orange** - Classic vitamin C source
3. **Kiwi** - More vitamin C than oranges
4. **Lemon** - Great for detox and immunity

💡 Tip: Eating these regularly can boost your immune system naturally!"""
        
        elif any(word in user_input for word in ['weight loss', 'low calorie', 'diet']):
            return """🥒 **Best for Weight Loss (Low Calorie):**

1. **Cucumber** - Only 16 calories per 100g
2. **Lettuce** - 15 calories, very filling
3. **Tomato** - 18 calories, high water content
4. **Watermelon** - 30 calories, keeps you hydrated

💡 Tip: These are mostly water, keeping you full with minimal calories!"""
        
        elif any(word in user_input for word in ['protein', 'muscle', 'workout']):
            return """💪 **Best for Protein (Vegetable Sources):**

1. **Spinach** - 2.9g protein per 100g
2. **Peas** - Good plant protein
3. **Corn** - 3.3g protein
4. **Potato** - 2.0g protein

💡 Tip: Combine with other protein sources for muscle building!"""
        
        elif any(word in user_input for word in ['fiber', 'digestion', 'digestive']):
            return """🌾 **Best for Fiber & Digestion:**

1. **Pomegranate** - 4.0g fiber
2. **Pear** - 3.1g fiber
3. **Kiwi** - 3.0g fiber
4. **Eggplant** - 3.0g fiber

💡 Tip: Fiber helps maintain healthy digestion and prevents constipation!"""
        
        elif any(word in user_input for word in ['energy', 'carb', 'fuel']):
            return """⚡ **Best for Energy (Healthy Carbs):**

1. **Banana** - 23g carbs, quick energy
2. **Corn** - 19g carbs, sustained energy
3. **Potato** - 17g carbs, filling
4. **Mango** - 15g carbs, natural sugars

💡 Tip: Great for pre-workout or when you need an energy boost!"""
        
        elif any(word in user_input for word in ['antioxidant', 'anti-aging', 'skin']):
            return """✨ **Best for Antioxidants & Skin Health:**

1. **Pomegranate** - Very high antioxidants
2. **Grapes** - Resveratrol content
3. **Tomato** - Lycopene for skin
4. **Bell Pepper** - Vitamin C for collagen

💡 Tip: These fight free radicals and promote youthful skin!"""
        
        else:
            return """🌟 **Top Overall Healthy Choices:**

**Fruits:**
1. **Pomegranate** - Antioxidant powerhouse
2. **Kiwi** - Vitamin C champion
3. **Banana** - Energy & potassium
4. **Orange** - Immune support

**Vegetables:**
1. **Spinach** - Iron & nutrients
2. **Bell Pepper** - Vitamin C king
3. **Carrot** - Vitamin A for eyes
4. **Tomato** - Heart health

💡 Tip: Eat a variety of colors for maximum nutrition! 🌈"""
    
    def _goodbye_response(self):
        return """👋 Thank you for using the Fruit & Vegetable Classifier!

Stay healthy and keep eating your fruits and veggies! 🍎🥕

Feel free to come back anytime for more classifications and nutrition info. 

Have a great day! 😊"""
    
    def _unknown_response(self):
        return """🤔 I'm not quite sure what you're asking. Here are some things you can try:

• "Classify the latest image"
• "Tell me about apple nutrition"
• "Show my history"
• "Compare apple and banana"
• "What's the healthiest fruit?"
• "Help" - to see all my capabilities

What would you like to know? 😊"""

# Initialize chatbot
@st.cache_resource
def get_chatbot():
    return FruitVegChatbot()

def main():
    # Set page config
    st.set_page_config(page_title="Fruits & Vegetables Classifier", page_icon="🍎", layout="wide")

    # Initialize session state
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'feedback' not in st.session_state:
        st.session_state.feedback = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'confidence_threshold' not in st.session_state:
        st.session_state.confidence_threshold = 70

    # Initialize chatbot
    chatbot = get_chatbot()

    # Sidebar
    with st.sidebar:
        st.header("📋 How to Use", help="Follow these steps to classify your image!")
        st.markdown("""
        1. Upload an image or use webcam (max 5MB).
        2. Adjust the confidence threshold if needed.
        3. Click 'Predict' to classify the image.
        4. View top-3 predictions, nutrition, and confidence chart.
        5. Chat with FREE AI assistant about results!
        6. Provide feedback on predictions.
        7. Click 'Reset' to clear and start over.
        8. Download report for summary.
        """, help="Ensure your image is well-lit and focused on a single item.")
        
        st.session_state.confidence_threshold = st.slider(
            "Confidence Threshold (%)", 
            min_value=50, 
            max_value=90, 
            value=st.session_state.confidence_threshold, 
            step=5, 
            help="Set the minimum confidence for a valid fruit/vegetable prediction."
        )
        
        st.subheader("💬 Feedback")
        feedback_text = st.text_area("Share your feedback:", help="Let us know if the prediction was accurate!")
        if st.button("Submit Feedback"):
            if feedback_text:
                st.session_state.feedback.append(feedback_text)
                st.success("Thank you for your feedback!")
            else:
                st.warning("Please enter feedback before submitting.")

    # Header
    st.markdown('<div class="title">🍊 Fruits & Vegetables Classifier 🥕</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">AI-Powered Classification with FREE Smart Chatbot!</div>', unsafe_allow_html=True)
    
    # Try to load header image
    try:
        if os.path.exists("upload_images/vege.png"):
            image = Image.open("upload_images/vege.png")
            st.image(image, use_container_width=True, caption="Discover the world of fruits and vegetables!")
    except:
        pass

    # Main tabs
    tab1, tab2 = st.tabs(["📸 Image Classification", "🤖 AI Chatbot Assistant"])
    
    # ===== TAB 1: IMAGE CLASSIFICATION =====
    with tab1:
        # Input options
        input_method = st.radio("Choose input method:", ("Upload Image", "Use Webcam"))

        img_file = None
        if input_method == "Upload Image":
            img_file = st.file_uploader("Upload an Image", type=["jpg", "png"], help="Upload a clear JPG or PNG image (max 5MB).")
        else:
            img_file = st.camera_input("Take a Picture", help="Capture a photo using your webcam.")

        # Display uploaded or captured image
        col1, col2 = st.columns([3, 2])
        with col1:
            if img_file:
                with col2:
                    try:
                        img = Image.open(img_file).resize((250, 250))
                        st.image(img, caption="Input Image", use_container_width=True)
                    except Exception as e:
                        st.error(f"Error displaying image: {str(e)}")

        # Buttons
        col_predict, col_reset = st.columns([1, 1])
        with col_predict:
            predict_button = st.button("Predict", key="predict_button", help="Click to classify the input image.")
        with col_reset:
            reset_button = st.button("Reset", key="reset_button", help="Clear all results and start over.")

        # Reset session state
        if reset_button:
            st.session_state.clear()
            upload_dir = "./upload_images"
            if os.path.exists(upload_dir):
                for file in os.listdir(upload_dir):
                    file_path = os.path.join(upload_dir, file)
                    if os.path.isfile(file_path) and file != "vege.png":
                        try:
                            os.remove(file_path)
                        except:
                            pass
            st.rerun()

        # Ensure upload directory exists
        os.makedirs("./upload_images", exist_ok=True)

        if predict_button and img_file:
            if img_file.size > 5 * 1024 * 1024:
                st.error("Image file is too large. Please upload an image smaller than 5MB.")
            else:
                save_image_path = f"./upload_images/{img_file.name}"
                try:
                    with open(save_image_path, "wb") as f:
                        f.write(img_file.getbuffer())
                except Exception as e:
                    st.error(f"Error saving image: {str(e)}")

                # Progress bar
                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress.progress(i + 1)

                # Prediction
                result, confidence, top3 = prepare_image(save_image_path, st.session_state.confidence_threshold)
                if result:
                    if result == "Not a fruit or vegetable":
                        st.markdown(f'<div class="error-box"><b>Result:</b> {result} (Confidence: {confidence:.2f}%)</div>', unsafe_allow_html=True)
                        st.session_state.history.append({"Image": img_file.name, "Prediction": result, "Confidence": f"{confidence:.2f}%", "Category": "N/A"})
                    else:
                        category = "Vegetable 🥕" if result in vegetables else "Fruit 🍎"
                        st.markdown(f'<div class="info-box"><b>Category:</b> {category}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="success-box"><b>Predicted:</b> {result} (Confidence: {confidence:.2f}%)</div>', unsafe_allow_html=True)

                        # Top-3 predictions
                        with st.expander("Top 3 Predictions", expanded=False):
                            top3_df = pd.DataFrame(top3, columns=["Label", "Confidence"])
                            top3_df["Confidence"] = top3_df["Confidence"].apply(lambda x: f"{x:.2f}%")
                            st.table(top3_df)

                        # Confidence bar chart
                        st.markdown('<div class="info-box"><b>Confidence Score:</b></div>', unsafe_allow_html=True)
                        chart_data = pd.DataFrame({"Confidence": [confidence], "Remaining": [100 - confidence]}, index=["Prediction"])
                        st.bar_chart(chart_data)

                        # Nutrition info
                        with st.expander("Nutrition Information", expanded=True):
                            nutrition = fetch_nutrition(result.lower())
                            if nutrition:
                                st.markdown('<div class="warning-box"><b>Nutrition (per serving):</b></div>', unsafe_allow_html=True)
                                st.table({
                                    "Nutrient": ["Calories", "Protein", "Fat", "Carbohydrates", "Fiber", "Sugars", "Sodium", "Serving Size"],
                                    "Value": [nutrition['calories'], nutrition['protein'], nutrition['fat'], nutrition['carbs'], nutrition['fiber'], nutrition['sugars'], nutrition['sodium'], nutrition['serving_size']]
                                })
                            else:
                                st.markdown('<div class="warning-box">Nutrition information not available.</div>', unsafe_allow_html=True)

                        # Download report
                        report = generate_report(result, category, nutrition, confidence, top3)
                        buffer = BytesIO(report.encode('utf-8'))
                        st.download_button(
                            label="Download Report",
                            data=buffer,
                            file_name=f"{result}_report.txt",
                            mime="text/plain",
                            help="Download a summary of the prediction and nutrition info."
                        )

                        st.session_state.history.append({"Image": img_file.name, "Prediction": result, "Confidence": f"{confidence:.2f}%", "Category": category})

                else:
                    st.error("Prediction failed. Please try a different image.")

        # History
        if st.session_state.history:
            with st.expander("Prediction History", expanded=False):
                history_df = pd.DataFrame(st.session_state.history)
                st.table(history_df)

        # Feedback history
        if st.session_state.feedback:
            with st.expander("Feedback History", expanded=False):
                for fb in st.session_state.feedback:
                    st.text(fb)
    
    # ===== TAB 2: FREE AI CHATBOT =====
    with tab2:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        st.success("✅ FREE AI Chatbot is ready! No API key needed! Ask me anything! 🎉")
        
        # Chat tips
        with st.expander("💡 What can I ask the FREE AI Chatbot?", expanded=True):
            st.markdown("""
            **🔍 Image Classification:**
            - "Classify the latest image"
            - "What did I just upload?"
            - "Analyze my last photo"
            
            **🥗 Nutrition Information:**
            - "How many calories in a banana?"
            - "Tell me about carrot nutrition"
            - "What are the benefits of spinach?"
            
            **⚖️ Compare Foods:**
            - "Compare apple and banana"
            - "Apple vs orange nutrition"
            - "Difference between tomato and potato"
            
            **📊 History:**
            - "Show my classification history"
            - "What have I classified?"
            
            **💡 Recommendations:**
            - "What's the healthiest fruit?"
            - "Best vegetable for vitamin C"
            - "Recommend low-calorie foods"
            
            **ℹ️ System Info:**
            - "How does this AI work?"
            - "Tell me about the model"
            
            **🆘 Help:**
            - "Help" - See all commands
            """)
        
        st.markdown("---")
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤 <b>You:</b><br>{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message">🤖 <b>AI Assistant:</b><br>{message["content"]}</div>', unsafe_allow_html=True)
        
        # Chat input
        col_input, col_clear = st.columns([5, 1])
        
        with col_clear:
            if st.button("🗑️ Clear", help="Clear chat history"):
                st.session_state.chat_history = []
                st.rerun()
        
        user_input = st.text_input("💬 Ask me anything:", key="chat_input", placeholder="e.g., Classify the latest image or What are the calories in an apple?")
        
        if st.button("Send", key="send_button") and user_input:
            # Add user message
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Get AI response
            with st.spinner("🤔 AI is thinking..."):
                try:
                    response = chatbot.get_response(user_input)
                    
                    # Add bot response
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_msg
                    })
            
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick action buttons
        st.markdown("### 🚀 Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔍 Classify Latest"):
                st.session_state.chat_history.append({"role": "user", "content": "Classify the latest image"})
                response = chatbot.get_response("Classify the latest image")
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col2:
            if st.button("📊 Show History"):
                st.session_state.chat_history.append({"role": "user", "content": "Show my history"})
                response = chatbot.get_response("Show my history")
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col3:
            if st.button("💡 Get Tips"):
                st.session_state.chat_history.append({"role": "user", "content": "Give me health recommendations"})
                response = chatbot.get_response("Give me health recommendations")
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col4:
            if st.button("🆘 Help"):
                st.session_state.chat_history.append({"role": "user", "content": "Help"})
                response = chatbot.get_response("Help")
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                st.rerun()

if __name__ == "__main__":
    main()