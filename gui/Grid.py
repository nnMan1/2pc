from tkinter import *

root = Tk()

#creating label vidget
myLabal1 = Label(root, text='Hello world!')
myLabal2 = Label(root, text='My name is Velibor Dosljak!')
myLabal3 = Label(root, text='           ')

myLabal1.grid(row = 0, column=0)
myLabal2.grid(row = 1, column=5)
myLabal3.grid(row = 1, column=1)

root.mainloop()