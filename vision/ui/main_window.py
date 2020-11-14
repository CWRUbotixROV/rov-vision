from tkinter import*
 
# creating button for autonomous mapping
window = Tk()
window.title("welcome")
window.geometry('300x300')
window.configure(width =50,height = 50, bg='blue')
 
lbl = Label(window, text = "Autonomous Mapping",  bg = 'red', fg ='white')
lbl.grid(column=0, row=0)
def clicked():
    lbl.configure(text="Autonomous Mapping (Clicked)")
btn = Button(window, text='Click Me', bg = 'white', fg ='red', command = clicked)
btn.grid(column=1, row=0)   
 
# creating button for non-autonomous mapping
lb2 = Label(window, text = "Non-autonomous Mapping", bg = 'white', fg ='red')
lb2.grid(column=0, row=2)
def clicked():
    lb2.configure(text="Non-autonomous Mapping (Clicked)" , bg = 'white', fg ='red')
btn2 = Button(window, text='Click Me', bg = "red", fg = "white", command= clicked)
btn2.grid(column=1, row=2)
 
 
# creating a button for Before coral photo
lb3 = Label(window, text = "Before Coral Photo", bg = 'red', fg ='white')
lb3.grid(column=0, row=3)
def clicked():
    lb3.configure(text="Before Coral Photo (Clicked)", bg = 'red', fg ='white')
btn3 = Button(window, text='Click Me', bg = "white", fg = "red", command= clicked)
btn3.grid(column=1, row=3)
 
# creating a button for After Coral Photo
lb4 = Label(window, text = "After Coral Photo", bg = 'white', fg ='red')
lb4.grid(column=0, row=4)
def clicked():
    lb4.configure(text="After Coral Photo (Clicked)")
btn4 = Button(window, text='Click Me', bg= "red",fg = "white", command = clicked)
btn4.grid(column=1, row=4)
 
# creating a button for Capture Subway Car
lb5 = Label(window, text = "Capture Subway Car", bg = 'red', fg ='white')
lb5.grid(column=0, row=5)
def clicked():
    lb5.configure(text="Capture Subway Car (Clicked)")
btn5 = Button(window, text='Click Me', bg = 'white', fg = 'red', command= clicked)
btn5.grid(column=1, row=5)
 
# creating a button for Stitch Subway Car
lb6 = Label(window, text = "Stitch Subway Car", bg = 'white', fg ='red')
lb6.grid(column=0, row=6)
def clicked():
    lb6.configure(text="Stich Subway Car (Clicked)")
btn6 = Button(window, text='Click Me', bg = 'red', fg = 'white', command= clicked)
btn6.grid(column=1, row=6)
 
# creating a button for Switch Camera
lb7 = Label(window, text = "Switch Camera", bg = 'red', fg ='white')
lb7.grid(column=0, row=7)
def clicked():
    lb7.configure(text="Switch Camera (Clicked)")
btn7 = Button(window, text='Click Me', bg = 'white', fg ='red', command = clicked)
btn7.grid(column=1, row=7)
 
 
window.mainloop()
 
