import tkinter.messagebox


def be_patient_message():
    tkinter.messagebox.showinfo(title="Work in progress",
                                message="Creating the PDF might take a few moments, please be patient",
                                icon='info', type='ok')


def PDF_done_message():
    tkinter.messagebox.showinfo(message="Your PDF is done!", icon='info', type='ok')
