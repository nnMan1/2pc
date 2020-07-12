from tkinter import *
from tkinter.ttk import Combobox
import networkx as nx
import matplotlib.pyplot as plt
from grave import plot_network
from grave.style import use_attributes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


root = Tk()

root.title('2PC protocol')


FAIL_OPTIONS = [
    "Never",
    "Before Vote",
    "Before Global Decision Recived",
    "Before ACK sent"
]

frame_coordinator = LabelFrame(root, text='Coordinator config')
frame_coordinator.grid(row = 0, column = 0, padx=10, pady=5)

fail_coordinator = StringVar(frame_coordinator)
fail_coordinator.set(FAIL_OPTIONS[0]) 
fail_coordinator_value = FAIL_OPTIONS[0]

Label(frame_coordinator, text='Fail coordinator time:', padx = 5).grid(row=0, column=0)
def selected_coordinator_fail(event):
    global fail_coordinator_value
    fail_coordinator_value = fail_coordinator_dropdown.get()
fail_coordinator_dropdown = Combobox(frame_coordinator, state="readonly", values = FAIL_OPTIONS, width = 17)
fail_coordinator_dropdown.current(0)
fail_coordinator_dropdown.bind("<<ComboboxSelected>>", selected_coordinator_fail)
fail_coordinator_dropdown.grid(row=0, column = 1, pady = 5, padx = 5)

frame_participant = LabelFrame(root, text='Participant config')
frame_participant.grid(row = 1, column = 0, padx=10, pady=5)

fail_participant = StringVar(frame_participant)
fail_participant.set(FAIL_OPTIONS[0]) 
fail_participant_value = FAIL_OPTIONS[0]

Label(frame_participant, text='Fail participant time:', padx = 5).grid(row=0, column=0)

Label(frame_coordinator, text='Vote:', padx = 5).grid(row=1, column=0,sticky='w')

v_coordinator = StringVar()
v_coordinator.set("COMMIT") # initialize

commit = Radiobutton(frame_coordinator, text="COMMIT", variable=v_coordinator, value='COMMIT').grid(row = 1, column = 1, sticky = 'e')
commit = Radiobutton(frame_coordinator, text="ABORT", variable=v_coordinator, value='ABORT').grid(row = 1, column = 1, sticky = 'w')


b1 = Button(frame_coordinator, text = 'Apply')
b1.grid(row = 2, column = 1, pady = 5, padx = 5, sticky='nsew')

def selected_participant_fail(event):
    global fail_participant_value
    fail_participant_value = fail_participant_dropdown.get()
fail_participant_dropdown = Combobox(frame_participant, state="readonly", values = FAIL_OPTIONS, width = 17)
fail_participant_dropdown.current(0)
fail_participant_dropdown.bind("<<ComboboxSelected>>", selected_participant_fail)
fail_participant_dropdown.grid(row=0, column = 1, pady = 5, padx = 5)

Label(frame_participant, text='Vote:', padx = 5).grid(row=1, column=0,sticky='w')

v = StringVar()
v.set("COMMIT") # initialize

commit = Radiobutton(frame_participant, text="COMMIT", variable=v, value='COMMIT').grid(row = 1, column = 1, sticky = 'e')
commit = Radiobutton(frame_participant, text="ABORT", variable=v, value='ABORT').grid(row = 1, column = 1, sticky = 'w')

b2 = Button(frame_participant, text = 'Apply')
b2.grid(row = 2, column = 1, pady = 5, padx = 5, sticky='nsew')


graph = nx.Graph()
graph.add_nodes_from(['shar1Repl', 'shard2Repl', 'shard3Repl', 'congifRepl', 'mongoClient'])

fig, ax = plt.subplots()

nx.draw(graph,with_labels=True)
canv = FigureCanvasTkAgg(fig, master = root)
canv.draw()

get_widz = canv.get_tk_widget()
get_widz.grid(row = 0, column = 1, padx = 20, pady = 20, rowspan = 2)

text1 = Text(frame_coordinator, height = 10, width = 40).grid(row  = 3, column = 0, columnspan = 2, padx = 5, pady = 5)
text2 = Text(frame_participant, height = 10, width = 40).grid(row  = 3, column = 0, columnspan = 2, padx = 5, pady = 5)

root.mainloop()