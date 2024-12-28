from PIL import Image

try:
    import streamlit as st
except ModuleNotFoundError:
    raise ModuleNotFoundError("The 'streamlit' module is not installed. Install it using 'pip install streamlit'.")

try:
    import google.generativeai as genai
except ModuleNotFoundError:
    raise ModuleNotFoundError("The 'google-generativeai' module is not installed. Install it using 'pip install google-generativeai'.")

from configs import SYSTEM_PROMPT, SAFETY_SETTINGS, GENERATION_CONFIG, MODEL_NAME

if __name__ == '__main__':
    # Configure Model
    try:
        genai.configure(api_key='AIzaSyCxzwGFFA1KWWunEB3PrfruOhXHROSvVkE')  # Check https://github.com/google-gemini/cookbook
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            safety_settings=SAFETY_SETTINGS,
            generation_config=GENERATION_CONFIG,
            system_instruction=SYSTEM_PROMPT
        )
    except Exception as e:
        raise RuntimeError(f"Failed to configure the Generative AI model: {e}")

    # Setup Page
    # Head
    st.set_page_config(page_title='Blood Report AI Analyzer')
    st.title('Blood Report AI Analyzer')
    st.subheader('Analyzing blood reports using AI.')

    # Body
    col1, col2 = st.columns([1, 5])
    submit_btn = col1.button('ANALYZE', use_container_width=True)
    uploaded_file = col2.file_uploader('Upload Blood Report Image:', type=['png', 'jpg', 'jpeg'], accept_multiple_files=False)
    col3, col4 = st.columns(2)
    if uploaded_file:
        try:
            image_data = Image.open(uploaded_file)
            col3.image(image_data, use_column_width=True)  # Display Image
            message = col4.chat_message("Model:")
        except Exception as e:
            st.error(f"Failed to process the uploaded image: {e}")

    if submit_btn:
        # Analyze uploaded image
        try:
            history = st.session_state['history'] if 'history' in st.session_state else []

            content = [
                "Analyze this blood report image for insights such as abnormalities, metrics, or potential issues.",
                image_data
            ]

            history.append({
                "role": "user",
                "parts": content,
            })

            chat_session = model.start_chat()
            response = chat_session.send_message(content)

            # Check if the response indicates a mismatch
            if "blood report" in response.text.lower():
                message.write("The system detected an image mismatch. This AI model is trained for blood report analysis, Please upload a valid blood report.")
            else:
                message.write(response.text)

            st.session_state['history'] = chat_session.history
        except Exception as e:
            st.error(f"Failed to analyze the image: {e}")
