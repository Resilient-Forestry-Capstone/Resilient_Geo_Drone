import fitz
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
import logging

class PDFParser:
    """Enhanced PDF Parser for WebODM Reports"""
    
    def __init__(self, pdf_path: Path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(str(pdf_path))
        self.logger = logging.getLogger(__name__)
        
    def extract_text(self) -> str:
        """Extract All Text Content"""
        text = []
        for page in self.doc:
            text.append(page.get_text())
        return "\n".join(text)
    
    def extract_images(self, output_dir: Path) -> List[Dict[str, Any]]:
        """Extract Images with Metadata"""
        output_dir.mkdir(parents=True, exist_ok=True)
        image_data = []
        
        for page_num, page in enumerate(self.doc):
            image_list = page.get_images()
            
            for img_idx, img in enumerate(image_list):
                try:
                    # Get image metadata
                    xref = img[0]
                    base_image = self.doc.extract_image(xref)
                    
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
                        
                except Exception as e:
                    self.logger.error(f"Failed to extract image {img_idx} from page {page_num}: {str(e)}")
                    continue
                    
        return image_data
    
    def close(self):
        """Close PDF Document"""
        if self.doc:
            self.doc.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()