# This script searches for a given term in a folder containing DITA files. If the term is found, it adds it to the existing index terms of the file, or it creates an <indexterm> section with the input term.

# Modules
import os
import re
import tkinter as tk
from tkinter import filedialog
from idlelib.tooltip import Hovertip
import tkinter.messagebox

# Define the folder_path variable
folder_path = ""

# Define a function to search for the string
def search_for_string():

    # Check if the folder path is set
    if not folder_path:
        clearToTextInput()
        result_label.insert('1.0', "Veuillez sélectionner un dossier.")
        result_label.config(state="disabled")
        return

    else:

        # Check if the selected folder contains any DITA files
        if not any(f.endswith(".dita") for f in os.listdir(folder_path)):
            clearToTextInput()
            result_label.insert('1.0', "Aucun fichier DITA trouvé dans le dossier sélectionné.")
            result_label.config(state="disabled")
            
        else:

            # The string to search for, strip removes any leading or trailing whitespace from the string
            search_string = search_entry.get().strip()

            # Check if the search string is empty
            if not search_string:
                clearToTextInput()
                result_label.insert('1.0', "Vous n'avez pas entré de chaîne, veuillez réessayer.")
                result_label.config(state="disabled")
                return

            # Convert the search string to lowercase to match no matter the case
            search_terms = [term.strip().lower() for term in search_string.split(",")]

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

                                # ('1.0', the new indexterm after the last indexterm tag
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

                count_strings = []
                for term in search_terms:
                    if change_counts[term] == 1 or change_counts[term] == 0:
                        count_strings.append(f"{change_counts[term]} fichier modifié pour \"{term}\"")
                    else:
                        count_strings.append(f"{change_counts[term]} fichiers modifiés pour \"{term}\"")

                # Join the list into a single string with line breaks
                count_string = "\n".join(count_strings)

                # Update the result label with the count string
                clearToTextInput()
                result_label.insert('1.0', count_string)
                result_label.config(state="disabled")
            
# Define a function to browse for the folder path
def browse_folder_path():
    global folder_path
    folder_path = filedialog.askdirectory()

    if folder_path:
        # Check if the selected folder contains any DITA files
        if not any(f.endswith(".dita") for f in os.listdir(folder_path)):
            clearToTextInput()
            result_label.insert('1.0', "Aucun fichier DITA trouvé dans le dossier sélectionné.")
            result_label.config(state="disabled")
        else:
            clearToTextInput()
            result_label.insert('1.0', "")
            result_label.config(state="disabled")

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
window.title("Recherche de termes d'index dans des fichiers DITA")
window.geometry("450x450")
window.resizable(True, True)  # Make the window resizable
window.minsize(450, 450)  # Set the minimum size of the window to the current size

# Create a label and button for the folder path
folder_label = tk.Label(window, text="Dossier sélectionné :\n", wraplength=350)
folder_label.pack(fill=tk.X, padx=10, pady=10)  # Fill the label horizontally and add padding
browse_button = tk.Button(window, text="Parcourir", command=browse_folder_path)
browse_button.pack(padx=10, pady=10)

# Create a label and entry for the search string
search_label = tk.Label(window, text="Entrez un ou plusieurs termes :")
search_label.pack(fill=tk.X, padx=10, pady=10)  # Fill the label horizontally and add padding
myTip = Hovertip(search_label,'Séparez plusieurs termes par des virgules sans espaces entre les mots.')

search_entry = tk.Entry(window)
search_entry.pack(fill=tk.X, padx=10, pady=10)  # Fill the entry horizontally and add padding
search_entry.bind("<KeyRelease-comma>", on_comma)  # Bind the key event for comma

# Create a checkbox for searching acronyms
acronym_var = tk.BooleanVar()
acronym_checkbox = tk.Checkbutton(window, text="Acronyme", variable=acronym_var)
acronym_checkbox.pack(fill=tk.X, padx=10, pady=5)
myTip = Hovertip(acronym_checkbox,'Si \"Acronyme\" est coché, le terme sera entièrement en majuscules. Possible avec un seul mot.')

# Create a button to start the search
search_button = tk.Button(window, text="Rechercher", command=search_for_string)
search_button.pack(padx=10, pady=10)

# Strip empty lines before specific opening tags and add a line break
def strip_empty_lines(file_contents):
    for section in ["body", "refbody", "conbody", "taskbody"]:
        opening_tag = "<{}>".format(section)
        if opening_tag in file_contents:
            start_index = file_contents.index(opening_tag)
            stripped_lines = [line for line in file_contents[:start_index].splitlines() if line.strip()]
            file_contents = "\n".join(stripped_lines) + "\n" + "\t" + file_contents[start_index:]
    return file_contents

# Define a function to be called when the button is clicked
def removal():

    # Check if the folder path is set
    if not folder_path:
        clearToTextInput()
        result_label.insert('1.0', "Veuillez sélectionner un dossier.")
        result_label.config(state="disabled")
        return
    
    if folder_path:

        # Check if the selected folder contains any DITA files
        if not any(f.endswith(".dita") for f in os.listdir(folder_path)):
            clearToTextInput()
            result_label.insert('1.0', "Aucun fichier DITA trouvé dans le dossier sélectionné.")
            result_label.config(state="disabled")

        else:
            
            # Get a list of all DITA files in the folder
            file_list = [f for f in os.listdir(folder_path) if f.endswith(".dita")]

            # Check if any file in the folder contains indexterms
            has_indexterms = False

            # Loop through the files in the folder
            for file_name in file_list:

                # Open the file in read mode
                with open(os.path.join(folder_path, file_name), "r", encoding="utf-8") as f:

                    # Read the entire file as a string
                    file_contents = f.read()

                    if re.search(r"<indexterm>", file_contents, re.IGNORECASE):
                        has_indexterms = True
                        break

            # Prompt the user to confirm that they want to continue
            if has_indexterms:
                confirmed = tkinter.messagebox.askyesno("Confirmation de suppression", "Êtes-vous sûr·e de vouloir supprimer tous les termes d'index de ce dossier ?", icon='warning')
                if not confirmed:
                    return
                
            else:
                clearToTextInput()
                result_label.insert('1.0', "Aucun terme d'index trouvé dans le dossier sélectionné.")
                result_label.config(state="disabled")
                return
            
            # Loop through the files in the folder
            for file_name in file_list:

                # Open the file in read mode
                with open(os.path.join(folder_path, file_name), "r", encoding="utf-8") as f:

                    # Read the entire file as a string
                    file_contents = f.read()

                    # Remove metadata section
                    if "<critdates>" in file_contents and "</critdates>" in file_contents and "<metadata>" in file_contents and "</metadata>" in file_contents:
                        start_index = file_contents.index("<metadata>")
                        end_index = file_contents.index("</metadata>") + len("</metadata>")
                        metadata_section = file_contents[start_index:end_index]
                        file_contents = file_contents.replace(metadata_section, "")

                        file_contents = strip_empty_lines(file_contents)
                    
                    elif "<prolog>" in file_contents and "</prolog>" in file_contents and "<metadata>" in file_contents and "</metadata>" in file_contents and not "<critdates>" in file_contents:
                        start_index = file_contents.index("<prolog>")
                        end_index = file_contents.index("</prolog>") + len("</prolog>")
                        metadata_section = file_contents[start_index:end_index]
                        file_contents = file_contents.replace(metadata_section, "")

                        file_contents = strip_empty_lines(file_contents)
                    
                    elif "<prolog>" in file_contents and "</prolog>" in file_contents and "<metadata>" in file_contents and "</metadata>" in file_contents and "<critdates>" in file_contents:
                        start_index = file_contents.index("<prolog>")
                        end_index = file_contents.index("</prolog>") + len("</prolog>")
                        metadata_section = file_contents[start_index:end_index]
                        file_contents = file_contents.replace(metadata_section, "")

                        file_contents = strip_empty_lines(file_contents)
                
                # Open the file in write mode
                with open(os.path.join(folder_path, file_name), "w", encoding="utf-8") as f:
                    
                    # Write the updated file contents to the file
                    f.write(file_contents)
            
            clearToTextInput()
            result_label.insert('1.0',"Suppression des termes d'index terminée.")
            result_label.config(state="disabled")

# Create a big red button and pack it at the bottom of the window
button = tk.Button(window, text="Suppression des termes d'index", bg="red", fg="white", command=removal)
button.pack(side=tk.BOTTOM, padx=10, pady=10)

#Define a function to clear the input text
def clearToTextInput():
    result_label.configure(state='normal')
    result_label.delete("1.0","end")
    result_label.config(wrap="word")

# Create a scrollbar widget and pack it on the right side of the window
scrollbar = tk.Scrollbar(window)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create a label to display the search results and attach it to the scrollbar
result_label = tkinter.Text(window, yscrollcommand=scrollbar.set)
result_label.pack(fill=tk.X, padx=10, pady=10)

# Configure the scrollbar to control the label's scrolling
scrollbar.config(command=result_label.yview)

# Start the tkinter event loop
window.mainloop()