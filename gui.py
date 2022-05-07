from tkinter import ttk
from tkinter import *
from tkinter import filedialog
from ttkthemes import ThemedStyle
from PyPDF2 import PdfFileMerger, PdfFileReader
import pytesseract
import uuid  # for generating random filename
import os
import tempfile
from pdf2image import convert_from_path
from PIL import ImageTk, Image, ImageEnhance
import io
import random

import popup_message
import tesseract_installation
import tilt_correction


class GUI(Tk):
    def __init__(self):
        super().__init__()
        # makes a program window

        # sets a custom app title
        self.title("Image Processing App")

        # sets app background color
        self.configure(bg="#465CA5")  # bg = E6E6E6

        # setting window size and position
        window_width = 1000
        window_height = 950

        # set the minimum window size
        self.minsize(1030, 720)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int(screen_width / 2 - window_width / 2)
        y = int(screen_height / 2 - window_height / 2)

        self.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # window style
        style = ThemedStyle(self)
        style.set_theme("aquativo")

        # page number display
        self.text = StringVar()
        self.text.set("Page " + "0/0")

        self.image_frame = None
        self.options_frame = None
        self.current_file = None

    def add_image_frame(self):
        # makes a frame for the bottom part

        self.image_frame = Frame(self, borderwidth=0, highlightthickness=0)
        # self.image_frame = image_frame

        # makes the frame invisible until the image is uploaded
        self.image_frame.pack_forget()

    def add_menu(self):
        # creates a menu object
        menu = Menu()
        self.config(menu=menu)

        # creates a File object
        file = Menu(menu, tearoff=False)

        # adds "File" to the menu
        menu.add_cascade(label="File", menu=file)

        # adds commands to the File menu
        file.add_command(label="Open Files...", command=lambda: File.upload_files(self))
        # () is causing the method to run upon starting the program, it is not needed
        file.add_command(label="Save as Images", command=lambda: self.current_file.save_as_images())
        file.add_command(label="Save as PDF", command=lambda: self.current_file.save_as_pdf())
        file.add_separator()
        file.add_command(label="Close File", command=lambda: self.close_files())
        file.add_command(label="Exit", command=self.destroy)

        # creates an edit object
        edit = Menu(menu, tearoff=False)

        # # creates a Help object
        # help = Menu(menu, tearoff=False)
        #
        # # adds "Help" to the menu
        # menu.add_cascade(label="Help", menu=help)

        # creates a tesseract object
        tesseract = Menu(menu, tearoff=False)

        # adds "Tesseract" to the menu
        menu.add_cascade(label="Tesseract", menu=tesseract)

        # Add commands to the Tesseract menu
        tesseract.add_command(label="Tesseract for Windows", command=lambda: tesseract_installation.open_for_windows())
        tesseract.add_command(label="Tesseract for Linux", command=lambda: tesseract_installation.open_for_linux())
        tesseract.add_command(label="Tesseract for MacOS", command=lambda: tesseract_installation.open_for_mac())

    def add_edit_options(self):
        # frame for buttons
        button_frame = Frame(self, height=130, bg="#FFD100", bd=0, highlightthickness=0)
        # #223985 for dark blue color, #FF7789 for pink
        button_frame2 = Frame(self, height=5, bg="#FFD100", bd=0, highlightthickness=0)
        # packs the button frame
        button_frame.pack(side=TOP, fill=BOTH)
        button_frame2.pack(side=BOTTOM, fill=BOTH)

        # prevents "bottom_frame" from shrinking when packing "options_frame"
        button_frame.pack_propagate(0)

        # Functionless button to hold the options text
        options_title = Button(text="Editing Options", font=("Arial", 12, "bold"),
                               relief=GROOVE, disabledforeground="blue")
        # options_title.config(disabledbackground = "yellow")
        options_title.config(state='disabled')

        # container for buttons
        self.options_frame = LabelFrame(button_frame, fg="green", bg="#FFD100",
                                        bd=3, labelanchor=NW, labelwidget=options_title)
        self.options_frame.pack(padx=6, pady=6, fill=BOTH, expand=TRUE)

        self.options_frame2 = LabelFrame(button_frame2, fg="green", bg="#FFD100",
                                         bd=1, labelanchor=NW, labelwidget=options_title)
        self.options_frame2.pack(padx=2, pady=2, fill=BOTH, expand=TRUE)

        # makes option buttons
        # button1 = Button(self.options_frame, text="Copy Text to Clipboard", font=("Arial", 9), bd=3)
        # button2 = Button(self.options_frame, text="Clean Background", font=("Arial", 9), bd=3)
        button3 = Button(self.options_frame, text="Fix Tilt", font=("Arial", 9), bd=3,
                         command=lambda: tilt_correction.correct_tilt(self, self.current_file.get_img(
                             self.current_file.page)))
        # button4 = Button(self.options_frame, text="Rotate 90°", font=("Arial", 9), bd=3,
        #                  command=lambda: self.rotate_90_degrees(self.current_file.get_img(self.current_file.page)))

        icon = PhotoImage(file='icon_rotate_left.png')
        button4 = Button(self.options_frame, text="Rotate 90°", image=icon, bd=3, compound="left",
                         command=lambda: self.rotate_90_degrees(self.current_file.get_img(
                             self.current_file.page)))
        # this line is necessary for preventing icon to be garbage-collected, otherwise icon does not appear
        button4.image = icon

        button5 = Button(self.options_frame, text="Enhance image", font=("Arial", 9), bd=3,
                         command=lambda: self.enhance_image(self.current_file.get_img(
                             self.current_file.page), cSlideBar.get(), 1 + bSlideBar.get() / 10))

        button6 = Button(self.options_frame2, text="size +", font=("Arial", 9), bd=3,
                         command=lambda: self.zoomimagelarger(self.current_file.get_img(
                             self.current_file.page)))

        button7 = Button(self.options_frame2, text="size -", font=("Arial", 9), bd=3,
                         command=lambda: self.zoomimagesmaller(self.current_file.get_img(
                             self.current_file.page)))

        button8 = Button(self.options_frame2, text="resize", font=("Arial", 9), bd=3,
                         command=lambda: self.resize(self.current_file.get_img(
                             self.current_file.page)))

        cSlideBar = Scale(self.options_frame, label="Contrast", from_=0, to=20, orient=HORIZONTAL)
        bSlideBar = Scale(self.options_frame, label="Brightness", from_=0, to=20, orient=HORIZONTAL)
        # set scale to to recommend value
        cSlideBar.set(5)
        bSlideBar.set(1)
        button9 = Button(self.options_frame, text="Undo", bd=3, compound="left",
                         command=lambda: self.undo())

        # packing buttons
        # button1.pack(padx=(170, 35), pady=(0, 14), ipadx=5, ipady=5, side=LEFT)
        # button2.pack(padx=35, pady=(0, 14), ipadx=5, ipady=5, side=LEFT)
        button3.pack(padx=20, pady=(0, 40), ipadx=5, ipady=5, side=LEFT)
        button4.pack(padx=20, pady=(0, 40), ipadx=5, ipady=5, side=LEFT)
        button5.pack(padx=5, pady=(0, 40), ipadx=5, ipady=5, side=LEFT)
        button6.pack(padx=5, pady=(0, 40), ipadx=5, ipady=5, side=RIGHT)
        button7.pack(padx=5, pady=(0, 40), ipadx=5, ipady=5, side=RIGHT)
        button8.pack(padx=5, pady=(0, 40), ipadx=5, ipady=5, side=RIGHT)
        button9.pack(padx=5, pady=(0, 40), ipadx=5, ipady=5, side=RIGHT)
        cSlideBar.pack(padx=5, pady=(0, 40), ipadx=5, ipady=5, side=LEFT)
        bSlideBar.pack(padx=5, pady=(0, 40), ipadx=5, ipady=5, side=LEFT)

        # entry box for entering numbers to display specific pages
        self.entry_frame = Frame(self.options_frame)
        # self.entry_frame.pack(padx=35, pady=(0, 14), ipadx=5, ipady=5, side=LEFT)
        self.entry_frame.pack(padx=35, pady=(0, 14), expand=TRUE, side=LEFT)

        left = Button(self.entry_frame, text="<", activebackground="lightskyblue", activeforeground="white",
                      bg="steelblue", bd=10, command=self.prev_page)
        page_number = Label(self.entry_frame, textvariable=self.text)
        right = Button(self.entry_frame, text=">", activebackground="lightskyblue", activeforeground="white",
                       bg="steelblue", bd=10, command=self.next_page)
        left.pack(side=LEFT)
        page_number.pack(side=LEFT)
        right.pack(side=LEFT)

    def scroll_on_mousewheel(self, canvas, event):
        canvas.yview_scroll(-1 * (event.delta // 120), "units")

    # getting an image and rendering it
    def upload_file_image(self, image_fileimage):
        from PIL import Image

        baseheight = 560
        basewidth = 400

        img = Image.open(image_fileimage)
        img = img.resize((basewidth, baseheight))
        render = ImageTk.PhotoImage(img)
        self.render = render  # prevent being garbage collected, might not show up the image otherwise
        w, h = img.size
        print("Image width:", w, "Height:", h)

        # making frame for image canvas
        frame = Frame(self.image_frame, bg="black")
        canvas = Canvas(frame, height=h, width=w, bg="green")

        # puts image into canvas and centers it
        canvas.create_image(w / 2, h / 2, image=render)

        # make 2 scrollbars
        # "master = frame" puts scrollbar next to image. "master = root" puts scrollbar to the side of the main window
        y_scrollbar = ttk.Scrollbar(self.image_frame, orient='vertical', command=canvas.yview)
        x_scrollbar = ttk.Scrollbar(frame, orient='horizontal', command=canvas.xview)

        canvas.configure(yscrollcommand=y_scrollbar.set)
        canvas.configure(xscrollcommand=x_scrollbar.set)

        # confines the scrolling region to be within the image height
        canvas.configure(scrollregion=canvas.bbox("all"))

        # makes canvas scroll along with the mousewheel
        canvas.bind_all("<MouseWheel>", lambda event: self.scroll_on_mousewheel(canvas, event))

        # making all the objects visible

        x_scrollbar.pack(side=BOTTOM, fill=X)
        self.image_frame.pack(fill=BOTH, expand=TRUE)  # expand leaves no empty grey spaces if the image is too small

        # put this right after defining the scrollbar to make it take all of the y-axis
        y_scrollbar.pack(side=RIGHT, fill=Y)
        frame.pack(expand=True)  # "expand = True" centers the image vertically in this case
        canvas.pack()

    def upload_image(self, image_file):

        img = Image.open(image_file)

        render = ImageTk.PhotoImage(img)
        self.render = render  # prevent being garbage collected, might not show up the image otherwise
        w, h = img.size
        print("Image width:", w, "Height:", h)

        # making frame for image canvas
        frame = Frame(self.image_frame, bg="black")
        canvas = Canvas(frame, height=h, width=w, bg="green")

        # puts image into canvas and centers it
        canvas.create_image(w / 2, h / 2, image=render)

        # make 2 scrollbars
        # "master = frame" puts scrollbar next to image. "master = root" puts scrollbar to the side of the main window
        y_scrollbar = ttk.Scrollbar(self.image_frame, orient='vertical', command=canvas.yview)
        x_scrollbar = ttk.Scrollbar(frame, orient='horizontal', command=canvas.xview)

        canvas.configure(yscrollcommand=y_scrollbar.set)
        canvas.configure(xscrollcommand=x_scrollbar.set)

        # confines the scrolling region to be within the image height
        canvas.configure(scrollregion=canvas.bbox("all"))

        # makes canvas scroll along with the mousewheel
        canvas.bind_all("<MouseWheel>", lambda event: self.scroll_on_mousewheel(canvas, event))

        # making all the objects visible

        x_scrollbar.pack(side=BOTTOM, fill=X)
        self.image_frame.pack(fill=BOTH, expand=True)  # expand leaves no empty grey spaces if the image is too small

        # put this right after defining the scrollbar to make it take all of the y-axis
        y_scrollbar.pack(side=RIGHT, fill=Y)
        frame.pack(expand=True)  # "expand = True" centers the image vertically in this case
        canvas.pack()

    def close_image(self):
        list = self.image_frame.pack_slaves()
        for item in list:
            item.destroy()
        self.image_frame.pack_forget()

    def close_files(self):
        self.close_image()
        self.text.set("Page " + "0/0")
        self.current_file = None

    def next_page(self):
        next_page = self.current_file.page + 1

        if self.current_file.get_img(next_page):
            self.close_image()
            self.current_file.page = next_page
            self.text.set("Page " + str(next_page) + "/" + str(self.current_file.num_pages))
            self.upload_image(self.current_file.get_img(next_page))

    def prev_page(self):
        prev_page = self.current_file.page - 1

        if self.current_file.get_img(prev_page):
            self.close_image()
            self.current_file.page = prev_page
            self.text.set("Page " + str(prev_page) + "/" + str(self.current_file.num_pages))
            self.upload_image(self.current_file.get_img(prev_page))

    def rotate_90_degrees(self, filepath):
        """This function rotates the displayed image/page by 90 degrees counter-clockwise"""
        old_file = filepath

        image = Image.open(filepath)
        image = image.rotate(90, expand=True)

        os.remove(old_file)

        image.save(filepath)
        self.close_image()
        self.upload_image(filepath)

    def resize(self, filepath):

        from PIL import Image

        img = Image.open(filepath)
        w, h = img.size
        w_s = 560
        h_s = 750
        img = img.resize((w_s, h_s), Image.ANTIALIAS)
        blank = 0
        img = img.crop((0, -blank, w_s, w_s - blank))
        # img = img.crop((100, 100, w_s+100, h_s-100))
        img.save(filepath)
        self.close_image()
        self.upload_image(filepath)

    def zoomimagelarger(self, filepath):

        from PIL import Image

        img = Image.open(filepath)
        w, h = img.size
        w_s = int(w * 1.15)
        h_s = int(h * 1.15)
        img = img.resize((w_s, h_s), Image.ANTIALIAS)
        blank = (w_s - h_s) * 1.15
        img = img.crop((0, -blank, w_s, w_s - blank))
        img.save(filepath)
        self.close_image()
        self.upload_image(filepath)

    def zoomimagesmaller(self, filepath):

        from PIL import Image

        img = Image.open(filepath)
        w, h = img.size
        w_s = int(w / 1.15)
        h_s = int(h / 1.15)
        img = img.resize((w_s, h_s), Image.ANTIALIAS)
        blank = (w_s - h_s) / 1.15
        img = img.crop((0, -blank, w_s, w_s - blank))
        img.save(filepath)
        self.close_image()
        self.upload_image(filepath)

    def enhance_image(self, filepath, cvalue, bvalue):
        """This function enhance the image to remove text bleed through"""
        old_file = filepath

        image = Image.open(filepath)

        contrast_enhancer = ImageEnhance.Contrast(image)
        bright_enhancer = ImageEnhance.Brightness(image)
        # give the factor to adjust the image
        contrast_image = contrast_enhancer.enhance(cvalue)
        bright_image = bright_enhancer.enhance(bvalue)

        image = contrast_image
        image.save(filepath)

        image = bright_image

        os.remove(old_file)

        image.save(filepath)
        self.close_image()
        self.upload_image(filepath)

    def undo_stack(self, file):
        """This function saves maximum 10 previous changes made by user"""


class File:
    def __init__(self):
        self.img_list = []
        self.current_img = None
        self.init_extension = None
        self.num_pages = 0
        self.page = 1

    def set_img_list(self, lst):
        self.img_list = lst

    def get_img_list(self):
        return self.img_list

    def get_img(self, page):

        lst = self.get_img_list()

        if 0 < page <= len(lst):
            result = lst[page - 1]
            return result
        else:
            pass

    def convert_pdf_to_images(self, pdf_path):
        poppler_path = \
            r'C:\Users\agnes\Documents\DREW\Software Engineering\Release-21.11.0-0\poppler-21.11.0\Library\bin'
        pages = convert_from_path(pdf_path, poppler_path=poppler_path, fmt="png")
        x = 1
        for page in pages:
            page.save("page-%i.png" % x, 'PNG', dpi=(200, 200))
            x += 1

    def upload_files(gui):
        # closes a file if it is open
        if gui.image_frame:
            gui.close_image()

        # file types/extensions allowed
        files = [("All Files", "*.*"), ("PDF", "*.pdf"), ("JPG", "*.jpg"), ("JPEG", "*.jpeg"), ("PNG", "*.png")]

        if not files:
            gui.text.set("Page " + "0/0")

        # gets file path
        files = filedialog.askopenfilenames(filetypes=files)

        file_list = list(files)  # creates a list of with filenames

        print(file_list)
        gui.current_file = File()

        temp_path = tempfile.mkdtemp()

        old = os.getcwd()
        os.chdir(temp_path)

        for file in file_list:
            filename, extension = os.path.splitext(file)
            f_name = os.path.basename(filename)

            if extension == ".pdf":
                gui.current_file.convert_pdf_to_images(file)
            else:
                converted_to_png = f_name + ".png"
                img_file = Image.open(file)
                img_file.save(converted_to_png, dpi=(200, 200))
                img_file.close()

        new_file_list = []

        for filename in os.listdir(temp_path):
            new_file_list.append(filename)
            print(type(filename))

        gui.current_file.set_img_list(new_file_list)

        gui.upload_file_image(gui.current_file.get_img(1))

        list_length = len(new_file_list)
        gui.current_file.num_pages = list_length
        gui.text.set("Page " + "1" + "/" + str(gui.current_file.num_pages))

    def save_as_pdf(self):
        files = [("PDF", "*.pdf")]

        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        random_name = str(uuid.uuid4())
        saver = filedialog.asksaveasfilename(initialfile=random_name, filetypes=files, defaultextension='.pdf')

        # lets the user know that OCR and saving PDF might take a while
        popup_message.be_patient_message()

        mergeFile = PdfFileMerger()

        for img in self.get_img_list():
            pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
            bytes_to_stream = io.BytesIO(pdf_bytes)
            mergeFile.append(PdfFileReader(bytes_to_stream))

        mergeFile.write(saver)

        # lets the user know that OCR and PDF creation is done
        popup_message.PDF_done_message()

    def save_as_images(self):
        # files = [("PNG", "*.png"),
        # ("JPG", "*.jpg"),
        # ("JPEG", "*.jpeg")]

        save_dir = filedialog.askdirectory()
        new_dir = save_dir + '/Edited Images ' + str(random.random())

        os.makedirs(new_dir)
        old_dir = os.getcwd()

        page = 1
        for img in self.get_img_list():
            os.chdir(old_dir)
            image = Image.open(img)
            # image.save(str(uuid.uuid4()))
            os.chdir(new_dir)
            image.save("page-%i.png" % page, dpi=(200, 200))
            page += 1

        os.chdir(old_dir)


# the main method
def main():
    # creates a window
    app = GUI()

    # adds edit options menu
    app.add_edit_options()

    app.add_image_frame()

    # adds the main menu
    app.add_menu()

    # runs the program
    app.mainloop()


main()
