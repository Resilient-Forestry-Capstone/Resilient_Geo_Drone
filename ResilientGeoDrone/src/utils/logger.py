import logging
import sys
from pathlib import Path
from datetime import datetime



"""

    Desc: This Module Provides A Logger Setup Class For Custom Logger
    Configuration. The Class Configures A Logger With File And Console
    Handlers. The Logger Is Configured To Log Messages With Timestamps
    And Log Levels. The Logger Is Configured To Log To A Logs Directory.

"""
class LoggerSetup:
    
    """
    
        Desc: Initializes Our Logger Setup With A name And Log Directory, log_dir.
        The Logger Setup Configures A Logger With File And Console Handlers.
        The Logger Is Configured To Log Messages With Timestamps And Log Levels.
    
        Preconditions:
            1. name: Name Of Logger
            2. log_dir: Directory To Save Log Files
        
        Postconditions:
            1. Configure Logger Instance
            2. Log Messages With Timestamps And Log Levels
            3. Log To Log Directory

    """
    def __init__(self, name: str, log_dir: str = "logs"):

        # Set-Up Logger Name And Log Directory
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Set-Up Logger With Timestamp And Log Levels
        self.logger = self._setup_logger()
    

    """
    
        Desc: Configure And Return Logger Instance With A Specified Timestamp,
        Log File, And Log Levels. The Logger Is Configured With File And Console
        Handlers.

        Preconditions:
            1. None

        Postconditions:
            1. Configure And Return Logger Instance
            2. Setup Log Messages With Timestamps And Log Levels
            3. Setup To Log To Log Directory
    
    """
    def _setup_logger(self) -> logging.Logger:
        # Create Logger Instance
        logger = logging.getLogger(self.name)

        # Set Log Level To Informative
        logger.setLevel(logging.INFO)
        
        # If No Handlers, Create File And Console Handlers
        if not logger.handlers:
            # Create Timestamp For Log File
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = self.log_dir / f"{self.name}_{timestamp}.log"
            
            # File Handler As DEBUG
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            # Console Handler For Standard Out As Using Informative
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Create Format For Log Messages
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add Handlers To Our Given Logger
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        # Return Configured Logger
        return logger
    

    """
    
        Desc: Return Configured Logger Instance.

        Preconditions:
            1. None

        Postconditions:
            1. Return Our Configured Logger Instance
    
    """
    def get_logger(self) -> logging.Logger:
        return self.logger