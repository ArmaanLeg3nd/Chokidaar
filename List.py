try:
    from tkinter import *
    from tkinter import ttk
except ImportError:
    from Tkinter import *
    import ttk

import encode
import json
import mysql.connector
from config import MYSQL_CONFIG
import pyperclip


NORM_FONT = ("Helvetica", 10)
LARGE_FONT = ("Verdana", 13)


class ListWindow(Toplevel):
    def __init__(self, *args):
        Toplevel.__init__(self, *args)
        self.title("List Database")

        self.frame = getTreeFrame(self, bd=3)
        self.frame.pack()


# Lots of Awesomeness
class getTreeFrame(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.addLists()

    def addLists(self, *arg):
        dataList = self.getData()
        headings = ["Service", "Username", "Password"]

        if dataList:
            Label(
                self,
                text="Click the Show Password button to view passwords",
                bd=2,
                font=LARGE_FONT,
            ).pack(side="top")

            scroll = ttk.Scrollbar(self, orient=VERTICAL, takefocus=True)
            self.tree = ttk.Treeview(self, columns=headings, show="headings")
            scroll.config(command=self.tree.yview)
            self.tree.configure(yscroll=scroll.set)

            scroll.pack(side=RIGHT, fill=Y)
            self.tree.pack(side=LEFT, fill="both", expand=1)

            for heading in headings[:-1]:
                self.tree.heading(
                    heading,
                    text=heading,
                    command=lambda c=heading: self.sortby(self.tree, c, 0),
                )
                self.tree.column(heading, width=200)

            self.tree.heading(headings[-1], text="Action", anchor="center")
            self.tree.column(headings[-1], width=100)

            for data in dataList:
                self.tree.insert("", "end", values=data, tags=("entry", "hidden"))

            self.tree.tag_configure("entry", background="white")

            self.tree.bind("<Button-1>", self.onSelect)
            self.tree.bind("<Delete>", self.deleteSelectedEntry)

            self.showPasswordButton = ttk.Button(
                self, text="Show Password", command=self.showPassword, state=DISABLED
            )
            self.showPasswordButton.pack(pady=5)

            self.deleteButton = ttk.Button(
                self, text="Delete", command=self.deleteSelectedEntry, state=DISABLED
            )
            self.deleteButton.pack(pady=5)

        else:
            self.errorMsg()

    def getData(self, *arg):
        # Retrieve data from MySQL database
        cnx = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = cnx.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS passwords ("
            "id INT AUTO_INCREMENT PRIMARY KEY, "
            "service VARCHAR(255) NOT NULL, "
            "username VARCHAR(255), "
            "password VARCHAR(255) NOT NULL)"
        )
        cursor.execute("SELECT service, username, password FROM passwords")
        rows = cursor.fetchall()
        cursor.close()
        cnx.close()

        dataList = []

        for row in rows:
            service = row[0]
            username = row[1] if row[1] else "NO ENTRY"
            password = row[2]
            dataList.append((service, username, "*"))

        return dataList

    def errorMsg(self, *args):
        msg = "There is no data yet!"
        label = Label(self, text=msg, font=NORM_FONT, bd=3, width=30)
        label.pack(side="top", fill="x", pady=10)
        B1 = ttk.Button(self, text="Okay", command=self.master.destroy)
        B1.pack(pady=10)

    def onSelect(self, event):
        item = self.tree.identify_row(event.y)
        self.tree.selection_set(item)
        self.updateButtonState()

    def deleteSelectedEntry(self, event=None):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            service = self.tree.item(item, "values")[0]

            # Delete record from MySQL database
            cnx = mysql.connector.connect(**MYSQL_CONFIG)
            cursor = cnx.cursor()
            cursor.execute("DELETE FROM passwords WHERE service = %s", (service,))
            cnx.commit()
            cursor.close()
            cnx.close()

            self.tree.delete(item)
            self.updateButtonState()

    def showPassword(self):
        self.selected_item = self.tree.focus()
        if self.selected_item:
            service = self.tree.item(self.selected_item, "values")[0]
            tags = self.tree.item(self.selected_item, "tags")
            if "hidden" in tags:
                # Retrieve the password from the MySQL database
                cnx = mysql.connector.connect(**MYSQL_CONFIG)
                cursor = cnx.cursor()
                cursor.execute("SELECT password FROM passwords WHERE service = %s", (service,))
                row = cursor.fetchone()
                if row:
                    password = row[0]
                    decoded_password = encode.decode(password)
                    self.tree.item(
                        self.selected_item,
                        values=(
                            *self.tree.item(self.selected_item, "values")[:2],
                            decoded_password,
                        ),
                    )
                    self.tree.item(self.selected_item, tags=("entry",))
                cursor.close()
                cnx.close()
            else:
                self.tree.item(
                    self.selected_item,
                    values=(*self.tree.item(self.selected_item, "values")[:2], "*"),
                )
                self.tree.item(self.selected_item, tags=("entry", "hidden"))

    def updateButtonState(self):
        if self.tree.selection():
            self.showPasswordButton.config(state=NORMAL)
            self.deleteButton.config(state=NORMAL)
        else:
            self.showPasswordButton.config(state=DISABLED)
            self.deleteButton.config(state=DISABLED)

    def updateList(self, regStr, *args):
        for x in self.tree.get_children(""):
            self.tree.delete(x)
        for data in self.getData():
            if re.search(regStr, data[0]) or re.search(regStr, data[1]):
                self.tree.insert("", "end", values=data)

    def sortby(self, tree, col, descending):
        data = [(tree.set(child, col), child) for child in tree.get_children("")]
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            tree.move(item[1], "", ix)
        tree.heading(
            col, command=lambda col=col: self.sortby(tree, col, int(not descending))
        )


if __name__ == "__main__":
    root = Tk()
    Tk.iconbitmap(root, default="icon.ico")
    Tk.wm_title(root, "Test")
    Label(root, text="Root window").pack()
    new = ListWindow(root)
    root.mainloop()
