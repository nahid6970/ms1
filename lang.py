import keyboard
import speech_recognition as sr
import pyperclip
import time
import tkinter as tk
from tkinter import messagebox
import threading
from googletrans import Translator
import pyautogui

class BanglaVoiceTyping:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.translator = Translator()
        self.is_listening = False
        
        # Adjust for ambient noise
        print("Adjusting for ambient noise... Please wait.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        print("Ready! Press Ctrl+H to start voice typing in Bangla.")
    
    def show_status_window(self, message, duration=3):
        """Show a small status window"""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Create a small status window
        status_window = tk.Toplevel(root)
        status_window.title("Voice Typing")
        status_window.geometry("300x100+100+100")
        status_window.attributes("-topmost", True)
        
        label = tk.Label(status_window, text=message, font=("Arial", 12), wraplength=280)
        label.pack(expand=True)
        
        # Auto close after duration
        status_window.after(duration * 1000, lambda: (status_window.destroy(), root.destroy()))
        
        return root, status_window
    
    def listen_and_transcribe(self):
        """Listen for speech and transcribe in Bangla"""
        if self.is_listening:
            return
            
        self.is_listening = True
        
        try:
            # Show listening status
            root, status_window = self.show_status_window("🎤 Listening... Speak in Bangla", 10)
            
            def listen_thread():
                try:
                    with self.microphone as source:
                        # Listen for audio with timeout
                        audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                    
                    # Update status
                    status_window.configure(bg="yellow")
                    for widget in status_window.winfo_children():
                        widget.configure(text="🔄 Processing...", bg="yellow")
                    
                    # Recognize speech in Bangla
                    try:
                        # Try Google Speech Recognition for Bangla
                        text = self.recognizer.recognize_google(audio, language='bn-BD')
                        print(f"Recognized (Bangla): {text}")
                        
                        # Update status to success
                        for widget in status_window.winfo_children():
                            widget.configure(text=f"✅ Recognized: {text[:50]}...", bg="lightgreen")
                        
                        # Copy to clipboard and paste
                        pyperclip.copy(text)
                        
                        # Small delay to ensure clipboard is ready
                        time.sleep(0.1)
                        
                        # Paste the text
                        pyautogui.hotkey('ctrl', 'v')
                        
                        # Close status window after showing result
                        status_window.after(2000, lambda: (status_window.destroy(), root.destroy()))
                        
                    except sr.UnknownValueError:
                        for widget in status_window.winfo_children():
                            widget.configure(text="❌ Could not understand audio", bg="lightcoral")
                        status_window.after(2000, lambda: (status_window.destroy(), root.destroy()))
                        
                    except sr.RequestError as e:
                        for widget in status_window.winfo_children():
                            widget.configure(text=f"❌ Error: {str(e)}", bg="lightcoral")
                        status_window.after(3000, lambda: (status_window.destroy(), root.destroy()))
                        
                except sr.WaitTimeoutError:
                    for widget in status_window.winfo_children():
                        widget.configure(text="⏰ Listening timeout", bg="lightgray")
                    status_window.after(2000, lambda: (status_window.destroy(), root.destroy()))
                    
                finally:
                    self.is_listening = False
            
            # Start listening in a separate thread
            thread = threading.Thread(target=listen_thread)
            thread.daemon = True
            thread.start()
            
            # Start the GUI event loop
            root.mainloop()
            
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.is_listening = False
    
    def start_hotkey_listener(self):
        """Start listening for the Ctrl+H hotkey"""
        print("Voice typing ready! Press Ctrl+H anywhere to start speaking in Bangla.")
        print("Press Ctrl+Q to quit the application.")
        
        # Register hotkeys
        keyboard.add_hotkey('ctrl+h', self.listen_and_transcribe)
        keyboard.add_hotkey('ctrl+q', self.quit_application)
        
        # Keep the script running
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            print("\nApplication stopped.")
    
    def quit_application(self):
        """Quit the application"""
        print("Quitting voice typing application...")
        keyboard.unhook_all()
        exit()

if __name__ == "__main__":
    try:
        # Check if required modules are available
        import speech_recognition
        import pyperclip
        import pyautogui
        import keyboard
        
        print("Starting Bangla Voice Typing Application...")
        print("Make sure you have an internet connection for speech recognition.")
        
        app = BanglaVoiceTyping()
        app.start_hotkey_listener()
        
    except ImportError as e:
        print(f"Missing required module: {e}")
        print("\nPlease install required packages:")
        print("pip install speechrecognition pyperclip pyautogui keyboard googletrans==4.0.0rc1")
        print("pip install pyaudio")  # For microphone access
        input("Press Enter to exit...")
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")