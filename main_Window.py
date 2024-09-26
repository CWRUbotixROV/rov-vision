from tkinter import*

def run(stream):
    
    window = Tk()
    window.title("welcome")
    window.geometry('600x600')
    window.configure(width =50,height = 50, bg='blue')

    #creating butoon for autonomous mapping 
    add_label(window, text = "Autonomous Mapping",  bg = 'red', fg ='white', column =0, row =7)
    def clicked():
        pass
    add_button(window, text='Click Me', bg = 'white', fg ='red', command = clicked, column=1, row=0 )
    
    # creating button for non-autonomous mapping
    add_label(window, text = "Non-autonomous Mapping", bg = 'white', fg ='red',column=0, row=2 )
    def clicked():
        pass
    add_button(window, text='Click Me', bg = "red", fg = "white", command= clicked,column=1, row=2 )

    # creating a button for Before coral photo
    add_label(window, text = "Before Coral Photo", bg = 'red', fg ='white',column=0, row=3 )
    def clicked():
        pass
    add_button( window, text='Click Me', bg = "white", fg = "red", command= clicked,column=1, row=3)

    # creating a button for After Coral Photo
    add_label(window, text = "After Coral Photo", bg = 'white', fg ='red',column=0, row=4 )
    def clicked():
        pass
    add_button(window, text='Click Me', bg= "red",fg = "white", command = clicked, column=1, row=4)
  
    # creating a button for Capture Subway Car
    add_label(window, text = "Capture Subway Car", bg = 'red', fg ='white', column=0, row=5)
    def clicked():
        pass
    add_button(window, text='Click Me', bg = 'white', fg = 'red', command= clicked, column=1, row=5)
    
    # creating a button for Stitch Subway Car
    add_label(window, text = "Stitch Subway Car", bg = 'white', fg ='red', column=0, row=6)
    def clicked():
        pass
    add_button(window, text='Click Me', bg = 'red', fg = 'white', command= clicked, column=1, row=6)
    
    # creating a button for Switch Camera
    add_label(window, text = "Switch Camera", bg = 'red', fg ='white', column=0, row=7)
    def clicked():
        pass
    add_button(window, text='Click Me', bg = 'white', fg ='red', command = clicked, column=1, row=7)
         
    window.mainloop()

def add_button(window, text, bg, fg, command, column, row):
    btn = Button(window, text, bg, fg, command)
    btn.grid(column, row)
def add_label(window, text , bg , fg, row, column ):
    lbl = Label(window, text , bg , fg )
    lbl.grid(row,column)




    


    
