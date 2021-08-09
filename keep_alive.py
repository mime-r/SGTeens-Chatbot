from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
    return "SGTeens Chatbot is ONLINE!"
    return "If you're looking at this, you're probably a coder :/"
    print("Your bot is alive!")

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()
