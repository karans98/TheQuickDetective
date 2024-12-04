import json
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import requests
import asyncio
import aioconsole

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
            "Provide them in JSON format with keys 'persons', 'locations', and 'items':\n{text}"
        )
    )
    return entity_extraction_prompt

def summary_and_entities(text):
    summary_chain = summarization_prompt() | load_llm()
    entity_chain = entity_extraction_prompt() | load_llm()

    print(f"Started processing clue: {text}")
    entities = entity_chain.invoke(text)
    print("\n Extract Entities", entities.content)
    entities_dict = json.loads(entities.content)
    print("\n Summary of the clue: ")
    summary = summary_chain.invoke(text)
    print(summary.content)

    return entities_dict

# Function to verify location in clue
async def location_processor(clue,entities_dict):
    for location in entities_dict['locations']:
        url = "mockurl{location}"
        #response = requests.get(url)
        #data = response.json()
        print("Waiting for API Response ... ")
        await asyncio.sleep(20)
        print(f" The location {location} is verified")
    print(f"Finished processing clue: {clue}\n")

# Function to read clues and add them to the queue
async def read_clues(queue):
    while True:
        clue = await aioconsole.ainput("Enter a new clue (or type 'quit' to stop): ")
        if clue.lower() == "quit":
            print("Stopping input...")
            await queue.put((None,None))
            break
        entities_dict = summary_and_entities(clue)
        if entities_dict.get("locations"):
            await queue.put((clue,entities_dict))
            print(f"Clue '{clue}' added to the queue.")
        else:
            print(f"Finished processing clue: {clue}\n")

# Function to process clues from the queue
async def process_clues(queue):
    while True:
        clue,entities_dict = await queue.get()
        if clue is None:
            break
        await location_processor(clue,entities_dict)
        queue.task_done()

async def main():

    queue = asyncio.Queue()
    input_task = asyncio.create_task(read_clues(queue))
    processing_task = asyncio.create_task(process_clues(queue))
    
    await input_task
    await processing_task

    print("All clues processed.")

if __name__ == '__main__':
    asyncio.run(main())
