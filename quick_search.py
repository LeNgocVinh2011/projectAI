from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from person_detec import predict_folder
import mimetypes

root = Tk()
root.title('Search Video Frame')
root.iconbitmap('images/img.ico')
root.geometry("350x140")
root.eval('tk::PlaceWindow . center')
root.resizable(0, 0)

def check_is_digit(input_str):
    if input_str.strip().isdigit():
        myLabel['text'] = ""
        return True
    else:
        myLabel['text'] = "Input seconds is invalid!"
        threshold_img.focus()
        return False

def files():
    try:
        root.filename = filedialog.askopenfilename(title="Select file")
        if mimetypes.guess_type(root.filename)[0].startswith('video'):
            pathFile.insert(END, root.filename)
            btSearch["state"] = "normal"
            myLabel['text'] = ""
        else:
            btSearch["state"] = "disabled"
            myLabel['text'] = "File video is invalid!"
    except:
        print("You must choose the file path")

def search():
    seconds = threshold_img.get()
    try:
        if threshold_img["state"] == "normal" and check_is_digit(seconds):
            predict_folder(pathFile.get(), seconds)
        elif threshold_img["state"] == "disabled":
            predict_folder(pathFile.get(), None)
    except:
        messagebox.showerror("Open Source File", "Detection error!")
def close():
    root.destroy()

def show_widget():
    threshold_img["state"] = "normal"
    btNormal.configure(text="Filter normal", command=hide_widget)

def hide_widget():
    threshold_img["state"] = "disabled"
    myLabel['text'] = ""
    btNormal.configure(text="Filter seconds", command=show_widget)

btNormal = Button(root, text = "Filter normal", command=hide_widget)
bt = Button(root, text="Get Video Path", command=files)
btSearch = Button(root, text="Search", command=search, state=DISABLED)
btExit = Button(root, text="Exit", command=close)
pathFile = Entry(root)
threshold_img = Entry(root);
myLabel = Label(root, fg='#FF0000')
lbSecond = Label(root, text="Miliseconds: ")
btNormal.grid(row=0, column=0, padx=5, pady=5)
bt.grid(row=1, column=0, padx=5, pady=5)
pathFile.grid(row=1, column=2, padx=5, pady=5)
btSearch.grid(row=1, column=4, padx=5, pady=5)
btExit.grid(row=1, column=5, padx=5, pady=5)
lbSecond.grid(row=2, column=0, padx=5, pady=5)
threshold_img.grid(row=2, column=1, columnspan=2, padx=5, pady=5)
myLabel.grid(row=3, column=1, columnspan=3, padx=5, pady=5)

root.mainloop()