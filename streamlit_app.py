import streamlit as st
from streamlit_drawable_canvas import st_canvas
import openai
from datetime import datetime

# Set OpenAI API key
openai.api_key = st.secrets.get("openai_api_key", None)

# Sidebar: Participant Information and Self-Assessments
st.sidebar.title("Participant Information")
participant_id = st.sidebar.text_input("Participant ID")
age = st.sidebar.number_input("Age", min_value=13, max_value=100)
gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
field_of_study = st.sidebar.text_input("Field of Study")
gpa = st.sidebar.number_input("GPA", min_value=0.0, max_value=4.0, step=0.01)

st.sidebar.title("Self-Assessments")
creative_mood = st.sidebar.slider("Current Creative Mood", 1, 10, 5)
current_mood = st.sidebar.slider("Current Mood", 1, 10, 5)
artistic_experience = st.sidebar.selectbox(
    "Artistic Experience", ["No experience", "Beginner", "Intermediate", "Advanced"]
)

# Main Panel: Instructions and Drawing Task
st.title("Visual Creativity Study")
st.write("Create a drawing based on the following prompts:")

# Generate or select prompts
prompts = ["transformation", "balance", "motion"]
st.write(f"**Prompts:** {', '.join(prompts)}")

# Initialize session state for AI interactions
if "ai_interactions" not in st.session_state:
    st.session_state.ai_interactions = []

# First Drawing Canvas
st.subheader("Your Drawing")
canvas_result1 = st_canvas(
    fill_color="rgba(255, 255, 255, 1)",
    stroke_width=3,
    stroke_color="#000000",
    background_color="#FFFFFF",
    width=600,
    height=400,
    drawing_mode="freedraw",
    key="canvas1",
)

# Button to indicate when the first drawing is done
if st.button("Done", key="done_button1"):
    if canvas_result1.image_data is not None:
        st.write("Here's your drawing:")
        st.image(canvas_result1.image_data)  # Display the drawing

        # Store the image data and mark drawing as done
        st.session_state["user_drawing1"] = canvas_result1.image_data
        st.session_state["drawing_done1"] = True
    else:
        st.write("Please draw something on the canvas to proceed.")

# If the first drawing is done, prompt for caption
if st.session_state.get("drawing_done1", False):
    caption1 = st.text_input("Enter a caption for your drawing:", key="caption_input1")

    # Add a submit button for the caption
    if st.button("Submit Caption", key="submit_caption_button1"):
        if caption1:
            # Store the caption and mark caption as submitted
            st.session_state["caption1"] = caption1
            st.session_state["caption_submitted1"] = True
        else:
            st.warning("Please enter a caption before submitting.")

# After the first caption is submitted, show inspiration options
if st.session_state.get("caption_submitted1", False):
    st.markdown("---")  # Add a divider
    st.write("Need some inspiration?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Get Inspiration", key="get_inspiration_button"):
            # AI generates a verbal prompt based on the caption
            def generate_ai_prompt(caption):
                prompt_text = f"Provide a creative suggestion for a drawing based on this caption: '{caption}'."
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt_text}],
                    max_tokens=50,
                    temperature=0.7,
                )
                ai_prompt = response["choices"][0]["message"]["content"].strip()
                return ai_prompt

            ai_prompt = generate_ai_prompt(st.session_state["caption1"])
            st.write(f"**AI Inspiration:** {ai_prompt}")
            st.session_state.ai_interactions.append({"type": "verbal_prompt", "content": ai_prompt})
    with col2:
        if st.button("Get Visual Inspiration", key="get_visual_inspiration_button"):
            # AI generates an image using DALL·E based on the caption
            def generate_ai_image(caption):
                prompt = f"{caption}"
                response = openai.Image.create(
                    prompt=prompt,
                    n=1,
                    size="512x512"
                )
                image_url = response["data"][0]["url"]
                return image_url

            ai_image_url = generate_ai_image(st.session_state["caption1"])
            if ai_image_url:
                st.image(ai_image_url, caption="AI-Generated Inspiration")
                st.session_state.ai_interactions.append({"type": "visual_prompt", "content": ai_image_url})
            else:
                st.error("Failed to generate AI image.")

    # Second Drawing Canvas
    st.subheader("Your Second Drawing")
    canvas_result2 = st_canvas(
        fill_color="rgba(255, 255, 255, 1)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#FFFFFF",
        width=600,
        height=400,
        drawing_mode="freedraw",
        key="canvas2",
    )

    # Button to indicate when the second drawing is done
    if st.button("Done", key="done_button2"):
        if canvas_result2.image_data is not None:
            st.write("Here's your second drawing:")
            st.image(canvas_result2.image_data)  # Display the drawing

            # Store the image data and mark drawing as done
            st.session_state["user_drawing2"] = canvas_result2.image_data
            st.session_state["drawing_done2"] = True
        else:
            st.write("Please draw something on the canvas to proceed.")

    # If the second drawing is done, prompt for caption
    if st.session_state.get("drawing_done2", False):
        caption2 = st.text_input("Enter a caption for your second drawing:", key="caption_input2")

        # Add a submit button for the caption
        if st.button("Submit Caption", key="submit_caption_button2"):
            if caption2:
                # Store the caption and mark caption as submitted
                st.session_state["caption2"] = caption2
                st.session_state["caption_submitted2"] = True
            else:
                st.warning("Please enter a caption before submitting.")

# Final Submission
if st.session_state.get("caption_submitted2", False):
    st.sidebar.title("Final Self-Assessments")
    self_assessed_creativity = st.sidebar.slider("Rate your overall creativity", 1, 10, 5)
    satisfaction_level = st.sidebar.slider("How satisfied are you with your drawings?", 1, 10, 5)
    ai_influence = st.sidebar.slider("How much did AI influence your work?", 1, 10, 1)

    if st.button("Submit All Responses"):
        # Collect all data
        data = {
            "participant_id": participant_id,
            "age": age,
            "gender": gender,
            "field_of_study": field_of_study,
            "gpa": gpa,
            "creative_mood": creative_mood,
            "current_mood": current_mood,
            "artistic_experience": artistic_experience,
            "drawing1": st.session_state.get("user_drawing1"),
            "caption1": st.session_state.get("caption1"),
            "drawing2": st.session_state.get("user_drawing2"),
            "caption2": st.session_state.get("caption2"),
            "ai_interactions": st.session_state.ai_interactions,
            "self_assessed_creativity": self_assessed_creativity,
            "satisfaction_level": satisfaction_level,
            "ai_influence": ai_influence,
            "submission_time": datetime.now(),
        }

        # Save 'data' to a database or file
        # For example:
        # save_data_to_database(data)
        st.success("Thank you for your participation!")
