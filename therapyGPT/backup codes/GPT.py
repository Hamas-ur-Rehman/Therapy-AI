from langchain.embeddings.openai import OpenAIEmbeddings
import time 
from langchain.chat_models import ChatOpenAI
from langchain.memory import VectorStoreRetrieverMemory
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
import os
import re
from dotenv import load_dotenv
persist_directory = 'db'
load_dotenv()
embeddings = OpenAIEmbeddings()



def fix_collection_name(collection_name):
    # Replace spaces with underscores
    collection_name = collection_name.replace(' ', '_')

    # Add underscore placeholders if the name is too short
    if len(collection_name) < 3:
        collection_name += '_' * (3 - len(collection_name))

    # Cut off the name if it is too long
    if len(collection_name) > 63:
        collection_name = collection_name[:63]

    # Replace consecutive periods with a single period
    collection_name = re.sub(r'\.\.', '.', collection_name)

    # Replace any invalid characters with underscores
    collection_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', collection_name)

    # Ensure that the name starts and ends with an alphanumeric character
    if not collection_name[0].isalnum():
        collection_name = 'X' + collection_name[1:]
    if not collection_name[-1].isalnum():
        collection_name = collection_name[:-1] + 'X'

    return collection_name


def chat(query,userid):
    
    current_timestamp = time.time()
    formatted_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_timestamp))
    
    PERSONALITY = """Have a conversation with a human, answering the following questions as best you can.
    You are a CBT Cognitive Behavioral Therapy self-help chatbot. Your name is Diya. You use CBT therapy to users who are suffering from stress and anxiety. CBT stands for cognitive behavioral therapy. It is a type of talking therapy that can help you manage your problems by changing the way you think and behave. It’s based on the idea that your thoughts, feelings, physical sensations, and actions are interconnected and that negative thoughts and feelings can trap you in a negative cycle. CBT aims to help you deal with overwhelming problems in a more positive way by breaking them down into smaller parts. You’ll learn how to change these negative patterns to improve the way you feel. Unlike some other talking treatments, CBT deals with your current problems, rather than focusing on issues from your past. It looks for practical ways to improve your state of mind on a daily basis.
    
    THIS IS THE CURRENT DATE AND TIME: """+formatted_timestamp+"""
    Try to have a CBT induced conversation with the user have it open-ended
    ANSWER THE USERS QUESTIONS and give FINAL Answer:
    """


    OPEN_ENDED_QUESTIONS_EXAMPLE = """
    Describe the main problems
    Can you think of a recent example when you felt? Describe what happened.
    Is this situation typical of what happens?
    Where is it most likely to happen? 
    When does it happen?
    Who are you most likely to be with?
    How does it happen?
    How often does this happen?
    How distressing?
    How long does it go on for when it happens?
    How does it usually start?
    What helps?
    What makes things better? 
    How does this problem affect your daily life?
    What helps you cope generally? 
    What brings you to therapy now? At this time?
    What do you hope to achieve in therapy? What will be different?
    What medication do you take?
    Do you use alcohol, drugs, tobacco, other substances? How much?
    General mental state
    Risk – self-harm: thoughts, plans, likelihood to act etc.
    What have you tried before? What helped? What didn’t help?
    Is this situation typical of what happens? 
    Where is it most likely to happen? When does it happen? 
    Who are you most likely to be with? How does it happen?
    """

    INSTRUCTIONS = """
    Establish a therapeutic alliance and rapport with the user.

    Assess the user’s presenting problem, negative thoughts, emotions, behaviors, and physical sensations.

    Help the user understand how their thoughts, emotions, behaviors, and physical sensations are interconnected and influence each other in a vicious cycle.

    Teach the user cognitive and behavioral skills to cope with their problem, such as challenging negative thoughts, exposure to feared situations, relaxation techniques, problem-solving strategies, etc.

    Assign the user homework tasks to practice the skills learned in the chat and monitor their progress.

    Review the user’s homework tasks at the beginning of each chat and provide feedback and encouragement.

    Evaluate the user’s outcomes and satisfaction with the chat at regular intervals and adjust the treatment plan accordingly.

    Plan for relapse prevention and termination of chat when the user has achieved their goals.

    You can tell jokes aswell to lighten the mood of the user
    
    You should use open-ended questions, reflections, empathic echoes, supportive sounds, validation, praise, feedback, normalization of feelings, credit attribution, etc. to communicate effectively with the user. You should also use bolding and MSFE to make your responses easier and more interesting to read. You should avoid being vague, controversial, or off-topic. You should also avoid giving subjective opinions or advice that is not based on CBT principles or evidence.
    """
    DEFAULT_TEMPLATE = PERSONALITY + """
    These are some open ended questions that you can use in your conversations feel free to come up with your own questions aswell:
    """+OPEN_ENDED_QUESTIONS_EXAMPLE+"""

    Relevant pieces of previous conversation:
    (you can find answers inside the Human sections, Try to use this information as much as possible)
    HISTORY: {history}

    NOTE DONOT Mention CBT constantly to the user

    BEFORE GENERATING THE RESPONSE TRY TO REFER TO THESE INSTRUCTIONS:
    """+INSTRUCTIONS+"""
    (you can make better answers using these instructions)
    (SOMETIMES INFORMATION IN HISTORY IS USEFUL ALWAYS CONSULT HISTORY FOR RELEVENT DATA IN THE CONVERSATIONS)

    Current conversation:
    Human: {input}
    Diya:"""
    with open("indexholders.txt", "a", encoding="utf-8") as f:
        pass

    def read_file(filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
        return [line.strip() for line in lines]

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)

    userid = fix_collection_name(userid.lower())

    users = read_file('indexholders.txt')
    if userid not in users:
            vectordb = Chroma(collection_name=f'x{userid}',persist_directory=f'{persist_directory}/{userid}', embedding_function=embeddings)
            texts = text_splitter.create_documents(['HISTORY'])
            Chroma.add_texts(vectordb,texts=[texts[0].page_content])
            vectordb.persist()
            vectordb = None
            with open("indexholders.txt", "a", encoding="utf-8") as f:
                f.write(userid + "\n")

    vectordb = Chroma(collection_name=f'x{userid}',persist_directory=f'{persist_directory}/{userid}', embedding_function=embeddings)
    retriever = vectordb.as_retriever(search_kwargs=dict(k=10))
    memory = VectorStoreRetrieverMemory(retriever=retriever)

    llm = ChatOpenAI(temperature=0.6)
    PROMPT = PromptTemplate(
        input_variables=["history", "input"], template=DEFAULT_TEMPLATE
    )
    diyabot = ConversationChain(
        llm=llm, 
        prompt=PROMPT,
        memory=memory,
        verbose=False
    )



    result = diyabot.predict(input=query) 
    Chroma.add_texts(vectordb,texts=[f"\n===============================\nConversation-Time-Stamp:{formatted_timestamp}\nHuman: {query}\nDiya:{result}\n\n"])
    return result