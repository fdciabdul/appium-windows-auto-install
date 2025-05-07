import subprocess
import os
import tempfile
import urllib.request
import zipfile
import shutil
import webbrowser
from tkinter import messagebox

class BaseInstaller:
    def __init__(self, log_function):
        self.write_log = log_function
        
    def run_command(self, cmd, shell=True):
        try:
            result = subprocess.run(
                cmd, 
                shell=shell, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return "", str(e), -1
            
    def check_command(self, command):
        try:
            subprocess.run(
                [command, "--version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                check=False
            )
            return True
        except:
            return False
    
    def download_file(self, url, destination):
        try:
            self.write_log(f"Downloading {url}...", "yellow")
            urllib.request.urlretrieve(url, destination)
            self.write_log("Download completed.", "green")
            return True
        except Exception as e:
            self.write_log(f"Download failed: {str(e)}", "red")
            return False

class NodeInstaller(BaseInstaller):
    def install(self):
        if not self.check_command("node"):
            self.write_log("Node.js not found. Starting automatic installation...", "yellow")
            
            if not self.install_nodejs():
                self.write_log("Automatic Node.js installation failed.", "red")
                if messagebox.askyesno("Open Download Page", "Open Node.js download page in browser?"):
                    webbrowser.open("https://nodejs.org/en/download/")
                return False
        else:
            stdout, stderr, code = self.run_command("node --version")
            self.write_log(f"Node.js is already installed: {stdout.strip()}", "green")
        return True
            
    def install_nodejs(self):
        arch = "x64" if "64" in os.environ.get("PROCESSOR_ARCHITECTURE", "x86") else "x86"
        
        self.write_log("Downloading Node.js...", "yellow")
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            nodejs_url = f"https://nodejs.org/dist/v20.11.1/node-v20.11.1-{arch}.msi"
            installer_path = os.path.join(temp_dir, "nodejs_installer.msi")
            
            if self.download_file(nodejs_url, installer_path):
                self.write_log("Installing Node.js...", "yellow")
                cmd = f'msiexec /i "{installer_path}" /qn'
                stdout, stderr, code = self.run_command(cmd)
                
                if code == 0:
                    self.write_log("Node.js installed successfully.", "green")
                    os.environ["Path"] = os.environ["Path"] + ";C:\\Program Files\\nodejs"
                    return True
                else:
                    self.write_log(f"Error installing Node.js: {stderr}", "red")
                    return False
            return False
        except Exception as e:
            self.write_log(f"Error installing Node.js: {str(e)}", "red")
            return False
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
                
    def verify(self):
        stdout, stderr, code = self.run_command("node --version")
        
        if code == 0:
            node_version = stdout.strip()
            self.write_log(f"Node.js version: {node_version}", "green")
            return f"Node.js: ✅ {node_version}"
        else:
            self.write_log("Node.js not found or version check failed!", "red")
            return "Node.js: ❌ Not installed or not working properly"

class JavaInstaller(BaseInstaller):
    def install(self):
        if not self.check_command("java"):
            self.write_log("Java not found. Starting automatic installation...", "yellow")
            
            if not self.install_java_jdk():
                self.write_log("Automatic Java installation failed.", "red")
                if messagebox.askyesno("Open Download Page", "Open Java download page in browser?"):
                    webbrowser.open("https://adoptium.net/temurin/releases/")
                return False
        else:
            self.write_log("Java is already installed.", "green")
        return True
            
    def install_java_jdk(self):
        self.write_log("Downloading Adoptium JDK...", "yellow")
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            arch = "x64" if "64" in os.environ.get("PROCESSOR_ARCHITECTURE", "x86") else "x86"
            
            jdk_url = f"https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.10%2B7/OpenJDK17U-jdk_{arch}_windows_hotspot_17.0.10_7.msi"
            installer_path = os.path.join(temp_dir, "jdk_installer.msi")
            
            if self.download_file(jdk_url, installer_path):
                self.write_log("Installing Java JDK...", "yellow")
                cmd = f'msiexec /i "{installer_path}" /qn ADDLOCAL=FeatureMain,FeatureEnvironment,FeatureJarFileRunWith,FeatureJavaHome'
                stdout, stderr, code = self.run_command(cmd)
                
                if code == 0:
                    self.write_log("Java JDK installed successfully.", "green")
                    return True
                else:
                    self.write_log(f"Error installing Java JDK: {stderr}", "red")
                    return False
            return False
        except Exception as e:
            self.write_log(f"Error installing Java JDK: {str(e)}", "red")
            return False
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
                
    def verify(self):
        stdout, stderr, code = self.run_command("java -version", shell=False)
        
        if code == 0:
            java_version = stderr.strip() if stderr else stdout.strip()
            self.write_log(f"Java version: {java_version}", "green")
            return "Java: ✅ Installed"
        else:
            self.write_log("Java not found or version check failed!", "red")
            return "Java: ❌ Not installed or not working properly"

class PlatformToolsInstaller(BaseInstaller):
    def __init__(self, log_function):
        super().__init__(log_function)
        self.android_home = os.path.join(os.path.expanduser("~"), "android-platform-tools")
        self.platform_tools_path = os.path.join(self.android_home, "platform-tools")
        
    def install(self):
        platform_tools_url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
        
        try:
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "platform-tools.zip")
            
            self.write_log(f"Downloading from {platform_tools_url}...", "yellow")
            urllib.request.urlretrieve(platform_tools_url, zip_path)
            self.write_log("Download completed.", "green")
            
            self.write_log("Extracting platform-tools...", "yellow")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            if not os.path.exists(self.android_home):
                os.makedirs(self.android_home)
            
            platform_tools_dir = os.path.join(temp_dir, "platform-tools")
            if os.path.exists(self.platform_tools_path):
                shutil.rmtree(self.platform_tools_path)
            shutil.copytree(platform_tools_dir, self.platform_tools_path)
            self.write_log(f"Android Platform Tools extracted to {self.android_home}", "green")
            
            shutil.rmtree(temp_dir)
            return self.platform_tools_path
        except Exception as e:
            self.write_log(f"Error downloading or extracting Android Platform Tools: {str(e)}", "red")
            self.write_log("You may need to download and install Android Platform Tools manually.", "yellow")
            return None
            
    def setup_environment_variables(self):
        try:
            cmd = f'setx ANDROID_HOME "{self.android_home}" /M'
            stdout, stderr, code = self.run_command(cmd)
            
            if code == 0:
                self.write_log("ANDROID_HOME environment variable set successfully.", "green")
            else:
                self.write_log(f"Error setting ANDROID_HOME: {stderr}", "red")
                return False
                
            cmd = f'setx PATH "%PATH%;{self.platform_tools_path}" /M'
            stdout, stderr, code = self.run_command(cmd)
            
            if code == 0:
                self.write_log("PATH environment variable updated successfully.", "green")
            else:
                self.write_log(f"Error updating PATH: {stderr}", "red")
                return False
                
            os.environ["ANDROID_HOME"] = self.android_home
            os.environ["PATH"] = os.environ["PATH"] + ";" + self.platform_tools_path
            return True
            
        except Exception as e:
            self.write_log(f"Error setting environment variables: {str(e)}", "red")
            return False
            
    def verify(self):
        adb_path = os.path.join(self.platform_tools_path, "adb.exe")
        
        if os.path.exists(adb_path):
            self.write_log(f"Android Platform Tools found at: {self.platform_tools_path}", "green")
            
            stdout, stderr, code = self.run_command(f'"{adb_path}" version')
            
            if code == 0:
                self.write_log(f"ADB version: {stdout.strip()}", "green")
            else:
                self.write_log("ADB found but version check failed!", "yellow")
                
            return "Android Platform Tools: ✅ Installed"
        else:
            self.write_log("Android Platform Tools not found!", "red")
            return "Android Platform Tools: ❌ Not installed or not in the expected location"

class AppiumInstaller(BaseInstaller):
    def install(self):
        if not self.check_command("appium"):
            self.write_log("Installing Appium...", "yellow")
            stdout, stderr, code = self.run_command("npm install -g appium")
            
            if code == 0:
                self.write_log("Appium installed successfully.", "green")
            else:
                self.write_log(f"Error installing Appium: {stderr}", "red")
                self.write_log("You may need to install Appium manually: npm install -g appium", "yellow")
                return False
        else:
            stdout, stderr, code = self.run_command("appium --version")
            self.write_log(f"Appium is already installed: {stdout.strip()}", "green")
        return True
        
    def install_driver(self):
        try:
            stdout, stderr, code = self.run_command("appium driver install uiautomator2")
            
            if code == 0:
                self.write_log("Appium Android Driver (uiautomator2) installed successfully.", "green")
                return True
            else:
                self.write_log(f"Error installing Appium Android Driver: {stderr}", "red")
                self.write_log("You may need to install Appium Android Driver manually: appium driver install uiautomator2", "yellow")
                return False
        except Exception as e:
            self.write_log(f"Error setting up Appium Driver: {str(e)}", "red")
            return False
            
    def verify(self):
        stdout, stderr, code = self.run_command("appium --version")
        
        if code == 0:
            appium_version = stdout.strip()
            self.write_log(f"Appium version: {appium_version}", "green")
            return f"Appium: ✅ {appium_version}"
        else:
            self.write_log("Appium not found or version check failed!", "red")
            return "Appium: ❌ Not installed or not working properly"
            
    def verify_driver(self):
        stdout, stderr, code = self.run_command("appium driver list --installed")
        
        if code == 0 and "uiautomator2" in stdout:
            self.write_log("Appium Android Driver (uiautomator2) is installed.", "green")
            return "Appium Android Driver: ✅ Installed"
        else:
            self.write_log("Appium Android Driver (uiautomator2) not found!", "red")
            return "Appium Android Driver: ❌ Not installed"