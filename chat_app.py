import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
from llama_cpp import Llama
import os

class GemmaChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemma AI Chat (With Stop Button)")
        self.root.geometry("600x700")
        
        self.llm = None
        self.stop_flag = False  # דגל לעצירה
        
        # --- חלק עליון: טעינה ---
        self.top_frame = tk.Frame(root, pady=10)
        self.top_frame.pack(fill="x")
        
        self.btn_load = tk.Button(self.top_frame, text="טען מודל (GGUF)", command=self.load_model_thread, bg="#e1e1e1")
        self.btn_load.pack(side="left", padx=10)
        
        self.lbl_status = tk.Label(self.top_frame, text="לא נטען מודל", fg="red")
        self.lbl_status.pack(side="left")

        # --- חלק מרכזי: צ'אט ---
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12), state='disabled')
        self.text_area.pack(padx=10, pady=10, fill="both", expand=True)
        
        # --- חלק תחתון: כפתורים ---
        self.bottom_frame = tk.Frame(root, pady=10)
        self.bottom_frame.pack(fill="x")
        
        self.entry_msg = tk.Text(self.bottom_frame, height=3, font=("Arial", 12))
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=10)
        self.entry_msg.bind("<Return>", lambda event: self.start_generate_thread())

        # כפתור שליחה
        self.btn_send = tk.Button(self.bottom_frame, text="שלח", command=self.start_generate_thread, bg="#4CAF50", fg="white", width=8)
        self.btn_send.pack(side="right", padx=5)

        # כפתור עצירה (מוסתר או כבוי בהתחלה)
        self.btn_stop = tk.Button(self.bottom_frame, text="עצור 🛑", command=self.stop_generation, bg="#f44336", fg="white", state="disabled", width=8)
        self.btn_stop.pack(side="right", padx=5)

    def load_model_thread(self):
        file_path = filedialog.askopenfilename(filetypes=[("GGUF Files", "*.gguf")])
        if not file_path: return
        
        self.lbl_status.config(text="טוען...", fg="orange")
        self.root.update()
        threading.Thread(target=self.load_model, args=(file_path,)).start()

    def load_model(self, model_path):
        try:
            self.llm = Llama(model_path=model_path, n_gpu_layers=0, n_ctx=2048, verbose=False)
            self.lbl_status.config(text=f"מחובר: {os.path.basename(model_path)}", fg="green")
            self.append_text("System", "המודל מוכן.")
        except Exception as e:
            self.lbl_status.config(text="שגיאה", fg="red")
            messagebox.showerror("Error", str(e))

    def stop_generation(self):
        """פונקציה שנקראת כשלוחצים על עצור"""
        self.stop_flag = True

    def start_generate_thread(self):
        if not self.llm:
            messagebox.showwarning("Warning", "קודם תטען מודל!")
            return
            
        user_input = self.entry_msg.get("1.0", tk.END).strip()
        if not user_input: return
        
        self.entry_msg.delete("1.0", tk.END)
        self.append_text("You", user_input + "\n")
        
        # שינוי מצב כפתורים
        self.btn_send.config(state="disabled")
        self.btn_stop.config(state="normal") # מפעיל את כפתור העצירה
        self.stop_flag = False # איפוס דגל העצירה
        
        threading.Thread(target=self.generate_response_stream, args=(user_input,)).start()

    def generate_response_stream(self, user_text):
        try:
            prompt = f"<start_of_turn>user\n{user_text}\n<end_of_turn>\n<start_of_turn>model\n"
            
            self.text_area.config(state='normal')
            self.text_area.insert(tk.END, "Gemma: ", ("bold"))
            self.text_area.tag_config("bold", font=("Arial", 12, "bold"))
            
            stream = self.llm(prompt, max_tokens=512, stop=["<end_of_turn>"], stream=True, echo=False)

            for output in stream:
                # בדיקה האם המשתמש לחץ על עצור
                if self.stop_flag:
                    self.text_area.insert(tk.END, " [נעצר על ידי משתמש]")
                    break
                
                token = output['choices'][0]['text']
                self.text_area.insert(tk.END, token)
                self.text_area.see(tk.END)

            self.text_area.insert(tk.END, "\n\n")
            self.text_area.config(state='disabled')
            
        except Exception as e:
            self.append_text("System", f"Error: {e}")
        finally:
            # החזרת הכפתורים למצב רגיל
            self.btn_send.config(state="normal")
            self.btn_stop.config(state="disabled")

    def append_text(self, sender, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, f"{sender}: ", ("bold"))
        self.text_area.insert(tk.END, f"{message}\n")
        self.text_area.tag_config("bold", font=("Arial", 12, "bold"))
        self.text_area.see(tk.END)
        self.text_area.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = GemmaChatApp(root)
    root.mainloop()
