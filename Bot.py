import ollama
import bs4
import chromadb
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import subprocess
import win32con, win32api, win32job

class ChatHistory:
    def __init__(self):
        # List of dictionary objects, each with a 'sender' and 'content'
        # field. Used to keep track of messages in chronological order (e.g. stack)
        self.message_log = []

        # Field to keep track of the number of messages exchanged
        self.num_messages = 0

    
    # Helper used to display the contents of the ChatHistory. Used for debugging
    def display(self):
        print(f"Number of messages: {self.num_messages}")
        print("Message log: ")
        for message in self.message_log:
            print(f"role: {message['role']} ||| content: {message['content']}\n\n")

    # Helper used to turn a role and content into a nicely formatted message
    def message(self, role, content):
        return {'role' : role, 'content' : content}

    # Helper to add messages to the log. It is assumed the message is passed in
    # the format outlined in the "message" helper
    def addMessage(self, message):
        self.message_log.append(message)
        self.num_messages += 1

    # Helper used to remove the last-added message. Used in the RagDB Query implementation
    # to preserve the message_log state during queries
    def popMessage(self):
        self.message_log.pop()
        self.num_messages -= 1


class Source:

    __model_name : str
    
    def __init__(self, model_name, test_mode = False):
        self.__model_name = model_name

    def Query(self, prompt, log, test_mode = False ):

        # Input: user prompt as a string, as well as the ChatHistory 
        # log so the model has a running context of the conversation.

        # Output: LLM response as a string
        
        # Append user prompt to the log (will be reverted below!)
        log.addMessage(log.message('user', prompt))

        # Query the LLM
        response = ollama.chat(
                model=self.__model_name,
                messages=log.message_log,
                stream=False)

        # Remove the last message from the log (These are handled in the
        # calling class)
        log.popMessage()

        # Return the content of the model's response
        return response['message']['content']


class RagDB(Source):
    
    # url : Link to source for RagDB
    __url : str
    
    # Chunks of text produced from processing the content located at the URL provided
    __chunks : [str]

    # Vectorbase to be queried by user prompts
    __collection : chromadb.Collection

    # ChromaDB client. Required to opreate the vectorbase
    __client : chromadb.Client

    # Name of the model used
    __model_name : str

    def __init__(self, url, model_name, test_mode = False):

        self.__model_name = model_name
        self.__url = url

        # Use the langchain tools to retrieve content from the URL provided, and split
        # it into useable chunks
        self.__chunks = RagDB.GetChunks(self.__url, test_mode)

        # Feed these chunks into ChromaDB to produce a useable vectorbase
        self.__client, self.__collection = RagDB.GetCollection(self.__chunks, test_mode)

        if test_mode : print("Foo!")

    def __del__(self):
        # Nuke the chromedb client collection. This doesn't have an
        # elegant 'off' switch!
        self.__client.delete_collection('docs')

    def GetChunks(url, test_mode=False):
        # First, check if the source document is a pdf link - this has to be handled
        # separately.

        # In either case, load the source file into a list of Documents
        if '.pdf' in url:
            docs = PyPDFLoader(url).load()
        else:
            docs = WebBaseLoader(url).load()

        if test_mode : print(f"DOCS: {docs}\n\n\n")

        # Initialize a text splitter object to split the docs into chunks
        # Testing with gemma:2b showed that a chunk size of 500 characters seems
        # to yield acceptable results. Ditch the spearator, since there's a lot of
        # newlines and whitespace in some of these docs.
        text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = 500,
                chunk_overlap = 100,
                keep_separator = False,
                add_start_index = True,
                )

        # Use a list comprehension to get the page content of each split doc.
        chunks = [x.page_content for x in text_splitter.split_documents(docs)]
        if test_mode : print(f"CHUNKS: {chunks}\n\n\n")

        # Return chunks as a 1 x n list of strings
        return chunks

    def GetCollection(chunks, test_mode=False):
        # Establish a chromadb client and use that to initialize a collection:
        client = chromadb.Client()
        collection = client.create_collection(name = 'docs')

        # Add each element from the chunks to the collection with an associated
        # ID
        for i, d in enumerate(chunks):
            collection.add(
                    ids = [str(i)],
                    documents = [d]
                    )

        if test_mode : print(collection)

        # Return the initialized collection
        return client, collection

    def Query(self, prompt, log, test_mode = False):

        # Input: Prompt as string, as well as a reference to the history
        # (this is necessary to provide all the context to the model!)
        
        # Output: string containing the model's response (punt to Bot class
        # to handle permanent interactions with chat history)

        # Get the query the vectorspace for the three responses most closely aligned
        # with the embedded prompt.
        db_response = self.__collection.query(
                query_texts = prompt,
                n_results = 3

                )
        
        # Unpack the response (this comes in the form of a list of lists of strings)
        context_list = [x for xs in db_response['documents'] for x in xs]

        # Wrapper prompt to ensure the model uses the context provided
        new_prompt = f"Using this data: {context_list}. Resopnd to the prompt: {prompt} "

        if test_mode : print(new_prompt)

        # Add the prompt to the chat history
        log.addMessage(log.message('user', new_prompt))

        # Ask the model your question
        response = ollama.chat(model=self.__model_name,
                               messages = log.message_log,
                               stream=False)

        # Remove the nasty blob of text appended to the chat history
        # (proper chat history management is the responsibility of the ChatManager)
        log.popMessage()

        if test_mode : log.display()

        # Return the response as a string
        return response['message']['content']


class ChatManager:

    # Chat history object used to keep track of all of the messages in the conversation.
    # Provided to the webUI by way of the GetHistory() method.
    __log : ChatHistory

    # Name and modelfile associated with the model being run.
    __model_name : str
    __modelfile : str

    # String field associated with how the user interacts with the Bot - either via
    # direct interface with the pre-trained model, or via retrieval-augmented generation.
    __mode : str

    # Object representing the processes associated with the ollama backend. The ollama
    # python library provides no way to clean these up, so we have to do it ourselves.
    # __llama_id  # I have no idea what object this is, the pywin32 docs are dead

    # Source object associated with the ChatManager. Changes based on the current value of
    # __mode; interacts with the webUI via the SetMode() method.
    __source : Source 

    __llama_id = None

    # This should definitely be a singleton, but Python doesn't support access modifiers
    # which kills my most favoritest and elegentest way of implementing that
    def __init__(self, model_name, modelfile, mode = ['!default'], log = None):
        
        # Initialize chat history
        if log == None:
            self.__log = ChatHistory()
        else:
            self.__log = log

        # Unpack salient parameters
        self.__model_name = model_name
        self.__modelfile = modelfile

        # Start ollama, keep track of the processes to kill on finalization
        self.__llama_id = ChatManager.Startup(self)

        # Initialize the Source based on the mode
        self.SetMode(mode)


    def __del__(self):
        # Function responsible for all clean-up required to safely terminate a session.
        # This mostly has to do with cleaning up after ollama and its zombie processes
        pid = self.__llama_id
        ChatManager.Teardown(pid)

    def Startup(self):

        # Start the ollama server in a new console, keep the process information
        new_process = subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)

        # "cast" this to a pywin32 compatable flavor:
        job = win32job.CreateJobObject(None, "")

        # I have no idea what this line of code does, but it does make it work.
        # Like I said, the pywin32 docs are dead. See for yourself: 
        # https://pypi.org/project/pywin32/
        perms = win32con.PROCESS_TERMINATE | win32con.PROCESS_SET_QUOTA

        # Using the subprocess pid, wrap the process in a win32 handle to bring
        # it into the ecosystem
        hProcess = win32api.OpenProcess(perms, False, new_process.pid) 

        # Assign our newly-wrapped process to a job
        win32job.AssignProcessToJobObject(job, hProcess)

        # Lastly, create an actual model to work with and return the job object
        # capture_output = True supresses output to the command line
        subprocess.run(["ollama", "create", f"{self.__model_name}", f"{self.__modelfile}"], capture_output = True)
        
        return job

    def Teardown(llama_id):
        # llama_id is a win32job object, which keeps track of all of the subprocesses
        # ollama spawns - this is difficult or impossible to do with the subprocess
        # module on Windows, which is what necessitated the dependance on win32obj in the 
        # first place.
        win32job.TerminateJobObject(llama_id, 0)

    def SetMode(self, mode):

        # Mode has to be a list of strings, max length 2: one for the mode command,
        # one for the url (if applicable)
        mode : [str]

        # Start by setting the current Source to None - this is to ensure that the finalizer
        # is called for any existing Source objects. If this doesn't happend, successive calls to
        # !rag can cause an exception
        self.__source = None

        # Given a valid mode, update the BotManager object to have a source corresponding
        # to that mode

        if mode[0] == '!default':
            self.__mode = mode[0]
            self.__source = Source(self.__model_name)
        elif mode[0] == '!rag':
            self.__mode = mode[0]
            url = mode[1]
            self.__source = RagDB(url, self.__model_name)
        else:
            # This should almost certainly be something more intelligent, but 
            # I don't really want to deal with error states right now
            self.__mode = 'default'
            self.__source = Source(self.__model_name)

    def GetHistory(self):
        return self.__log.message_log

    def Query(self, prompt):
        
        # Query the source, passing the current chat history as context:
        response = self.__source.Query(prompt, self.__log)

        # Append the query and response to the chat history
        self.__log.addMessage(self.__log.message('user', prompt))

        # Append the response to the chat history
        self.__log.addMessage(self.__log.message('assistant', response))

        # Return the response
        return response

