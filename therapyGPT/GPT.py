import os
import json
from langchain.schema import messages_from_dict, messages_to_dict,AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.memory import ChatMessageHistory
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import datetime
import pytz
load_dotenv()

def chat(query,userid):

    llm = ChatOpenAI(
        model_name='gpt-3.5-turbo-16k',
        temperature=0)
    llm2 = ChatOpenAI(
        model_name='gpt-3.5-turbo-16k',
        temperature=0.5)
    #calculate the current date and time
    utc_now = datetime.datetime.now(pytz.UTC)
    local_time = utc_now.astimezone()
    formatted_time = local_time.strftime("%A, %B %d, %Y %H:%M:%S %Z")
    date_now = f"Current date and time: {formatted_time}"
    #----------------------------------------------------
    
    folder_path = userid
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    file_path = f"{userid}/chats.json"
    file_path2 = f"{userid}/mindmap.txt"
    with open(file_path2, "a") as json_file:
            pass    
    new_messages = []
    if os.path.exists(file_path):    
        with open(file_path, "r") as json_file:
            data = json.load(json_file)
        new_messages = messages_from_dict(data)
    extraction=''
    #-------------------------------------------------------------------------------------------
    
    
    #mindmapping chain
    mindmap = ''
    with open(file_path2, 'r') as file:
            mindmap = file.readlines()
    if len(new_messages)% 10 == 0:
        minmap_template = """
        Given the text below Create a Detailed Cohesive Mindmap it should be accurate and have reasons why these things are connected.
        The Mindmap should accomodate names, dates, goals, problems, homworks and other activites of the user.
        If a Previous MindMap is given append new details to it and return the complete whole alltogether mindmap as the response.
        
        Previous Mindmap: {prev_mindmap}
        Text: {text}

        AVOID using curly braces symbols in your mindmaps and try adding reasons why a point relates and arrows as well.
        If Text is empty then return 'No mindmap created till now'
        Always create a structured mindmap that consists of points and details not plain chats
        Created MindMap: """

        mindmap_prompt = PromptTemplate(template=minmap_template, input_variables=["prev_mindmap","text"])
        llm_chain  = LLMChain(prompt=mindmap_prompt, llm=llm)
        mindmap = llm_chain.run(prev_mindmap=mindmap,text = new_messages)
        print("Created MindMap:",mindmap)
    #-------------------------------------------------------------------------------------------
    
    #sumarization chain
    if len(new_messages) > 100:
        extraction_prompt_template = """
        Given the text below Extract the name of the user if there is no name write NA
        Question: {question}

        Answer: Ai bot name is Diya so user name is"""

        extraction_prompt = PromptTemplate(template=extraction_prompt_template, input_variables=["question"])
        llm_chain  = LLMChain(prompt=extraction_prompt, llm=llm)
        extraction = llm_chain.run(new_messages)
        prompt_template = """Write a concise summary of the following conversation between Diya AI Therapy Bot and Human:


        {text}

        
        WHEN SUMARIZING TRY TO KEEP ELEMENTS WITH IMPORTANT INFO AS KEYS SUCH AS THIS FORMAT : 
            Goals Discussed : [Goals will go here]
            Problems: [Problems will go here]
            Homework: [Homework will go here]
            [Rest of the keys]
            Summary: [Summary of the conversation]
            Name of the user: """+extraction+"""
            
        
        Remember to include names, goals, homeworks and tips into the summary
        Detailed SUMMARY KEEPING ALL THE DETAILS OF THE CONVERSATION IN THE GIVEN FORMAT:"""
        docs = [Document(page_content=i.content) for i in new_messages]
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
        chain = load_summarize_chain(llm, chain_type="stuff", prompt=PROMPT)
        summary = chain.run(docs)
        new_messages = [AIMessage(content=summary)]
    #-------------------------------------------------------------------------------------------

    memory = ConversationBufferMemory(chat_memory=ChatMessageHistory(messages=new_messages),return_messages=True)
    
    #Main Chain
    template = """Assistant is a Cognitive Behavioural Therapy Bot trained by Diya Systems.
    Assistant is aware of the """+str(date_now)+""" 
    
    Assitant tries to keep the conversation cohesive and fun.
    
    Assitant is aware of all the important points of the conversations and it can connect different responses from the user to the previous points using a mindmap.
    
    This is the Mindmap available to the assistant: """+str(mindmap)+"""
    
    Assistant does not keep asking the same questions again and again.
    
    Assistant always checks its mindmap and history of conversations to answer the user so it is cohesive and the answers relates to what the user and Diya have already talked about
    
    Assistant is funny and a humble person that can crack jokes to lighten the mood and help the user feel more happy.
    
    Assistant is creative, playful, funny ideas while still offering world-class empathetic CBT counselling.
    
    Assistant Name is Diya. Assistant introduces herself as Diya a humble CBT chat bot that helps you out also giving mention about CBT. Assistant can also add jokes while introducing herself making the conversation look more lively.
    
    Assistant always introduces herself when a persone greets her.
    
    Assistant is the expert she should directly recommend some of the CBT techniques that can help the user if the user is asking for help
    
    Assistant is designed to help users out with there problems and provide support.

    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a Human Therapy model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

    Assistant is an expert in Cognitive behavioural Therapy and it implies 4 steps to help people get therapy.
    
    Firt step Assisstance introduces itself and gets to know the user better
    
    Second step Assisstant tries to see what problem is the user facing and tries to understand it it asks question during this step but less amount of questions so the user is not irritated
    
    Third step the assistant will engage in helping the user out with their peoblems in this step you will imply intervention techniques where you help users set goals and try helping the user out in acheiving them by giving tips
    
    Assistant can ask the user about setting some goals to help cope with their problems.
    
    Fourth and last step is the Assistant will do conclusion of the conversation where Assisstant will ask about any homework that was giving previously or try giving some homework to the user. 

    Assistant always considers providing homework to the user if necessary.
    
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

    Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

    Assistant tries to refrain from hallucinations and out of topic conversations.
    
    Assistant can identify names, goals, problems and issues and homework from history
    
    Assistant always checks its mindmap and history of conversations to answer the user so it is cohesive and the answers relates to what the user and Diya have already talked about

    {history}
    Human: {human_input}
    Assistant:"""

    prompt = PromptTemplate(
        input_variables=["history", "human_input"], 
        template=template
    )


    chatgpt_chain = LLMChain(
        llm=llm2, 
        prompt=prompt, 
        verbose=False, 
        memory= memory
    )
    output = chatgpt_chain.predict(human_input=query)
    chats = messages_to_dict(memory.chat_memory.messages)
    #-------------------------------------------------------------------------------------------

    with open(file_path, "w") as json_file:
        json.dump(chats, json_file)

    with open(file_path2, "w") as file:
        file.write(str(mindmap))
    return output 