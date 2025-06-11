from bs4 import BeautifulSoup
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, simpledialog
# import pyperclip # Reverted to Tkinter clipboard
# import threading # Not directly used by this application logic
import queue
import concurrent.futures
import json
import os
from datetime import datetime
import traceback

SESSIONS_METADATA_FILE = "sessions_metadata.json"

def extract_content(html_content):
    """
    Extract titles and paragraphs from HTML content.
    
    Args:
        html_content (str): The HTML content to parse
        
    Returns:
        list: A list of tuples containing (title, paragraph)
    """
    # Create BeautifulSoup object
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all heading elements (h1-h6)
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    # Find all paragraph elements
    paragraphs = soup.find_all('p')
    
    # Clean and organize content
    content = []
    current_title = "Untitled Section"
    
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']):
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # Update current title
            current_title = element.get_text().strip()
            current_title = re.sub(r'\s+', ' ', current_title)
        elif element.name == 'p':
            # Get paragraph text and clean it
            text = element.get_text().strip()
            text = re.sub(r'\s+', ' ', text)
            # Only add non-empty paragraphs
            if text:
                content.append((current_title, text))
    
    return content

class ParagraphExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HTML Content Extractor")
        self.root.geometry("800x600")
        self.sessions_file_path = SESSIONS_METADATA_FILE
        
        # Create main frame
        main_frame = tk.Frame(root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input HTML label and text area
        input_label = tk.Label(main_frame, text="Enter HTML Content:", font=("Arial", 12, "bold"))
        input_label.pack(anchor=tk.W)
        
        # Input frame for buttons and text area
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X)
        
        # Input buttons frame
        input_buttons_frame = tk.Frame(input_frame)
        input_buttons_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        # Paste button for input
        paste_input_btn = tk.Button(input_buttons_frame, text="Paste HTML", 
                                  command=self.paste_to_input,
                                  font=("Arial", 9),
                                  bg="#2196F3", fg="white")
        paste_input_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear input button
        clear_input_btn = tk.Button(input_buttons_frame, text="Clear Input", 
                                  command=self.clear_input,
                                  font=("Arial", 9),
                                  bg="#FF5722", fg="white")
        clear_input_btn.pack(side=tk.LEFT, padx=(0,5))
        
        # Save Session button
        save_session_btn = tk.Button(input_buttons_frame, text="Save Session",
                                   command=self.save_session,
                                   font=("Arial", 9),
                                   bg="#FFC107", fg="black")
        save_session_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Load Session button
        load_session_btn = tk.Button(input_buttons_frame, text="Load Session",
                                   command=self.load_session,
                                   font=("Arial", 9),
                                   bg="#03A9F4", fg="white")
        load_session_btn.pack(side=tk.LEFT)
        
        # Frame for Save Directory Input
        save_dir_frame = tk.Frame(input_frame)
        save_dir_frame.pack(fill=tk.X, pady=(5,0))

        save_dir_label = tk.Label(save_dir_frame, text="Save Directory:", font=("Arial", 9))
        save_dir_label.pack(side=tk.LEFT, padx=(0,5))

        self.save_dir_entry = tk.Entry(save_dir_frame, width=50)
        self.save_dir_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
        # Set a default save directory (e.g., a subfolder in the script's directory)
        default_save_path = os.path.join(os.getcwd(), "HTML_Sessions")
        self.save_dir_entry.insert(0, default_save_path)

        browse_save_dir_btn = tk.Button(save_dir_frame, text="Browse",
                                        command=self.browse_save_directory,
                                        font=("Arial", 9),
                                        bg="#607D8B", fg="white")
        browse_save_dir_btn.pack(side=tk.LEFT)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, height=10, width=80)
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Extract button frame
        extract_frame = tk.Frame(main_frame)
        extract_frame.pack(fill=tk.X, pady=10)
        
        # Extract button
        self.extract_button = tk.Button(extract_frame, text="Extract Content", 
                                      command=self.start_extraction,
                                      font=("Arial", 10, "bold"),
                                      bg="#4CAF50", fg="white")
        self.extract_button.pack(side=tk.LEFT)
        
        # Progress label
        self.progress_label = tk.Label(extract_frame, text="", font=("Arial", 9))
        self.progress_label.pack(side=tk.LEFT, padx=10)
        
        # Output label and text area
        output_label = tk.Label(main_frame, text="Extracted Content:", font=("Arial", 12, "bold"))
        output_label.pack(anchor=tk.W)
        
        # Output frame for buttons and text area
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # Output buttons frame
        output_buttons_frame = tk.Frame(output_frame)
        output_buttons_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        # Copy button for output
        copy_output_btn = tk.Button(output_buttons_frame, text="Copy Results", 
                                  command=self.copy_output,
                                  font=("Arial", 9),
                                  bg="#2196F3", fg="white")
        copy_output_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear output button
        clear_output_btn = tk.Button(output_buttons_frame, text="Clear Output", 
                                   command=self.clear_output,
                                   font=("Arial", 9),
                                   bg="#FF5722", fg="white")
        clear_output_btn.pack(side=tk.LEFT)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=15, width=80)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure a tag for bold titles in the output text area
        # Using Arial 12 bold, similar to the section labels
        base_font_family = "Arial" # Or derive from default ScrolledText font if needed
        base_font_size = 10 # Assuming a base size for paragraphs
        self.output_text.tag_configure("bold_title_tag", 
                                     font=(base_font_family, base_font_size + 2, "bold"))
        self.output_text.tag_configure("paragraph_tag",
                                     font=(base_font_family, base_font_size, "normal"))
        self.output_text.tag_configure("separator_tag",
                                     font=(base_font_family, base_font_size, "normal"), 
                                     foreground="gray") # Optional: make separator gray

        # Add some example HTML
        self.input_text.insert(tk.END, """<html>
    <body>
        <h1>Main Title</h1>
        <p>This is the first paragraph under the main title.</p>
        <h2>Subsection</h2>
        <p>This is a paragraph in the subsection.</p>
        <p>This is another paragraph in the same subsection.</p>
        <h3>Sub-subsection</h3>
        <p>This is a paragraph in a deeper subsection.</p>
    </body>
</html>""")
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-v>', lambda e: self.paste_to_input())
        self.root.bind('<Control-c>', lambda e: self.copy_output())
        
        # Thread control
        self.result_queue = queue.Queue()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.root.after(100, self.check_queue)
    
    def check_queue(self):
        """Check for results from the extraction thread and update GUI."""
        try:
            while True: # Process all items currently in the queue
                item = self.result_queue.get_nowait()
                
                if isinstance(item, tuple) and len(item) >= 2: # Ensure it's a tuple with at least type and value
                    msg_type = item[0]
                    msg_value = item[1]

                    if msg_type == "TITLE":
                        self.output_text.insert(tk.END, "\n" + msg_value + "\n", ("bold_title_tag",))
                    elif msg_type == "SEPARATOR":
                        self.output_text.insert(tk.END, msg_value + "\n\n", ("separator_tag",))
                    elif msg_type == "PARAGRAPH":
                        self.output_text.insert(tk.END, msg_value + "\n\n", ("paragraph_tag",))
                    elif msg_type == "MESSAGE":
                        self.output_text.insert(tk.END, msg_value + "\n", ("paragraph_tag",)) # Use paragraph for general messages
                    elif msg_type == "CONTROL":
                        if msg_value == "DONE":
                            self.extract_button.config(state=tk.NORMAL, text="Extract Content")
                            self.update_progress("Done!")
                        elif msg_value == "ERROR" and len(item) >= 3:
                            error_message = item[2]
                            messagebox.showerror("Extraction Error", error_message, parent=self.root)
                            self.extract_button.config(state=tk.NORMAL, text="Extract Content")
                            self.update_progress("Error during extraction.")
                    else:
                        # Fallback for older string-based messages or unknown tuple types
                        if isinstance(msg_value, str):
                             self.output_text.insert(tk.END, msg_value + "\n") # Default insertion
                        
                elif isinstance(item, str): # Handle legacy string messages (e.g., from old queue items if any)
                    self.output_text.insert(tk.END, item + "\n")
                
                if item != ("CONTROL", "DONE") and not (isinstance(item, tuple) and item[0] == "CONTROL" and item[1] == "ERROR"):
                    self.output_text.see(tk.END) # Scroll to the end for new content

        except queue.Empty:
            pass
        except Exception as e:
            print(f"Error in check_queue: {e}\n{traceback.format_exc()}")
            self.extract_button.config(state=tk.NORMAL, text="Extract Content") 
            self.update_progress("GUI Error.")
        finally:
            self.root.after(100, self.check_queue)
    
    def start_extraction(self):
        """Start the extraction process in a separate thread"""
        # Clear output and prepare UI
        self.output_text.delete("1.0", tk.END)
        self.extract_button.config(state=tk.DISABLED, text="Processing...")
        self.update_progress("Extracting content...")
        
        # Get HTML content
        html_content = self.input_text.get("1.0", tk.END)
        
        # Submit extraction task to thread pool
        self.executor.submit(self.extract_and_display, html_content)
    
    def update_progress(self, message):
        """Update the progress label"""
        self.progress_label.config(text=message)
    
    def paste_to_input(self):
        try:
            clipboard_content = self.root.clipboard_get()
            
            # If the input field is not empty, add a newline before pasting
            if self.input_text.get("1.0", tk.END).strip(): 
                self.input_text.insert(tk.END, "\n")
            
            self.input_text.insert(tk.END, clipboard_content)
        except tk.TclError: 
            messagebox.showwarning("Paste Error", "Clipboard is empty or does not contain text.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste content: {str(e)}", parent=self.root)
    
    def copy_output(self):
        try:
            content = self.output_text.get("1.0", tk.END)
            # Use Tkinter's clipboard methods
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.root.update() # Make sure it's immediately available
            messagebox.showinfo("Success", "Content copied to clipboard!", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy content: {str(e)}", parent=self.root)
    
    def clear_input(self):
        self.input_text.delete("1.0", tk.END)
    
    def clear_output(self):
        self.output_text.delete("1.0", tk.END)
    
    def browse_save_directory(self):
        directory = filedialog.askdirectory(parent=self.root, title="Select Save Directory")
        if directory:
            self.save_dir_entry.delete(0, tk.END)
            self.save_dir_entry.insert(0, directory)
    
    def _load_sessions_metadata(self):
        if not os.path.exists(self.sessions_file_path):
            return []
        try:
            with open(self.sessions_file_path, 'r') as f:
                metadata = json.load(f)
                return metadata if isinstance(metadata, list) else []
        except (json.JSONDecodeError, IOError):
            return []

    def _save_sessions_metadata(self, metadata):
        try:
            with open(self.sessions_file_path, 'w') as f:
                json.dump(metadata, f, indent=4)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save session metadata: {str(e)}")
    
    def save_session(self):
        # Generate session name based on current date and time
        current_time = datetime.now()
        session_name = current_time.strftime("Session_%Y-%m-%d_%H-%M-%S")

        # Get the save directory from the entry field
        save_directory = self.save_dir_entry.get().strip()

        if not save_directory:
            messagebox.showerror("Error", "Save directory cannot be empty.", parent=self.root)
            return

        # Ensure the directory exists, create if it doesn't
        if not os.path.exists(save_directory):
            try:
                os.makedirs(save_directory)
                messagebox.showinfo("Directory Created", f"Save directory '{save_directory}' was created.", parent=self.root)
            except OSError as e:
                messagebox.showerror("Error", f"Could not create save directory: {save_directory}\n{str(e)}", parent=self.root)
                return
        elif not os.path.isdir(save_directory):
            messagebox.showerror("Error", f"The specified save path '{save_directory}' is not a directory.", parent=self.root)
            return

        # Construct the full file path
        file_name = f"{session_name}.json"
        file_path = os.path.join(save_directory, file_name)

        # Check if file already exists (optional, could overwrite or ask)
        if os.path.exists(file_path):
            # This case should be rare with timestamped names but could happen if saved within the same second.
            # Or if a user manually names a file the same.
            # For now, let's just overwrite. 
            # Alternatively, could add a counter to the filename or ask user.
            pass 

        data_to_save = {
            "html_content": self.input_text.get("1.0", tk.END),
            "extracted_content": self.output_text.get("1.0", tk.END)
        }

        try:
            with open(file_path, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            
            metadata = self._load_sessions_metadata()
            metadata = [s for s in metadata if s.get("name") != session_name] # Avoid duplicate names if somehow possible
            metadata.append({"name": session_name, "path": file_path})
            self._save_sessions_metadata(metadata)
            
            messagebox.showinfo("Success", f"Session '{session_name}' saved to \n{file_path}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save session: {str(e)}", parent=self.root)

    def load_session(self):
        self.show_load_sessions_dialog()

    def _perform_load_session(self, file_path):
        """Helper to actually load a session from a given path."""
        try:
            with open(file_path, 'r') as f:
                loaded_data = json.load(f)
            
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, loaded_data.get("html_content", ""))
            
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, loaded_data.get("extracted_content", ""))
            messagebox.showinfo("Success", "Session loaded successfully!")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Session file not found: {file_path}")
            # Optionally remove this session from metadata if file is not found
            metadata = self._load_sessions_metadata()
            updated_metadata = [s for s in metadata if s.get("path") != file_path]
            if len(metadata) != len(updated_metadata):
                self._save_sessions_metadata(updated_metadata)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load session: {str(e)}")

    def show_load_sessions_dialog(self):
        sessions_metadata = self._load_sessions_metadata()

        if not sessions_metadata:
            messagebox.showinfo("Load Session", "No saved sessions found.", parent=self.root)
            # Optionally, call the old file dialog
            # file_path = filedialog.askopenfilename(...)
            # if file_path: self._perform_load_session(file_path)
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Load Session")
        dialog.geometry("400x300")
        dialog.transient(self.root) # Keep dialog on top of the main window
        dialog.grab_set() # Modal behavior

        tk.Label(dialog, text="Select a session to load:", font=("Arial", 12)).pack(pady=(10,5))

        sessions_listbox = tk.Listbox(dialog, exportselection=False, height=10)
        for session in sessions_metadata:
            sessions_listbox.insert(tk.END, session.get("name", "Unnamed Session"))
        sessions_listbox.pack(pady=5, padx=10, fill=tk.X, expand=True)

        if not sessions_metadata: # Should not happen if we check earlier, but good for safety
            sessions_listbox.insert(tk.END, "No sessions available.")
            sessions_listbox.config(state=tk.DISABLED)

        def on_load_selected():
            selected_indices = sessions_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select a session to load.", parent=dialog)
                return
            
            selected_index = selected_indices[0]
            selected_session_path = sessions_metadata[selected_index].get("path")
            
            if selected_session_path:
                dialog.destroy()
                self._perform_load_session(selected_session_path)
            else:
                messagebox.showerror("Error", "Selected session path is missing.", parent=dialog)

        def on_delete_selected():
            nonlocal sessions_metadata # Moved to the top of the function
            selected_indices = sessions_listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("No Selection", "Please select a session to delete.", parent=dialog)
                return

            selected_index = selected_indices[0]
            # Ensure sessions_metadata is up-to-date before trying to access it
            # This might be redundant if it's always the one from the outer scope,
            # but good for clarity if there were other modifications.
            current_sessions_list = sessions_metadata 
            session_to_delete = current_sessions_list[selected_index]
            confirm_delete = messagebox.askyesno(
                "Confirm Delete", 
                f"Are you sure you want to delete session '{session_to_delete.get('name')}'?\nThis will not delete the session file itself, only remove it from this list.",
                parent=dialog
            )
            if confirm_delete:
                sessions_listbox.delete(selected_index)
                updated_metadata = [s for i, s in enumerate(current_sessions_list) if i != selected_index]
                self._save_sessions_metadata(updated_metadata)
                sessions_metadata = updated_metadata # Update the non-local variable
                messagebox.showinfo("Success", "Session removed from the list.", parent=dialog)
                if not updated_metadata:
                    sessions_listbox.insert(tk.END, "No sessions available.")
                    sessions_listbox.config(state=tk.DISABLED)

        buttons_frame = tk.Frame(dialog)
        buttons_frame.pack(pady=10, fill=tk.X)

        load_button = tk.Button(buttons_frame, text="Load Selected", command=on_load_selected, bg="#4CAF50", fg="white")
        load_button.pack(side=tk.LEFT, expand=True, padx=(10,5))

        delete_button = tk.Button(buttons_frame, text="Delete from List", command=on_delete_selected, bg="#f44336", fg="white") # Red color
        delete_button.pack(side=tk.LEFT, expand=True, padx=5)

        cancel_button = tk.Button(buttons_frame, text="Cancel", command=dialog.destroy, bg="#9E9E9E", fg="white")
        cancel_button.pack(side=tk.RIGHT, expand=True, padx=(5,10))

        # Center the dialog on the root window
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        dialog.wait_window() # Wait for the dialog to be closed before returning

    def extract_and_display(self, html_content):
        """Extract content and display it in the output area, sending structured chunks to the queue."""
        try:
            content_pairs = extract_content(html_content)

            if content_pairs:
                current_title_text = None # To track changes in title text
                for title, paragraph in content_pairs:
                    if title != current_title_text:
                        self.result_queue.put(("TITLE", title))
                        self.result_queue.put(("SEPARATOR", "=" * len(title)))
                        current_title_text = title
                    self.result_queue.put(("PARAGRAPH", paragraph))
            else:
                self.result_queue.put(("MESSAGE", "No content found in the HTML."))
            
            self.result_queue.put(("CONTROL", "DONE"))

        except Exception as e:
            error_info = ("CONTROL", "ERROR", f"An error occurred during extraction: {str(e)}")
            self.result_queue.put(error_info)
            print(f"Error in extraction thread: {e}")

def main():
    root = tk.Tk()
    app = ParagraphExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
