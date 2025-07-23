import keyboard
import whisper
import pyperclip
import time
import tkinter as tk
from tkinter import messagebox
import threading
import pyautogui
import sounddevice as sd
import numpy as np
import tempfile
import wave
import os

class BanglaVoiceTypingWhisper:
    def __init__(self):
        self.model = None
        self.is_listening = False
        self.is_recording = False
        self.sample_rate = 16000
        self.channels = 1
        
        # Load Whisper model
        self.load_model()
        
        print("Ready! Press Ctrl+H to start voice typing in Bangla.")
        print("First time usage will download the Whisper model (~1GB)")
    
    def load_model(self):
        """Load Whisper model with progress indication"""
        print("Loading Whisper model... (This may take a moment on first run)")
        try:
            # Use 'base' model for good balance of speed and accuracy
            # Options: tiny, base, small, medium, large
            self.model = whisper.load_model("base")
            print("✅ Whisper model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading Whisper model: {e}")
            raise e
    
    def show_status_window(self, message, bg_color="lightblue"):
        """Show a small status window"""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Create a small status window
        status_window = tk.Toplevel(root)
        status_window.title("Voice Typing")
        status_window.geometry("350x120+100+100")
        status_window.attributes("-topmost", True)
        status_window.configure(bg=bg_color)
        
        label = tk.Label(
            status_window, 
            text=message, 
            font=("Arial", 11), 
            wraplength=330,
            bg=bg_color,
            fg="black"
        )
        label.pack(expand=True, padx=10, pady=10)
        
        return root, status_window, label
    
    def record_audio(self, duration=10):
        """Record audio from microphone"""
        try:
            print(f"🎤 Recording for {duration} seconds...")
            recording = sd.rec(
                int(duration * self.sample_rate), 
                samplerate=self.sample_rate, 
                channels=self.channels,
                dtype=np.float32
            )
            
            # Wait for recording to complete or until stopped
            start_time = time.time()
            while self.is_recording and (time.time() - start_time) < duration:
                sd.sleep(100)  # Check every 100ms
            
            sd.stop()  # Stop recording
            
            # Trim to actual recorded length
            actual_duration = min(time.time() - start_time, duration)
            recording = recording[:int(actual_duration * self.sample_rate)]
            
            return recording.flatten()
            
        except Exception as e:
            print(f"❌ Recording error: {e}")
            return None
    
    def save_audio_temp(self, audio_data):
        """Save audio data to temporary WAV file"""
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_filename = temp_file.name
            temp_file.close()
            
            # Convert float32 to int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            with wave.open(temp_filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 2 bytes for int16
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_int16.tobytes())
            
            return temp_filename
            
        except Exception as e:
            print(f"❌ Error saving audio: {e}")
            return None
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio using Whisper"""
        try:
            # Transcribe with Bangla language hint
            result = self.model.transcribe(
                audio_file, 
                language='bn',  # Bengali language code
                fp16=False  # Use fp32 for better compatibility
            )
            return result["text"].strip()
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return None
    
    def listen_and_transcribe(self):
        """Main function to record, transcribe and paste text"""
        if self.is_listening:
            return
            
        self.is_listening = True
        self.is_recording = True
        
        try:
            # Show initial status
            root, status_window, label = self.show_status_window(
                "🎤 Recording... Speak in Bangla\n(Recording will stop automatically or press Ctrl+H again)", 
                "lightgreen"
            )
            
            def process_audio():
                try:
                    # Record audio
                    audio_data = self.record_audio(duration=10)  # 10 second max
                    
                    if audio_data is None or len(audio_data) == 0:
                        label.configure(text="❌ No audio recorded", bg="lightcoral")
                        status_window.configure(bg="lightcoral")
                        status_window.after(2000, lambda: (status_window.destroy(), root.destroy()))
                        return
                    
                    # Update status
                    label.configure(text="🔄 Processing audio...", bg="yellow")
                    status_window.configure(bg="yellow")
                    
                    # Save to temporary file
                    temp_audio_file = self.save_audio_temp(audio_data)
                    if temp_audio_file is None:
                        label.configure(text="❌ Error saving audio", bg="lightcoral")
                        status_window.configure(bg="lightcoral")
                        status_window.after(2000, lambda: (status_window.destroy(), root.destroy()))
                        return
                    
                    # Transcribe
                    text = self.transcribe_audio(temp_audio_file)
                    
                    # Clean up temp file
                    try:
                        os.unlink(temp_audio_file)
                    except:
                        pass
                    
                    if text and text.strip():
                        print(f"✅ Transcribed: {text}")
                        
                        # Update status
                        display_text = text if len(text) <= 50 else text[:47] + "..."
                        label.configure(text=f"✅ Transcribed: {display_text}", bg="lightgreen")
                        status_window.configure(bg="lightgreen")
                        
                        # Copy to clipboard and paste
                        pyperclip.copy(text)
                        time.sleep(0.1)  # Small delay
                        pyautogui.hotkey('ctrl', 'v')
                        
                        # Close after showing result
                        status_window.after(2000, lambda: (status_window.destroy(), root.destroy()))
                        
                    else:
                        label.configure(text="❌ No speech detected", bg="lightcoral")
                        status_window.configure(bg="lightcoral")
                        status_window.after(2000, lambda: (status_window.destroy(), root.destroy()))
                        
                except Exception as e:
                    print(f"❌ Processing error: {e}")
                    label.configure(text=f"❌ Error: {str(e)[:30]}...", bg="lightcoral")
                    status_window.configure(bg="lightcoral")
                    status_window.after(3000, lambda: (status_window.destroy(), root.destroy()))
                    
                finally:
                    self.is_listening = False
                    self.is_recording = False
            
            # Add button to stop recording early
            stop_btn = tk.Button(
                status_window, 
                text="Stop Recording (or press Ctrl+H)", 
                command=lambda: setattr(self, 'is_recording', False),
                bg="orange"
            )
            stop_btn.pack(pady=5)
            
            # Start processing in separate thread
            thread = threading.Thread(target=process_audio)
            thread.daemon = True
            thread.start()
            
            # Start GUI
            root.mainloop()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.is_listening = False
            self.is_recording = False
    
    def stop_recording(self):
        """Stop current recording"""
        if self.is_recording:
            self.is_recording = False
            print("🛑 Recording stopped by user")
    
    def start_hotkey_listener(self):
        """Start listening for hotkeys"""
        print("\n" + "="*50)
        print("🎤 Bangla Voice Typing Ready!")
        print("="*50)
        print("📌 Press Ctrl+H to start/stop voice recording")
        print("📌 Press Ctrl+Q to quit application")
        print("📌 First transcription may be slower (model loading)")
        print("="*50)
        
        # Register hotkeys
        keyboard.add_hotkey('ctrl+h', self.handle_ctrl_h)
        keyboard.add_hotkey('ctrl+q', self.quit_application)
        
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            print("\n👋 Application stopped by user.")
    
    def handle_ctrl_h(self):
        """Handle Ctrl+H press - start recording or stop current recording"""
        if self.is_recording:
            self.stop_recording()
        elif not self.is_listening:
            self.listen_and_transcribe()
    
    def quit_application(self):
        """Quit the application"""
        print("\n👋 Quitting voice typing application...")
        keyboard.unhook_all()
        exit()

if __name__ == "__main__":
    try:
        print("🚀 Starting Bangla Voice Typing with Whisper...")
        print("📦 Checking required packages...")
        
        # Check imports
        import whisper
        import sounddevice
        import numpy
        import pyperclip
        import pyautogui
        import keyboard
        
        print("✅ All packages found!")
        
        app = BanglaVoiceTypingWhisper()
        app.start_hotkey_listener()
        
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("\n📦 Please install required packages:")
        print("pip install openai-whisper sounddevice numpy pyperclip pyautogui keyboard")
        print("\n💡 Note: First run will download Whisper model (~1GB)")
        input("\nPress Enter to exit...")
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("\nPress Enter to exit...")