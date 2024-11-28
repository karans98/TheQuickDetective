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

async def verify_location(location):
    url = "mockurl{location}"
    #response = requests.get(url)
    #data = response.json()
    print("Waiting for API Response ... ")
    await asyncio.sleep(20)
    return f" The location {location} is verified"

# Function to extract entities and location
async def clue_processor(clue):
    print(f"Started processing clue: {clue}")
    entities = entity_chain.invoke(clue)
    print("Extract Entities", entities.content)
    entities_dict = json.loads(entities.content)
    if entities_dict.get("locations"):
        for location in entities_dict['locations']:
            verification_result = await verify_location(location)
            print(verification_result)
    print(f"Finished processing clue: {clue}")

# Function to read clues and add them to the queue
async def read_clues(queue,all_clues):
    while True:
        clue = await aioconsole.ainput("Enter a new clue (or type 'quit' to stop): ")
        if clue.lower() == "quit":
            print("Stopping input...")
            await queue.put(None)
            break
        all_clues +=clue
        await queue.put(clue)
        print(f"Clue '{clue}' added to the queue.")

# Function to process clues from the queue
async def process_clues(queue):
    while True:
        clue = await queue.get()
        if clue is None:
            break
        await clue_processor(clue)
        queue.task_done()

async def main():

    queue = asyncio.Queue()
    all_clues=[]
    input_task = asyncio.create_task(read_clues(queue,all_clues))
    processing_task = asyncio.create_task(process_clues(queue))
    
    await input_task
    await processing_task

    print("All clues processed.")
    print("Summary of all clues till now: ")
    all_clues_str = "".join(all_clues)
    summary = summary_chain.invoke(all_clues_str)
    print(summary.content)


if __name__ == '__main__':
    summary_chain = summarization_prompt() | load_llm()
    entity_chain = entity_extraction_prompt() | load_llm()

    asyncio.run(main())
