# LLM-RAG-WebUI-integration

## Important note
* You muse code in Python.
* Some of the libraries and dependencies to fulfill this problem may require python version of atleast 3.8 to 3.10 I think ( I only tried Python 3.8), I don't think python 3.11 works with some dependencies. This is just my opinion, you can try out different python environments using conda or python venv. Ideally please use conda.
* The "bare-minimum" task can be accomplished with just CPU. If your GPU is good enough just use that though.
* This task will require you to run yoiur code from your machines OS terminal. For windows, its the powershell (there's another shell too I think), for macOS and Linux machines a common terminal is bash. 
* After completing this task you will need to screen record to make a video showing that your code works. Obviously in the screen recording you MUST run your program from the terminal.
  

## Problem
Our lab works with Large Language Models (LLMs) and other transformer based models in a social robotics research (both applied and fundamental). We are looking for people who are either familair with these topics or can quickly familiarize themselves. You are to create software to communicate with an LLM to perform different tasks:
* Back and forth communication. Which means, you provide a user query like "hey what's up!", and the LLM replies with an output: "not much just here to assist you".
** All
* Software must go in a mode

[ollama](https://ollama.com/) 
[ollama repo](https://github.com/ollama/ollama)
Must be able to run program on the terminal of your machine. Talk to the program so you need a Voice Activity Detector (webrtcvad, sileroVAD etc.), 
a speech to text transcriber model (i.e whisper, faster-whisper etc.), and a text-to-speech library for the program to talk back as a bonus (the library doesnt have to be great, again this is a bonus). 

mode for Retreival Augmented Generation (RAG) using ollama. There are some example tutorials in the ollama repo. You sould be able to send website links for the program to perform RAG on. For this you can paste the website link on the terminal to provide input.

streamlit and Flask. User bubble and LLM response bubbles must be different color.

LLMs that are small i.e gemma:2b, tiny-llama etc.

If PC is good (extra points) mode for multi-modal input (llava:7b).
