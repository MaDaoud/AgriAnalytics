from feralyx import ask_chatbot

print("=== Chatbot Feralyx ===")
print("Tape 'exit' pour quitter.")

while True:
    user_input = input("Vous : ")
    if user_input.lower() in ["exit", "quit"]:
        print("Chatbot : À bientôt !")
        break
    answer = ask_chatbot(user_input)
    print("Chatbot :", answer)
