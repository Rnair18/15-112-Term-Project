# resizableDemo.py
# with sizeChanged (Configure) event
# and with minsize

from Tkinter import *

def sizeChanged(event):
    canvas = event.widget.canvas
    canvas.width = event.width - 4
    canvas.height = event.height - 4
    redrawAll(canvas)
    
def redrawAll(canvas):
    canvas.delete(ALL)
    # Draw the demo info
    font = ("Arial", 16, "bold")
    msg = "Resizable Demo"
    canvas.create_text(canvas.width/2, canvas.height/3, text=msg, font=font)
    # Draw the canvas size
    size = ( canvas.width, canvas.height )
    msg = "size = " + str(size)
    canvas.create_text(canvas.width/2, canvas.height*2/3, text=msg, font=font)

def init(canvas):
    canvas.width = canvas.winfo_reqwidth()
    canvas.height = canvas.winfo_reqheight()
    redrawAll(canvas)

########### copy-paste below here ###########

def run():
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=400, height=200)
    canvas.pack(fill=BOTH, expand=YES)
    # Store canvas in root and in canvas itself for callbacks
    root.canvas = canvas.canvas = canvas
    # Set up canvas data and call init
    canvas.data = { }
    init(canvas)
    # set up events
    # root.bind("<Button-1>", leftMousePressed)
    # root.bind("<KeyPress>", keyPressed)
    # timerFired(canvas)
    root.bind("<Configure>", sizeChanged)
    root.minsize(204,104) # 4 extra pixels for frame boundaries
    # and launch the app
    root.mainloop()  # This call BLOCKS (so your program waits until you close the window!)

run()