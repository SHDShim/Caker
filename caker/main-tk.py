import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext
from ds_cake import DiffImg
from utils import get_temp_dir, read_any_poni_file, \
        modify_poni_file, modify_file_name
import shutil
import os
import sys
from version import __version__

class CakeFileMakerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CAKE File Maker ver." + str(__version__))

        # Initialize variables
        self.image_files = []
        self.poni_filename = ""
        self.overwrite = tk.BooleanVar(value=True)

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # Label for image files
        self.label_image_files = tk.Label(self.root, text="Select Image Files:")
        self.label_image_files.grid(row=0, column=0, padx=10, pady=5)

        # Button to choose specific image files
        self.button_image_files = tk.Button(self.root, text="Browse Files", command=self.select_image_files)
        self.button_image_files.grid(row=0, column=1, padx=10, pady=5)

        # Button to choose a directory for image files
        self.button_image_folder = tk.Button(self.root, text="Browse Folder", command=self.select_image_folder)
        self.button_image_folder.grid(row=0, column=2, padx=10, pady=5)

        # Display selected image files (increased height)
        self.listbox_image_files = tk.Listbox(self.root, height=15, width=50)  # Height increased by factor of 3
        self.listbox_image_files.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        # Label for PONI file
        self.label_poni_file = tk.Label(self.root, text="PONI File:")
        self.label_poni_file.grid(row=2, column=0, padx=10, pady=5)

        # Textbox to show selected PONI file name (adjusted width)
        self.text_poni_file = tk.Entry(self.root, width=50)  # Width adjusted to match other textboxes
        self.text_poni_file.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

        # Button to choose PONI file
        self.button_poni_file = tk.Button(self.root, text="Browse", command=self.select_poni_file)
        self.button_poni_file.grid(row=2, column=1, padx=10, pady=5)

        # Overwrite checkbox
        self.check_overwrite = tk.Checkbutton(self.root, text="Overwrite", variable=self.overwrite)
        self.check_overwrite.grid(row=4, column=1, columnspan=2, padx=10, pady=5)

        # Button to make cakes
        self.button_make_cakes = tk.Button(self.root, text="Make Cakes", command=self.make_cakes)
        self.button_make_cakes.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Output Text Box for displaying messages (height increased by factor of 3)
        self.output_text = scrolledtext.ScrolledText(self.root, height=30, width=60, wrap=tk.WORD)  # Height increased by factor of 3
        self.output_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        # Redirect print output to text box after initializing the output_text widget
        self.old_stdout = sys.stdout
        sys.stdout = self

    def select_image_files(self):
        """Allow user to select specific image files."""
        file_paths = filedialog.askopenfilenames(title="Select Image Files", filetypes=[("H5 Files", "*.h5")])
        if file_paths:
            self.image_files = list(file_paths)
            self.listbox_image_files.delete(0, tk.END)
            for file in self.image_files:
                self.listbox_image_files.insert(tk.END, file)

    def select_image_folder(self):
        """Allow user to select a folder and get all .h5 files in that folder."""
        directory = filedialog.askdirectory(title="Select a Directory")
        if directory:
            # Search for all .h5 files in the directory and subdirectories
            self.image_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.h5'):
                        self.image_files.append(os.path.join(root, file))

            # Update the listbox with the found .h5 files
            self.listbox_image_files.delete(0, tk.END)
            for file in self.image_files:
                self.listbox_image_files.insert(tk.END, file)

    def select_poni_file(self):
        """Allow user to select a single PONI file."""
        file_path = filedialog.askopenfilename(title="Select PONI File", filetypes=[("PONI Files", "*.poni")])

        if file_path:
            poni_content = read_any_poni_file(file_path)
            if 'poni_version' in poni_content:
                if poni_content['poni_version'] != 2:
                    # Call the function to modify the file
                    output_file = modify_file_name(file_path)
                    modify_poni_file(file_path, output_file)
                else:
                    output_file = file_path
            else:
                output_file = file_path

            self.poni_filename = output_file
            self.text_poni_file.delete(0, tk.END)  # Clear the textbox before inserting new text
            self.text_poni_file.insert(0, output_file)  # Display the PONI file name in the textbox

    def make_cakes(self):
        """Process the images and create CAKE files."""
        if not self.image_files or not self.poni_filename:
            self.write_output("Please select image files and a PONI file.\n")
            return
        
        # Create the DiffImg object
        diff_img = DiffImg()

        for image_file in self.image_files:
            try:
                # Load image file
                diff_img.load(image_file)

                # Set calibration using the PONI file
                diff_img.set_calibration(self.poni_filename)

                # Create temporary directory
                temp_dir = get_temp_dir(image_file)

                # Generate filenames for the temporary files
                tth_filen, azi_filen, int_filen = diff_img.make_temp_filenames(temp_dir=temp_dir, original=True)

                # Integrate and write cake files
                if self.overwrite.get():
                    diff_img.integrate_to_cake()
                    diff_img.write_temp_cakefiles(temp_dir, original=True)
                    self.write_output(f"CAKE files created for {image_file}.\n")
                else:
                    if os.path.exists(tth_filen):
                        self.write_output(f"CAKE files already exist for {image_file}. Skipping integration.\n")
                    else:
                        diff_img.integrate_to_cake()
                        diff_img.write_temp_cakefiles(temp_dir, original=True)
                        self.write_output(f"CAKE files created for {image_file}.\n")

                # Copy PONI file to TEMP directory
                destination_poni = os.path.join(temp_dir, os.path.basename(self.poni_filename))
                if self.overwrite.get():
                    shutil.copy(self.poni_filename, destination_poni)
                    self.write_output(f"PONI file copied for {image_file}.\n")
                else:
                    if not os.path.exists(destination_poni):
                        shutil.copy(self.poni_filename, destination_poni)
                        self.write_output(f"PONI file copied for {image_file}.\n")
                self.write_output('-------------------------------\n\n')
            except Exception as e:
                self.write_output(f"Failed to process {image_file}: {e}\n")

        # Display message after all files are processed
        self.write_output("*** All H5 files were converted. ***\n")

    def write_output(self, message):
        """Write message to the text output box."""
        if self.output_text:
            self.output_text.insert(tk.END, message)
            self.output_text.yview(tk.END)  # Auto scroll to the end
            self.output_text.update_idletasks()  # Force update the UI immediately

    def write(self, message):
        """Override the default print function to capture and display in the text box."""
        self.write_output(message)

    def flush(self):
        """Implement flush to satisfy sys.stdout redirection."""
        pass

def main():
    root = tk.Tk()
    app = CakeFileMakerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
