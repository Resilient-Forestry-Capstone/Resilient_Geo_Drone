# ResilientGeoDrone
3-Staged Python Script Which Utilizes Provided Digital Aerial Photogrammetry To Create High Quality Point Clouds For Use In Geospatial Analysis Of Forest Canopies.

Program Uses _**QGIS**_ And _**WebODM**_ As Two Main Software Facillitators For The Point Cloud And Geospatial Analysis. Because Of The External Dependency To Interface With The _**QGIS**_ API We Utilize `Window`'s .bat Files For Linking.


----------------------------------------------


<h3>📑 Table of Contents</h3>

1. [📂 Directory Structure](#-directory-structure)
2. [🛠️ Setup](#-setup)
   - [Before Initialization](#before-initialization)
   - [Initialization](#initialization)
3. [🔍 The Breakdown](#-the-breakdown)
   - [Architecture Diagram](#architecture-diagram)
   - [Core Components](#core-components)
   - [Stage-Specific Components](#stage-specific-components)
   - [Stage 1: Preprocessing Digital Aerial Photographs](#stage-1-preprocessing-digital-aerial-photographs)
   - [Stage 2: WebODM Point-Cloud Generation](#stage-2-webodm-point-cloud-generation)
   - [Stage 3: QGIS Geospatial Analysis](#stage-3-qgis-geospatial-analysis)
   - [Stage 4: Output Packaging](#stage-4-output-packaging)
4. [🌟 Features](#-features)
5. [🏗️ Additional Documentation](#documentation)


----------------------------------------------


<h3>📂 Directory Structure</h3>


```plaintext
.
├── README.md # Project overview and team introduction
├── run_qgis_setup.bat # Batch script for setting up QGIS environment
├── setup.py # Setup script for the project
├── requirements.txt # Project dependencies
├── main.py # Main application script (likely launches the GUI)
├── .gitignore # Specifies intentionally untracked files
├── config/ # Configuration files
│   ├── config.yaml # Main configuration for the pipeline
│   └── default_config.yaml # Default configuration settings
├── data/ # UAV imagery and output datasets
│   ├── raw/ # Placeholder for raw UAV image data (user-provided)
│   ├── processed/ # Intermediate processed data (e.g., validated images, temporary files)
│   │   └── (timestamped_subfolders_during_processing)/
│   └── output/ # Final output data from pipeline runs
│       ├── point_cloud/ # Point cloud related outputs (DSM, DTM, Orthophotos, CHM, reports from WebODM)
│       │   └── (timestamped_task_subfolders)/ # Each subfolder for a processing task
│       │       ├── dsm.tif
│       │       ├── dtm.tif
│       │       ├── orthophoto.tif
│       │       ├── chm.tif
│       │       └── report.pdf 
│       └── analysis/ # Geospatial analysis outputs (gap polygons, statistics)
│           └── (timestamped_task_subfolders)/
│               ├── gaps.geojson
│               └── gap_analysis_report.txt
├── logs/ # Log files from application runs
│   └── resilient_geodrone.log # Main log file
├── src/ # Source code for the application
│   ├── __init__.py
│   ├── front_end/ # PyQt5 GUI components
│   │   ├── __init__.py
│   │   ├── client_window.py # Main application window
│   │   ├── drag_drop_widget.py # Widget for image input
│   │   ├── pipeline_worker.py # QThread for running pipeline tasks
│   │   ├── progress_bar.py # Custom progress bar widget
│   │   ├── result_dialog.py # Dialog for showing results (likely obsolete or integrated)
│   │   ├── result_viewer.py # Widget for viewing pipeline outputs
│   │   └── settings_window.py # Window for application settings
│   ├── preprocessing/ # Scripts for UAV image preprocessing
│   │   ├── __init__.py
│   │   ├── batch_processor.py # Processes batches of images
│   │   ├── image_validator.py # Validates image properties
│   │   └── quality_metrics.py # Calculates image quality metrics
│   ├── point_cloud/ # Scripts for point cloud generation
│   │   ├── __init__.py
│   │   ├── cloud_processor.py # Processes outputs from WebODM (CHM generation etc.)
│   │   └── webodm_client.py # Client for interacting with WebODM API
│   ├── geospatial/ # Scripts for geospatial analysis
│   │   ├── __init__.py
│   │   └── gap_detector.py # Performs gap detection analysis
│   └── utils/ # Utility scripts
│       ├── __init__.py
│       ├── config_loader.py # Loads and manages YAML configuration
│       ├── file_handler.py # Handles file and directory operations
│       └── logger.py # Sets up and provides logging services
├── tests/ # Unit and integration tests
│   ├── __init__.py
│   ├── conftest.py # Pytest fixtures and configuration
│   ├── pytest.ini # Pytest configuration file
│   ├── data/ # Test data (e.g., sample images, mock config files)
│   │   └── (various_test_files_and_folders)/
│   └── unit/ # Unit tests for individual modules
│       ├── __init__.py
│       ├── test_batch_processor.py
│       ├── test_config_loader.py
│       ├── test_file_handler.py
│       ├── test_gap_detector.py
│       ├── test_image_validator.py
│       ├── test_logger.py
│       ├── test_pipeline_worker.py
│       ├── test_quality_metrics.py
│       ├── test_result_viewer.py
│       ├── test_settings_window.py
│       └── test_webodm.py
└── gap_detection/ # Standalone or experimental gap detection scripts (separate from src/geospatial)
    ├── gap_detection_demo.py
    ├── gap_renderer.py
    └── requirements_gap.txt
```


----------------------------------------------


<img src="https://github.com/user-attachments/assets/256a675f-65c3-4469-a943-436709c5eb71" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/256a675f-65c3-4469-a943-436709c5eb71" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/256a675f-65c3-4469-a943-436709c5eb71" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/256a675f-65c3-4469-a943-436709c5eb71" alt="Monkeys With A Drone" width="55" height="59"> 



<h3>🛠️ Setup:</h3>

<h6>Before Initialization</h6>

Before Starting Up The Scripts There Are 3 Main Things That Need To Be Done:

* WebODM Is Currently Being Hosted Locally On Your System Under The Default, `http://localhost:8000`.
* QGIS Is Installed On The System Under It's Standard Location, `C:\Program Files\...`
* You Are Running The Program Through A Windows OS **_(Or A Windows Virtual-Machine)_**


<h6>Initialization</h6>

To Run The Program Properly With All Dependencies Linked, You Must Call The `run_qgis_setup.bat` File Which Will Call The Linking .bat For QGIS And Pip Install All Python Library Dependencies In A Python Virtual Environment.

When Running `run_qgis_setup.bat`, You Will Be Stopped At A Python Script:

```Python Terminal

Starting QGIS Environment Setup...
  Checking Python Edition...
    Python Version: 312 
  Creating Python Virtual Environment...
    Virtual Environment Created And Activated.
  Initializing QGIS Dependency Linker .bat...
Python 3.12.7 (main, Oct 25 2024, 11:18:09) [MSC v.1938 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> ^Z

```

Press `Ctrl + Z` Then `Enter` To Then Actually Start The Pipeline (The _**QGIS**_ Needs To Call Python To Load In Everything For Python Before We Execute).


<img src="https://github.com/user-attachments/assets/2770954d-c025-4fbc-bb42-a33b38385cad" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/2770954d-c025-4fbc-bb42-a33b38385cad" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/2770954d-c025-4fbc-bb42-a33b38385cad" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/2770954d-c025-4fbc-bb42-a33b38385cad" alt="Monkeys With A Drone" width="55" height="59"> 

----------------------------------------------

<img src="https://github.com/user-attachments/assets/a2c98a65-196d-490f-85bf-7d0dbd0e3dfe" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/a2c98a65-196d-490f-85bf-7d0dbd0e3dfe" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/a2c98a65-196d-490f-85bf-7d0dbd0e3dfe" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/a2c98a65-196d-490f-85bf-7d0dbd0e3dfe" alt="Monkeys With A Drone" width="55" height="59"> 



<h3>🔍 The Breakdown:</h3>

<h4>Architecture Diagram</h4>

![image](https://github.com/user-attachments/assets/45cb664f-aa24-4c66-8da9-68a81582e6f4)

The Process Will Be Initialized With An Raw Digital Aerial Image-Set As One Of The Main Inputted Arguments--With The Other Being A Provided Environmental Tag For Fine-Tuning Of Parameters For The _**QGIS**_ And _**WebODM**_ Software. 

Because Of The _**QGIS**_ External Dependency, We Utilize A Custom .bat (`run_qgis_setup.bat`) At Runtime To Properly Stage Our Program For All Dependencies Without Need For User Involvement. This Mainly Links _**QGIS**_ Through Its Provided Python .bat Setup Located In `"C:\Program Files\QGIS 3.40.1\bin\python-qgis.bat"` But Also Pip Installs Dependencies Pertaining To Our Codebase. This Is All Wrapped In A Virtual Environment Provided In Python Through `python -m venv .venv`.

After All Linking, `run_qgis_setup.bat` Will Call Our `main.py` Which Starts Our 3-Staged Pipeline. In `main.py` There Is A `Pipeline` Class In Which Facillitates The Staging Of Our Script With It Containing Classes We've Created For Each Component Of Our Codebase This Includes:

<h6>Core Components</h6>
 
* A Logger Class (`LoggerSetup`): Provides Detailed, Timestamped Logs Across All Pipeline Stages. Allows Users And Developers To Know Who, What, Where, And Why Specific Operations Are Going On.
* A Config Loader (`ConfigLoader`): For Our Tunable Parameters For Our User Through A _**YAML** _-Formatted Settings File. Applied To Allow Users Freedom To Change Specific Parameters Throughout Codebase's Lifetime.
* A File Handler (`FileHandler`): Orchestrates File Operations And Directory Management Throughout Runtime. Mainly Being Utilized To Allow A More Modifiable, Debuggable, And Dynamic Means Of File Mangement Than Simple Operations In-Line.


<h6>Stage-Specific Components</h6>

* A Batch Image Processor (`BatchProcessor`): Preprocesses And Validates Raw Drone Imagery For Usage In Point-Cloud Generation With Multiple Worker Threads. Allows User To Gain Some Runtime By Avoiding Sequential Processing Of Images By One Thread.
* A API Interfacer With _**WebODM**_ (`WebODMClient`): Interfaces With WebODM For Our Point-Cloud Generation, Including Parameterization As Well As Generation. To Be Utilized In The Codebase To Automate Point-Cloud Generation With Specific Parameters So User Doesn't Need To Do Manual Intervention.
* A Point-Cloud Processor (`CloudProcessor`): Will Post-Process _**WebODM**_ Point-Cloud Outputs To Provide More Pertinent Information To Our Primary User-Group With Generation Of Canopy Height Models As Well As Other Quality Metrics Not Covered In The _**WebODM**_ Quality-Report. Largely Needed Class Which Helps Extrapolate A Lot Of Necessary Information Our Users Wish To Have Automatically Computed And Considered In Their Reports.
* A Geospatial Analysis Processor (`QGISAnalzer`): Integrates _**QGIS**_ To Utilize Point-Clouds Created By _**WebODM**_ As Well As Their Metadata To Create A Geospatial Model For More Detailed Analysis By Ecologists. Largely Focused Class For Our Project Which Creates The End Model Wanting To Be Outputted By The Pipeline, Utilizing Point-Cloud As Well As Public Geospatial Datasets For More Fine-Tuned Reports Pertaining To The User Group.


After Our Members Are Initialized, We Call Our Main Function Of `Pipeline` Which Is `run(...)`. This Takes In The Input Directory With All Our Digital Aerial Photos, The Output Directory We Will Utilize For Our End Report, As Well As The Environmental Tag Which Helps Tune Parameters Based On The Captured Conditions (I.E. Rainy, Foggy, Or Sunny).

The Pipeline Will Firstly Call Our `FileHandler`'s Processing/Output Directory Function `create_processing_directories(...)` In Order To Set-Up A Timestamped File Of The Outputs We Create During This Initialization. 

<h6>Stage 1: Preprocessing Digital Aerial Photographs</h6>

After The Directory Is Created, The Logger Will Send A Report Of Our Status Through Its `info(...)` Function Then Utilizing `FileHandler` Will Grab All The Digital Aerial Photographs We Will Be Utilizing Using `get_image_files(...)`. The Photo's Given Will Then Be Validated And Preprocessed Through Our Call To Our `BatchProcessor`'s Function, `process_batch(...)`. 


<h6>Stage 2: WebODM Point-Cloud Generation</h6>

After We Finish This First Stage Of Preprocessing/Validation Of Our Image-Set, We Call Our Running _**WebODM**_ Execution To Then Generate A Point Cloud Using Our Images; This Is Done Through Our `process_webodm_results(...)` Function.


<h6>Stage 3: QGIS Geospatial Analysis</h6>

Utilizing Our `QGISAnalyzer` Instance, We Use The Point-Cloud Results Of Our Last Stage Using _**WebODM**_ To Pass Into `QGISAnalyzer` And It's `analyze(...)` Function Which Generates A Canopy Heigh Model As Well As Digital Terrain Model, Displaying These Through QGIS.

<h6>Stage 4: Output Packaging</h6>

At The End, All Necesary Data Is Packaged Into A New _**YAML**_ File Which Contains The Results From _**WebODM**_, As Well As _**QGIS**_. As Well As This Report, Other Provided Reports Like The _**WebODM**_ Benchmark Will Also Be Provided At This End Time. 


<img src="https://github.com/user-attachments/assets/0bba6fb1-10f6-4aa2-ad82-1277bee58961" alt="Monkeys With A Drone" width="45" height="59"> <img src="https://github.com/user-attachments/assets/0bba6fb1-10f6-4aa2-ad82-1277bee58961" alt="Monkeys With A Drone" width="45" height="59"> <img src="https://github.com/user-attachments/assets/0bba6fb1-10f6-4aa2-ad82-1277bee58961" alt="Monkeys With A Drone" width="45" height="59"> <img src="https://github.com/user-attachments/assets/0bba6fb1-10f6-4aa2-ad82-1277bee58961" alt="Monkeys With A Drone" width="45" height="59"> 

----------------------------------------------

<img src="https://github.com/user-attachments/assets/9b992420-cac1-409d-ac26-fbbbff952879" alt="Cornstarch <3" width="55" height="69"> <img src="https://github.com/user-attachments/assets/9b992420-cac1-409d-ac26-fbbbff952879" alt="Cornstarch <3" width="55" height="69"> <img src="https://github.com/user-attachments/assets/9b992420-cac1-409d-ac26-fbbbff952879" alt="Cornstarch <3" width="55" height="69"> <img src="https://github.com/user-attachments/assets/9b992420-cac1-409d-ac26-fbbbff952879" alt="Cornstarch <3" width="55" height="69"> 


<h3>🌟 Features:</h3>

<h4>Main View:</h4>
<img src="https://github.com/user-attachments/assets/61f53aa5-64c9-4eb8-a6a3-c5e122686955">

<h4>Main View (Pipeline Progress):</h4>
<img src="https://github.com/user-attachments/assets/eccac15c-cf8e-4855-9367-89f722e01f45">

<h4>Results Viewer (Low Contour):</h4>
<img src="https://github.com/user-attachments/assets/b39f87e5-30e2-4e81-9916-e600fba52714">

<h4>Results Viewer (High Contour):</h4>
<img src="https://github.com/user-attachments/assets/53160292-e889-46b2-8467-93f607e373b0">

<h4>Settings Window (Preprocessing Tab):</h4>
<img src="https://github.com/user-attachments/assets/7da2fef9-6195-4942-a78c-0cdde40cb011">

<h4>Settings Window (Logs Tab):</h4>
<img src="https://github.com/user-attachments/assets/aaf0b765-a8ac-46e4-8a08-7acb440e4598">

<h4>Settings Window (Point Cloud Tab):</h4>
<img src="https://github.com/user-attachments/assets/78297b2f-0fc7-4414-828e-f433aadec029">

<h4>Settings Window (Geospatial Tab):</h4>
<img src=https://github.com/user-attachments/assets/b1d45f73-a5ff-4501-a085-5d137a0acdf5>


<img src="https://github.com/user-attachments/assets/8d00db25-670b-4312-85ac-ee926787047b" alt="Cornstarch <3" width="55" height="59"> <img src="https://github.com/user-attachments/assets/8d00db25-670b-4312-85ac-ee926787047b" alt="Cornstarch <3" width="55" height="59"> <img src="https://github.com/user-attachments/assets/8d00db25-670b-4312-85ac-ee926787047b" alt="Cornstarch <3" width="55" height="59"> <img src="https://github.com/user-attachments/assets/8d00db25-670b-4312-85ac-ee926787047b" alt="Cornstarch <3" width="55" height="59"> 

--------------------------------------------------------

<h3 id="documentation">🏗️ Additional Documentation:</h3>

<h4>Project Documents (<b>.docx</b>):</h4>
<a href="https://docs.google.com/document/d/1Bqws8frZD-5I0rI0Xwkueb98Aeva9kvB/edit?usp=sharing&ouid=113497198781082727325&rtpof=true&sd=true">Project Document</a><br>
<a href="https://docs.google.com/document/d/1ZxcAY7KImUwXDi1PurcVOaRES5GLi2UW/edit?usp=sharing&ouid=113497198781082727325&rtpof=true&sd=true">Scope Document</a><br>
<a href="https://docs.google.com/document/d/1nacwGeTUOO5oRy9UE1OUEOxUP9ydSuve/edit?usp=sharing&ouid=113497198781082727325&rtpof=true&sd=true">Design Document</a><br><br>

<h4>Architecture/Codebase Documents (<b>.ipynb</b>):</h4>
<a href="https://colab.research.google.com/drive/1jNO7_kG1UmCKrqQNBmvPGhgTCfkMYllN?usp=sharing">ResilientGeoDrone User Manual</a><br>
<a href="https://colab.research.google.com/drive/1jcTHM3HCaJ1qFnkUvrGkAXTe_YUrozMf?usp=sharing">ResilientGeoDrone Documentation</a><br><br>

<h4>Workflow Diagram Document (<b>.drawio</b>):</h4>
<a href="https://drive.google.com/file/d/1wZVwqdxwkLVvG8hE8RgRAt65EdRGJXSt/view?usp=sharing">ResilientGeoDrone Flow Diagram</a><br>
