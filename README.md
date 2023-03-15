# auto_indexterm_dita

This script searches for a given term in a folder containing DITA files.

If the term is found, it adds it to the existing index terms of the file, or it creates an <indexterm> section with the input term.

## To do
- [X] GUI
- [X] PyInstaller?
- [ ] CSV file as input?
- [X] Delete all ```<indexterms>```  feature
- [ ] Make the number of changes scrollable 

## Issues
- [ ] Acronym mode works but won't display a number of changes
- [ ] The number of changes seems doubled most of the time
- [ ] Edge case of selecting a folder/rechercher/acronyme where error priority is wrong
