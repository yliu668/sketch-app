import streamlit as st
from streamlit_drawable_canvas import st_canvas
import random
import openai

# Allow users to input their OpenAI API key
st.sidebar.title("Participant number")

# Access OpenAI API key from secrets
openai.api_key = st.secrets["openai_api_key"]

# Initialize the session state to store the inspiration words
if 'selected_words' not in st.session_state:
    # Define eight key themes and associated words
    themes = {
        "Nature": ["forest", "river", "mountain", "sun"],
        "Technology": ["robot", "AI", "computer", "internet"],
        "Space": ["planet", "galaxy", "star", "astronaut"],
        "Art": ["painting", "sculpture", "abstract", "canvas"],
        "Architecture": ["building", "bridge", "skyscraper", "monument"],
        "Music": ["melody", "instrument", "rhythm", "harmony"],
        "History": ["pyramid", "ancient", "renaissance", "medieval"],
        "Adventure": ["exploration", "journey", "treasure", "wild"]
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

# Function to interact with OpenAI's ChatCompletion API
def get_feedback_from_gpt(description):
    prompt = f"Evaluate this drawing inspired by the words {', '.join(st.session_state.selected_words)}. Provide constructive feedback."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an art evaluator."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message['content']

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
        st.write("ChatGPT's Feedback on your drawing:")
        st.write(feedback)

    else:
        st.write("Please draw something on the canvas to get feedback.")
