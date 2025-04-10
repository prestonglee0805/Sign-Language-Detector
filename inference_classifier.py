import pickle
import cv2
import mediapipe as mp
import numpy as np
import time

# Load the model
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

# Camera setup
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Set a single color for all boxes - green
box_color = (0, 255, 0)  # Green in BGR

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        time.sleep(0.5)
        continue

    H, W, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        # Draw all hands
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
        
        # Process only the first hand for prediction
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # Reset data for each prediction
        data_aux = []
        x_ = []
        y_ = []
        
        # Get coordinates
        for i in range(len(hand_landmarks.landmark)):
            x = hand_landmarks.landmark[i].x
            y = hand_landmarks.landmark[i].y
            x_.append(x)
            y_.append(y)
        
        # Normalize and collect features
        for i in range(len(hand_landmarks.landmark)):
            x = hand_landmarks.landmark[i].x
            y = hand_landmarks.landmark[i].y
            data_aux.append(x - min(x_))
            data_aux.append(y - min(y_))
        
        # Make prediction
        try:
            prediction = model.predict([np.asarray(data_aux)])
            # The prediction is already a string letter, no need for conversion
            predicted_character = prediction[0]
            
            # Draw bounding box
            x1 = int(min(x_) * W) - 10
            y1 = int(min(y_) * H) - 10
            x2 = int(max(x_) * W) - 10
            y2 = int(max(y_) * H) - 10
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 4)
            cv2.putText(frame, predicted_character, (x1, y1 - 10), 
                      cv2.FONT_HERSHEY_SIMPLEX, 1.3, box_color, 3, cv2.LINE_AA)
        except Exception as e:
            print(f"Prediction error: {e}")
    
    cv2.imshow('ASL Alphabet Detector', frame)
    
    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()