from bs4 import BeautifulSoup
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyperclip
import threading
import queue
import concurrent.futures

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
        clear_input_btn.pack(side=tk.LEFT)
        
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
        """Check for results from the extraction thread"""
        try:
            while True:
                result = self.result_queue.get_nowait()
                if result == "DONE":
                    self.extract_button.config(state=tk.NORMAL, text="Extract Content")
                    self.update_progress("Done!")
                elif result == "ERROR":
                    self.extract_button.config(state=tk.NORMAL, text="Extract Content")
                    self.update_progress("Error occurred")
                else:
                    self.output_text.insert(tk.END, result)
        except queue.Empty:
            pass
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
            clipboard_content = pyperclip.paste()
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert(tk.END, clipboard_content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste content: {str(e)}")
    
    def copy_output(self):
        try:
            content = self.output_text.get("1.0", tk.END)
            pyperclip.copy(content)
            messagebox.showinfo("Success", "Content copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy content: {str(e)}")
    
    def clear_input(self):
        self.input_text.delete("1.0", tk.END)
    
    def clear_output(self):
        self.output_text.delete("1.0", tk.END)
    
    def extract_and_display(self, html_content):
        """Extract content and display it in the output area"""
        try:
            # Extract content
            content = extract_content(html_content)
            
            # Display results
            if content:
                result = []
                current_title = None
                for title, paragraph in content:
                    if title != current_title:
                        result.append(f"\n{title}\n")
                        result.append("=" * len(title) + "\n\n")
                        current_title = title
                    result.append(f"{paragraph}\n\n")
                
                self.result_queue.put("".join(result))
            else:
                self.result_queue.put("No content found in the HTML.")
            
            self.result_queue.put("DONE")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.result_queue.put("ERROR")

def main():
    root = tk.Tk()
    app = ParagraphExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
