# Split_Chapters_Script_Compleated
This Creates a split chapters folder containing a list chapters made from Crossing EPUB and TXT files.
## How to use
Download all the script and put them in the same folder along with the EPUB and TXT then RUN the controller.py

What each one does is Told bellow
## final_validator.py
Takes the Folder chapters_txt(txt) and chapters_txt(epub) generated from the split_epub.py and split_txt.py and cross checks them to see if they are worthy to survive if yes they are sent to chapters_txt

## split_txt.py
takes a large txt and splits it into multiple chapters based on the chapters header

## split_epub.py
takes a large EPUB and splits it into multiple chapters based on the Metadata

## rename_and_merge.py
renames and merges the files by reading the fiile header and file name

## controller.py
Controls everything.
