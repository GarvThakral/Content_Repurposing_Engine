from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from os import getenv
from langchain.prompts import ChatPromptTemplate
from helpers.classes_varibales import *
from langchain.document_loaders import YoutubeLoader
import requests
from bs4 import BeautifulSoup
import streamlit as st
import pypdf

load_dotenv()


def get_openrouter(model="alibaba/tongyi-deepresearch-30b-a3b:free") -> ChatOpenAI:
    return ChatOpenAI(
        model=model,
        openai_api_key=getenv("OPENAI_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1"
    )


def prompt_to_generate_media(list_of_media_to_generate, instructions_of_media_to_generate, userInput, context):
    media_instructions = {
        "twitter": [
            "Generate post content",
            "Add relevant hashtags",
            "Include engaging call-to-action",
            "Keep it concise within character limits"
        ],
        "instagram": [
            "Generate post content",
            "Add visually appealing captions",
            "Use trending hashtags",
            "Suggest image/video ideas",
            "Include call-to-action in caption"
        ],
        "email": [
            "Generate email newsletter snippets",
            "Craft engaging subject lines",
            "Write short but valuable body content",
            "Add CTA links or buttons"
        ],
        "tiktok scripts": [
            "Generate full TikTok video scripts",
            "Include attention-grabbing hooks",
            "Structure with storytelling",
            "Add trending sounds/effects suggestions",
            "Include clear CTA at the end"
        ],
        "reel scripts": [
            "Generate full Instagram Reel scripts",
            "Include opening hook",
            "Write engaging narration/dialogue",
            "Suggest visuals and transitions",
            "End with CTA or punchline"
        ]
    }
    list_of_media_to_generate_string = " ,".join(list_of_media_to_generate)
    print(list_of_media_to_generate_string)

    media_instructions_string = " ".join(["'" + k + " instruction' : " + " ,".join(
        v) + "\n" for k, v in media_instructions.items() if k in list_of_media_to_generate])
    print(media_instructions_string)

    user_instructions_string = " ".join(["'" + k + " instruction' : " + v + "\n" for k,
                                        v in instructions_of_media_to_generate.items() if k in list_of_media_to_generate])
    print(user_instructions_string)

    user_input = userInput + " \n\n Context : " + context

    prompt = ChatPromptTemplate.from_messages([
        ("system", """"
            You are a content generation AI agent , you are supposed to generate content for {list_of_media_to_generate_string} . Based on the
            following user instructions : {user_instructions_string} . You have to follow certain System instructions to reach the desired output , these instructins are {media_instructions_string}.
            Generate all what is asked using the context/transcripts of the content provided by the user . 
        """),

        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    result = prompt.invoke({"input": user_input, "list_of_media_to_generate_string": list_of_media_to_generate_string,
                           "media_instructions_string": media_instructions_string, "user_instructions_string": user_instructions_string})

    return result


def extract_content(platforms_selected , platforms_instructions,prompt , content_type, input_context):
    content = None
    if content_type == "Youtube Video":
        loader = YoutubeLoader.from_youtube_url(
            input_context
        )
        content = loader.load()[0].page_content

    elif content_type == "Blog post":
        response = requests.get(input_context)
        soup = BeautifulSoup(response.text, "html.parser")
        all_text = soup.get_text(separator=" ", strip=True)
        print(all_text)
    elif content_type == "PDF":
        if input_context:
            reader = pypdf.PdfReader(input_context)
            input_context = ""
            for x in reader.pages:
                text = x.extract_text()
                clean_string = ' '.join(text.split())
                if text:
                    input_context += " " + clean_string
    elif content_type == "Text input":
        input_context = input_context
        
    model = get_openrouter()
    prompt = prompt_to_generate_media(
        platforms_selected , platforms_instructions ,prompt, content)
    content_gen = generate_content(model, prompt, MediaOutput)
    st.write(platforms_selected)

    return content_gen


def generate_content(model, prompt, structure):
    return model.with_structured_output(structure).invoke(prompt)
