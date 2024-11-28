import json
import os
import string
import time
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import requests
import asyncio

load_dotenv()

def load_llm():
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    return llm

def summarization_prompt():
    summarization_prompt = PromptTemplate(
        input_variables=["text"],
        template="Summarize the following text in one or two sentences:\n{text}"
    )
    return summarization_prompt

def entity_extraction_prompt():
    entity_extraction_prompt = PromptTemplate(
        input_variables=["text"],
        template=(
            "Extract the following entities from the text: persons, locations, and items. "
            "Provide them in JSON format with keys 'person', 'location', and 'item':\n{text}"
        )
    )
    return entity_extraction_prompt

def verify_location(location):
    url = "mockurl{location}"
    #response = requests.get(url)
    #data = response.json()
    print("Waiting for API Response ... ")
    time.sleep(5)
    return f"{location} is verified"

def main():
    st.title('The Quick Detective Chatbot')

    entity_chain = entity_extraction_prompt() | load_llm()
    summary_chain = summarization_prompt() | load_llm()
    all_clues = []


    user_input = st.text_area("Hello! I am your AI assistant. Please provide a clue: ")
    all_clues += user_input

    st.write('\n')
    if st.button("Extract Entities"):

        entities = entity_chain.invoke(user_input)
        st.write("Extracted Entities", entities.content)
        entities_dict = json.loads(entities.content)

        if entities_dict.get("location"):
            for location in entities_dict['location']:
                verification_result = verify_location(location)
                st.write(verification_result)


    

                
        required_entities = ["person", "location", "item"]
        missing_entities = [key for key in required_entities if not entities_dict.get(key)]
        st.write("The missing entities are - ",missing_entities)
        
        
        if len(missing_entities)>0:
            for entity in missing_entities:
                user_response = st.text_area(f"Could you please provide me details about the {entity}? ","")
                all_clues += user_input

                if st.button(f"Submit {entity} clue"):
                    complete_input += user_response
                    new_entities = entity_chain.invoke(user_response)
                    new_dict = json.loads(new_entities.content)
                    entities_dict = {key: entities_dict[key] + new_dict.get(key, []) for key in entities_dict}
                    st.write("Updated Entity obtained",entities_dict)
        
            
        st.write("Final Entity obtained",entities_dict)



    
    if st.button("Extract Summary"):
        all_clues_str = "".join(all_clues)
        summary = summary_chain.invoke(all_clues_str)
        st.write(summary.content)




if __name__ == '__main__':
    main()

