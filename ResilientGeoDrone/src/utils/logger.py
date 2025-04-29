import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict



"""

    Desc: This Module Provides A Logger Setup Class For Custom Logger
    Configuration. The Class Configures A Logger With File And Console
    Handlers. The Logger Is Configured To Log Messages With Timestamps
    And Log Levels. The Logger Is Configured To Log To A Logs Directory.

"""
class LoggerSetup:
    
    # Create A Singleton Logger
    _instances: Dict[str, "LoggerSetup"] = {}


    """
    
      Desc: Create A Singleton Logger Instance. If The Logger Instance
      Is None, Create A New Logger Instance. If The Logger Instance Is
      Not None, Return The Existing Logger Instance. The Logger Instance
      Is Configured With File And Console Handlers So It Can Log Messages
      In A Universal Log File For All Modules.

      Preconditions:
          1. None

      Postconditions:
          1. Create A Singleton Logger Instance
          2. Return Existing Logger Instance If Not None
          3. Create New Logger Instance If None
    
    """
    def __new__(class_, name: str = f"Log_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}", log_dir: str = None, *args, **kwargs):
        
        if name not in class_._instances:
            # Create Logger Instance
            instance = super(LoggerSetup, class_).__new__(class_)
            # Before We Send Back For __init__ Call, Set __initialized To False
            instance.initialized = False
            instance.__init__(name, log_dir, *args, **kwargs)
            class_._instances[name] = instance
        return class_._instances[name]
    

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
    def __init__(self, name: str = f"Log_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}", log_dir: str = None, verbose : bool = False):
        
        # Skip Intialization If Already Initialized
        if self.initialized: return

        self.initialized = True

        # Set-Up Logger Name And Log Directory
        self.name = name

        # If None Provided, Goto Default Log Directory
        if log_dir == None:
            self.log_dir = Path(__file__).parent.parent.parent / "logs"
            self.log_dir.mkdir(exist_ok=True)
        elif not Path(log_dir).is_absolute():
            raise FileNotFoundError(f"LoggerSetup ID: {self}  -  Log Directory Not Found: {log_dir}")
        else:
            self.log_dir = Path(log_dir)
            self.log_dir.mkdir(exist_ok=True)
        self.verbose = verbose

        # Set-Up Logger With Timestamp And Log Levels
        self.logger = self._setup_logger()

        self.logger.info(f"LoggerSetup ID: {self}  -  Logger Setup Initialized.\n\n\n")
    

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
            
            
            
            # Create Format For Log Messages
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            if self.verbose:
              # Console Handler For Standard Out As Using Informative
              console_handler = logging.StreamHandler(sys.stdout)
              console_handler.setLevel(logging.INFO)
              console_handler.setFormatter(formatter)
              logger.addHandler(console_handler)
              
            # Add Handlers To Our Given Logger
            logger.addHandler(file_handler)
            
        
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