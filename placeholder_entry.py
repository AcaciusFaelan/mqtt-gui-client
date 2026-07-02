import tkinter as tk


class PlaceholderEntry(tk.Entry):

    def __init__(self, master=None, placeholder="Enter text...", *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = "grey"
        self.default_color = self["fg"]  # Save original text color

        # Bind focus events
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

        # Initialize placeholder
        self._add_placeholder()

    def _add_placeholder(self, event=None):
        # If empty, insert placeholder text and make it grey
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)

    def _clear_placeholder(self, event=None):
        # If user clicked in and the text is the placeholder, clear it
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_color)

    def get_actual_text(self) -> str:
        """Helper method to get text without returning the placeholder."""
        current_text = self.get()
        if current_text == self.placeholder:
            return ""
        return current_text

if __name__ == "__main__":
    # --- Example Usage ---
    root = tk.Tk()
    root.geometry("300x100")
    root.title("Placeholder Example")

    # Create the custom entry widget
    entry = PlaceholderEntry(root, placeholder="mqtt.broker.com", font=("Arial", 11))
    entry.pack(pady=15, padx=20, fill="x")

    # Just a dummy widget to click on to test losing focus
    dummy_btn = tk.Button(root, text="Click away to lose focus")
    dummy_btn.pack()

    root.mainloop()