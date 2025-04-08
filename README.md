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


----------------------------------------------


<h3>📂 Directory Structure</h3>


```plaintext
. 
├── README.md # Project overview and team introduction
├── run_qgis_setup.bat # Batch script for setting up QGIS environment
├── setup.py # Setup script for the project
├── setup_env.py # Script for setting up the environment
├── requirements.txt # Project dependencies
├── main.py # Main pipeline script
├── data/ # UAV imagery and ground truth datasets
│   ├── raw/ # Raw UAV image data
│   │   └── Image-Set/ # Sample File Containing Images
│   ├── processed/ # Processed and georeferenced data
│   └── output/ # Output data
│       ├── point_cloud/
│       ├── processed/
│       └── analysis/
├── logs/ # Log files
├── src/ # Source code for automated workflows
│   ├── preprocessing/ # Scripts for UAV image preprocessing
│   │   ├── __init__.py
│   │   ├── batch_processor.py
│   │   ├── image_validator.py
│   │   └── quality_metrics.py
│   ├── point_cloud/ # Scripts for point cloud generation and analysis
│   │   ├── __init__.py
│   │   ├── cloud_processor.py
│   │   ├── environment_params.py
│   │   └── webodm_client.py
│   ├── geospatial/ # Scripts for geospatial analysis
│   │   ├── __init__.py
│   │   ├── canopy_analysis.py
│   │   ├── qgis_analyzer.py
│   │   └── terrain_analysis.py
│   └── utils/ # Utility scripts
│       ├── __init__.py
│       ├── config_loader.py
│       ├── file_handler.py
│       ├── logger.py
│       ├── pdf_parser.py
│       └── report_metadata.py
├── tests/ # Unit and integration tests
└── config/ # Configuration files
    └── config.yaml
```


----------------------------------------------


<img src="https://github.com/user-attachments/assets/256a675f-65c3-4469-a943-436709c5eb71" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/256a675f-65c3-4469-a943-436709c5eb71" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/256a675f-65c3-4469-a943-436709c5eb71" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/256a675f-65c3-4469-a943-436709c5eb71" alt="Monkeys With A Drone" width="55" height="59"> 



<h3>🛠️ Setup:</h3>

<h6>Before Initialization (CLI):</h6>

Before Starting Up The Scripts There Are 3 Main Things That Need To Be Done:

* WebODM Is Currently Being Hosted Locally On Your System Under The Default, `http://localhost:8000`.
* QGIS Is Installed On The System Under It's Standard Location, `C:\Program Files\...`
* You Are Running The Program Through A Windows OS **_(Or A Windows Virtual-Machine)_**


<h6>Initialization (CLI):</h6>

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


<h6>Before Initialization (UI):</h6>

Before Starting The Scripts There Is 2 Main Things That Needs To Be Done:

* The Underlying Operating System Is Windows.
* Call The `setup.bat` Which Will Set-Up The Environment For You.

<h6>Initialization (UI):</h6>

To Run The Program Now, All You Have To Do Is Call `main.py` Which Is Located Relatively, `ResilientGeoDrone/main.py`.

After Calling This, It Should Take A Second For The UI To Display Itself, But After Should Provide You With Functionality.

<h6>After Initialization (UI):</h6>

After You Initialize The Process, You May Need To Go Into Settings And Alter Some Of The Default Parameters. These Can Be Found Under The `Settings` Button.

One Main Setting You May Need To Change Is Your WebODM Login Credentials For API Access Which Is Found In `Settings` -> `Point Cloud`.

After That, You Should Be Able To Call The Pipeline Properly Through The UI.

<h6>UI Functionality:</h6>

The UI Has Some Basic Functionality Presented:

* Main Page:
     - gg


<img src="https://github.com/user-attachments/assets/2770954d-c025-4fbc-bb42-a33b38385cad" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/2770954d-c025-4fbc-bb42-a33b38385cad" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/2770954d-c025-4fbc-bb42-a33b38385cad" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/2770954d-c025-4fbc-bb42-a33b38385cad" alt="Monkeys With A Drone" width="55" height="59"> 

----------------------------------------------

<img src="https://github.com/user-attachments/assets/a2c98a65-196d-490f-85bf-7d0dbd0e3dfe" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/a2c98a65-196d-490f-85bf-7d0dbd0e3dfe" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/a2c98a65-196d-490f-85bf-7d0dbd0e3dfe" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/a2c98a65-196d-490f-85bf-7d0dbd0e3dfe" alt="Monkeys With A Drone" width="55" height="59"> 



<h3>🔍 The Breakdown:</h3>

<h4>Architecture Diagram</h4>

![image](https://github.com/user-attachments/assets/3ba7e594-e03c-4020-aa2b-ba5eda7621da)


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


<img src="https://github.com/user-attachments/assets/8d00db25-670b-4312-85ac-ee926787047b" alt="Cornstarch <3" width="55" height="59"> <img src="https://github.com/user-attachments/assets/8d00db25-670b-4312-85ac-ee926787047b" alt="Cornstarch <3" width="55" height="59"> <img src="https://github.com/user-attachments/assets/8d00db25-670b-4312-85ac-ee926787047b" alt="Cornstarch <3" width="55" height="59"> <img src="https://github.com/user-attachments/assets/8d00db25-670b-4312-85ac-ee926787047b" alt="Cornstarch <3" width="55" height="59"> 

