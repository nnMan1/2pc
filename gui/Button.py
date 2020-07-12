from tkinter import *

root = Tk()

def myClick():
    myLabel = Label(root, text='I clicked button!')
    myLabel.pack()

#myButton = Button(root, text = 'click me', state=DISABLED)
#myButton = Button(root, text = 'click me', padx=50, pady=40)
myButton = Button(root, text = 'click me', command=myClick, fg='blue', bg='red')

myButton.pack()

root.mainloop()