import streamlit as st
from streamlit_drawable_canvas import st_canvas
import openai
from datetime import datetime
from PIL import Image
import numpy as np
import tempfile
import os  # Needed for checking file existence
import pandas as pd  # For saving data

# Set OpenAI API key
openai.api_key = st.secrets.get("openai_api_key", None)

# Consent Page
if "consent_given" not in st.session_state:
    st.title("Consent to Participate")
    st.write("Please read the consent information carefully before participating in this study...")
    st.write("By clicking 'I Agree', you consent to participate in this study voluntarily. You understand the study involves drawing tasks and providing feedback on creative activities.")
    
    if st.button("I Agree"):
        st.session_state["consent_given"] = True
        st.success("Please fill in the information below!")
    else:
        st.stop()

# Participant Information Page
if "consent_given" in st.session_state and "participant_info_collected" not in st.session_state:
    st.header("Participant Information")
    participant_id = st.text_input("Participant ID")
    age = st.number_input("Age", min_value=18, max_value=100)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    
    st.header("Self-Assessments")
    current_mood = st.slider("Current Mood", 1, 10, 5)
    artistic_experience = st.selectbox(
        "Artistic Experience", ["No experience", "Beginner", "Intermediate", "Advanced"]
    )

    if st.button("Proceed to Instructions"):
        if participant_id:
            st.session_state["participant_info_collected"] = True
            st.session_state.update({
                "participant_id": participant_id,
                "age": age,
                "gender": gender,
                "current_mood": current_mood,
                "artistic_experience": artistic_experience
            })
            st.success("Participant information recorded. Proceeding to instructions...")
        else:
            st.warning("Please complete all required fields.")

# Randomly assign participants based on participant ID
if "participant_info_collected" in st.session_state and "group_assigned" not in st.session_state:
    try:
        participant_id_num = int(st.session_state["participant_id"])
        if participant_id_num % 2 == 0:
            st.session_state["group"] = "visual"
            st.info("You have been assigned to the Visual Inspiration group.")
        else:
            st.session_state["group"] = "verbal"
            st.info("You have been assigned to the Verbal Inspiration group.")
        st.session_state["group_assigned"] = True
    except ValueError:
        st.warning("Please ensure the Participant ID is a valid number.")

# Instructions Page
if st.session_state.get("participant_info_collected", False) and "instructions_displayed" not in st.session_state:
    st.title("Instructions")
    st.write("Please read the following instructions carefully before proceeding to the study tasks...")
    st.write("You will be asked to draw based on given prompts and may receive feedback or inspiration for your creativity.")
    # Add any other instructions here

    if st.button("Proceed to Study"):
        st.session_state["instructions_displayed"] = True

if st.session_state.get("instructions_displayed", False):
    st.write("Create a drawing based on the following prompts:")
    prompts = ["transformation", "balance", "motion"]
    st.write(f"**Prompts:** {', '.join(prompts)}")

    # Initialize session state for AI interactions
    if "ai_interactions" not in st.session_state:
        st.session_state.ai_interactions = []

    # First Drawing Canvas
    st.subheader("Your First Drawing")
    canvas_result1 = st_canvas(
        fill_color="rgba(255, 255, 255, 1)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#FFFFFF",
        width=600,
        height=400,
        drawing_mode="freedraw",
        display_toolbar=True,
        key="canvas1",
    )

    # Button to indicate when the first drawing is done
    if st.button("Done with First Drawing", key="done_button1"):
        if canvas_result1.image_data is not None:
            st.write("Here's your drawing:")
            st.image(canvas_result1.image_data)  # Display the drawing

            # Convert image data to PIL Image
            img = Image.fromarray(canvas_result1.image_data.astype('uint8'), 'RGBA')
            # Save image to a file
            img.save(f"participant_{st.session_state['participant_id']}_drawing1.png")

            # Store the image data and mark drawing as done
            st.session_state["user_drawing1"] = canvas_result1.image_data
            st.session_state["drawing_done1"] = True
        else:
            st.warning("Please draw something on the canvas before clicking 'Done'.")

    # If the first drawing is done, prompt for caption
    if st.session_state.get("drawing_done1", False):
        caption1 = st.text_input("Enter a caption for your drawing:", key="caption_input1")

        # Add a submit button for the caption
        if st.button("Submit Caption", key="submit_caption_button1"):
            if caption1:
                # Store the caption and mark caption as submitted
                st.session_state["caption1"] = caption1
                st.session_state["caption_submitted1"] = True
                st.success("Response submitted")
            else:
                st.warning("Please enter a caption before submitting.")

    # Display the appropriate inspiration button based on the assigned group
    if st.session_state.get("caption_submitted1", False):
        st.markdown("---")  # Add a divider
        st.write("Need some inspiration?")
        
        group = st.session_state.get("group", None)
        
        if group == "verbal":
            if st.button("Get Verbal Inspiration", key="get_verbal_inspiration_button"):
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
        elif group == "visual":
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
        else:
            st.warning("Group assignment not found. Please ensure you have entered a valid Participant ID.")

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
        if st.button("Done with Second Drawing", key="done_button2"):
            if canvas_result2.image_data is not None:
                st.write("Here's your second drawing:")
                st.image(canvas_result2.image_data)  # Display the drawing

                # Convert image data to PIL Image
                img = Image.fromarray(canvas_result2.image_data.astype('uint8'), 'RGBA')
                # Save image to a file
                img.save(f"participant_{st.session_state['participant_id']}_drawing2.png")

                # Store the image data and mark drawing as done
                st.session_state["user_drawing2"] = canvas_result2.image_data
                st.session_state["drawing_done2"] = True
            else:
                st.warning("Please draw something on the canvas before clicking 'Done'.")

        # If the second drawing is done, prompt for caption
        if st.session_state.get("drawing_done2", False):
            caption2 = st.text_input("Enter a caption for your second drawing:", key="caption_input2")

            # Add a submit button for the caption
            if st.button("Submit Caption", key="submit_caption_button2"):
                if caption2:
                    # Store the caption and mark caption as submitted
                    st.session_state["caption2"] = caption2
                    st.session_state["caption_submitted2"] = True
                    st.success("Response submitted")
                else:
                    st.warning("Please enter a caption before submitting.")

# Final Submission
if st.session_state.get("caption_submitted2", False):
    st.header("Final Self-Assessments")
    self_assessed_creativity = st.slider("Rate your overall creativity", 1, 10, 5)
    satisfaction_level = st.slider("How satisfied are you with your drawings?", 1, 10, 5)
    ai_influence = st.slider("How much did AI influence your work?", 1, 10, 1)

    if st.button("Submit All Responses"):
        # Collect all data
        data = {
            "participant_id": st.session_state.get("participant_id"),
            "age": st.session_state.get("age"),
            "gender": st.session_state.get("gender"),
            "current_mood": st.session_state.get("current_mood"),
            "artistic_experience": st.session_state.get("artistic_experience"),
            "drawing1": f"participant_{st.session_state.get('participant_id')}_drawing1.png",
            "caption1": st.session_state.get("caption1"),
            "drawing2": f"participant_{st.session_state.get('participant_id')}_drawing2.png",
            "caption2": st.session_state.get("caption2"),
            "ai_interactions": st.session_state.get("ai_interactions"),
            "self_assessed_creativity": self_assessed_creativity,
            "satisfaction_level": satisfaction_level,
            "ai_influence": ai_influence,
            "submission_time": datetime.now(),
        }

        # Save 'data' to a database or file
        # For example, save to a CSV file
        df = pd.DataFrame([data])
        df.to_csv("participant_data.csv", mode='a', header=not os.path.exists("participant_data.csv"), index=False)

        st.success("Thank you for your participation!")
