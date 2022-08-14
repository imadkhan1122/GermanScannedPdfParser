# GermanScannedPdfParser

## Scanned PDF INFORMATION PARSER:
    1.  In this project I have used fitz for loading and PDF pages and conversion to image.
    2.  Used PIL library to read images
    3.  Used Pytesseract OCR to extract all text from all images
    4.  Used regex and string operations to clean data and mine information
    
### PROJECT FOLDER STRUTUE
    PDF_PARSER
        > DATA folder having PDF files
        PARSER.py
        main.py
        Result.csv
        Readme.md
        deu.traineddata
        requirements.txt
        
    1. The "PARSER.py" file have all the code.
    2. "main.py" will be used for running.
    3. "requirements.txt" is use for packages Installation.
    4. Result will be stored in "Result.csv".
    
### PACKAGES INSTALLATION:
    1. cd to "PDF_PARSER" directory and open cmd or terminal and type .
    "pip install -r requirements.txt" by doing this required packages will be installed.
    
### RUN THE SCRIPT:
    1. Open main.py in any text editor and change 'path' to your folder path where you placed pdf files or open main.ipynb file in jupyter notebook and change path and run.
    2. It will save all the results in Output.csv file which will exists in PDF_PARSER directory.
