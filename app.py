import streamlit as st
import requests
import json
from io import BytesIO
import base64
from datetime import datetime
import time
import uuid
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# Configure Streamlit page
st.set_page_config(
    page_title="BrainScan AI - Brain Tumor Detection",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


API_BASE_URL = "http://localhost:8000"


st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f4788;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .section-header {
        color: #2e5c8a;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding: 0.5rem 0;
        border-bottom: 2px solid #e0e0e0;
    }
    .stAlert {
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None

def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def make_prediction(file, patient_data):
    try:
        
        file.seek(0)
        file_content = file.read()
        
        
        file_name = file.name.lower()
        if file_name.endswith(('.png', '.PNG')):
            content_type = 'image/png'
        elif file_name.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
            content_type = 'image/jpeg'
        elif file_name.endswith(('.tiff', '.tif', '.TIFF', '.TIF')):
            content_type = 'image/tiff'
        else:
            content_type = 'image/png'  
        
        # Debug information (remove this after testing)
        st.write(f"🔍 Debug - File: {file.name}, Type: {content_type}, Size: {len(file_content)} bytes")
        
        
        files = {'file': (file.name, file_content, content_type)}
        data = {
            'name': patient_data['name'],
            'age': patient_data['age'],
            'gender': patient_data['gender'],
            'symptoms': patient_data['symptoms']
        }
        
        response = requests.post(
            f"{API_BASE_URL}/prediction",
            files=files,
            data=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Prediction failed: {response.text}")
            return None
    except requests.exceptions.Timeout:
        st.error("Request timeout. The server is taking too long to respond.")
        return None
    except Exception as e:
        st.error(f"Error making prediction: {str(e)}")
        return None

def download_report(filename):
    try:
        response = requests.get(f"{API_BASE_URL}/report/{filename}", timeout=30)
        if response.status_code == 200:
            return response.content
        else:
            st.error("Report not found")
            return None
    except Exception as e:
        st.error(f"Error downloading report: {str(e)}")
        return None

def send_chat_message(message):
    
    try:
        data = {
            'message': message,
            'session_id': st.session_state.session_id
        }
        
        response = requests.post(
            f"{API_BASE_URL}/chat",
            data=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()['bot_response']
        else:
            return "Sorry, I encountered an error. Please try again."
    except requests.exceptions.Timeout:
        return "The response is taking longer than expected. Please try again in a moment."
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    
    st.markdown('<h1 class="main-header">🧠 BrainScan AI - Brain Tumor Detection System</h1>', unsafe_allow_html=True)
    
    
    if not check_backend_health():
        st.markdown('<div class="error-box"> Backend server is not running. Please start the FastAPI server first.</div>', unsafe_allow_html=True)
        st.code("cd 'D:\\AI ML\\Brain Tumor Detection\\AI Based Brain tumor detection'\npython main.py", language="bash")
        return
    
    
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a feature:", ["🔬 Brain Tumor Analysis", "🤖 AI Medical Assistant"])
    
    if page == "🔬 Brain Tumor Analysis":
        brain_tumor_analysis()
    elif page == "🤖 AI Medical Assistant":
        chatbot_interface()

def brain_tumor_analysis():
    st.markdown('<h2 class="section-header">Brain Tumor Analysis</h2>', unsafe_allow_html=True)
    
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Patient Information")
        
        
        with st.form("patient_form"):
            name = st.text_input("Patient Name*", placeholder="Enter patient's full name")
            age = st.number_input("Age*", min_value=1, max_value=120, value=30)
            gender = st.selectbox("Gender*", ["male", "female", "other"])
            symptoms = st.text_area(
                "Symptoms", 
                placeholder="Describe any symptoms or medical history...",
                value="No specific symptoms reported"
            )
            
            st.markdown("### MRI Scan Upload")
            uploaded_file = st.file_uploader(
                "Upload Brain MRI Scan*",
                type=['png', 'jpg', 'jpeg', 'tiff'],
                help="Supported formats: PNG, JPG, JPEG, TIFF"
            )
            

            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded MRI Scan", use_container_width=True)
            
            submit_button = st.form_submit_button("🔬 Analyze Brain Scan", use_container_width=True)
        
        
        if submit_button:
            if not name or not uploaded_file:
                st.error("Please fill in all required fields (*) and upload an MRI scan.")
            else:
                
                allowed_extensions = ['png', 'jpg', 'jpeg', 'tiff', 'tif']
                file_extension = uploaded_file.name.split('.')[-1].lower()
                
                if file_extension not in allowed_extensions:
                    st.error(f"Unsupported file type: {file_extension}. Please upload PNG, JPG, JPEG, or TIFF files.")
                else:
                    patient_data = {
                        'name': name,
                        'age': age,
                        'gender': gender,
                        'symptoms': symptoms
                    }
                    
                    with st.spinner("🔄 Analyzing brain scan... This may take a moment."):
                        # Reset file pointer before sending
                        uploaded_file.seek(0)
                        result = make_prediction(uploaded_file, patient_data)
                    
                    if result:
                        st.session_state.prediction_result = result
                        st.success("✅ Analysis completed successfully!")
                        st.rerun()
    
    with col2:
        if st.session_state.prediction_result:
            display_results(st.session_state.prediction_result)

def display_results(result):
    st.markdown("### 📋 Analysis Results")
    
    # Prediction Summary with clean styling
    prediction = result['prediction'].replace('_', ' ').title()
    confidence = result['confidence'] * 100
    
    # Determine styling based on prediction
    if result['prediction'] == 'no_tumor':
        bg_color = "#d4edda"
        border_color = "#28a745"
        status_icon = "✅"
        text_color = "#155724"
    else:
        bg_color = "#f8d7da"
        border_color = "#dc3545"
        status_icon = "⚠️"
        text_color = "#721c24"
    
    # Main prediction display
    st.markdown(f"""
    <div style="padding: 1.5rem; border-radius: 0.8rem; background-color: {bg_color}; border: 2px solid {border_color}; margin: 1rem 0;">
        <h3 style="color: {text_color}; margin: 0 0 0.5rem 0; text-align: center;">
            {status_icon} Diagnosis: {prediction}
        </h3>
        <p style="text-align: center; font-size: 1.2rem; margin: 0.5rem 0; color: {text_color};">
            <strong>Confidence: {confidence:.1f}%</strong>
        </p>
        <p style="text-align: center; color: #666; margin: 0; font-size: 0.9rem;">
            Analysis completed: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for organized display
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Probability Breakdown")
        probabilities = result.get('probabilities', {})
        
        for condition, prob in probabilities.items():
            condition_name = condition.replace('_', ' ').title()
            prob_percent = prob * 100
            
            # Use Streamlit's built-in metric display
            st.metric(
                label=condition_name,
                value=f"{prob_percent:.1f}%",
                delta=None
            )
    
    with col2:
        st.markdown("#### 👤 Patient Information")
        patient = result.get('patient', {})
        
        # Clean patient info display
        st.write(f"**Name:** {patient.get('name', 'Unknown')}")
        st.write(f"**Age:** {patient.get('age', 'Unknown')} years")
        st.write(f"**Gender:** {patient.get('gender', 'Unknown').title()}")
        st.write(f"**Symptoms:** {patient.get('symptoms', 'Not specified')}")
    
    # Medical Report Section
    if result.get('report_filename'):
        st.markdown("---")
        st.markdown("#### 📄 Medical Report")
        
        # Download buttons in columns
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            if st.button("📥 Download PDF Report", use_container_width=True, type="primary"):
                with st.spinner("📄 Preparing report..."):
                    pdf_content = download_report(result['report_filename'])
                    
                    if pdf_content:
                        st.download_button(
                            label="💾 Save Report",
                            data=pdf_content,
                            file_name=result['report_filename'],
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.success("✅ Report ready for download!")
        
        with btn_col2:
            if st.button("🔄 New Analysis", use_container_width=True):
                st.session_state.prediction_result = None
                st.rerun()
        
        # Report preview
        if result.get('report_content'):
            with st.expander("� Preview Medical Report"):
                # Display clean report content
                report_lines = result['report_content'].split('\n')
                for line in report_lines:
                    if line.strip():
                        if any(header in line.upper() for header in ['CLINICAL', 'DESCRIPTION', 'PRECAUTIONS', 'RECOMMENDATIONS']):
                            st.markdown(f"**{line.strip()}**")
                        else:
                            st.write(line.strip())
    
    # Medical interpretation
    st.markdown("---")
    if result['prediction'] != 'no_tumor':
        st.info(f"""
        **⚕️ Medical Information:**
        
        The AI analysis detected signs consistent with **{prediction}** with {confidence:.1f}% confidence.
        
        **Important:** This is an AI screening tool. Please consult with a qualified neurologist 
        or medical professional for proper diagnosis and treatment.
        """)
    else:
        st.success(f"""
        **✅ Good News!**
        
        The AI analysis suggests no signs of brain tumor with {confidence:.1f}% confidence.
        
        **Note:** Regular medical check-ups are still recommended for optimal brain health.
        """)

def chatbot_interface():
    st.markdown('<h2 class="section-header">AI Medical Assistant</h2>', unsafe_allow_html=True)
    
    st.markdown("### 🤖 Ask me anything about brain tumors, symptoms, or medical information!")
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("#### 💬 Conversation History:")
        for i, (user_msg, bot_msg) in enumerate(st.session_state.chat_history):
            # User message
            with st.container():
                st.markdown(f"**You:** {user_msg}")
                st.markdown(f"**🤖 AI Medical Support:** {bot_msg}")
                st.markdown("---")
    
    # Chat input form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "Your Question:",
            placeholder="Ask about brain tumors, symptoms, treatments, or any medical questions...",
            help="Type your medical question here"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            send_button = st.form_submit_button("Send Message 💬", use_container_width=True, type="primary")
        with col2:
            clear_button = st.form_submit_button("Clear Chat 🗑️", use_container_width=True)
    
    if send_button and user_input:
        with st.spinner("🤖 AI is thinking..."):
            bot_response = send_chat_message(user_input)
            st.session_state.chat_history.append((user_input, bot_response))
            st.rerun()
    
    if clear_button:
        st.session_state.chat_history = []
        st.session_state.session_id = str(uuid.uuid4())
        st.success("✅ Chat history cleared!")
        st.rerun()
    
    # Quick questions section
    if not st.session_state.chat_history:
        st.markdown("#### 💡 Quick Start - Try These Questions:")
        suggestions = [
            "What are the symptoms of brain tumors?",
            "What's the difference between benign and malignant tumors?",
            "How accurate is this AI analysis?",
            "What should I do if a tumor is detected?",
            "What are the treatment options for brain tumors?"
        ]
        
        for i, suggestion in enumerate(suggestions):
            if st.button(f"💡 {suggestion}", key=f"suggestion_{i}"):
                with st.spinner("🤖 AI Doctor is thinking..."):
                    bot_response = send_chat_message(suggestion)
                    st.session_state.chat_history.append((suggestion, bot_response))
                    st.rerun()

# Information sidebar
with st.sidebar:
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    **BrainScan AI** is an advanced brain tumor detection system using:
    
    - 🤖 **AI Analysis**: Deep learning model for MRI scan analysis
    - 📊 **Medical Reports**: Comprehensive PDF reports
    - 💬 **AI Assistant**: Medical knowledge chatbot
    - 🔬 **4 Tumor Types**: Glioma, Meningioma, Pituitary, No Tumor
    """)
    
    st.markdown("---")
    st.markdown("### ⚠️ Medical Disclaimer")
    st.markdown("""
    This tool is for **screening purposes only**. 
    
    Always consult with qualified medical professionals for proper diagnosis and treatment.
    """)

if __name__ == "__main__":
    main()