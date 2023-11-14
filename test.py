import openai
openai.api_key = "key"

#initialize a dictionary to store message histories with unique identifiers (Chat 1, Chat 2, ..)
chat_lists = {}
chat_number = 1  #initialize the chat number

#pre-defined initial conversation history
def initialize_chatbot():
    return [
        {
            "role": "user",
            "content": "Start interview preparation."
        },
        {
            "role": "assistant",
            "content": "Hello! I'm your interview preparation assistant. Please let me know what specific information or tips you need."
        }
    ]

#create a default chat_list (Chat 1)
default_chat = initialize_chatbot()
chat_lists[f"Chat {chat_number}"] = default_chat

def initialize_current_chat_list():
    return None
'''
convo function- core conversation handling
              - takes 2 parameters: User Input and chat history list for current chat session
'''
def convo(input, current_chat_list):
    #appends new user input into the chat_list
    #specify the message object role as "user"
    current_chat_list.append({"role": "user", "content": input})

    #generate reponse from OpenAI using openai.ChatCompletion.create method
    #model - specifies which model of openAI to use
    #messages - creates a response based on chat_list
    generateResponse = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=current_chat_list
    )

    #extract the reply from the chatbot's response and store in reply_content variable
    #use current_chat_list as messages to get reply based on chat history
    reply_content = generateResponse.choices[0].message.content

    print(reply_content)

    #append the chatbot's reply to current_chat_list
    #specify message object role as "assistant"
    current_chat_list.append({"role": "assistant", "content": reply_content})

    #return the updated conversation history as pairs
    return current_chat_list

def main(chat_number):

    while True:
        # Prompt the user for command
        menu = input("Main Menu: Select an option: \n"
                     "[1] Select a Chat\n"
                     "[2] Create a New Chat\n"
                     "[3] Delete a Chat\n"
                     "[4] Exit\n")

        if menu == "1":
            print("Available Chats:")
            for chat_list_name in chat_lists:
                print(chat_list_name)
            selected_chat_list = input("Select a Chat (Chat 1, ..): ")
            if selected_chat_list in chat_lists:
                current_chat_list = chat_lists[selected_chat_list]
                while True:
                    user_input = input(
                        "Chat Menu: Select an option: \n[1] Use chatbot\n"
                        "[2] Delete last two messages\n"
                        "[3] Print all messages in Current Chat\n"
                        "[e2] Return to the Main Menu\n")
                    if user_input == "e2":
                        break
                    elif user_input == "1":
                        while True:
                            user_input = input("Enter input for chatbot (or 'e2' to return to the Chat Menu): ")
                            if user_input == "e2":
                                break
                            current_chat_list = convo(user_input, current_chat_list)
                    elif user_input == "2":
                        if len(current_chat_list) >= 2:
                            current_chat_list.pop()
                            current_chat_list.pop()
                            print("Last 2 items deleted.")
                        else:
                            print("Not enough items to delete.")
                    elif user_input == "3":
                        print("All messages in Current Chat:")
                        print("Number of items: ", len(current_chat_list))
                        for item in current_chat_list:
                            print(item)
                    else:
                        print("Invalid option. Please select a valid option.")
            else:
                print("Invalid Chat selected.")
        elif menu == "2":
            chat_number += 1
            chat_list_name = f"Chat {chat_number}"
            chat_lists[chat_list_name] = default_chat
            print(f"New Chat '{chat_list_name}' created.")
            print("Available Chats:")
            for chat_list_name in chat_lists:
                print(chat_list_name)
        elif menu == "3":
            print("Available Chats:")
            for chat_list_name in chat_lists:
                print(chat_list_name)
            selected_chat_list = input("Select a Chat to delete: ")
            if selected_chat_list in chat_lists:
                del chat_lists[selected_chat_list]
                print(f"'{selected_chat_list}' deleted.")
            else:
                print("Invalid Chat selected.")
        elif menu == "4":
            print("Exiting program.")
            break
        else:
            print("Invalid option. Please select a valid option.")
    return chat_number

# if __name__ == "__main__":
#     chat_number = main(chat_number)
