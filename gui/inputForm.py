from tkinter import *

root = Tk()

def myClick():
    hello = "Hello" + e.get()
    myLabel = Label(root, text=hello)
    myLabel.pack()

e = Entry(root, width=50, borderwidth=5)
e.pack()
e.insert(0,'Enter your name')

myButton = Button(root, text = 'Enter your name', command=myClick)
myButton.pack()

f = plt.Figure(figsize=(5, 5), dpi=100)

root.mainloop()