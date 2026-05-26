from flask import Flask, render_template, request, jsonify
from keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = load_model("keras_model.h5", compile=False)

# Load the labels
class_names = open("labels.txt", "r").readlines()

# Disease information database
DISEASE_INFO = {
    "Meningioma": {
        "description": "A type of brain tumor that forms in the meninges (protective layers around the brain and spinal cord).",
        "causes": [
            "Exposure to radiation",
            "Genetic factors and inherited conditions",
            "Hormonal factors (more common in women)",
            "Age (risk increases with age)"
        ],
        "home_remedies": [
            "Maintain a healthy diet rich in antioxidants",
            "Practice stress-reduction techniques like meditation",
            "Get adequate sleep (7-9 hours)",
            "Stay hydrated",
            "Avoid exposure to toxins and chemicals"
        ],
        "medicines": [
            "Dexamethasone (to reduce swelling)",
            "Anticonvulsants (if seizures occur)",
            "Pain relievers (as prescribed)",
            "Consult neurosurgeon for surgical options"
        ],
        "severity": "High - Requires immediate medical attention"
    },
    "Glioma": {
        "description": "A type of tumor that occurs in the brain and spinal cord, originating from glial cells.",
        "causes": [
            "Genetic mutations",
            "Exposure to ionizing radiation",
            "Family history of gliomas",
            "Age factor (more common in adults)"
        ],
        "home_remedies": [
            "Consume turmeric (curcumin) for anti-inflammatory properties",
            "Eat foods rich in omega-3 fatty acids",
            "Practice yoga and meditation",
            "Maintain healthy weight",
            "Avoid processed foods and sugar"
        ],
        "medicines": [
            "Temozolomide (chemotherapy)",
            "Bevacizumab (targeted therapy)",
            "Steroids to reduce brain swelling",
            "Anti-seizure medications",
            "Consult oncologist for treatment plan"
        ],
        "severity": "High - Requires immediate medical attention"
    },
    "Pituitary": {
        "description": "A tumor in the pituitary gland that can affect hormone production and regulation.",
        "causes": [
            "Genetic mutations",
            "Family history of endocrine disorders",
            "Multiple endocrine neoplasia (MEN) syndrome",
            "Unknown factors in most cases"
        ],
        "home_remedies": [
            "Maintain balanced diet",
            "Regular exercise to regulate hormones",
            "Stress management techniques",
            "Adequate sleep schedule",
            "Avoid hormone-disrupting chemicals"
        ],
        "medicines": [
            "Cabergoline (for prolactinomas)",
            "Bromocriptine (dopamine agonist)",
            "Somatostatin analogs",
            "Hormone replacement therapy if needed",
            "Consult endocrinologist for proper treatment"
        ],
        "severity": "Moderate to High - Medical consultation required"
    },
    "Risk of Lung Cancer": {
        "description": "Indicators suggest potential lung cancer risk. Early detection is crucial for treatment.",
        "causes": [
            "Smoking and tobacco use",
            "Exposure to secondhand smoke",
            "Radon gas exposure",
            "Asbestos and carcinogen exposure",
            "Air pollution",
            "Family history of lung cancer"
        ],
        "home_remedies": [
            "Quit smoking immediately",
            "Consume green tea (antioxidants)",
            "Eat cruciferous vegetables (broccoli, cauliflower)",
            "Practice deep breathing exercises",
            "Use air purifiers at home",
            "Consume ginger and turmeric"
        ],
        "medicines": [
            "Consult pulmonologist immediately",
            "Targeted therapy drugs (if confirmed)",
            "Immunotherapy options",
            "Chemotherapy (if required)",
            "Pain management medications"
        ],
        "severity": "High - Immediate medical screening required"
    },
    "CKD Disease Predicted": {
        "description": "Chronic Kidney Disease (CKD) - Progressive loss of kidney function over time.",
        "causes": [
            "Diabetes (leading cause)",
            "High blood pressure",
            "Glomerulonephritis",
            "Polycystic kidney disease",
            "Prolonged urinary tract obstruction",
            "Recurrent kidney infections"
        ],
        "home_remedies": [
            "Reduce salt intake",
            "Stay well hydrated (consult doctor for amount)",
            "Limit protein intake",
            "Control blood sugar levels",
            "Maintain healthy blood pressure",
            "Avoid NSAIDs and nephrotoxic substances"
        ],
        "medicines": [
            "ACE inhibitors (blood pressure control)",
            "Diuretics (fluid management)",
            "Erythropoietin (for anemia)",
            "Phosphate binders",
            "Vitamin D supplements",
            "Consult nephrologist for dialysis options"
        ],
        "severity": "High - Requires ongoing medical management"
    },
    "Presence of Parkinsons": {
        "description": "A progressive nervous system disorder affecting movement, causing tremors and stiffness.",
        "causes": [
            "Genetic mutations",
            "Environmental toxins exposure",
            "Age (risk increases with age)",
            "Gender (more common in men)",
            "Head trauma",
            "Loss of dopamine-producing neurons"
        ],
        "home_remedies": [
            "Regular physical exercise and physiotherapy",
            "Consume foods rich in antioxidants",
            "Practice tai chi and yoga",
            "Maintain social connections",
            "Eat foods high in omega-3 fatty acids",
            "Get adequate sleep"
        ],
        "medicines": [
            "Levodopa/Carbidopa (primary treatment)",
            "Dopamine agonists (Pramipexole, Ropinirole)",
            "MAO-B inhibitors (Selegiline)",
            "COMT inhibitors",
            "Amantadine (for dyskinesia)",
            "Consult neurologist for personalized treatment"
        ],
        "severity": "Moderate to High - Requires neurological care"
    },
    "Notumor": {
        "description": "No tumor detected. Brain scan appears normal.",
        "causes": ["N/A - Healthy brain scan"],
        "home_remedies": [
            "Maintain healthy lifestyle",
            "Regular exercise",
            "Balanced diet",
            "Adequate sleep",
            "Stress management"
        ],
        "medicines": ["No medication required - Continue healthy lifestyle"],
        "severity": "None - Healthy"
    },
    "No Lung Cancer Detected": {
        "description": "Lung scan appears normal with no signs of cancer.",
        "causes": ["N/A - Healthy lung scan"],
        "home_remedies": [
            "Avoid smoking and secondhand smoke",
            "Regular cardiovascular exercise",
            "Maintain healthy diet",
            "Practice breathing exercises",
            "Avoid air pollution"
        ],
        "medicines": ["No medication required - Continue preventive care"],
        "severity": "None - Healthy"
    },
    "Absence of CKD": {
        "description": "Kidney function appears normal with no signs of chronic kidney disease.",
        "causes": ["N/A - Healthy kidney function"],
        "home_remedies": [
            "Stay hydrated",
            "Limit salt intake",
            "Maintain healthy blood pressure",
            "Control blood sugar",
            "Regular exercise"
        ],
        "medicines": ["No medication required - Continue preventive care"],
        "severity": "None - Healthy"
    },
    "Absence of Parkinsons": {
        "description": "No signs of Parkinson's disease detected.",
        "causes": ["N/A - Normal neurological function"],
        "home_remedies": [
            "Regular physical activity",
            "Mental exercises and puzzles",
            "Healthy diet",
            "Social engagement",
            "Adequate sleep"
        ],
        "medicines": ["No medication required - Continue healthy lifestyle"],
        "severity": "None - Healthy"
    },
    "Enter a Valid Image": {
        "description": "The uploaded image could not be processed or is not a valid medical scan.",
        "causes": ["Invalid image format or non-medical image"],
        "home_remedies": ["Please upload a valid medical scan image"],
        "medicines": ["N/A"],
        "severity": "N/A - Invalid Input"
    }
}

def predict_disease(image_path):
    """Predict disease from image"""
    try:
        # Create the array of the right shape to feed into the keras model
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        
        # Load and preprocess image
        image = Image.open(image_path).convert("RGB")
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        
        # Turn the image into a numpy array
        image_array = np.asarray(image)
        
        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
        
        # Load the image into the array
        data[0] = normalized_image_array
        
        # Predict
        prediction = model.predict(data, verbose=0)
        index = np.argmax(prediction)
        class_name = class_names[index].strip()
        confidence_score = float(prediction[0][index])
        
        # Extract disease name (remove index number)
        disease_name = class_name.split(' ', 1)[1] if ' ' in class_name else class_name
        
        return disease_name, confidence_score
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Enter a Valid Image", 0.0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        try:
            # Save the uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            print(f"File saved to: {filepath}")
            
            # Predict disease
            disease_name, confidence = predict_disease(filepath)
            
            print(f"Predicted: {disease_name} with confidence: {confidence}")
            
            # Get disease information
            disease_data = DISEASE_INFO.get(disease_name, DISEASE_INFO["Enter a Valid Image"])
            
            # Prepare response
            response = {
                'disease': disease_name,
                'confidence': f"{confidence * 100:.2f}%",
                'description': disease_data['description'],
                'causes': disease_data['causes'],
                'home_remedies': disease_data['home_remedies'],
                'medicines': disease_data['medicines'],
                'severity': disease_data['severity'],
                'image_path': filepath
            }
            
            print(f"Response prepared successfully")
            
            return jsonify(response)
        
        except Exception as e:
            print(f"Error in predict route: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Error processing image: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid request'}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
