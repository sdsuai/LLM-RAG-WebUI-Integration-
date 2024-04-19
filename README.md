# LLM-RAG-WebUI-integration

## Important note
* You must code in Python.
* Some of the libraries and dependencies to fulfill this problem may require python version of atleast 3.8 to 3.10 I think ( I only tried Python 3.8), I don't think python 3.11 works with some dependencies. This is just my opinion, you can try out different python environments using conda or python venv. Ideally please use conda.
* The "bare-minimum" task can be accomplished with just CPU. If your GPU is good enough just use that though.
* This task will require you to run yoiur code from your machines OS terminal. For windows, its the powershell (there's another shell too I think), for macOS and Linux machines a common terminal is bash. 
* After completing this task you will need to screen record to make a video showing that your code works and you explaining how it works. Obviously in the screen recording you MUST run your program from the terminal.
* This is the link to the [google folder](https://drive.google.com/drive/folders/1NPePoOOE4NwcWdrEWzLUcbdNbilXJIIx?usp=drive_link) you must submit your work to. Submit a folder containing all fo your code as well as the video. The folder should have your name.
* You may freely use any tool available to you to accomplish this task. The internet, ChatGPT, anything, just get it done.
  

## Problem
Our lab works with Large Language Models (LLMs) and other transformer based models in a social robotics research (both applied and fundamental). We are looking for people who are either familair with these topics or can quickly familiarize themselves. You are to create software to communicate with an LLM to perform different tasks:
* Back and forth communication. Which means, you provide a user query like "hey what's up!", and the LLM replies with an output: "not much just here to assist you". This will be the primary function of the software.
* The software must have a mode where it performs Retreival Augmented Generation (RAG). This way to can provide the LLM with articles from links and pdf-links. This way the user can ask the LLM about information from these articles. You may use these: [blog](https://ollama.com/blog/run-llama2-uncensored-locally) and [pdf-link](https://d18rn0p25nwr6d.cloudfront.net/CIK-0001813756/975b3e9b-268e-4798-a9e4-2a9a7c92dc10.pdf)
* **For clarity, the software MUST have the ability to switch in and out of both modes without having to restart the software.**
* Software displays both user queries and LLM responses in a WebUI. That is to say the webUI does not show up empty or restart, after every mode switch. user query and LLM response must be different color on the GUI. So either color of text ot word-bubble must be different.

## Tools you can use
The platform I advise to run LLMs from is [ollama](https://ollama.com/), here is their [repo](https://github.com/ollama/ollama). The ollama repo also provides some example scripts that might provide some inspiration on how to go about solving some parts of the problem.
For those with not so good PCs, again the "bare-minimum" can be done with just CPU, you can pull a small LLM like `gemma:2b` or `tinyllama` (these are around 2GB in size) locally on your ollama and just use those. For the webUI you may use streamlit and Flask as a server to retreive user queries and LLM responses from. I have provided two scripts which use streamlit and Flask to show a simple example of to get user input to show up on the streamlit webUI. Again, this is just advice, any other way you can get this done, you can just do that. You don't have to use ollama , or streamlit or Flask.

## "bare-minimum"
* You can provide the LLM with user query by typing it in terminal
* You can provide some kind of trigger word or phrase in terminal to switch modes
* use tiny models like gemma (2 billion parameters) or tiny llama (some 1 billion parameters or so)


## Extra Credit
Those who are able to go some extra mile will be picked first for interview. Have your software have these extra capabiltiies. These extra capabilities should not be confused with modes. The software should have this capability from any mode.

* Talk to your computer instead of typing in terminal. Here are some tools you may need:
  * A tool to stream audio. You can use `pyaudio` or some other library.
  * A tool to detect human speech in audio, so a Voice Activity Detector (`webrtcvad`, `sileroVAD` etc.).
  * A tool to derive text from speech, so maybe a  transcriber model (i.e whisper, faster-whisper etc.). Even with a "bare-minimum" PC, some of these transcriber models can run on only CPU.
* Your machine talks back
    * You will need some text-to-speech library or model for the program to talk back as a bonus. The voice doesn't have to be great. 
* If you have a decent enough PC:
    * Use bigger LLMs like mistral (fine-tuned instruct version)
    * You can also create a mode that uses a multimodal model like Llava.
