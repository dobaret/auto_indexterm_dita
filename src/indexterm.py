# This script searches for a given term in a folder containing DITA files. If the term is found, it adds it to the existing index terms of the file, or it creates an <indexterm> section with the input term.

# Modules
import os
import re
import tkinter as tk
from tkinter import filedialog
from tktooltip import ToolTip

# Define the folder_path variable
folder_path = ""

# Define a function to search for the string
def search_for_string():
    # Check if the folder path is set
    if not folder_path:
        result_label.config(text="Veuillez sélectionner un dossier.")
        return

    # The string to search for, strip removes any leading or trailing whitespace from the string
    search_string = search_entry.get().strip()

    # Check if the search string is empty
    if not search_string:
        result_label.config(text="Vous n'avez pas entré de chaîne, veuillez réessayer.")
        return

    # Convert the search string to lowercase to match no matter the case
    search_terms = [term for term in search_string.split(",")]

    # Check if the search string contains a comma
    if "," in search_string:
        acronym_var.set(0)  # Disable the acronym checkbox
        acronym_checkbox.config(state="disabled")
        search_entry.unbind("<KeyRelease-comma>")  # Unbind the key event for comma
    else:
        acronym_checkbox.config(state="normal")  # Enable the acronym checkbox
        search_entry.bind("<KeyRelease-comma>", on_comma)  # Bind the key event for comma

    # Initialize a dictionary to store the change count for each search term
    change_counts = {term: 0 for term in search_terms}

    # Loop through each search term
    for search_term in search_terms:

        # Convert the search term to lowercase to match no matter the case
        search_term = search_term.lower()

        # Get a list of all DITA files in the folder
        file_list = [f for f in os.listdir(folder_path) if f.endswith(".dita")]

        # Loop through the files in the folder
        for file_name in file_list:

            # Open the file in read mode
            with open(os.path.join(folder_path, file_name), "r", encoding="utf-8") as f:

                # Read the entire file as a string
                file_contents = f.read()
                
            # Check if the search string is in the file
            if search_term in file_contents.lower():

                # Increment the count of files that contain the search term
                change_counts[search_term.lower()] += 1

                # The search string was found, so check if there are any existing indexterm tags
                existing_indexterms = [term.lower() for term in re.findall(r"<indexterm>([^<]*)</indexterm>", file_contents)]
                    
                # If the search string is not in the list of existing indexterms, then,
                if search_term not in existing_indexterms:

                    # If there are existing indexterm tags, add the search string after the last one
                    if len(existing_indexterms) > 0:

                        # Get the index of the last indexterm tag
                        last_index = file_contents.find("</indexterm>")

                        # Add the length of the closing indexterm tag to get the index immediately after it
                        last_index += len("</indexterm>")

                        # Insert the new indexterm after the last indexterm tag
                        if acronym_var.get():
                            new_contents = file_contents[:last_index] + "\n                <indexterm>" + search_term.upper() + "</indexterm>" + file_contents[last_index:]
                        else:
                            new_contents = file_contents[:last_index] + "\n                <indexterm>" + search_term.capitalize() + "</indexterm>" + file_contents[last_index:]

                    # If there are no existing indexterm tags, add the search string after the title or shortdesc tag
                    else:
                        # Check if the shortdesc tag is present in the file
                        if "<critdates>" in file_contents:
                            new_contents = re.sub(
                                r"<critdates>(.*)(?<!<)</critdates>",
                                r"<critdates>\1</critdates>\n        <metadata>\n            <keywords>\n                <indexterm>" + (search_term.upper() if acronym_var.get() else search_term.capitalize()) + "</indexterm>\n            </keywords>\n        </metadata>",
                                file_contents,
                                flags=re.DOTALL
                            )
                        elif "<shortdesc>" in file_contents:
                            # Use the shortdesc tag instead of the title tag
                            new_contents = re.sub(
                                r"<shortdesc>(.*)(?<!<)</shortdesc>",
                                r"<shortdesc>\1</shortdesc>\n    <prolog>\n        <metadata>\n            <keywords>\n                <indexterm>" + (search_term.upper() if acronym_var.get() else search_term.capitalize()) + "</indexterm>\n            </keywords>\n        </metadata>\n    </prolog>",
                                file_contents,
                                flags=re.DOTALL
                            )
                        else:
                            new_contents = re.sub(
                                r"<title>(.*)(?<!<)</title>",
                                r"<title>\1</title>\n    <prolog>\n        <metadata>\n            <keywords>\n                <indexterm>" + (search_term.upper() if acronym_var.get() else search_term.capitalize()) + "</indexterm>\n            </keywords>\n        </metadata>\n    </prolog>",
                                file_contents,
                                count=1
                            )

                    # Open the file in write mode
                    with open(os.path.join(folder_path, file_name), "w", encoding="utf-8") as f:
                        
                        # Write the updated file contents to the file
                        f.write(new_contents)

                        # Increment the change counter
                        change_counts[search_term] += 1

        # Create a list of strings with the count for each search term
        count_strings = [f"{change_counts[term.lower()]} fichier(s) modifié(s) pour \"{term}\"" for term in search_terms]

        # Join the list into a single string with line breaks
        count_string = "\n".join(count_strings)

        # Update the result label with the count string
        result_label.config(text=count_string)
            
# Define a function to browse for the folder path
def browse_folder_path():
    global folder_path
    folder_path = filedialog.askdirectory()

    if folder_path:
        # Check if the selected folder contains any DITA files
        if not any(f.endswith(".dita") for f in os.listdir(folder_path)):
            result_label.config(text="Aucun fichier DITA trouvé dans le dossier sélectionné.")
        else:
            result_label.config(text="")

        folder_label.config(text="Dossier sélectionné :\n{}".format(folder_path))
    else:
        # Do nothing if no folder is selected
        pass

def on_comma(event):
    search_entry.unbind("<KeyRelease-comma>")  # Unbind the key event for comma
    acronym_var.set(0)  # Disable the acronym checkbox
    acronym_checkbox.config(state="disabled")

    # Bind the key event for the backspace key
    search_entry.bind("<KeyRelease-BackSpace>", on_backspace)

def on_backspace(event):
    # Check if the comma was removed
    if "," not in search_entry.get():
        search_entry.bind("<KeyRelease-comma>", on_comma)  # Bind the key event for comma
        acronym_checkbox.config(state="normal")  # Enable the acronym checkbox

# Create a tkinter window
window = tk.Tk()
window.iconbitmap("logo.ico")
window.title("Recherche de termes dans des fichiers DITA")
window.geometry("400x350")
window.resizable(True, True)  # Make the window resizable

# Create a label and button for the folder path
folder_label = tk.Label(window, text="Dossier sélectionné :\n", wraplength=350)
folder_label.pack(fill=tk.X, padx=10, pady=10)  # Fill the label horizontally and add padding
browse_button = tk.Button(window, text="Parcourir", command=browse_folder_path)
browse_button.pack(padx=10, pady=10)

# Create a label and entry for the search string
search_label = tk.Label(window, text="Entrez un ou plusieurs termes :")
search_label.pack(fill=tk.X, padx=10, pady=10)  # Fill the label horizontally and add padding
ToolTip(search_label, msg="Séparez plusieurs termes par des virgules sans espaces entre les mots.")

search_entry = tk.Entry(window)
search_entry.pack(fill=tk.X, padx=10, pady=10)  # Fill the entry horizontally and add padding
search_entry.bind("<KeyRelease-comma>", on_comma)  # Bind the key event for comma

# Create a checkbox for searching acronyms
acronym_var = tk.BooleanVar()
acronym_checkbox = tk.Checkbutton(window, text="Acronyme", variable=acronym_var)
acronym_checkbox.pack(fill=tk.X, padx=10, pady=5)
ToolTip(acronym_checkbox, msg="Si \"Acronyme\" est coché, le terme sera entièrement en majuscules. Possible avec un seul mot.")

# Create a button to start the search
search_button = tk.Button(window, text="Rechercher", command=search_for_string)
search_button.pack(padx=10, pady=10)

# Create a label to display the search results
result_label = tk.Label(window, text="")
result_label.pack(fill=tk.X, padx=10, pady=10)  # Fill the label horizontally and add padding

# Start the tkinter event loop
window.mainloop()