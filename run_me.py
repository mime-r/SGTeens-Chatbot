# Sorts out the dependencies
from keep_alive import keep_alive

#import telegram

# keep_alive service in repl.it flask page
keep_alive()

exec(open("chat.py").read())
