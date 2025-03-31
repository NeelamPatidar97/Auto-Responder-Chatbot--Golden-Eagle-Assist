import tkinter as tk
from tkinter import messagebox, PhotoImage
import requests
import webbrowser


class AutoResponderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CalState LA Auto Responder App")
        self.root.geometry("400x600")
        self.root.configure(bg="#000000")

        # Add Header Bar
        self.header_frame = tk.Frame(root, bg="#FFC72C")
        self.header_frame.pack(fill=tk.X)

        # Add an Icon to the Header (Left Side)
        self.header_icon = PhotoImage(file="calstatela_logo.png")  # Replace with your logo file
        self.header_icon = self.header_icon.subsample(64, 68)  # Resize the logo for the header
        self.icon_label = tk.Label(self.header_frame, image=self.header_icon, bg="#FFC72C")
        self.icon_label.pack(side=tk.LEFT, padx=10)

        # Header Label (Center Position)
        self.header_label = tk.Label(
            self.header_frame,
            text="GOLDEN EAGLE ASSIST",
            bg="#FFC72C",
            fg="#000000",
            font=("Arial", 16, "bold"),
            pady=10,
        )
        self.header_label.pack(side=tk.LEFT, padx=10)

        # Messaging frame with scrollbar
        self.chat_canvas_frame = tk.Frame(root, bg="#000000")
        self.chat_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add a vertical scrollbar
        self.scrollbar = tk.Scrollbar(self.chat_canvas_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_canvas = tk.Canvas(self.chat_canvas_frame, bg="#000000", highlightthickness=0, yscrollcommand=self.scrollbar.set)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar.config(command=self.chat_canvas.yview)

        self.chat_display = tk.Frame(self.chat_canvas, bg="#000000")
        self.chat_window = self.chat_canvas.create_window((0, 0), window=self.chat_display, anchor="nw")

        self.chat_display.bind("<Configure>", self.auto_scroll)
        self.chat_canvas.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        self.chat_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Message entry
        self.entry_frame = tk.Frame(root, bg="#000000")
        self.entry_frame.pack(fill=tk.X, padx=5, pady=5)

        self.message_entry = tk.Entry(self.entry_frame, width=30, font=("Arial", 12), bg="#ffffff", fg="#000000", relief="flat")
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.message_entry.insert(0, "Enter your question here ...")
        self.message_entry.bind("<FocusIn>", lambda e: self.message_entry.delete(0, tk.END))
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        # Load the send icon
        self.send_icon = PhotoImage(file="send_icon.png")  # Replace with your send icon file
        self.send_icon = self.send_icon.subsample(5, 5)  # Adjust the size of the icon here

        self.send_button = tk.Button(
            self.entry_frame,
            image=self.send_icon,
            command=self.send_message,
            bg="#000000",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
        )
        self.send_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # Footer
        self.footer_frame = tk.Frame(root, bg="#000000")
        self.footer_frame.pack(pady=5)
        self.footer_label = tk.Label(self.footer_frame, text="© Powered by Cal State LA ", bg="#000000", fg="#FFC72C", font=("Arial", 10))
        self.footer_label.pack()

    def _on_mousewheel(self, event):
        self.chat_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def auto_scroll(self, event=None):
        """Automatically scrolls to the bottom of the canvas."""
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.yview_moveto(1.0)

    def send_message(self):
        user_message = self.message_entry.get().strip()
        if not user_message:
            messagebox.showerror("Error", "Please enter a message.")
            return

        # Display user message
        self.add_message("You", user_message, align="e", bubble_color="#FFC72C", text_color="#000000")
        self.message_entry.delete(0, tk.END)

        # Send message to chatbot server
        try:
            payload = {"sender": "user", "message": user_message}
            url = "https://b520-35-194-133-232.ngrok-free.app/webhooks/rest/webhook"
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                bot_response = response.json()
                if bot_response:
                    for resp in bot_response:
                        self.add_message("Golden Eagle Assist", resp.get('text', '...'), align="w", bubble_color="#333333", text_color="#FFC72C")
                else:
                    self.add_message("Golden Eagle Assist", "Sorry, I didn't understand that.", align="w", bubble_color="#333333", text_color="#FFC72C")
            else:
                self.add_message("Golden Eagle Assist", f"Error: Server returned status code {response.status_code}.", align="w", bubble_color="#333333", text_color="#FFC72C")
        except Exception as e:
            self.add_message("Golden Eagle Assist", f"Error: {e}", align="w", bubble_color="#333333", text_color="#FFC72C")

    def add_message(self, sender, message, align="w", bubble_color="#333333", text_color="#FFC72C"):
        # Set alignment dynamically based on sender
        align = "e" if sender == "You" else "w"
        bubble_color = "#FFC72C" if sender == "You" else "#333333"
        text_color = "#000000" if sender == "You" else "#FFC72C"
        
        # Create a bubble frame
        bubble_frame = tk.Frame(self.chat_display, bg="#000000")
        bubble_frame.pack(anchor=align, pady=2, padx=5)

        # Add sender label
        sender_label = tk.Label(bubble_frame, text=sender, bg="#000000", fg=text_color, font=("Arial", 8, "italic"))
        sender_label.pack(anchor=align, pady=2)

        # Add message bubble
        bubble = tk.Label(
            bubble_frame,
            text=message,
            wraplength=300,
            bg=bubble_color,
            fg=text_color,
            font=("Arial", 10),
            padx=8,
            pady=4,
            justify="left",
            relief="ridge",
            bd=2
        )
        bubble.pack(anchor=align)

        # Add clickable link handling for URLs
        words = message.split()
        for word in words:
            if word.startswith("http://") or word.startswith("https://"):
                bubble.bind("<Button-1>", lambda e, url=word: self.open_link(url))
                bubble.config(cursor="hand2")

        # Auto-scroll to the bottom after adding a message
        self.auto_scroll()

    def open_link(self, url):
        webbrowser.open_new_tab(url)


# Main loop
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoResponderApp(root)
    root.mainloop()
