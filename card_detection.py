# import streamlit as st
# import cv2
# import numpy as np
# import pytesseract
# import re
# from datetime import datetime

# # --- Tesseract Configuration ---
# # Ensure this path is correct for your system
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # --- Page Configuration ---
# st.set_page_config(page_title="Card Expiry Validator", page_icon="💳", layout="centered")

# st.title("💳 Credit Card Expiry OCR Validator")
# st.write("Upload an image of a credit card to extract and validate its expiry date.")

# # --- File Uploader ---
# uploaded_file = st.file_uploader("Choose a card image...", type=["jpg", "jpeg", "png"])

# if uploaded_file is not None:
#     # 1. Convert uploaded file into an OpenCV image
#     # Streamlit file uploaders return a file-like object; we convert it to bytes then to a numpy array for OpenCV
#     file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
#     img = cv2.imdecode(file_bytes, 1)
#     img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
#     # 2. Run Tesseract OCR with a loading spinner
#     with st.spinner("Analyzing image..."):
#         try:
#             data = pytesseract.image_to_data(img_rgb, output_type=pytesseract.Output.DICT)
#         except Exception as e:
#             st.error(f"Error running Tesseract. Is it installed correctly?\n\nDetails: {e}")
#             st.stop()

#         # 3. Process Data & Draw Bounding Boxes
#         n = len(data['text'])
#         expiry_text = None

#         for i in range(n):
#             text = data['text'][i].strip()
#             conf = float(data['conf'][i])

#             # Look for MM/YY pattern with confidence > 30
#             if conf > 30 and re.search(r'\b(0[1-9]|1[0-2])/\d{2}\b', text):
#                 expiry_text = text
                
#                 # Draw Rectangle
#                 x = int(data['left'][i])
#                 y = int(data['top'][i])
#                 w = int(data['width'][i])
#                 h = int(data['height'][i])
#                 cv2.rectangle(img_rgb, (x, y), (x + w, y + h), (0, 255, 0), 3)
                
#                 # Add label above rectangle
#                 cv2.putText(img_rgb, "Expiry", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
#                 break # Stop after finding the first valid expiry

#     # 4. Display Results
#     st.divider()
#     st.subheader("Validation Result")
    
#     if expiry_text is None:
#         st.warning("⚠️ Could not detect an expiry date on this image.")
#         st.image(img_rgb, caption="Original Image (No Date Detected)", use_container_width=True)
#     else:
#         try:
#             # Parse the detected date
#             month, year = expiry_text.split("/")
#             month = int(month)
#             year = int("20" + year)

#             today = datetime.now()

#             # Check logic
#             if today.year > year or (today.year == year and today.month > month):
#                 st.error(f"❌ Card EXPIRED on {expiry_text}")
#             else:
#                 months_left = (year - today.year) * 12 + (month - today.month)
#                 st.success(f"✅ Card VALID — ({months_left} months left)")
            
#             # Show processed image with bounding boxes
#             st.image(img_rgb, caption=f"Detected Expiry: {expiry_text}", use_container_width=True)
            
#         except Exception as e:
#             st.error(f"Error parsing the detected date: {e}")














import streamlit as st
import cv2
import numpy as np
import pytesseract
import re
from datetime import datetime

# --- Tesseract Configuration ---
# Ensure this path is correct for your system
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# --- Page Configuration ---
# Set to 'wide' to accommodate the side-by-side design from the mockup
st.set_page_config(page_title="Card Expiry Validator", page_icon="💳", layout="wide")

# --- Custom Theme CSS ---
st.markdown("""
<style>
    /* Dark slate background matching the image */
    .stApp {
        background-color: #212d33;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* Global Text Colors */
    p, span, label, div {
        color: #e2e8f0 !important;
    }
    
    /* Typography matching the mockup */
    h1 {
        font-size: 4.5rem !important;
        font-weight: 800 !important;
        line-height: 1.1 !important;
        color: #ffffff !important;
        padding-bottom: 0 !important;
        margin-bottom: 1.5rem !important;
        margin-top: 2rem !important;
    }
    
    .small-caps {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        font-weight: 600 !important;
        margin-bottom: -15px !important;
        display: block;
    }

    /* File Uploader - Frosted Glass Effect */
    [data-testid="stFileUploadDropzone"] {
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px);
        padding: 2rem !important;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        background: linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%) !important;
    }
    
    /* Status Alerts */
    [data-testid="stAlert"] {
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
        color: white !important;
    }

    /* Container for the image and results (right side) */
    .glass-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.01) 100%);
        border-radius: 24px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        backdrop-filter: blur(20px);
        margin-top: 2rem;
    }
    
    /* Hide top padding of Streamlit */
    .block-container {
        padding-top: 3rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Layout ---
# Using columns to create a "Hero Section" split view
col1, col2 = st.columns([1.1, 1], gap="large")

with col1:
    # Mimicking the text from the dark UI mockup
    st.markdown("<span class='small-caps'>VALIDATE YOUR CARDS</span>", unsafe_allow_html=True)
    st.markdown("<h1>Smart OCR<br>check your cards<br>expiry date.</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <p style='font-size: 1.1rem; color: #cbd5e1 !important; margin-bottom: 2rem;'>
        Upload an image of a credit card to securely extract<br>and validate its expiry date in seconds.
    </p>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload a card image to begin...", type=["jpg", "jpeg", "png"])

with col2:
    if uploaded_file is not None:
        # Wrap results in a custom glassmorphism container
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        
        # 1. Convert uploaded file into an OpenCV image
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 2. Run Tesseract OCR with a loading spinner
        with st.spinner("Analyzing image..."):
            try:
                data = pytesseract.image_to_data(img_rgb, output_type=pytesseract.Output.DICT)
            except Exception as e:
                st.error(f"Error running Tesseract. Is it installed correctly?\n\nDetails: {e}")
                st.stop()

            # 3. Process Data & Draw Bounding Boxes
            n = len(data['text'])
            expiry_text = None

            for i in range(n):
                text = data['text'][i].strip()
                conf = float(data['conf'][i])

                # Look for MM/YY pattern with confidence > 30
                if conf > 30 and re.search(r'\b(0[1-9]|1[0-2])/\d{2}\b', text):
                    expiry_text = text
                    
                    # Draw Rectangle
                    x = int(data['left'][i])
                    y = int(data['top'][i])
                    w = int(data['width'][i])
                    h = int(data['height'][i])
                    cv2.rectangle(img_rgb, (x, y), (x + w, y + h), (0, 255, 0), 3)
                    
                    # Add label above rectangle
                    cv2.putText(img_rgb, "Expiry", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    break # Stop after finding the first valid expiry

        # 4. Display Results
        if expiry_text is None:
            st.warning("⚠️ Could not detect an expiry date on this image.")
            st.image(img_rgb, caption="Original Image (No Date Detected)", use_container_width=True)
        else:
            try:
                # Parse the detected date
                month, year = expiry_text.split("/")
                month = int(month)
                year = int("20" + year)

                today = datetime.now()

                # Check logic
                if today.year > year or (today.year == year and today.month > month):
                    st.error(f"❌ Card EXPIRED on {expiry_text}")
                else:
                    months_left = (year - today.year) * 12 + (month - today.month)
                    st.success(f"✅ Card VALID — ({months_left} months left)")
                
                # Show processed image with bounding boxes
                st.image(img_rgb, caption=f"Detected Expiry: {expiry_text}", use_container_width=True)
                
            except Exception as e:
                st.error("Error parsing the detected date.")
                
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        # Show an empty placeholder glass card if no file is uploaded yet
        st.markdown("""
        <div class='glass-container' style='height: 450px; display: flex; align-items: center; justify-content: center; flex-direction: column; opacity: 0.5;'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>💳</div>
            <p style='color: #94a3b8 !important; font-size: 1.1rem; text-align: center;'>
                Card preview and validation results<br>will appear here.
            </p>
        </div>
        """, unsafe_allow_html=True)