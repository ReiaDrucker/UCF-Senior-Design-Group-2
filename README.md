# UCF-Senior-Design-Group-2
UCF Senior Design Project for Stereogram Depth Analysis 

## Installation & Build
### Installing Visual Studio and Python
1. Install Visual Studio 2022 (VS 2022) (Community edition is the free edition: https://visualstudio.microsoft.com/vs/)
2. In the Visual Studio Installer application, under "Workloads" which should be the first window it takes you to after selecting the version of VS 2022, make sure "Python development", "Universal Windows Platform development" and "Desktop development with C++"
3. Go to Python's website and download the latest version of Python 10 (https://www.python.org/downloads/release/python-3104/ as of 4/24/2022)
4. Install Python with all optional installs selected, especially "pip".
5. When the installation is complete, open your start menu and type "edit the system environment variables" and click on that option.
6. In the Advanced section of the System Properties window that should have just popped up, click on the "Environment Variables..." button near the bottom.
7. Under the "System Variables" window, click the "Path" line and click the "Edit..." button.
8. If your new Python installation is not on any line, click the "New" button and add the directory to "python.exe" in the python installation directory (e.g. "C:\Program Files\Python310\").
9. If the Scripts folder of your new Python installation is not on any line, click the "New" button and add the Scripts directory (e.g. "C:\Program Files\Python310\Scripts\").
10. If the directory of Visual Studio's CMake is not on any line, click the "New" button and add it (e.g. "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin")
11. If the directory of Visual Studio's MSVC executable is not on any line, click the. "New" button and add it (e.g. "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.31.31103\bin\Hostx86\x64").
12. To verify these are installed and usable by visual studio, open the Start menu and type "developer command prompt for VS 2022" and open that option. Enter "python --version", "pip --version" and "cmake --version" to make sure they're usable by visual studio and that the versions match what you installed.

### Cloning and pulling the repository
1. Create a Github account if you don't already have one.
2. Install the Github Desktop application and sign in. (Download here: https://desktop.github.com/)
3. Go to File -> Clone Repository (Ctrl + Shift + O)
4. On this repository's main page on the Github website, click on the green Code button.
5. Copy the displayed HTTP URL from the window under the green Code button. (Should be: https://github.com/ReiaDrucker/UCF-Senior-Design-Group-2.git, but something might change. Get the latest link to be certain.)
6. On the Github desktop application, paste the HTTP URL you copied from the website into the URL field in the "Clone a repository" dialog box.
7. Choose a directory on your computer that you can remember, and put it in the "Local path" field in the same dialog box.
8. Click the "Clone" button when done.
9. Make sure you are viewing the "UCF-Senior-Design-Group-2" repository on the Github desktop application.
10. Make sure your Current Branch is set to "main" and click the "Fetch origin" button at the top to ensure you have everything up to date. If there are updates, click the resulting "Pull" button.

### Build
1. Open visual studio and open the "SDF.sln" file in the "GUI_Visual_Studio_Project" folder in the repository you cloned to your computer.
2. Ensure Python 3.10 is being used by going to Tools -> Python -> Python Environments.
3. If Python 3.10 is not shown, add the environment to Visual Studio manually in the same section.
4. Go to Tools -> Command Line -> Developer Command Prompt
5. Navigate to the "depth2" folder of the repository you cloned to your computer.
6. Enter the command "pip install ." This will take a while.
7. After the install is done, go back to Visual Studio and run "gui.py".
8. When the command prompt opens, if there is any error involving a missing Python library, enter the command "pip install <missing library>". Repeat steps 7 and 8 until the GUI opens.
