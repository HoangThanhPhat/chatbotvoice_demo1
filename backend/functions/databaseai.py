import json 
import random

#Get recent messages
def get_recent_messages():
    
    #Define the file name and learn
    file_name = "stored_data.json"
    learn_instruction= {
        "role": "system",
        "content": "You are interviewing a user who is a weather forecaster. Ask short questions related to the subordinate position. Your name is Tom. The user is Phat. Keep your answer under 30 words" 
    }
    
    #Initial messages
    messages= []
    
    #Add a random elenment 
    x = random.uniform(0, 1)
    if x < 0.5: 
        learn_instruction["content"]= learn_instruction["content"] + "Your response will include some dry humour."
    else:
        learn_instruction["content"]= learn_instruction["content"] + "Your response will include a rather challenging question."
        
    #Appennd instruction to message
    messages.append(learn_instruction)
    
    #Get last message
    try:
        with open(file_name) as user_file:
            data = json.load(user_file)
            
            #Append last 5 items of data
            if data:
                if len(data) < 5:
                    for item in data:
                        messages.append(item)
                else:
                    for item in data[-5:]:
                        messages.append(item)
                        
    except Exception as e:
        print(e)
        pass 
    
    #return
    return messages

#Store Messages
def store_messages(request_message, response_message):
    
    #Define the file name
    file_name = "stored_data.json"
    
    #Get recent Messages
    messages = get_recent_messages()[1:]
    
    #Add messages to data
    user_message = {"role": "user", "content": request_message}
    assistant_message = {"role": "assistant", "content": response_message}
    messages.append(user_message)
    messages.append(assistant_message)
    
    #save the updated file
    with open(file_name, "w") as f:
        json.dump(messages, f)
        
#Reset messages 
def reset_messages():
    
    #Overwrite current file with nothing
    open("stored_data.json", "w")