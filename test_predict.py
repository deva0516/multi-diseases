import requests
import os

# Find a test image
test_images_dir = "Test Images/Brain Stroke/glioma"
if os.path.exists(test_images_dir):
    test_files = os.listdir(test_images_dir)
    if test_files:
        test_image = os.path.join(test_images_dir, test_files[0])
        print(f"Testing with image: {test_image}")
        
        with open(test_image, 'rb') as f:
            files = {'file': f}
            try:
                response = requests.post('http://localhost:5000/predict', files=files)
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.json()}")
            except Exception as e:
                print(f"Error: {e}")
                print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
else:
    print("Test images directory not found")
