from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import pickle
import ast

app = Flask(__name__)

# Load the model, scaler, and label encoder
with open('models/model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('models/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)
with open('models/label_encoder.pkl', 'rb') as f:
    le = pickle.load(f)

# Load supporting datasets
medicine_df = pd.read_csv('data/medications.csv')
diet_df = pd.read_csv('data/diets.csv')
precaution_df = pd.read_csv('data/precautions.csv')
workout_df = pd.read_csv('data/workout.csv')
description_df = pd.read_csv('data/description.csv')

# Define feature columns (based on Disease_pred.csv)
feature_columns = [
    'Age', 'Gender', 'nausea', 'joint_pain', 'abdominal_pain', 'high_fever', 'chills',
    'fatigue', 'runny_nose', 'pain_behind_the_eyes', 'dizziness', 'headache', 'chest_pain',
    'vomiting', 'cough', 'shivering', 'asthma_history', 'high_cholesterol', 'diabetes',
    'obesity', 'hiv_aids', 'nasal_polyps', 'asthma', 'high_blood_pressure', 'severe_headache',
    'weakness', 'trouble_seeing', 'fever', 'body_aches', 'sore_throat', 'sneezing',
    'diarrhea', 'rapid_breathing', 'rapid_heart_rate', 'pain_behind_eyes', 'swollen_glands',
    'rashes', 'sinus_headache', 'facial_pain', 'shortness_of_breath', 'reduced_smell_and_taste',
    'skin_irritation', 'itchiness', 'throbbing_headache', 'confusion', 'back_pain', 'knee_ache'
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        age = data['age']
        gender = data['gender']
        symptoms = data['symptoms']

        # Create feature vector
        feature_vector = [0] * len(feature_columns)
        feature_vector[0] = age
        feature_vector[1] = gender  # Assuming gender is encoded as in dataset
        for symptom in symptoms:
            if symptom in feature_columns:
                feature_vector[feature_columns.index(symptom)] = 1

        # Scale features
        feature_vector = np.array(feature_vector).reshape(1, -1)
        feature_vector_scaled = scaler.transform(feature_vector)

        # Predict
        prediction = model.predict(feature_vector_scaled)
        disease = le.inverse_transform(prediction)[0]

        # Fetch additional information
        mask_diet = diet_df['Disease'].str.lower() == disease.lower()
        mask_medicine = medicine_df['Disease'].str.lower() == disease.lower()
        mask_precaution = precaution_df['Disease'].str.lower() == disease.lower()
        mask_workout = workout_df['disease'].str.lower() == disease.lower()
        mask_des = description_df['Disease'].str.lower() == disease.lower()

        filtered_medicine = medicine_df[mask_medicine]
        filtered_diet = diet_df[mask_diet]
        filtered_precaution = precaution_df[mask_precaution]
        filtered_workout = workout_df[mask_workout]
        filtered_des = description_df[mask_des]

        row_medicine = filtered_medicine.iloc[0] if not filtered_medicine.empty else {}
        row_diet = filtered_diet.iloc[0] if not filtered_diet.empty else {}
        row_precaution = filtered_precaution.iloc[0] if not filtered_precaution.empty else {}
        row_des = filtered_des.iloc[0] if not filtered_des.empty else {}

        diet = ast.literal_eval(row_diet.get('Diet', '[]'))
        medicine = ast.literal_eval(row_medicine.get('Medication', '[]'))
        precautions = [row_precaution.get(f'Precaution_{i}', '') for i in range(1, 5) if pd.notna(row_precaution.get(f'Precaution_{i}'))]
        description = row_des.get('Description', '')
        workout = list(filtered_workout['workout']) if not filtered_workout.empty else []

        return jsonify({
            'disease': disease,
            'description': description,
            'medicines': ', '.join(medicine),
            'diet': ', '.join(diet),
            'precautions': precautions,
            'workout': workout
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)