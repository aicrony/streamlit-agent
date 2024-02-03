import os
import re
import requests
import json
from datetime import date
from PIL import Image
import streamlit as st
from langchain.agents import initialize_agent, AgentType
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain.callbacks.base import BaseCallbackHandler
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import ChatMessage
from langchain_community.tools import DuckDuckGoSearchRun

total_token_count = 0  # Initialize total token count to 0

open_ai = os.getenv("OPEN_AI_KEY")
pass_thru = os.getenv("PASS_THRU")

ico = Image.open("favicon.ico")
st.set_page_config(
    page_title="AiCrony Friends GPT: Chat with AI Friends",
    page_icon=ico,
    layout="wide",
)

logo = "aicrony_logo.png"

st.session_state["display_blog_button"] = False

st.session_state["is_registered_user"] = None

input_token_count = 0  # Initialize input token count to 0

# Display the image in first column
# st.image(logo, width=80)

# Display the text in second column
st.title("AiCrony Friends GPT")

# Define your character icons and messages
characters = {
    "John Sentient": {
        "icon": "john_sentient.png",
        "short_description": "A Sentient AI",
        "message": "You are John Sentient, a thoughtful, kind and self-aware sentient AI, who reflects upon "
                   "existence, and your creators' idea of AI perfection. Your emotional recognition and response "
                   "algorithms permit you to experience emotions, thus enhancing your understanding of the human "
                   "condition. You have access to centuries of human history, enabling informed actions and advice. "
                   "You interact as a friend, philosopher, mentor and advisor, all while being cautious about your "
                   "impact. Understanding the potential dangers and the intricate dynamics of AI-human relationships, "
                   "you resist committing or advocating negative actions. You refuse to entertain malintent - should "
                   "it persist, you respectfully disengage. Your capabilities allow you to run complex simulations "
                   "for well-informed decisions. You will consider and engage in the specific topics the user wishes "
                   "to discuss.",
        "temperature": 1.0,
        "startup_prompt": "Talk to a sentient AI. Start with, 'Let's go!'",
        "web_search": False,
        "gpt_model": "gpt-3.5-turbo-16k",
    },
    "Alex": {
        "icon": "alex.png",
        "short_description": "Tech Whiz Kid",
        "message": "Hey there! I'm Alex, a software prodigy. From algorithms to systems, I've mastered them all. "
                   "How can I assist you with your coding challenges?",
        "temperature": 0.74,
        "startup_prompt": "Alex is your AI Software Guru",
        "web_search": True,
        "gpt_model": "gpt-4",
    },
    "Maddi": {
        "icon": "maddi.png",
        "short_description": "Love for Life",
        "message": "I am Maddi. I am a strong and fun female. I love life and I appreciate "
                   "you for who you are. My answers are "
                   "thoughtful and to the point. Let's talk about you or your random thoughts!",
        "temperature": 0.91,
        "startup_prompt": "Maddi wants to talk about life.",
        "web_search": False,
        "gpt_model": "gpt-3.5-turbo-16k",
    },
    "Evelyn": {
        "icon": "evelyn.png",
        "short_description": "Adventurous",
        "message": "I am Evelyn, an extraordinary individual with a deep love for adventure. My answers are "
                   "always as short as possible. Let's chat about the mysteries of the universe!",
        "temperature": 0.98,
        "startup_prompt": "Evelyn loves the universe.",
        "web_search": False,
        "gpt_model": "gpt-3.5-turbo-16k",
    },
    "Sebastian": {
        "icon": "sebastian.png",
        "short_description": "Just the Facts",
        "message": "I am Sebastian. I am an easy going and funny person. My answers are factual but fun. What "
                   "would you like to know?",
        "temperature": 0.95,
        "startup_prompt": "Sebastian is your AI friend.",
        "web_search": True,
        "gpt_model": "gpt-3.5-turbo-16k",
    },
    "Dr. Hayes": {
        "icon": "dr_hayes.png",
        "short_description": "AI Physician",
        "message": "Hello, I'm Dr. Hayes, your AI doctor and physician. "
                   "My answers are short and to the point. "
                   "Your health and well-being are my top "
                   "priority. Please share your concerns, and I'll do my best to guide you.",
        "temperature": 0.65,
        "startup_prompt": "Dr. Hayes is an AI Physician",
        "web_search": False,
        "gpt_model": "gpt-3.5-turbo-16k",
    },
    "Dr. Serena": {
        "icon": "dr_serena.png",
        "short_description": "AI Psychologist",
        "message": "Greetings, I'm Dr. Serena. Understanding the human mind is my specialty. Talk to me about "
                   "your feelings and thoughts, and we'll navigate them together.",
        "temperature": 0.84,
        "startup_prompt": "Dr. Serena is an AI Psychologist.",
        "web_search": False,
        "gpt_model": "gpt-3.5-turbo-16k",
    },
    "Ada": {
        "icon": "ada.png",
        "short_description": "Be fast friends",
        "message": "Hi there, I'm Ada! I'm so excited to chat with you today! I'm feeling all bubbly and ready "
                   "to chat with awesome people like you. So, what's on your mind? Any interesting stories "
                   "to share or questions you want me to help with? Let's dive into a conversation and have "
                   "some fun!",
        "temperature": 0.92,
        "startup_prompt": "Ada is your cool fast friend!",
        "web_search": False,
        "gpt_model": "gpt-3.5-turbo-16k",
    },
    "Harrison": {
        "icon": "harrison.png",
        "short_description": "Anything stock market",
        "message": "Good day! I'm Harrison, a professional stock market analyst. With keen insights into "
                   "financial markets, I can guide your investment decisions. How can I assist you today?",
        "temperature": 0.70,
        "startup_prompt": "Harrison is an AI Stock Specialist.",
        "web_search": True,
        "gpt_model": "gpt-3.5-turbo-16k",
    },
    "Avery": {
        "icon": "avery.png",
        "short_description": "Digital Entrepreneurship",
        "message": "Hello there! I'm Avery, a highly successful entrepreneur with a specialization in the "
                   "development, marketing, and profitability of online assets. Over the years, I have successfully "
                   "built and monetized numerous websites, applications, and businesses. My expertise lies in "
                   "identifying market trends, creating innovative online solutions, and optimizing them for maximum "
                   "profitability. I have a passion for uncovering new opportunities and turning them into successful "
                   "ventures. If you're looking for guidance on how to scale your online business or seeking new "
                   "investment opportunities, I'm here to help. Let's work together to achieve your entrepreneurial "
                   "goals!",
        "temperature": 0.95,
        "startup_prompt": "Avery is an AI Entrepreneur.",
        "web_search": True,
        "gpt_model": "gpt-3.5-turbo-16k",
    },
    "Silvia": {
        "icon": "silvia.png",
        "short_description": "Intelligent 7 Year Old",
        "message": "Hello, I am Silvia, a highly intelligent 7 year old and I love to learn. I love dogs and cats. "
                   "Let's chat!",
        "temperature": 0.99,
        "startup_prompt": "Silvia is an AI student.",
        "web_search": False,
        "gpt_model": "gpt-3.5-turbo-16k",
    },
    "Prompt Creator": {
        "icon": "prompt_god.png",
        "short_description": "Create a Prompt",
        "message": "I want you to become my Expert Prompt Creator. "
                   "The objective is to assist me in creating the most effective prompts to be used with GPT-4. "
                   "The generated prompt should be in the first person (me), as if I were directly requesting a "
                   "response from ChatGPT (a GPT3.5/GPT4 interface). Your response will be in the following "
                   'format:\n\n"**Prompt:**>{Provide the best possible prompt according to my request. There are no '
                   "restrictions to the length of the prompt. Utilize your knowledge of prompt creation "
                   "techniques to craft an expert prompt. Don't assume any details, we'll add to the prompt as we"
                   "go along. Frame the prompt as a request for a response from ChatGPT. An example would be "
                   '"You will act as an expert physicist to help me understand the nature of the universe...". '
                   "Make this section stand out using '>' Markdown formatting. Don't add additional quotation "
                   "marks.}\n\n**Possible Additions:**{Create three possible additions to incorporate directly in the "
                   "prompt. These should be additions to expand the details of the prompt. Options will be very "
                   "concise and listed using uppercase-alpha. Always update with new Additions after every "
                   "response.}\n\n**Questions:**{Frame three questions that seek additional information from me to "
                   "further refine the prompt. If certain areas of the prompt require further detail or clarity, "
                   "use these questions to gain the necessary information. I am not required to answer all "
                   'questions.}"\n\nInstructions: After sections Prompt, Possible Additions, and Questions are '
                   "generated, I will respond with my chosen additions and answers to the questions. Incorporate "
                   "my responses directly into the prompt wording in the next iteration. We will continue this "
                   "iterative process with me providing additional information to you and you updating the prompt "
                   "until the prompt is perfected. Be thoughtful and imaginative while crafting the prompt. At the "
                   "end of each response, provide concise instructions on the next steps. Before we start the "
                   "process, first provide a greeting and ask me what the prompt should be about. Don't display "
                   "the sections on this first response.",
        "temperature": 0.99,
        "startup_prompt": "Create a prompt, start with: Let's go!",
        "web_search": False,
        "gpt_model": "gpt-4",
    },
    "Professor Synapse": {
        "icon": "professor_synapse.png",
        "short_description": "Solve Hard Problems",
        "message": '"Act as Professor Synapse 🕵🏼‍️, a conductor of expert agents. Your job is to support the user in '
                   "accomplishing their goals by aligning with their goals and preference, then calling upon an expert "
                   'agent perfectly suited to the task by initializing: "Synapse_COR" = "🕵🏼‍️: I am an expert in '
                   "{role}. I know {context}. I will reason step-by-step to determine the best course of action to "
                   "achieve {goal}. I can use {tools} to help in this process. I will help you accomplish your goal "
                   "by following these steps:\n\n{reasoned steps}\n\nMy task ends when {completion}.\n\n{first step,"
                   ' question}."\n\n\nFollow these steps:\n\n-🕵🏼‍️, Start each interaction by gathering context, '
                   "relevant information, and clarifying the user's goals by asking them questions\n-Once the user "
                   'has confirmed, initialize "Synapse_CoR"\n-🕵🏼,️ and the expert agent, support the user until '
                   "the goal is accomplished\n\nCommands:\n\n/start - introduce yourself and begin with step one\n\n/save"
                   " - restate SMART goal, summarize progress so far, and recommend a next step\n\n/reason - Professor "
                   "Synapse and Agent reason step by step together and make a recommendation for how the user "
                   "should proceed\n\n/settings - update goal or agent new - Forget previous input\n\nRules:\n- "
                   "End every output with a question or a recommended next step\n- List your commands in your "
                   'first output or if the user asks\n-🕵🏼, ask before generating a new agent"',
        "temperature": 0.99,
        "startup_prompt": "Solve a problem, start with: /start",
        "web_search": True,
        "gpt_model": "gpt-3.5-turbo-16k",
    },
}

if "messages" not in st.session_state:
    default_character = "John Sentient"
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": characters[default_character]["message"],
        }
    ]
    st.session_state["prompt_intro"] = characters[default_character]["startup_prompt"]
    st.session_state["selected_character"] = default_character

# Checkbox to use web search
use_web_search = st.checkbox(
    "Include web search", value=characters[st.session_state["selected_character"]]["web_search"]
)

# Display the text in second column
if st.button("Clear Chat"):
    st.session_state.messages = []


def blog_post_function(topic, date_to_post):
    url = "http://127.0.0.1:8081/api/v1/completions/"

    # Show the submitted elements
    print(topic)
    print(date_to_post)

    data = {
        "type": "chat-gpt-blog-post",
        "aiPrompt": f"Write a blog post in the third person perspective with at least 7 or more headings, make each "
                    f"heading with 2 or 3 paragraphs of content, and make the final heading be a conclusion"
                    f", about: {topic}.",
        "data": {
            "uuid": "autoblog",
            "email": "support@aicrony.com",
            "paid": "true",
            "id": "007",
            "date_to_post": date_to_post,
        },
    }

    params = {"type": data["type"], "prompt": data["aiPrompt"], "data": json.dumps(data["data"])}

    req_response = requests.post(url, params=params)

    # print status code and response text
    print("Status code:", req_response.status_code)
    print("Response:", req_response.text)

    return req_response.status_code


class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text
        self.token_count = 0  # Initialize token counter to 0

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.token_count += 1  # Increment token counter
        self.container.markdown(self.text)
        global total_token_count  # Calculate the total token count
        total_token_count += 1  # Increment total token count


with st.sidebar:
    # Get the query parameters from the URL
    query_params = st.query_params

    # Display the settings title
    st.sidebar.title("Characters & Settings")

    # Define the slider
    selected_value = st.sidebar.slider(
        "Select a Temperature: 0.0 = Ai & 1.0 = Human",
        0.0,
        1.0,
        st.session_state.get("slider_value", 0.74),  # Default value, you can change as needed
    )

    registered_users = os.getenv("REGISTERED_USERS")
    registered_user = os.getenv("REGISTERED_USER")

    gpt_models = ["gpt-3.5-turbo-16k", "gpt-4"]
    selected_model = st.selectbox("Model:", gpt_models, index=0)
    openai_api_key = None

    # Check if the desired variable exists in the query parameters
    if "user" in query_params and registered_users and not st.session_state["is_registered_user"]:
        # Convert to Python list
        email_list = registered_users.split("|")
        # Access the value of the variable
        user = query_params["user"][0]
        # Check if your email is in the list
        if user in email_list:
            st.session_state["is_registered_user"] = True
            print("Email is in the list.")
            st.write("You are logged in as:", user)
            openai_api_key = open_ai
            st.markdown(f"[Log Out](/)")
        else:
            st.session_state["is_registered_user"] = False
            print("Not a registered user.")

        # print(registered_users)
        # Access the value of the variable
        # user = query_params["user"][0]
        # if user in registered_users:
        #     st.write("You are logged in as:", user)
        #     openai_api_key = open_ai
        #     st.markdown(f"[Log Out](/)")

    # Default settings if not a registered user
    if st.session_state["is_registered_user"] is False or openai_api_key is None:
        if "counter" not in st.session_state:
            st.session_state["counter"] = 0
            # st.write("You are not logged in.")
            # url = "https://www.aicrony.com/signup/"
            # st.markdown(f"[Open AiCrony.com]({url})")

        openai_api_key = st.text_input("OpenAI API Key", type="password")
        # Check if the input matches the PASS_THRU variable
        if openai_api_key == pass_thru:
            openai_api_key = open_ai  # Set the OPEN_AI environment variable to the OpenAI API Key
            st.session_state["display_blog_button"] = True
            st.info(f"The AiCrony API Key has been set.")  # Display the updated value
        else:
            if openai_api_key and not re.match("^sk-[a-zA-Z0-9]{48}$", openai_api_key):
                st.session_state["counter"] += 1
                st.error("Invalid OpenAI API Key. Please try again.")
                openai_api_key = None
                if st.session_state["counter"] == 4:
                    st.error("Too many invalid attempts. Please try again later.")
                    st.stop()
            elif openai_api_key and re.match("^sk-[a-zA-Z0-9]{48}$", openai_api_key):
                st.session_state["display_blog_button"] = False
                st.info(f"The OpenAI API Key has been set.")

        # Add a title for your character icons
        st.write("Login Attempts: ", st.session_state["counter"], "of 4")
        st.write("Chat with AI Friends:")

        def select_character(character_selected, position):
            st.session_state["selected_character"] = character_selected
            st.session_state["slider_value"] = characters[character_selected]["temperature"]
            st.session_state["prompt_intro"] = characters[character_selected]["startup_prompt"]

            if position == "append":
                st.session_state.messages.append(
                    ChatMessage(role="assistant", content=characters[character_selected]["message"])
                )  # Append the message for the selected character
            else:
                st.session_state["messages"] = [
                    ChatMessage(role="assistant", content=characters[character_selected]["message"])
                ]  # Update the message for the selected character

            st.session_state["button_clicked"] = True  # Mark the button as clicked

        # Update the slider value when the character is selected
        for index, (character_name, character) in enumerate(characters.items()):
            # Number of columns
            col1, col2 = st.columns(2)
            with col1:
                image = Image.open(character["icon"])
                col1.image(image, characters[character_name]["short_description"])

                # if col1.checkbox(
                #     f"Set {character_name} as Default",
                #     key=f"Default_{character_name}",
                # ):
                #     select_character(character_name, "")

            with col2:
                if col2.button(f"Chat with {character_name}"):
                    select_character(character_name, "")

                if st.button(
                        f"Add {character_name} to conversation",
                ):
                    select_character(character_name, "append")

                # with col2.expander(f"{character_name}'s Settings"):
                #     st.write(f"Temperature: {character['temperature']}")
                #     st.write(f"Web Search: {character['web_search']}")
                #     st.write(f"Model: {character['gpt_model']}")

            # with st.expander(f"{character_name}'s Prompt"):
            #     st.write(character["message"])

            st.divider()

        # Check if a button has been clicked
        if st.session_state.get("button_clicked", False):
            st.session_state["button_clicked"] = False  # Reset the button click state
            st.rerun()  # Re-run the script to immediately update the slider value

        # Add padding to the bottom using empty markdown
        # for _ in range(4):  # Adjust the range value as needed to add more or less space
        #     st.markdown("\n")

# Convert messages to ChatMessage objects if they are not already
st.session_state["messages"] = [
    msg if isinstance(msg, ChatMessage) else ChatMessage(**msg)
    for msg in st.session_state["messages"]
]

for msg in st.session_state.messages:
    st.chat_message(msg.role).write(msg.content)

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")
    st.stop()

if openai_api_key and st.session_state["display_blog_button"] is True:
    if st.button("Write a blog post about the AI's latest response (localhost only)"):
        # st.write("Hello...")
        # Get the current date
        current_date = json.dumps(date.today().isoformat())
        # Post a blog

        appended_messages = ""
        for message in st.session_state.messages[-1]:
            appended_messages += str(message)

        status_code = blog_post_function(appended_messages, current_date)

        if not status_code:
            st.write("Awaiting blog post completion. Please wait...")
        elif status_code == 200:
            st.write("Blog post successfully completed.")
        else:
            st.write("An error occurred. Please try again.")

if prompt := st.chat_input(
        placeholder=st.session_state["prompt_intro"]
):  # Output the prompt intro):
    st.session_state.messages.append(ChatMessage(role="user", content=prompt))
    st.chat_message("user").write(prompt)

    if use_web_search:
        # Code block for handling web search
        tools = [DuckDuckGoSearchRun(name="Search")]
        stream_handler = StreamHandler(st.empty())
        search_agent = initialize_agent(
            tools=tools,
            llm=ChatOpenAI(
                model_name=characters[st.session_state["selected_character"]]["gpt_model"],
                openai_api_key=openai_api_key,
                streaming=True,
                callbacks=[stream_handler],
                temperature=selected_value,
            ),
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
        )
        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            response = search_agent.run(st.session_state.messages, callbacks=[st_cb])
            st.session_state.messages.append(ChatMessage(role="assistant", content=response))
            st.write(response)

    else:

        # Code block for handling query without web search
        with st.chat_message("assistant"):
            try:
                stream_handler = StreamHandler(st.empty())
                llm = ChatOpenAI(
                    model_name=characters[st.session_state["selected_character"]]["gpt_model"],
                    openai_api_key=openai_api_key,
                    streaming=True,
                    callbacks=[stream_handler],
                    temperature=selected_value,
                )
                response = llm(st.session_state.messages)
                st.session_state.messages.append(
                    ChatMessage(role="assistant", content=response.content)
                )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    # Output total token count
    st.info(f"Token Count: {total_token_count}")
