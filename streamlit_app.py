import streamlit as st
from streamlit_drawable_canvas import st_canvas
import random
import openai

# Access OpenAI API key from secrets
OPENAI_API_KEY = st.secrets.get("openai_api_key", None)
if OPENAI_API_KEY is None:
    st.error("OpenAI API key not found. Please set it in Streamlit secrets.")
else:
    openai.api_key = OPENAI_API_KEY

# Sidebar for participant information
st.sidebar.title("Participant Information")
participant_number = st.sidebar.text_input("Participant Number")
gender = st.sidebar.selectbox("Select Gender", ["Male", "Female", "Other"])
if st.sidebar.button("Submit"):
    st.session_state["participant_info"] = {
        "number": participant_number,
        "gender": gender
    }
    st.sidebar.success("Information saved!")

# Initialize the session state to store the inspiration words
if 'selected_words' not in st.session_state:
    # Define key themes and associated words
    themes = {
        "Nature": ["tree", "flower", "waterfall", "butterfly"],
        "Technology": ["smartphone", "robot", "computer", "camera"],
        "Adventure": ["compass", "treasure map", "jungle", "cave"]
    }

    # Select three random keywords from the themes and store them in session state
    selected_words = []
    for theme in random.sample(list(themes.keys()), 3):  # Pick 3 random themes
        selected_words.append(random.choice(themes[theme]))  # Pick 1 word from each selected theme
    st.session_state.selected_words = selected_words

# Display the selected inspiration words
st.title("🎨 Leverage your imagination with AI feedback")
st.write("Draw something inspired by the following words:")
st.write(f"Inspiration Words: {', '.join(st.session_state.selected_words)}")

# Hint button to generate feedback based on the inspiring words
if st.button("Hint"):
    def get_hint_from_gpt():
        prompt = f"Provide a creative hint or suggestion for a drawing based on the words: {', '.join(st.session_state.selected_words)}."
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.7,
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return None

    hint = get_hint_from_gpt()
    if hint:
        st.write("Here's a hint to inspire your creativity:")
        st.write(hint)

# Sidebar creativity slider
add_slider = st.sidebar.slider(
    'How creative do you feel at the moment?',
    0.0, 100.0, 50.0
)

# Initialize session state variables for drawing and caption
if 'drawing_done' not in st.session_state:
    st.session_state['drawing_done'] = False
if 'caption_submitted' not in st.session_state:
    st.session_state['caption_submitted'] = False

# Canvas for drawing
st.subheader("Draw something below:")
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",  # Color for the brush
    stroke_width=2,
    stroke_color="#000000",
    background_color="#FFFFFF",
    width=500,
    height=300,
    drawing_mode="freedraw",
    key="canvas",
)

# Button to indicate when the drawing is done
if st.button("Done", key='done_button'):
    if canvas_result.image_data is not None:
        st.write("Here's your drawing:")
        st.image(canvas_result.image_data)  # Display the drawing

        # Store the image data and mark drawing as done
        st.session_state['user_drawing'] = canvas_result.image_data
        st.session_state['drawing_done'] = True
    else:
        st.write("Please draw something on the canvas to proceed.")

# If the drawing is done, prompt for caption
if st.session_state.get('drawing_done', False):
    caption = st.text_input("Enter a caption for your drawing:", key='caption_input')

    # Add a submit button for the caption
    if st.button("Submit Caption", key='submit_caption_button'):
        if caption:
            # Store the caption and mark caption as submitted
            st.session_state['caption'] = caption
            st.session_state['caption_submitted'] = True
        else:
            st.warning("Please enter a caption before submitting.")

# If the caption is submitted, generate an image using DALL·E
if st.session_state.get('caption_submitted', False):
    # Function to generate an image using DALL·E
    def get_image_from_dalle(prompt):
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="512x512"
            )
            image_url = response['data'][0]['url']
            return image_url
        except Exception as e:
            st.error(f"An error occurred while generating the image: {e}")
            return None

    # Use the caption as the prompt for DALL·E
    prompt = st.session_state['caption']

    st.write("Generating an AI image based on your caption...")
    generated_image_url = get_image_from_dalle(prompt)

    if generated_image_url:
        st.write("Here's an AI-generated image based on your caption:")
        st.image(generated_image_url)
    else:
        st.write("Failed to generate an image.")
