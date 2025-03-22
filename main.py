import cv2
import numpy as np
from pyzbar.pyzbar import decode

def preprocess_image(image):
    """Enhances barcode visibility using grayscale, thresholding, and sharpening."""cvb n 
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    
    # Increase contrast
    alpha = 1.5  # Contrast control
    beta = 10    # Brightness control
    contrast_img = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)

    # Adaptive thresholding to binarize the image
    binary = cv2.adaptiveThreshold(contrast_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    
    # Sharpen the image using kernel filter
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])  # Sharpening kernel
    sharp = cv2.filter2D(binary, -1, kernel)
    
    return sharp

def scan_barcode():
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        processed_frame = preprocess_image(frame)
        decoded_objects = decode(processed_frame)

        for obj in decoded_objects:
            barcode_data = obj.data.decode("utf-8")
            print(f"Scanned Barcode: {barcode_data}")
            
            # Draw bounding box
            points = obj.polygon
            if len(points) == 4:
                pts = np.array(points, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 2)

            cap.release()
            return barcode_data
        
        cv2.imshow("Barcode Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

barcode_result = scan_barcode()
print(f"Medicine Barcode: {barcode_result}")
