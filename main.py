import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.constants import END
import random
import pyperclip
import json


class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.config(padx=20, pady=20)

        # Apply a modern theme
        self.style = ttk.Style()
        self.style.theme_use("clam")  # Modern theme

        # Load logo
        self.canvas = tk.Canvas(height=200, width=200)
        self.logo_img = tk.PhotoImage(file="logo.png")
        self.canvas.create_image(100, 100, image=self.logo_img)
        self.canvas.grid(row=0, column=1)

        # Labels
        self.website_label = ttk.Label(text="Website:")
        self.website_label.grid(row=1, column=0, sticky="w", pady=5)
        self.email_label = ttk.Label(text="Email/Username:")
        self.email_label.grid(row=2, column=0, sticky="w", pady=5)
        self.password_label = ttk.Label(text="Password:")
        self.password_label.grid(row=3, column=0, sticky="w", pady=5)

        # Entries
        self.website_entry = ttk.Entry(width=25)
        self.website_entry.grid(row=1, column=1, pady=5)
        self.website_entry.focus()

        self.email_entry = ttk.Entry(width=35)
        self.email_entry.grid(row=2, column=1, columnspan=2, pady=5)
        self.email_entry.insert(0, "mihirprasad75")

        # Combobox for common email domains
        self.email_domain = ttk.Combobox(width=12, values=["@gmail.com", "@yahoo.com", "@outlook.com"])
        self.email_domain.grid(row=2, column=2, pady=5)
        self.email_domain.set("@gmail.com")

        # Password Entry with Placeholder and Dynamic Strength Update
        self.password_var = tk.StringVar()
        self.password_var.trace_add("write", self.update_password_strength)  # Bind to password changes
        self.password_entry = ttk.Entry(width=21, textvariable=self.password_var)
        self.password_entry.grid(row=3, column=1, pady=5)
        self.add_placeholder(self.password_entry, "password")  # Add placeholder text

        # Buttons
        self.search_button = ttk.Button(text="Search", width=10, command=self.search_password)
        self.search_button.grid(row=1, column=2, pady=5)

        self.generate_password_button = ttk.Button(text="Generate Password", command=self.generate_password)
        self.generate_password_button.grid(row=3, column=2, pady=5)

        self.add_button = ttk.Button(text="Add", width=36, command=self.save_password)
        self.add_button.grid(row=4, column=1, columnspan=2, pady=10)

        # Password Strength Indicator
        self.strength_label = ttk.Label(text="Password Strength: ")
        self.strength_label.grid(row=5, column=1, columnspan=2, pady=5)

    def add_placeholder(self, entry, placeholder):
        """Add placeholder text to an entry widget."""
        entry.insert(0, placeholder)
        entry.config(foreground="grey")
        entry.bind("<FocusIn>", lambda event: self.clear_placeholder(event, entry, placeholder))
        entry.bind("<FocusOut>", lambda event: self.restore_placeholder(event, entry, placeholder))

    def clear_placeholder(self, event, entry, placeholder):
        """Clear placeholder text when the entry is focused."""
        if entry.get() == placeholder:
            entry.delete(0, END)
            entry.config(foreground="black")

    def restore_placeholder(self, event, entry, placeholder):
        """Restore placeholder text if the entry is empty and loses focus."""
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(foreground="grey")

    def generate_password(self):
        """Generate a random password and insert it into the password entry."""
        letters = [chr(i) for i in range(97, 123)] + [chr(i) for i in range(65, 91)]
        numbers = [str(i) for i in range(10)]
        symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

        password_letters = [random.choice(letters) for _ in range(random.randint(8, 10))]
        password_symbols = [random.choice(symbols) for _ in range(random.randint(2, 4))]
        password_numbers = [random.choice(numbers) for _ in range(random.randint(2, 4))]

        password_list = password_letters + password_symbols + password_numbers
        random.shuffle(password_list)

        password = "".join(password_list)
        self.password_entry.delete(0, END)
        self.password_entry.insert(0, password)
        self.password_entry.config(foreground="black")  # Ensure text color is black
        self.update_password_strength()
        pyperclip.copy(password)  # Copy password to clipboard

    def update_password_strength(self, *args):
        """Update the password strength label dynamically."""
        password = self.password_var.get()
        strength = self.calculate_password_strength(password)
        self.strength_label.config(text=f"Password Strength: {strength}")

    def calculate_password_strength(self, password):
        """Calculate password strength based on length and character diversity."""
        if len(password) < 8:
            return "Weak"
        elif any(c.isdigit() for c in password) and any(c.isalpha() for c in password) and any(c in "!@#$%^&*()" for c in password):
            return "Strong"
        else:
            return "Medium"

    def save_password(self):
        """Save the entered details to a JSON file."""
        website = self.website_entry.get()
        email = self.email_entry.get() + self.email_domain.get()
        password = self.password_var.get()

        if not website or not email or not password or password == "password":
            messagebox.showwarning("Empty Fields", "Please fill in all fields.")
            return

        new_data = {
            website: {
                "email": email,
                "password": password,
            }
        }

        try:
            # Try to read existing data
            with open("passwords.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            # If file doesn't exist, create new data
            data = new_data
        else:
            # Update existing data with new entry
            data.update(new_data)

        # Write updated data back to file
        with open("passwords.json", "w") as file:
            json.dump(data, file, indent=4)

        self.clear_entries()
        messagebox.showinfo("Success", "Password saved successfully!")

    def search_password(self):
        """Search for a website's password and display it."""
        website = self.website_entry.get().lower()

        if not website:
            messagebox.showwarning("Empty Field", "Please enter a website to search.")
            return

        try:
            with open("passwords.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            messagebox.showwarning("Error", "No passwords saved yet.")
        else:
            if website in data:
                email = data[website]["email"]
                password = data[website]["password"]
                messagebox.showinfo(website, f"Email: {email}\nPassword: {password}")
                pyperclip.copy(password)  # Copy password to clipboard
            else:
                messagebox.showwarning("Not Found", f"No details found for {website}.")

    def clear_entries(self):
        """Clear all input fields."""
        self.website_entry.delete(0, END)
        self.email_entry.delete(0, END)
        self.password_entry.delete(0, END)
        self.add_placeholder(self.password_entry, "password")  # Restore placeholder
        self.website_entry.focus()


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManager(root)
    root.mainloop()