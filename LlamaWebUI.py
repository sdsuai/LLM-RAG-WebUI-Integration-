import streamlit as st
import Bot


def Startup():
    # Add a guard to make sure this is only called once
    if 'initialized' in st.session_state:
        return

    st.session_state['initialized'] = True

    # Define the model name and prompt
    model_name = 'gemma:2b'
    system_prompt = 'You are a helpful chatbot assistant named Jaykwellin'
    mf = f'''
    FROM {model_name}
    SYSEM {system_prompt}
    '''

    # Create a ChatManager and add it to the session_state
    st.session_state['chat_manager'] = Bot.ChatManager(model_name, mf)



def help_me():
    # I really can't excuse this code structure
    # What I really want is a #define - style syntax where I can
    # alias this string literal as something else, but here we are.
    return '''
    !quit - Quit the program\n
    !default - Engage the LLM in conversational mode\n
    !rag {url} - Ask the LLM questions about a source at {url} using Retrieval Augmented Generation\n
    !help - Display this message\n
    '''

def ParseInput(val, manager):
    # Helper function responsible for taking a string input from the user and interacting with the
    # language model based on the value of the string. Returns a code indicating the operation
    # performed (None for regular interaction)

    # If the user wants to quit, throw back to program control to terminate
    if val == '!quit':
       return  '!quit'

    # Set mode to 'default'; in this mode, the model answers questions without consulting any
    # vectorbase
    elif val == '!default':
        manager.SetMode([val])
        return 'Mode set to default!'

    # Set mode to Retreival Augmented Generation; in this mode, the model queries a vectorbase
    # containing chunks of the page at the provided URl to produce an answer.
    elif val.find('!rag') != -1:

        split_val = val.split(' ')
        if len(split_val) != 2:
            return 'Usage: !rag {url}'
        
        manager.SetMode(split_val)
        return 'Mode set to Retrieval Augmented Generation!'
    
    # Print the help screen displaying current commands
    elif val == '!help':
        return help_me()

    # Catch mistyped commands
    elif val.find('!') == 0:
        return "Please input a valid prompt or command. Type !help for a list of valid commands"
    
    # If none of those special cases are encountered, query the chatbot. The response
    # to the query is captured in the manager's ChatHistory, which is why this returns
    # None.
    else:
        prompt = val
        response = manager.Query(prompt)
        return None


def WriteHistory(chat_history):
    # Helper function which writes the program history to the screen in chronological order
    # Reads from the current chat_history

    # Guard to prevent the program from trying to access elements that
    # do not exist.
    if len(chat_history) < 1:
        return

    for chat in chat_history:
        role = chat['role']
        content = chat['content']
        with st.chat_message(role):
            st.write(content)

def run(manager):
    # Setup the page
    st.title('Welcome to the Jaykwellin Chatbot!')
    
    # Post up a button for the user to submit a query to the model
    val = st.chat_input('Chat with the bot. !help for a list of commands')
    response = None
    
    # Parse the input and print the result, if it exists
    if val != None:
        response = ParseInput(val, manager)

    if response == '!quit':
        return -1

    # Finally, write the chat history thus far to the page
    WriteHistory(manager.GetHistory())
    
    # If the user modified the model mode, output the corresponding
    # message here as the 'notification' role
    if response is not None:
        with st.chat_message('notification'):
            st.write(response)

    return 0

if __name__ == "__main__" :
    # This function sets up the page for the first time
    Startup()

    # This function handles all of the logic associated with regular
    # program operation. 
    curr_state = run(st.session_state['chat_manager'])

    # If the current state is updated to -1, it means the user input has 
    # entered the !quit command and program execution should stop.
    if curr_state == -1:
        st.stop()
