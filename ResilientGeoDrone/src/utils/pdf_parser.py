import fitz
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from .logger import LoggerSetup



"""

    Desc: This Module Provides Us A PDF Parser For Extracting Text And
    Images From PDF Reports. The PDF Parser Is Enhanced For WebODM Reports
    Specifically. The Parser Utilizes PyMuPDF (fitz) To Extract Text And
    Images From PDF Reports.

"""
class PDFParser:

    """
    
        Desc: Initializes Our PDF Parser With A PDF Path (pdf_path) To
        Load And Extract Text And Images From. The PDF Path Is Expected
        To Be A Valid Path To A PDF Report From WebODM.

        Preconditions:
            1. pdf_path: Path To PDF Report From WebODM
            2. pdf_path Must Be A Valid Path

        Postconditions:
            1. Set Our PDF Path
            2. Load PDF Report Using PyMuPDF (fitz)
    
    """
    def __init__(self, pdf_path: Path):
        self.logger = LoggerSetup().getLogger()
        self.logger.info(f"PDF Parser ID: {self}  -  Initializing PDF Parser...")
        try:
          self.pdf_path = pdf_path
          self.doc = fitz.open(str(pdf_path))
          self.logger.info(f"PDF Parser ID: {self}  -  PDF Parser Initialized.")
        except Exception as e:
            self.logger.error(f"PDF Parser ID: {self}  -  PDF Parser Initialization Failed: {str(e)}.")
            raise
        
<<<<<<< HEAD
        

    """
    
        Desc: This Function Extracts All Text Content From The PDF Report.
        The Function Returns The Extracted Text As A Single String. The
        Text Content Is Extracted From All Pages Of The PDF Report For Utilization
        In Our Pipeline For Analysis.

        Preconditions:
            1. PDF Report Must Be Loaded

        Postconditions:
            1. Extracts All Text Content From PDF Report
            2. Returns Extracted Text As A Single String
            3. Extracted Text Is Concatenated From All Pages
    
    """
    def extract_text(self) -> str:
        self.logger.info(f"PDF Parser ID: {self}  -  Extracting Text From PDF Report...")
        try:
          text = []
          for page in self.doc:
              text.append(page.get_text())

          result = "\n".join(text)
          self.logger.info(f"PDF Parser ID: {self}  -  Text Extracted From PDF Report.")

          # Return Text Content As Single String With Newlines For Pages
          return result
        except Exception as e:
            self.logger.error(f"PDF Parser ID: {self}  -  Failed To Extract Text From PDF Report: {str(e)}.")
            return ""
    
=======

    """
    
        Desc: This Function Extracts All Text Content From The PDF Report.
        The Function Returns The Extracted Text As A Single String. The
        Text Content Is Extracted From All Pages Of The PDF Report For Utilization
        In Our Pipeline For Analysis.

        Preconditions:
            1. PDF Report Must Be Loaded

        Postconditions:
            1. Extracts All Text Content From PDF Report
            2. Returns Extracted Text As A Single String
            3. Extracted Text Is Concatenated From All Pages
    
    """
    def extract_text(self) -> str:
        text = []
        for page in self.doc:
            text.append(page.get_text())

        # Return Text Content As Single String With Newlines For Pages
        return "\n".join(text)
    
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576
    """
    
        Desc: This Function Extracts All Images From The PDF Report. The
        Function Returns A List Of Dictionaries Containing Image Metadata.
        The Image Metadata Includes Path To Image, Image Format, Image Width,
        Image Height, Image Colorspace, And Page Number. The Images Are
        Extracted And Saved To The Output Directory, output_dir.

        Preconditions:
            1. PDF Report Must Be Loaded
            2. output_dir Must Be A Valid Directory To Save Images

        Postconditions:
            1. Extracts All Images From PDF Report
            2. Returns A List Of Image Metadata
            3. Saves Images To Output Directory
    
    """
    def extract_images(self, output_dir: Path) -> List[Dict[str, Any]]:
<<<<<<< HEAD
        self.logger.info(f"PDF Parser ID: {self}  -  Extracting Images From PDF Report...")
=======
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576
        # Create Output Direcotry If It Does Not Exist
        output_dir.mkdir(parents=True, exist_ok=True)
        image_data = []
        
        # Go Through Each Page And Extract Images
        for page_num, page in enumerate(self.doc):
            image_list = page.get_images()
            
            # For Each Image On Page
            for img_idx, img in enumerate(image_list):
                # Try Extracting Key Metadata From img
                try:
                    # Get Image Start Index
                    xref = img[0]
                    base_image = self.doc.extract_image(xref)
                    
                    # If Image Is Extracted, Save Image And Metadata
                    if base_image:
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # Save image with original format
                        image_path = output_dir / f"page_{page_num+1}_img_{img_idx+1}.{image_ext}"
                        with open(image_path, "wb") as f:
                            f.write(image_bytes)
                        
                        # Store metadata
                        image_data.append({
                            'path': image_path,
                            'format': image_ext,
                            'width': base_image.get('width'),
                            'height': base_image.get('height'),
                            'colorspace': base_image.get('colorspace'),
                            'page': page_num + 1
                        })

                # Goto Next Image If Failed To Extract   
                except Exception as e:
                    self.logger.error(f"Failed To Extract Image {img_idx} From Page {page_num}: {str(e)}")
                    continue

<<<<<<< HEAD
        self.logger.info(f"PDF Parser ID: {self}  -  Images Extracted From PDF Report.")
=======
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576
        # Return Image Metadata      
        return image_data
    

    """
    
        Desc: This Function Closes The PDF Document. The Function Should
        Be Called To Close The PDF Document After Extraction Of Text And
        Images. The Function Ensures That The PDF Document Is Closed
        To Prevent Memory Leaks.

        Preconditions:
            1. PDF Report Must Be Loaded

        Postconditions:
            1. Closes PDF Document

    """
    def close(self):
<<<<<<< HEAD
        self.logger.info(f"PDF Parser ID: {self}  -  Closing PDF Document...")
=======
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576
        if self.doc:
            self.doc.close()
            self.logger.info(f"PDF Parser ID: {self}  -  PDF Document Closed.")
        else:
            self.logger.warning(f"PDF Parser ID: {self}  -  PDF Document Already Closed.")
    

    """
<<<<<<< HEAD
    
        Desc: This Function Acts As A Context Manager For The PDF Parser.
        The Function Allows The PDF Parser To Be Used As A Context Manager
        To Ensure Proper Resource Management. The PDF Document Is Closed
        After Exiting The Context Manager using __exit__(...).

        Preconditions:
            1. PDF Report Must Be Loaded

        Postconditions:
            1. PDF Document Is Closed After Exiting Context Manager
            2. Opens PDF Document's Context
    
    """
    def __enter__(self):
        return self 
    
=======
    
        Desc: This Function Acts As A Context Manager For The PDF Parser.
        The Function Allows The PDF Parser To Be Used As A Context Manager
        To Ensure Proper Resource Management. The PDF Document Is Closed
        After Exiting The Context Manager using __exit__(...).

        Preconditions:
            1. PDF Report Must Be Loaded

        Postconditions:
            1. PDF Document Is Closed After Exiting Context Manager
            2. Opens PDF Document's Context
    
    """
    def __enter__(self):
        return self 
    
>>>>>>> 2c625a31f8302b2a8d38108e3b47c5b0ea12b576

    """
    
        Desc: This Function Acts As A Context Manager For The PDF Parser.
        The Function Allows The PDF Parser To Be Used As A Context Manager
        To Ensure Proper Resource Management. The PDF Document Is Closed
        After Exiting The Context Manager After Opening The Context Manager
        With __enter__(...).

        Preconditions:
            1. PDF Report Must Be Loaded
            2. exc_type: Exception Type
            3. exc_val: Exception Value
            4. exc_tb: Exception Traceback

        Postconditions:
            1. PDF Document Is Closed After Exiting Context Manager
            2. Closes PDF Document's Context
    
    """
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()