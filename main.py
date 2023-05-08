import streamlit as st
from streamlit_chat import message
import os
import openai
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient 
from azure.search.documents.models import QueryType
from dotenv import load_dotenv
from datetime import datetime
load_dotenv(override=True)

st.set_page_config(page_title="Custom ChatGPT", page_icon="💬")

st.markdown("# Custom ChatGPT")
st.sidebar.header("Custom ChatGPT")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

AZURE_SEARCH_SERVICE = os.environ.get("AZURE_SEARCH_SERVICE")
AZURE_SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX")
AZURE_OPENAI_SERVICE = os.environ.get("AZURE_OPENAI_SERVICE")
AZURE_OPENAI_GPT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_GPT_DEPLOYMENT")
AZURE_OPENAI_CHATGPT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_CHATGPT_DEPLOYMENT")
SEARCH_SERVICE_ADMIN_API_KEY = os.environ.get("SEARCH_SERVICE_ADMIN_API_KEY")

# Used by the OpenAI SDK
openai.api_type = "azure"
openai.api_base = f"https://{AZURE_OPENAI_SERVICE}.openai.azure.com"
openai.api_version = os.environ.get("OPENAI_API_VERSION")
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Set up clients for Cognitive Search and Storage
search_client = SearchClient(
    endpoint=f"https://{AZURE_SEARCH_SERVICE}.search.windows.net",
    index_name=AZURE_SEARCH_INDEX,
    credential=AzureKeyCredential(SEARCH_SERVICE_ADMIN_API_KEY))

prompt_prefix = """<|im_start|>system
Assistant helps the company employees with their healthcare plan questions and employee handbook questions. 
Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below. If asking a clarifying question to the user would help, ask the question. 
Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brakets to reference the source, e.g. [info1.txt]. Don't combine sources, list each source separately, e.g. [info1.txt][info2.pdf].

Sources:
{sources}

<|im_end|>"""
turn_prefix = """
<|im_start|>user
"""
turn_suffix = """
<|im_end|>
<|im_start|>assistant
"""

prompt_history = turn_prefix
history = []
summary_prompt_template = """
Below is a summary of the conversation so far, and a new question asked by the user that needs to be answered by searching in a knowledge base. Generate a search query based on the conversation and the new question. Source names are not good search terms to include in the search query.

Summary:
{summary}

Question:
{question}

Search query:
"""
# Execute this cell multiple times updating user_input to accumulate chat history
# user_input = input()
user_input = st.text_input("You: ","Hello, how are you?", key="input")

if user_input:
    # Exclude category, to simulate scenarios where there's a set of docs you can't see
    exclude_category = None

    if len(history) > 0:
        completion = openai.Completion.create(
            engine=AZURE_OPENAI_GPT_DEPLOYMENT,
            prompt=summary_prompt_template.format(summary="\n".join(history), question=user_input),
            temperature=0.7,
            max_tokens=32,
            stop=["\n"])
        search = completion.choices[0].text
    else:
        search = user_input

    # Alternatively simply use search_client.search(q, top=3) if not using semantic search
    print("Searching:", search)
    print("-------------------")
    filter = "category ne '{}'".format(exclude_category.replace("'", "''")) if exclude_category else None
    r = search_client.search(search, 
                            filter=filter,
                            query_type=QueryType.SEMANTIC, 
                            query_language="zh-tw", 
                            query_speller="lexicon", 
                            semantic_configuration_name="default", 
                            top=3, include_total_count=True, logging_enable=True)

    content = r

    prompt = prompt_prefix.format(sources=content) + prompt_history + user_input + turn_suffix

    completion = openai.Completion.create(
        engine=AZURE_OPENAI_CHATGPT_DEPLOYMENT, 
        prompt=prompt, 
        temperature=0.7, 
        max_tokens=1024,
        stop=["<|im_end|>", "<|im_start|>"])

    prompt_history += user_input + turn_suffix + completion.choices[0].text + "\n<|im_end|>" + turn_prefix
    history.append("user: " + user_input)
    history.append("assistant: " + completion.choices[0].text)

    st.session_state.past.append(user_input)
    st.session_state.generated.append(completion.choices[0].text)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['past'][i], avatar_style = 'big-ears',is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], avatar_style = 'bottts', key=str(i))

print("\n-------------------\n".join(history))
print("\n-------------------\nPrompt:\n" + prompt)