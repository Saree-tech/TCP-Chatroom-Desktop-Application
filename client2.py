import socket
import threading
from tkinter import *

# Connection Data
SERVER = '127.0.0.1'
PORT = 55555
FORMAT = "utf-8"

# Setting up client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))


class ChatGUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("Chatroom")
        self.root.geometry("600x700")
        self.root.configure(bg="#1C2833")

        self.nickname = ""

        # Show login screen
        self.login_screen()

    def login_screen(self):
        # Clear previous widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title Label
        Label(self.root, text="Welcome to the Chatroom", font="Helvetica 20 bold", bg="#1C2833", fg="#EAECEE").pack(pady=30)

        # Nickname Entry
        Label(self.root, text="Enter Your Nickname", font="Helvetica 14", bg="#1C2833", fg="#ABB2B9").pack(pady=10)
        self.nickname_entry = Entry(self.root, font="Helvetica 14", bg="#566573", fg="#EAECEE", bd=2, relief="solid")
        self.nickname_entry.pack(pady=10)
        self.nickname_entry.focus()

        # Join Chat Button
        Button(self.root, text="Join Chat", font="Helvetica 14 bold", bg="#28B463", fg="#EAECEE", relief="raised", command=self.connect_to_server).pack(pady=20)

    def connect_to_server(self):
        self.nickname = self.nickname_entry.get()
        if self.nickname:
            client.send(self.nickname.encode(FORMAT))
            self.chat_screen()
            threading.Thread(target=self.receive_messages).start()

    def chat_screen(self):
        # Clear previous widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Chat Frame
        self.chat_frame = Frame(self.root, bg="#1C2833")
        self.chat_frame.pack(fill=BOTH, expand=True)

        # Text Area
        self.text_area = Text(self.chat_frame, font="Helvetica 14", bg="#17202A", fg="#EAECEE", state=DISABLED, wrap=WORD)
        self.text_area.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Input Frame
        self.input_frame = Frame(self.root, bg="#566573")
        self.input_frame.pack(fill=X)

        # Message Entry
        self.message_entry = Entry(self.input_frame, font="Helvetica 14", bg="#212F3D", fg="#EAECEE", relief="solid", bd=2)
        self.message_entry.pack(side=LEFT, fill=X, expand=True, padx=10, pady=10)
        self.message_entry.bind("<Return>", lambda _: self.send_message())

        # Send Button
        self.send_button = Button(self.input_frame, text="Send", font="Helvetica 14 bold", bg="#28B463", fg="#EAECEE", relief="raised", command=self.send_message)
        self.send_button.pack(side=LEFT, padx=10, pady=10)

        # Leave Button
        self.leave_button = Button(self.input_frame, text="Leave Chat", font="Helvetica 14 bold", bg="#E74C3C", fg="#EAECEE", relief="raised", command=self.leave_chat)
        self.leave_button.pack(side=RIGHT, padx=10, pady=10)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.message_entry.delete(0, END)
            client.send(f"{self.nickname}: {message}".encode(FORMAT))

    def receive_messages(self):
        while True:
            try:
                message = client.recv(1024).decode(FORMAT)
                self.text_area.config(state=NORMAL)
                if message.startswith("Server:"):
                    self.text_area.insert(END, message + "\n", "server")
                else:
                    self.text_area.insert(END, message + "\n")
                self.text_area.tag_config("server", foreground="red", font="Helvetica 14 bold")
                self.text_area.config(state=DISABLED)
                self.text_area.see(END)
            except:
                client.close()
                break

    def leave_chat(self):
        client.send(f"{self.nickname} left the chat!".encode(FORMAT))
        client.close()
        self.root.destroy()


if __name__ == "__main__":
    app = ChatGUI()
    app.root.mainloop()
