try:
    from tkinter import *
    from tkinter import ttk
except ImportError:
    from Tkinter import *
    import ttk

import json
import encode

LABEL_FONT = ("Monospace", 12)
BUTTON_FONT = ("Sans-Serif", 10, "bold")
INFO_FONT = ("Verdana", 12)


class AddWindow(Toplevel):
    def __init__(self, *args):
        Toplevel.__init__(self, *args)
        self.title("Add Credentials")
        self.setFrames()

    def setFrames(self, **kwargs):
        add = Frame(self, padx=2, pady=2, bd=3)
        add.pack()

        Label(add, text="Service *", width=30, bd=3, font=LABEL_FONT).pack()
        service = ttk.Entry(add)
        service.pack()

        Label(add, text="Username", width=30, bd=3, font=LABEL_FONT).pack()
        username = ttk.Entry(add)
        username.pack()

        Label(add, text="Password *", width=30, bd=3, font=LABEL_FONT).pack()
        password = ttk.Entry(add, show="*")
        password.pack()

        tag = "Submit"
        for elm in (username, password, service):
            elm.bindtags((tag,) + elm.bindtags())

        self.bind_class(
            tag,
            "<Return>",
            lambda _: self.addClicked(
                info=info, username=username, password=password, service=service
            ),
        )

        s = ttk.Style()
        s.configure("Submit.TButton", font=BUTTON_FONT, sticky="s")

        info = Label(add, width=30, bd=3, fg="red", font=INFO_FONT)
        info.pack()

        addBtn = ttk.Button(
            add,
            text="Add to Manager",
            style="Submit.TButton",
            command=lambda: self.addClicked(
                info=info, username=username, password=password, service=service
            ),
        )

        addBtn.pack()

    def addClicked(self, **kwargs):
        fileName = ".data"
        if kwargs["password"].get() != "" and kwargs["service"].get() != "":
            data = None
            details = [
                kwargs["username"].get(),
                encode.encode(kwargs["password"].get()),
            ]

            try:
                with open(fileName, "r") as outfile:
                    data = outfile.read()
            except IOError:
                open(fileName, "a").close()

            if data:
                data = json.loads(data)
                data[kwargs["service"].get()] = details
            else:
                data = {}
                data[kwargs["service"].get()] = details

            with open(fileName, "w") as outfile:
                outfile.write(json.dumps(data, sort_keys=True, indent=4))

            for widg in ("username", "service", "password"):
                kwargs[widg].delete(0, "end")

            kwargs["info"].config(text="Added!!")
        else:
            kwargs["info"].config(text="Service or Password can't be empty!!")


if __name__ == "__main__":
    root = Tk()
    Tk.iconbitmap(root, default="icon.ico")
    Tk.wm_title(root, "Test")
    Label(root, text="Root window").pack()
    new = AddWindow()
    root.mainloop()
