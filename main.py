#please make sure to install streamlit and openai to run
import streamlit as st
import openai
from openai import OpenAI
import re

openai.api_key = "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"

def trim_content(input_str):
    # Find the starting index of "content="
    start_index = input_str.find("content=")
    
    # Find the ending index of "role='assistant'"
    end_index = input_str.find("role='assistant'")
    
    # If both substrings are found
    if start_index != -1 and end_index != -1:
        # Adjust start_index to the end of "content=" to exclude it
        start_index += len("content=")
        
        # Keep end_index as the start of "role='assistant'" to exclude it
        # Extract the substring between "content=" and "role='assistant'"
        trimmed_str = input_str[start_index:end_index].strip()
    else:
        # If the necessary substrings aren't found, return the original string or a custom message
        trimmed_str = input_str  # or "Required patterns not found"
        
    #formatted_str = trimmed_str.replace("\n", "<br>")
    return trimmed_str

def newline_content(input_str):
    # Replace newlines with HTML line breaks
    formatted_str = input_str.replace("\n", "<br>")
    return formatted_str

def extract_content(choice):
    # Assuming the 'text' attribute contains the response text you want to process
    response_text = choice.text if hasattr(choice, 'text') else str(choice)

    # Define the regular expression pattern to capture the content between 'content="' and '", role='assistant''
    pattern = r'content="(.*?)", role=\'assistant\''

    # Search the string using the defined pattern
    match = re.search(pattern, response_text)

    # If a match is found, return the captured content; otherwise, return an empty string
    if match:
        return match.group(1)
    else:
        return ""
    
def extract_content2(choice):
    # Assuming the 'text' attribute contains the response text you want to process
    response_text = choice.text if hasattr(choice, 'text') else str(choice)

    # Define the regular expression pattern to capture the content between 'content="' and '", role='assistant''
    pattern = r'content="(.*?)", role=\'assistant\''

    # Search the string using the defined pattern
    match = re.search(pattern, response_text)

    # If a match is found, return the captured content; otherwise, return an empty string
    if match:
        return match.group(1)
    else:
        return ""

def extract_content3(choice):
    # Assuming the 'text' attribute contains the response text you want to process
    response_text = choice.text if hasattr(choice, 'text') else str(choice)

    # Define the regular expression pattern to capture the content between 'content="' and '", role='assistant''
    pattern = r'content="(.*?)", role=\'assistant\''

    # Search the string using the defined pattern
    match = re.search(pattern, response_text)

    # If a match is found, return the captured content; otherwise, return an empty string
    if match:
        return match.group(1)
    else:
        return ""

def recommend_garden_design(image_url, preferences):
    client = openai.OpenAI(api_key=openai.api_key)

    # First GPT instance for garden design recommendation
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that recommends garden design ideas based on a provided photo and aesthetic preferences."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Here are my aesthetic preferences: {preferences}"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    },
                    {"type": "text", "text": "Please recommend garden design ideas based on the provided photo and my aesthetic preferences."}
                ],
            }
        ],
        max_tokens=300,
    )

   # first_gpt_output = extract_content(response.choices[0])
    first_gpt_output = response.choices[0]

    # Second GPT instance for aesthetic feedback
    feedback_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an AI specialized in providing aesthetic feedback on garden designs. Consider the design ideas and the image provided and give your feedback."
            },
            {
                "role": "user",
                "content": f"The proposed garden design ideas are: {first_gpt_output} Based on the image at {image_url}, how can these ideas be improved aesthetically?"
            }
        ],
        max_tokens=150,
    )

    #feedback = extract_content(feedback_response.choices[0])
    feedback = feedback_response.choices[0]
    refined_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an AI that refines garden design ideas by incorporating feedback. Use the original design ideas and the feedback provided to enhance the garden design."
            },
            {
                "role": "user",
                "content": f"Original garden design ideas: {first_gpt_output} Feedback: {feedback} Please refine the original design ideas based on this feedback and the photo at {image_url}."
            }
        ],
        max_tokens=300,
    )
    refined_design = refined_response.choices[0]
    refined_design = newline_content(trim_content(str(refined_design)))
    feedback = newline_content(trim_content(str(feedback_response.choices[0])))
    first_gpt_output = newline_content(trim_content(str(response.choices[0])))
    #refined_design = extract_content(refined_response.choices[0])
    #feedback = extract_content2(feedback_response.choices[0])
    #first_gpt_output = extract_content3(response.choices[0])
    #refined_design = refined_response.choices[0]
    return first_gpt_output, feedback, refined_design


def query_home_depot_database_assistant(initial_recommendation, feedback, refined_recommendation, assistant_id):
    from openai import OpenAI  # Import OpenAI here to ensure the client is initialized locally

    # Initialize the OpenAI client with your API key
    client = OpenAI(api_key="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")

    # Step 1: Create a Thread for the conversation
    thread = client.beta.threads.create()

    # Step 2: Add the user's message to the Thread
    # Combine the initial recommendation, feedback, and refined recommendation into one message for simplicity
    user_message_content = f"Initial Recommendation: {initial_recommendation} Feedback: {feedback} Refined Recommendation: {refined_recommendation} Can you provide further insights or product recommendations?"
    user_message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message_content
    )

    # Step 3: Create a Run and retrieve the response
    # For simplicity, we'll use the blocking version without streaming in this example
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
        instructions="Provide insights on garden designs and products."
    )

    # Step 4: List the messages in the thread after the run is completed
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        # Extract the assistant's response from the messages
        assistant_response = None
        for message in messages:
            if message.role == 'assistant':
                assistant_response = message.content
                break
        
        if assistant_response:
            # Process the assistant's response for display in Streamlit
            assistant_response_processed = newline_content(trim_content(assistant_response))
            return assistant_response_processed
        else:
            return "No assistant response found in the messages."
    else:
        return "The run did not complete successfully."

st.title("Garden Design Recommendation and Feedback")

# Input for image URL instead of uploading an image
image_url = st.text_input("Enter the image URL:")

preferences = st.text_input("Enter your aesthetic preferences:")
wait_message = st.empty()

# Modify your Streamlit app to include querying the HomeDepotDatabaseAssistant
if st.button("Recommend Garden Design and Refine with Feedback"):
    wait_message.text("Processing your request, this may take a while. Please wait...")

    if image_url and preferences:
        recommendation, feedback, refined_recommendation = recommend_garden_design(image_url, preferences)
        
        # Query HomeDepotDatabaseAssistant
        home_depot_insights = query_home_depot_database_assistant(recommendation, feedback, refined_recommendation,"asst_kvtvo95iEPGVxF75cQS4V9mz")

        # Clear the wait message after processing
        wait_message.empty()

        st.markdown("### Initial Garden Design Recommendation:")
        st.markdown(f"> {recommendation}")
        
        st.markdown("### Aesthetic Feedback:")
        st.markdown(f"> {feedback}")
        
        st.markdown("### Refined Garden Design Recommendation:")
        st.markdown(f"> {refined_recommendation}")

        # Display the insights from HomeDepotDatabaseAssistant
        st.markdown("### Insights from HomeDepotDatabaseAssistant:")
        st.markdown(f"> {home_depot_insights}")
    else:
        # Clear the wait message if inputs are missing and show a warning instead
        wait_message.empty()
        st.warning("Please enter both the image URL and your aesthetic preferences.")
