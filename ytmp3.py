import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import pkg_resources

class YtDlpGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader (yt-dlp GUI)")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Initialize status_var early
        self.status_var = tk.StringVar(value="Ready")
        
        # Create console first so we can log the installation
        # Set up the main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create console before checking for yt-dlp
        ttk.Label(main_frame, text="Output:").pack(anchor=tk.W)
        self.console = scrolledtext.ScrolledText(main_frame, height=10)
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Check if yt-dlp is installed
        self.check_ytdlp()
        
        # URL input
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(url_frame, text="Video URL:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        paste_button = ttk.Button(url_frame, text="Paste", command=self.paste_url)
        paste_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Download location
        path_frame = ttk.Frame(main_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(path_frame, text="Save to:").pack(side=tk.LEFT)
        self.path_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=60)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        browse_button = ttk.Button(path_frame, text="Browse", command=self.browse_path)
        browse_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Options frame with checkboxes using a Notebook for categories
        options_notebook = ttk.Notebook(main_frame)
        options_notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Format options tab
        format_frame = ttk.Frame(options_notebook, padding="10")
        options_notebook.add(format_frame, text="Format Options")
        
        # Format options
        self.format_var = tk.StringVar(value="bestvideo+bestaudio/best")
        ttk.Label(format_frame, text="Format:").grid(row=0, column=0, sticky=tk.W)
        formats = ["bestvideo+bestaudio/best", "best", "bestvideo", "bestaudio", "worst"]
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, values=formats)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Video options
        self.video_only = tk.BooleanVar()
        video_check = ttk.Checkbutton(format_frame, text="Video only", variable=self.video_only)
        video_check.grid(row=1, column=0, sticky=tk.W)
        
        self.audio_only = tk.BooleanVar()
        audio_check = ttk.Checkbutton(format_frame, text="Audio only", variable=self.audio_only)
        audio_check.grid(row=1, column=1, sticky=tk.W)
        
        # Quality options
        quality_frame = ttk.LabelFrame(format_frame, text="Quality")
        quality_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        self.quality_var = tk.StringVar(value="1080")
        qualities = ["144", "240", "360", "480", "720", "1080", "1440", "2160"]
        ttk.Label(quality_frame, text="Max video quality:").pack(side=tk.LEFT)
        quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var, values=qualities, width=5)
        quality_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Advanced tab
        advanced_frame = ttk.Frame(options_notebook, padding="10")
        options_notebook.add(advanced_frame, text="Advanced Options")
        
        # Subtitle options
        subtitle_frame = ttk.LabelFrame(advanced_frame, text="Subtitles")
        subtitle_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.download_subs = tk.BooleanVar()
        subs_check = ttk.Checkbutton(subtitle_frame, text="Download subtitles", variable=self.download_subs)
        subs_check.pack(anchor=tk.W)
        
        self.auto_subs = tk.BooleanVar()
        auto_subs_check = ttk.Checkbutton(subtitle_frame, text="Download auto-generated subtitles", variable=self.auto_subs)
        auto_subs_check.pack(anchor=tk.W)
        
        # Miscellaneous options
        misc_frame = ttk.LabelFrame(advanced_frame, text="Miscellaneous")
        misc_frame.pack(fill=tk.X)
        
        self.extract_audio = tk.BooleanVar()
        extract_check = ttk.Checkbutton(misc_frame, text="Extract audio", variable=self.extract_audio)
        extract_check.pack(anchor=tk.W)
        
        self.skip_dash = tk.BooleanVar()
        dash_check = ttk.Checkbutton(misc_frame, text="Skip DASH formats (faster)", variable=self.skip_dash)
        dash_check.pack(anchor=tk.W)
        
        self.embed_thumbnail = tk.BooleanVar()
        thumbnail_check = ttk.Checkbutton(misc_frame, text="Embed thumbnail", variable=self.embed_thumbnail)
        thumbnail_check.pack(anchor=tk.W)
        
        # Additional options tab
        extra_frame = ttk.Frame(options_notebook, padding="10")
        options_notebook.add(extra_frame, text="Extra Options")
        
        # Additional command-line options
        ttk.Label(extra_frame, text="Additional yt-dlp options:").pack(anchor=tk.W)
        self.extra_options = tk.StringVar()
        extra_entry = ttk.Entry(extra_frame, textvariable=self.extra_options, width=60)
        extra_entry.pack(fill=tk.X, pady=(0, 10))
        
        options_help = ttk.Label(extra_frame, text="Examples: --playlist-items 1,2,5 --age-limit 18\nSee full options: https://github.com/yt-dlp/yt-dlp#options")
        options_help.pack(anchor=tk.W)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.download_button = ttk.Button(button_frame, text="Download", command=self.start_download)
        self.download_button.pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="Clear", command=self.clear_fields).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(button_frame, text="Exit", command=root.quit).pack(side=tk.RIGHT)
        
        # Output console
        ttk.Label(main_frame, text="Output:").pack(anchor=tk.W)
        self.console = scrolledtext.ScrolledText(main_frame, height=10)
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Set focus to URL entry
        url_entry.focus()

    def check_ytdlp(self):
        """Check if yt-dlp is installed and accessible, install if missing"""
        # First try to check using pkg_resources
        try:
            pkg_resources.get_distribution('yt-dlp')
            self.log_message("yt-dlp is already installed.")
        except pkg_resources.DistributionNotFound:
            # Fall back to command line check
            try:
                subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
                self.log_message("yt-dlp is already installed.")
            except FileNotFoundError:
                self.log_message("yt-dlp not found. Attempting to install automatically...")
                if messagebox.askyesno("yt-dlp Not Found", "yt-dlp is not installed. Would you like to install it now?"):
                    self.install_ytdlp()
                else:
                    self.log_message("ERROR: yt-dlp not installed. You need to install it to use this application.")
                    return
        
        # Check if ffmpeg is installed
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
            self.log_message("ffmpeg is already installed.")
        except FileNotFoundError:
            self.log_message("ffmpeg not found. It's required for audio extraction.")
            if messagebox.askyesno("ffmpeg Not Found", "ffmpeg is not installed but required for audio conversion. Would you like to install it now?"):
                self.install_ffmpeg()
            else:
                self.log_message("WARNING: ffmpeg not installed. Some features like audio extraction may not work.")
    def install_ytdlp(self):
        """Install yt-dlp using pip"""
        self.log_message("Installing yt-dlp...")
        self.status_var.set("Installing yt-dlp...")
        
        def run_install():
            try:
                process = subprocess.Popen(
                    [sys.executable, "-m", "pip", "install", "yt-dlp"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Read and display output
                for line in process.stdout:
                    self.log_message(line.strip())
                    
                process.wait()
                
                if process.returncode == 0:
                    self.log_message("yt-dlp installed successfully!")
                    self.status_var.set("yt-dlp installed successfully!")
                    messagebox.showinfo("Success", "yt-dlp was installed successfully.")
                else:
                    self.log_message(f"Installation failed with code {process.returncode}")
                    self.status_var.set("Installation failed")
                    messagebox.showerror("Error", "Failed to install yt-dlp. Please install it manually with:\npip install yt-dlp")
            except Exception as e:
                self.log_message(f"Installation error: {str(e)}")
                self.status_var.set("Installation error")
                messagebox.showerror("Error", f"An error occurred during installation: {str(e)}")
        
        # Run installation in a separate thread
        threading.Thread(target=run_install, daemon=True).start()

    def paste_url(self):
        """Paste clipboard content into URL field"""
        try:
            clipboard = self.root.clipboard_get()
            self.url_var.set(clipboard)
        except:
            pass

    def browse_path(self):
        """Browse for download directory"""
        path = filedialog.askdirectory(initialdir=self.path_var.get())
        if path:
            self.path_var.set(path)

    def log_message(self, message):
        """Add message to console and ensure it's visible"""
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.console.update_idletasks()

    def clear_fields(self):
        """Clear input fields"""
        self.url_var.set("")
        self.extra_options.set("")
        self.console.delete(1.0, tk.END)
        self.status_var.set("Ready")

    def build_command(self):
        """Build yt-dlp command based on selected options"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return None
            
        cmd = ["yt-dlp"]
        
        # Add ffmpeg location if we installed it
        ffmpeg_path = os.path.join(os.environ['APPDATA'], 'YouTube_Downloader')
        if os.path.exists(os.path.join(ffmpeg_path, 'ffmpeg.exe')):
            cmd.extend(["--ffmpeg-location", ffmpeg_path])
        
        # Format options
        if self.audio_only.get():
            cmd.extend(["-f", "bestaudio", "-x"])
        elif self.video_only.get():
            cmd.extend(["-f", f"bestvideo[height<={self.quality_var.get()}]"])
        else:
            cmd.extend(["-f", f"{self.format_var.get()}[height<={self.quality_var.get()}]/best[height<={self.quality_var.get()}]"])
        
        # Output directory
        output_path = self.path_var.get()
        if output_path:
            cmd.extend(["-o", os.path.join(output_path, "%(title)s.%(ext)s")])
            
        # Subtitle options
        if self.download_subs.get():
            cmd.append("--write-subs")
        if self.auto_subs.get():
            cmd.append("--write-auto-subs")
            
        # Other options
        if self.extract_audio.get():
            cmd.extend(["-x", "--audio-format", "mp3"])
        if self.skip_dash.get():
            cmd.append("--no-check-formats")
        if self.embed_thumbnail.get():
            cmd.append("--embed-thumbnail")
            
        # Additional options
        extra_opts = self.extra_options.get().strip()
        if extra_opts:
            cmd.extend(extra_opts.split())
            
        # Add URL
        cmd.append(url)
        
        return cmd

    def start_download(self):
        """Start the download process in a separate thread"""
        cmd = self.build_command()
        if not cmd:
            return
            
        self.download_button.config(state=tk.DISABLED)
        self.status_var.set("Downloading...")
        
        # Clear console
        self.console.delete(1.0, tk.END)
        
        # Log the command being executed
        self.log_message(f"Executing: {' '.join(cmd)}")
        
        # Start download in a separate thread
        threading.Thread(target=self.download_thread, args=(cmd,), daemon=True).start()

    def download_thread(self, cmd):
        """Run the download command in a separate thread"""
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read and display output
            for line in process.stdout:
                self.log_message(line.strip())
                
            process.wait()
            
            if process.returncode == 0:
                self.status_var.set("Download completed successfully!")
            else:
                self.status_var.set(f"Download failed with code {process.returncode}")
                
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            self.status_var.set("Error occurred during download")
            
        finally:
            # Re-enable the download button
            self.root.after(0, lambda: self.download_button.config(state=tk.NORMAL))
            
    def install_ffmpeg(self):
        """Install ffmpeg"""
        self.log_message("Installing ffmpeg...")
        self.status_var.set("Installing ffmpeg...")
        
        def run_install():
            try:
                # Create a temporary directory for ffmpeg
                import tempfile
                import zipfile
                import urllib.request
                import shutil
                
                temp_dir = tempfile.mkdtemp()
                self.log_message(f"Created temporary directory: {temp_dir}")
                
                # Download ffmpeg
                ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
                zip_path = os.path.join(temp_dir, "ffmpeg.zip")
                
                self.log_message("Downloading ffmpeg...")
                urllib.request.urlretrieve(ffmpeg_url, zip_path)
                self.log_message("Download complete.")
                
                # Extract the zip file
                self.log_message("Extracting ffmpeg...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find the ffmpeg.exe file
                ffmpeg_dir = None
                for root, dirs, files in os.walk(temp_dir):
                    if 'ffmpeg.exe' in files:
                        ffmpeg_dir = root
                        break
                
                if not ffmpeg_dir:
                    raise Exception("Could not find ffmpeg.exe in the downloaded package")
                
                # Create directory in user's AppData
                app_dir = os.path.join(os.environ['APPDATA'], 'YouTube_Downloader')
                os.makedirs(app_dir, exist_ok=True)
                
                # Copy ffmpeg files
                for file in ['ffmpeg.exe', 'ffprobe.exe']:
                    src_file = os.path.join(ffmpeg_dir, file)
                    if os.path.exists(src_file):
                        shutil.copy2(src_file, app_dir)
                        self.log_message(f"Copied {file} to {app_dir}")
                
                # Add to PATH for current session
                if app_dir not in os.environ['PATH']:
                    os.environ['PATH'] += os.pathsep + app_dir
                
                # Clean up
                shutil.rmtree(temp_dir)
                self.log_message("Temporary files cleaned up")
                
                self.log_message("ffmpeg installed successfully!")
                self.status_var.set("ffmpeg installed successfully!")
                messagebox.showinfo("Success", "ffmpeg was installed successfully.")
                
            except Exception as e:
                self.log_message(f"Installation error: {str(e)}")
                self.status_var.set("ffmpeg installation error")
                messagebox.showerror("Error", f"An error occurred during ffmpeg installation: {str(e)}\n\nPlease install ffmpeg manually from https://ffmpeg.org/download.html")
        
        # Run installation in a separate thread
        threading.Thread(target=run_install, daemon=True).start()

def main():
    root = tk.Tk()
    app = YtDlpGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()