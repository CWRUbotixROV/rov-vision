from tkinter import*

# creating button for autonomous mapping
window = Tk()
window.title("welcome")
window.geometry('600x600')
lbl = Label(window, text = "Autonomous Mapping")
lbl.grid(column=0, row=0)
btn = Button(window, text='Click Me')
btn.grid(column=1, row=0)

# creating button for non-autonomous mapping
lbl = Label(window, text = "Non-autonomous Mapping")
lbl.grid(column=0, row=2)
btn = Button(window, text='Click Me')
btn.grid(column=1, row=2)

# creating a button for Before coral photo
lbl = Label(window, text = "Before Coral Photo")
lbl.grid(column=0, row=3)
btn = Button(window, text='Click Me')
btn.grid(column=1, row=3)

# creating a button for After Coral Photo
lbl = Label(window, text = "After Coral Photo")
lbl.grid(column=0, row=4)
btn = Button(window, text='Click Me')
btn.grid(column=1, row=4)

# creating a button for Capture Subway Car
lbl = Label(window, text = "Capture Subway Car")
lbl.grid(column=0, row=5)
btn = Button(window, text='Click Me')
btn.grid(column=1, row=5)

# creating a button for Stitch Subway Car
lbl = Label(window, text = "Stitch Subway Car")
lbl.grid(column=0, row=6)
btn = Button(window, text='Click Me')
btn.grid(column=1, row=6)

# creating a button for Switch Camera
lbl = Label(window, text = "Switch Camera")
lbl.grid(column=0, row=7)
btn = Button(window, text='Click Me')
btn.grid(column=1, row=7)

window.mainloop()