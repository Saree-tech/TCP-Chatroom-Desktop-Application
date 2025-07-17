
import socket
import threading
import tkinter as tk

host = '127.0.0.1'
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []
addresses = []  # List to store client addresses
chat_history = {}
lock = threading.Lock()

def broadcast(message):
    with lock:
        for client in clients:
            try:
                client.send(message)
            except Exception:
                pass

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            nickname = nicknames[clients.index(client)]
            
            with lock:
                if nickname not in chat_history:
                    chat_history[nickname] = []
                chat_history[nickname].append(message.decode('ascii'))
                if 'global' not in chat_history:
                    chat_history['global'] = []
                chat_history['global'].append(f"{message.decode('ascii')}")
            
            broadcast(message)
        except Exception:
            with lock:
                if client in clients:
                    index = clients.index(client)
                    nickname = nicknames[index]
                    clients.remove(client)
                    nicknames.remove(nickname)
                    addresses.remove(addresses[index])  # Remove the address as well
                    client.close()
                    broadcast(f'{nickname} left the chat!'.encode('ascii'))
                    update_user_list()
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        
        client.send("".encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        
        with lock:
            nicknames.append(nickname)
            clients.append(client)
            addresses.append(address)  # Store the client address
            
        print(f"Nickname is {nickname}")
        broadcast(f"{nickname} joined the chat!\n".encode('ascii'))
        client.send('Connected to server!'.encode('ascii'))
        update_user_list()
        
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def update_user_list():
    with lock:
        user_list_text.delete(1.0, tk.END)
        user_list_text.insert(tk.END, "Connected Users:\n")
        for nickname, address in zip(nicknames, addresses):
            user_list_text.insert(tk.END, f"{nickname} ({address[0]}:{address[1]})\n")  # Display nickname with address

def admin_broadcast():
    message = admin_message_entry.get()
    if message:
        formatted_message = f"Server: {message}"
        broadcast(formatted_message.encode('ascii'))
        admin_message_entry.delete(0, tk.END)

def view_chat_history():
    nickname = chat_history_entry.get()
    chat_history_text.delete(1.0, tk.END)
    with lock:
        if not nickname:
            chat_history_text.insert(tk.END, "Complete Chat History:\n")
            if 'global' in chat_history:
                for message in chat_history['global'][-50:]:  
                    chat_history_text.insert(tk.END, f"{message}\n")
            else:
                chat_history_text.insert(tk.END, "No messages yet.\n")
        else:
            if nickname in chat_history:
                chat_history_text.insert(tk.END, f"Chat History for {nickname}:\n")
                for message in chat_history[nickname][-50:]:
                    chat_history_text.insert(tk.END, f"{message}\n")
            else:
                chat_history_text.insert(tk.END, f"No chat history found for {nickname}.\n")

def end_session():
    try:
        broadcast("Server is shutting down. Please disconnect.".encode('ascii'))
        with lock:
            for client in clients:
                client.close()
        server.close()
    except Exception as e:
        print(f"Error while shutting down server: {e}")
    finally:
        root.quit()
        root.destroy()

root = tk.Tk()
root.title("Server Admin")
root.geometry("800x600")
root.configure(bg='white')  

# Main layout frames
frame_left = tk.Frame(root, bg='lightblue')  
frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

frame_right = tk.Frame(root, bg='lightgreen') 
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

user_list_label = tk.Label(frame_left, text="Connected Users:", font=("Helvetica", 14), fg="black", bg="lightblue")
user_list_label.pack(pady=10, padx=10, anchor="w")

user_list_text = tk.Text(frame_left, font=("Helvetica", 12), wrap=tk.WORD, bg="white", fg="black", bd=2, relief="solid")
user_list_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

admin_message_label = tk.Label(frame_right, text="Enter Message to Broadcast:", font=("Helvetica", 14), fg="black", bg="lightgreen")
admin_message_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="w")

admin_message_entry = tk.Entry(frame_right, font=("Helvetica", 12), bg="white", fg="black", bd=2, relief="solid")
admin_message_entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew", columnspan=2)

admin_broadcast_button = tk.Button(frame_right, text="Broadcast Message", font=("Helvetica", 14, "bold"), bg="cyan", fg="black", command=admin_broadcast, relief="solid")
admin_broadcast_button.grid(row=2, column=0, columnspan=2, pady=10, padx=10)

chat_history_label = tk.Label(frame_right, text="Enter Nickname to View Chat History:", font=("Helvetica", 14), fg="black", bg="lightgreen")
chat_history_label.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="w")

chat_history_entry = tk.Entry(frame_right, font=("Helvetica", 12), bg="white", fg="black", bd=2, relief="solid")
chat_history_entry.grid(row=4, column=0, padx=10, pady=10, sticky="ew", columnspan=2)

chat_history_button = tk.Button(frame_right, text="View Chat History", font=("Helvetica", 14, "bold"), bg="orange", fg="black", command=view_chat_history, relief="solid")
chat_history_button.grid(row=5, column=0, columnspan=2, pady=10, padx=10)

chat_history_text = tk.Text(frame_right, font=("Helvetica", 12), wrap=tk.WORD, bg="white", fg="black", bd=2, relief="solid")
chat_history_text.grid(row=6, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

end_session_button = tk.Button(frame_right, text="End Session", font=("Helvetica", 14, "bold"), bg="red", fg="white", command=end_session, relief="solid")
end_session_button.grid(row=7, column=0, columnspan=2, pady=20, padx=10)

frame_right.grid_rowconfigure(6, weight=1)
frame_right.grid_columnconfigure(0, weight=1)
frame_right.grid_columnconfigure(1, weight=1)

server_thread = threading.Thread(target=receive, daemon=True)
server_thread.start()

root.mainloop()
