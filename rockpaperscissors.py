# Import dependencies
import ollama
import os
import time
import re
from langchain.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# The model used for the internal large language model
# Preferably use a smaller model, as it will work better on weaker or older hardware, specifically that without a dGPU
model = "smollm2:latest"

# The prompt for the internal large language model used as your opponent in rock paper scissors
prompt = """
You are an AI designed solely to play rock paper scissors. You will chose either rock, paper, or scissors. Analyse your data to make the best choice. You will 
ONLY output either rock, paper, or scissors, depending on what you chose, with no feedback or other. DO NOT PRODUCE ANY OTHER OUTPUT OTHER THAN 
EITHER rock, paper, or scissors. Don't overthink this prompt, just pick logically. Make sure to pick a different result each time, but if the same result is the most logical choice, then go with it.
MAKE SURE TO USE YOUR DATA. Also, use your knowledge on the probability of playing rock paper scissors to your advantage. 
Do note that you are not given the current response of your opponent, only the previous responses.
"""

# Initialize the internal variables
previous = []
ai_prev = []
human_prev = []
ai_current = ""
human_current = ""
human_wins = 0
ai_wins = 0


# Check if the models listed above are available
os.system('clear')
if model in str(ollama.list()):
    print("The selected model is available!")
else:
    print("The selected model is not available!")
    print("Downloading now")
    ollama.pull(model)
os.system('clear')

# Initialize the LLM
llm = ChatOllama(base_url="http://localhost:11434", model=model, reasoning=False)
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)


def human(human_temp, ai_temp):
    global human_current
    global ai_current
    os.system('clear')
    # Gather inputs from the player to compare to the AI's result
    print("Your previous responses: " + human_temp)
    print("Your opponent's previous responses: " + ai_temp)
    print(" ")
    while True:
        response = str(input("What move do you make? (scissors/paper/rock): "))
        if response == 'scissors' or response == 'paper' or response == 'rock':
            break
        else:
            os.system('clear')
            print("This response is invalid!")
            time.sleep(2)
            os.system('clear')
    human_current = response
    return

def ai(human_temp, ai_temp):
    global human_current
    global ai_current
    os.system('clear')
    # Create the AI prompt
    context_prompt = ChatPromptTemplate.from_messages([
        ("system", prompt),
        ("human", human_temp + ai_temp)
    ])
    chain = context_prompt | llm
    print("AI Processing ...")
    print("This may take a while, depending on your hardware")
    # Trigger the prompt to generate a response
    response = str(chain.invoke({"context": context_prompt, "main_prompt": prompt}).content)
    os.system('clear')
    # Clean the response
    response = re.sub(r"<think>[\s\S]*?</think>\n*\n*", "", response)
    # Find all words in the string
    words = re.findall(r'\b\w+\b', response)
    # Return the last one if it exists
    response = words[-1] if words else ""
    ai_current = response
    print(ai_current)
    time.sleep(2)
    return

def match():
    global human_current
    global ai_current
    global ai_wins
    global human_wins
    os.system('clear')
    # This section checks what answers were picked and chooses a winner based on that result
    if human_current == "paper" and ai_current == "rock":
        print("Paper covers rock!")
        print("Human wins!")
        human_wins += 1
    elif human_current == "scissors" and ai_current == "paper":
        print("Scissors cuts paper!")
        print("Human wins!")
        human_wins += 1
    elif human_current == "rock" and ai_current == "scissors":
        print("Rock crushes scissors!")
        print("Human wins!")
        human_wins += 1
    elif human_current == "paper" and ai_current == "scissors":
        print("Scissors cuts paper!")
        print("AI wins!")
        ai_wins += 1
    elif human_current == "rock" and ai_current == "paper":
        print("Paper covers rock!")
        print("AI wins!")
        ai_wins += 1
    elif human_current == "scissors" and ai_current == "rock":
        print("Rock crushes scissors!")
        print("AI wins!")
        ai_wins += 1
    elif human_current == ai_current:
        print("Tie!")
    else:
        # If the LLM produces an invalid response, redo the prompt
        print("The large language model has produced an invalid response! Reattempting")
        ai(human_temp, ai_temp)
        match()
        return
    print("The AI now has " + str(ai_wins) + " wins")
    print("You now have " + str(human_wins) + " wins")
    time.sleep(4)
    human_prev.append(human_current)
    ai_prev.append(ai_current)
    return
# Main game loops
while True:
    os.system('clear')
    # Ask the user how many games they would like to play initially
    repeat_count = input("How many games would you like to play?: ")
    if repeat_count.isdigit() == True:
        repeat_count = int(repeat_count)
        break
    else:
        os.system('clear')
        print("This is an invalid input!")
        time.sleep(2)
        os.system('clear')
for i in range(0, repeat_count):
    human_temp = ''
    ai_temp = ''
    for i in range(0, len(human_prev)):
        human_temp += str(human_prev[i]) + ", "
        ai_temp += str(ai_prev[i]) + ", "
    human(human_temp, ai_temp)
    ai(human_temp, ai_temp)
    match()
while True:
        os.system('clear')
        end_game = input("Would you like to play again? (True/False): ")
        if end_game == 'true' or end_game == 'True' or end_game == 't' or end_game == 'T':
            break
        elif end_game == 'false' or end_game == 'False' or end_game == 'f' or end_game == 'F':
            os.system('clear')
            print("Final Results: ")
            print(" ")
            print("AI wins: " + str(ai_wins))
            print("Your wins: " + str(human_wins))
            exit()
        else:
            os.system('clear')
            print("This is an invalid input!")
            time.sleep(2)
            os.system('clear')
while True:
    human_temp = ''
    ai_temp = ''
    for i in range(0, len(human_prev)):
        human_temp += str(human_prev[i]) + ", "
        ai_temp += str(ai_prev[i]) + ", "
    human(human_temp, ai_temp)
    ai(human_temp, ai_temp)
    match()
    os.system('clear')
    while True:
        end_game = input("Would you like to play again? (True/False): ")
        if end_game == 'true' or end_game == 'True' or end_game == 't' or end_game == 'T':
            break
        elif end_game == 'false' or end_game == 'False' or end_game == 'f' or end_game == 'F':
            os.system('clear')
            print("Final Results: ")
            print(" ")
            print("AI wins: " + str(ai_wins))
            print("Your wins: " + str(human_wins))
            exit()
        else:
           os.system('clear')
           print("This is an invalid input!")
           time.sleep(2)
           os.system('clear')
