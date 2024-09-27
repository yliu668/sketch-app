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
    # Define eight key themes and associated words
    themes = {
         "Nature": ["tree", "flower", "waterfall", "butterfly"],
        "Technology": ["smartphone", "robot", "drone", "camera"],
        "Space": ["rocket", "moon", "astronaut", "satellite"],
        "Art": ["paintbrush", "palette", "easel", "sculpture"],
        "Architecture": ["castle", "lighthouse", "bridge", "pagoda"],
        "Music": ["guitar", "piano", "microphone", "violin"],
        "History": ["pyramid", "knight", "ancient ship", "chariot"],
         "Adventure": ["compass", "treasure map", "jungle", "cave"]
    }

    # Select three random keywords from the eight themes and store them in session state
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

# Function to interact with OpenAI's ChatCompletion API for feedback
def get_feedback_from_gpt(description):
    prompt = f"Evaluate this drawing inspired by the words {', '.join(st.session_state.selected_words)}. Provide constructive feedback."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Button to indicate when the drawing is done
if st.button("Done"):
    if canvas_result.image_data is not None:
        st.write("Here's your drawing:")
        st.image(canvas_result.image_data)  # Display the drawing

        # Example description (you could add image analysis here in future)
        drawing_description = f"Drawing based on the words {', '.join(st.session_state.selected_words)}."

        # Send the description to OpenAI for feedback
        feedback = get_feedback_from_gpt(drawing_description)

        # Display feedback
        if feedback:
            st.write("ChatGPT's Feedback on your drawing:")
            st.write(feedback)
    else:
        st.write("Please draw something on the canvas to get feedback.")
