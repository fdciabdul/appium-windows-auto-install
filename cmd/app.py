import tkinter as tk
from tkinter import scrolledtext, messagebox
import customtkinter as ctk
import os
import ctypes
import threading
from cmd.installers import NodeInstaller, JavaInstaller, PlatformToolsInstaller, AppiumInstaller

class AppiumSetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("APPIUM WINDOWS AUTO INSTALLER")
        self.root.geometry("525x700")
        
        self.install_steps = [
            "Checking administrator rights",
            "Installing Node.js",
            "Installing Appium",
            "Downloading Android Platform Tools",
            "Setting up Android environment variables",
            "Installing Java JDK",
            "Setting up Appium Driver"
        ]
        
        self.total_steps = len(self.install_steps)
        self.setup_ui()
        
    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.root.configure(bg="#1E1E1E")
        
        title_font = ("Arial", 18, "bold")
        normal_font = ("Consolas", 10)
        primary_color = "#007BFF"
        dark_bg = "#1E1E1E"
        button_color = "#0056b3"
        hover_color = "#004494"
        
        # Calculate proper dimensions based on window size
        window_width = 525
        content_width = window_width - 20  # Full width minus padding
        
        title_label = ctk.CTkLabel(
            self.root, 
            text="APPIUM WINDOWS AUTO INSTALLER",
            font=title_font,
            text_color="white",
            width=content_width,
            height=30
        )
        title_label.place(x=10, y=10)
        
        description_label = ctk.CTkLabel(
            self.root,
            text="This utility will install and configure everything needed for Appium Android testing on Windows.",
            font=normal_font,
            text_color="#AAAAAA",
            wraplength=content_width,
            width=content_width,
            height=40,
            justify="left"
        )
        description_label.place(x=10, y=40)
        
        # Button and progress area
        button_width = 160
        verify_button_x = 10 + button_width + 10  # First button width + padding
        
        self.install_button = ctk.CTkButton(
            self.root,
            text="INSTALL ALL",
            font=("Arial", 12, "bold"),
            text_color="#FFFFFF",
            fg_color=button_color,
            hover_color=hover_color,
            border_width=1,
            border_color="#FFFFFF",
            command=self.start_installation,
            width=button_width,
            height=40
        )
        self.install_button.place(x=10, y=90)
        
        self.verify_button = ctk.CTkButton(
            self.root,
            text="VERIFY INSTALLATION",
            font=("Arial", 12, "bold"),
            text_color="#FFFFFF",
            fg_color="#333333",
            hover_color="#222222",
            border_width=1,
            border_color="#FFFFFF",
            command=self.verify_installation,
            width=button_width,
            height=40
        )
        self.verify_button.place(x=verify_button_x, y=90)
        
        # Progress bar positioning
        progress_x = verify_button_x + button_width + 10
        progress_width = window_width - progress_x - 10
        
        self.progress_bar = ctk.CTkProgressBar(
            self.root,
            orientation="horizontal",
            progress_color=primary_color,
            fg_color="#333333",
            width=progress_width,
            height=15
        )
        self.progress_bar.place(x=progress_x, y=95)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            self.root,
            text="0%",
            font=normal_font,
            text_color="white",
            width=progress_width,
            height=20
        )
        self.progress_label.place(x=progress_x, y=115)
        
        # Log text area - extending to full window width
        self.log_text_frame = ctk.CTkFrame(
            self.root,
            fg_color="#000000",
            border_width=1,
            border_color="#444444",
            width=content_width,
            height=530
        )
        self.log_text_frame.place(x=10, y=150)
        
        self.log_text = scrolledtext.ScrolledText(
            self.log_text_frame,
            wrap=tk.WORD,
            width=61,  # Adjusted for proper fit with wider frame
            height=30,
            font=("Consolas", 9),
            bg="#000000",
            fg="#AAAAAA",
            insertbackground="white",
            selectbackground=primary_color
        )
        self.log_text.pack(padx=5, pady=5, fill="both", expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        self.setup_log_colors()
        
    def setup_log_colors(self):
        self.log_text.tag_configure("black", foreground="#AAAAAA")
        self.log_text.tag_configure("red", foreground="#FF3333")
        self.log_text.tag_configure("green", foreground="#00AA00")
        self.log_text.tag_configure("yellow", foreground="#AAAA00")
        self.log_text.tag_configure("blue", foreground="#3333FF")
        self.log_text.tag_configure("darkblue", foreground="#0000AA")
        self.log_text.tag_configure("darkgreen", foreground="#006600")
        
    def write_log(self, message, color="black"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n", color)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
        
    def update_progress(self, step, status):
        percent = (step / self.total_steps) * 100
        self.progress_bar.set(percent / 100)
        self.progress_label.configure(text=f"{int(percent)}%")
        self.write_log(f"[{step}/{self.total_steps}] {status}", "blue")
            
    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
            
    def start_installation(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.write_log("Starting installation process...", "darkgreen")
        threading.Thread(target=self.install_components, daemon=True).start()
        
    def install_components(self):
        try:
            step = 1
            self.update_progress(step, self.install_steps[0])
            
            if not self.is_admin():
                self.write_log("Not running as Administrator. Some steps may fail.", "red")
                if messagebox.askyesno("Admin Rights", "This script requires administrative privileges. Continue anyway?"):
                    self.write_log("Continuing without admin rights...", "yellow")
                else:
                    self.write_log("Installation cancelled.", "red")
                    return
            else:
                self.write_log("Running with administrative privileges.", "green")
            
            node_installer = NodeInstaller(self.write_log)
            java_installer = JavaInstaller(self.write_log)
            platform_tools_installer = PlatformToolsInstaller(self.write_log)
            appium_installer = AppiumInstaller(self.write_log)
            
            step += 1
            self.update_progress(step, self.install_steps[1])
            self.write_log("\nChecking for Node.js...", "darkblue")
            if not node_installer.install():
                return
                
            step += 1
            self.update_progress(step, self.install_steps[2])
            self.write_log("\nChecking for Appium...", "darkblue")
            if not appium_installer.install():
                return
                
            step += 1
            self.update_progress(step, self.install_steps[3])
            self.write_log("\nDownloading Android Platform Tools...", "darkblue")
            platform_tools_path = platform_tools_installer.install()
            if not platform_tools_path:
                return
                
            step += 1
            self.update_progress(step, self.install_steps[4])
            self.write_log("\nSetting up Android environment variables...", "darkblue")
            if not platform_tools_installer.setup_environment_variables():
                return
                
            step += 1
            self.update_progress(step, self.install_steps[5])
            self.write_log("\nChecking for Java...", "darkblue")
            if not java_installer.install():
                return
                
            step += 1
            self.update_progress(step, self.install_steps[6])
            self.write_log("\nSetting up Appium Android Driver...", "darkblue")
            if not appium_installer.install_driver():
                return
            
            self.progress_bar.set(1)
            self.progress_label.configure(text="100%")
            self.write_log("\nInstallation complete!", "green")
            self.write_log("You can now verify the installation by clicking the 'VERIFY INSTALLATION' button.", "blue")
            
        except Exception as e:
            self.write_log(f"Error during installation: {str(e)}", "red")
            self.write_log("Installation failed. Please check the logs for details.", "red")
            
    def verify_installation(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.write_log("Verifying installation...", "darkgreen")
        threading.Thread(target=self.verify_components, daemon=True).start()
        
    def verify_components(self):
        verification_results = []
        
        try:
            node_installer = NodeInstaller(self.write_log)
            java_installer = JavaInstaller(self.write_log)
            platform_tools_installer = PlatformToolsInstaller(self.write_log)
            appium_installer = AppiumInstaller(self.write_log)
            
            self.write_log("\nChecking Node.js...", "darkblue")
            node_result = node_installer.verify()
            verification_results.append(node_result)
            
            self.write_log("\nChecking Appium...", "darkblue")
            appium_result = appium_installer.verify()
            verification_results.append(appium_result)
            
            self.write_log("\nChecking Java...", "darkblue")
            java_result = java_installer.verify()
            verification_results.append(java_result)
            
            self.write_log("\nChecking Android Platform Tools...", "darkblue")
            platform_tools_result = platform_tools_installer.verify()
            verification_results.append(platform_tools_result)
            
            self.write_log("\nChecking Appium Android Driver...", "darkblue")
            driver_result = appium_installer.verify_driver()
            verification_results.append(driver_result)
            
            self.write_log("\nVerification Summary:", "darkblue")
            for result in verification_results:
                if "❌" in result:
                    self.write_log(result, "red")
                else:
                    self.write_log(result, "green")
                    
        except Exception as e:
            self.write_log(f"Error during verification: {str(e)}", "red")