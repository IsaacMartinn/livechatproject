import random
from mistralai import Mistral
import math

# gonna need to add leetcode param to determind attacks
def attackValue(value, scoreInfo):

    perc = (random.randint(0, 100))
    toreturn = 0
    if(value == "Punch"):
        if(perc <= 80):
            toreturn = 10
        else:
            toreturn = 8
    elif(value == "Kick"):
        if(perc <= 50):
            toreturn =  15
        else:
            toreturn = 6
    elif(value == "Blast"):
        if(perc <= 30):
            toreturn =  20
        else:
            toreturn = 2
    elif(value == "Special"):
        if(perc < 10):
            toreturn = 25
        else:
            toreturn = 0
    
    toadd = math.floor(((scoreInfo[value.lower()]-50)/100) * toreturn)
    final = toreturn + toadd
    return final
    
def getRoboName(name):
    try:
        api_key = "NOTHER API"
        model = "mistral-large-latest"

        client = Mistral(api_key=api_key)

        chat_response = client.chat.complete(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": f"give me 1 scary robot name with the username {name}. The name should be no more than 12 characters. Please only print the name nothing else.",
                },
            ]
        )
        content = chat_response.choices[0].message.content
        words = content.split()
        last_word = words[-1] if words else ''
        return(last_word)
    except:
        return(name + "botty")
    
def toAdd(solved, submissions, ranking):
    perc = solved/submissions
    if(perc > 0.5):
        perc = 6
    elif(perc > 0.4):
        perc = 4
    else:
        perc = 2
    
    if(solved > 80):
        solved = 7
    elif(solved > 50):
        solved = 5
    elif(solved > 30):
        solved = 3
    else:
        solved = 1
    
    if (ranking > 4000000):
        ranking = 1
    elif (ranking > 3000000):
        ranking = 2
    elif(ranking > 2000000):
        ranking = 3 
    elif (ranking > 1000000):
        ranking = 4
    else:
        ranking = 6

    return({
        "perc": perc,
        "solved": solved,
        "ranking": ranking
    })
    