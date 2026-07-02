import threading
import tkinter as tk
from tkinter import scrolledtext
import paho.mqtt.client as mqtt
from placeholder_entry import PlaceholderEntry
from tkinter import filedialog

MQTT_BROKER = "localhost"
MQTT_PORT = 8883
MQTT_TOPIC = "tkinter/terminal/test"

HEADER_FONT = ("Arial", 16, "bold")
NORMAL_FONT = ("Arial", 12)

class MqttCliet:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MQTT Cliet - Dev")
        self.root.geometry("1280x720")
        self.root.config(padx=20, pady=20)

        # --- Grid Column Configuration ---
        # Cols 0 & 1 are for the left panels. Cols 2 & 3 are for the right panels.
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=5)
        self.root.columnconfigure(3, weight=1)

        # Space above Server Info (Row 5) and space below the Status Label (Row 12)
        # This acts like a spring, pushing the Server Info block slightly upward
        self.root.rowconfigure(5, weight=1)
        self.root.rowconfigure(12, weight=1)

        # ==========================================
        # LEFT COLUMN: CREDENTIALS (Rows 0 to 4)
        # ==========================================
        
        # --- Row 0: Creds Title ---
        self.creds_title_label = tk.Label(self.root, text="Credentials", font=HEADER_FONT)
        self.creds_title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 0))

        # --- Row 1: Username Entry ---
        self.username_entry = PlaceholderEntry(self.root, placeholder="Username", font=NORMAL_FONT, justify="center")
        self.username_entry.grid(row=1, column=0, columnspan=2, sticky="ew", ipady=10, pady=5)

        # --- Row 2: Password Entry ---
        self.password_entry = PlaceholderEntry(self.root, placeholder="Password", font=NORMAL_FONT, justify="center")
        self.password_entry.grid(row=2, column=0, columnspan=2, sticky="ew", ipady=10, pady=5)

        # --- Row 3: Anonymous Checkbutton ---
        self.anon_var = tk.BooleanVar(value=False)
        self.anon_check = tk.Checkbutton(self.root, text="Anonymous", variable=self.anon_var, command=self.toggle_creds_input, font=NORMAL_FONT)
        self.anon_check.grid(row=3, column=0, columnspan=2, sticky="w", pady=10)

        # --- Row 4: Action Buttons (Set & Unset) ---
        self.set_btn = tk.Button(self.root, text="Set", font=NORMAL_FONT)
        self.set_btn.grid(row=4, column=0, sticky="ew", ipady=5, padx=(0, 10))
        
        self.unset_btn = tk.Button(self.root, text="Unset", font=NORMAL_FONT)
        self.unset_btn.grid(row=4, column=1, sticky="ew", ipady=5, padx=(10, 0))

        # ==========================================
        # LEFT COLUMN: SERVER INFO (Rows 6 to 10)
        # ==========================================
        
        # --- Row 6: Server Info Title ---
        self.server_title_label = tk.Label(self.root, text="Server Info", font=HEADER_FONT)
        self.server_title_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(20, 5))

        # --- Row 7: Server Address ---
        self.address_entry = PlaceholderEntry(self.root, placeholder="Server Address", font=NORMAL_FONT, justify="center")
        self.address_entry.grid(row=7, column=0, columnspan=2, sticky="ew", ipady=10, pady=5)

        # --- Row 8: Server Port ---
        self.port_entry = PlaceholderEntry(self.root, placeholder="Server Port", font=NORMAL_FONT, justify="center")
        self.port_entry.grid(row=8, column=0, columnspan=2, sticky="ew", ipady=10, pady=5)

        # --- Row 9: TLS Check & CA Cert Selection ---
        self.tls_var = tk.BooleanVar(value=False)
        self.tls_check = tk.Checkbutton(self.root, text="TLS", variable=self.tls_var, command=self.toggle_file_input, font=NORMAL_FONT)
        self.tls_check.grid(row=9, column=0, sticky="w", pady=10)

        # Create a nested frame in column 1 to hold both the Entry and the Button
        self.ca_cert_frame = tk.Frame(self.root)
        self.ca_cert_frame.grid(row=9, column=1, sticky="ew")
        
        # Configure the inner frame so the entry stretches, but the button stays fixed width
        self.ca_cert_frame.columnconfigure(0, weight=1)
        self.ca_cert_frame.columnconfigure(1, weight=0)

        # CA Cert Path Entry
        self.ca_cert_entry = PlaceholderEntry(
            self.ca_cert_frame, placeholder="CA Cert Path", font=NORMAL_FONT
        )
        # Note the ipady=5 matches the height of the button next to it
        self.ca_cert_entry.grid(row=0, column=0, sticky="ew", ipady=5, padx=(0, 5))

        # Browse Button
        self.ca_cert_browse_btn = tk.Button(
            self.ca_cert_frame, text="Browse", font=NORMAL_FONT, command=self.browse_ca_cert
        )
        self.ca_cert_browse_btn.grid(row=0, column=1, sticky="ew", ipady=5)

        # --- Row 10: Connect & Disconnect ---
        self.connect_btn = tk.Button(self.root, text="Connect", font=NORMAL_FONT)
        self.connect_btn.grid(row=10, column=0, sticky="ew", ipady=5, padx=(0, 10))

        self.disconnect_btn = tk.Button(self.root, text="Disconnect", font=NORMAL_FONT)
        self.disconnect_btn.grid(row=10, column=1, sticky="ew", ipady=5, padx=(10, 0))

        # --- Row 11: Connection Status ---
        self.status_label = tk.Label(
            self.root, 
            text="Disconnected", 
            font=HEADER_FONT, 
            fg="red"  # Sets the text color to red
        )
        self.status_label.grid(row=11, column=0, columnspan=2, pady=(30, 0))


        # ==========================================
        # RIGHT COLUMN: TERMINAL & PUBLISH 
        # ==========================================
        # Note: padx=(40, 0) creates the vertical gap between the left and right halves

        # --- Row 0: Subscribe Topic & Button ---
        self.sub_topic_entry = PlaceholderEntry(self.root, placeholder="Topic", font=NORMAL_FONT)
        self.sub_topic_entry.grid(row=0, column=2, sticky="ew", ipady=10, padx=(40, 10))

        self.sub_btn = tk.Button(self.root, text="Subscribe", font=NORMAL_FONT)
        self.sub_btn.grid(row=0, column=3, sticky="ew", ipady=5)

        # --- Rows 1-8: Large Terminal Area ---
        # rowspan=8 forces it to stretch all the way down to the Publish controls
        self.terminal = scrolledtext.ScrolledText(self.root, font=NORMAL_FONT, state="disabled")
        self.terminal.grid(row=1, column=2, columnspan=2, rowspan=8, sticky="nsew", padx=(40, 0), pady=(15, 15))

        # --- Row 9: Publish Topic ---
        self.pub_topic_entry = PlaceholderEntry(self.root, placeholder="Topic", font=NORMAL_FONT)
        self.pub_topic_entry.grid(row=9, column=2, sticky="ew", ipady=10, padx=(40, 10), pady=(0, 5))
        # No widget in column 3 here, leaving the space above the Publish button empty

        # --- Row 10: Publish Message & Button ---
        self.pub_msg_entry = PlaceholderEntry(self.root, placeholder="Message", font=NORMAL_FONT)
        self.pub_msg_entry.grid(row=10, column=2, sticky="ew", ipady=10, padx=(40, 10))

        self.pub_btn = tk.Button(self.root, text="Publish", font=NORMAL_FONT)
        self.pub_btn.grid(row=10, column=3, sticky="ew", ipady=5)


    def run(self) -> None:
        self.toggle_creds_input()
        self.toggle_file_input()
        self.root.mainloop()

    def toggle_creds_input(self) -> None:
        if self.anon_var.get():
            self.username_entry.config(state="disabled")
            self.password_entry.config(state="disabled")
        else:
            self.username_entry.config(state="normal")
            self.password_entry.config(state="normal")

    def toggle_file_input(self) -> None:
        if not self.tls_var.get():
            self.ca_cert_entry.config(state="disabled")
            self.ca_cert_browse_btn.config(state="disabled")
        else:
            self.ca_cert_entry.config(state="normal")
            self.ca_cert_browse_btn.config(state="normal")

    def browse_ca_cert(self):
        """Opens a file dialog to select a CA Certificate and updates the entry."""
        file_path = filedialog.askopenfilename(
            title="Select CA Certificate",
            filetypes=[
                ("Certificate Files", "*.crt;*.pem;*.cer"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            # Clear the entry (including the placeholder if it's there)
            self.ca_cert_entry.delete(0, tk.END)
            # Insert the newly selected file path
            self.ca_cert_entry.insert(0, file_path)
            # Ensure the text color is reset from the grey placeholder color
            self.ca_cert_entry.config(fg="black")

    def log_to_terminal(self, message: str):
        """Safely writes to the read-only terminal and scrolls to the bottom."""
        # 1. Unlock the widget
        self.terminal.config(state="normal")
        
        # 2. Insert the message at the end (with a newline)
        self.terminal.insert(tk.END, message + "\n")
        
        # 3. Auto-scroll to the bottom so the newest messages are always visible
        self.terminal.see(tk.END)
        
        # 4. Lock the widget again
        self.terminal.config(state="disabled")

# --- Main Application Loop ---
if __name__ == "__main__":
    MqttCliet(tk.Tk()).run()