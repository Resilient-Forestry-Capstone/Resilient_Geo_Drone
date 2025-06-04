# ResilientGeoDrone
3-Staged Python Script Which Utilizes Provided Digital Aerial Photogrammetry To Create High Quality Point Clouds For Use In Geospatial Analysis Of Forest Canopies.

Program Uses _WebODM_ As The Main Software Facilitator For Point Cloud Generation, With Custom Python-Based Gap Detection Algorithms For Advanced Forestry Analysis. The End-To-End Pipeline Processes Raw UAV Imagery Into Actionable Ecological Insights Through An Intuitive _PyQt5_ GUI Or Command Line Interface

----------------------------------------------


<h3>📑 Table of Contents</h3>

1. [📂 Directory Structure](#-directory-structure)
2. [🏃 Quick Start](#quick-start)
3. [🔍 The Breakdown](#-the-breakdown)
   - <a href="#architecture-diagram">Architecture Diagram</a>
   - <a href="#core-components">Core Components</a>
   - <a href="#stage-specific-components">Stage-Specific Components</a>
   - <a href="#stage-1-preprocessing-digital-aerial-photographs">Stage 1: Preprocessing Digital Aerial Photographs</a>
   - <a href="#stage-2-webodm-point-cloud-generation">Stage 2: WebODM Point-Cloud Generation</a>
   - <a href="#stage-3-gap-detection-and-geospatial-analysis">Stage 3: Gap Detection and Geospatial Analysis</a>
   - <a href="#stage-4-output-packaging">Stage 4: Output Packaging</a>
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




<h3 id="quick-start">🏃 Quick Start</h3>

<h3>1. Clone Repository</h3>
<pre><code>git clone https://github.com/Resilient-Forestry-Capstone/Resilient_Geo_Drone.git
cd Resilient_Geo_Drone/ResilientGeoDrone</code></pre>


<h3>2. Create Virtual Environment (Optional)</h3>
<pre><code># Create virtual environment
python -m venv venv

<br>
# Activate virtual environment
venv\Scripts\activate              # Windows
source venv/bin/activate           # macOS/Linux</code></pre>

<h4>Alternative: Run Without Activation</h4>
<p>Instead of activating the virtual environment, you can run directly:</p>

<pre><code># Install dependencies without activation
venv\Scripts\python.exe -m pip install -r requirements.txt        # Windows
venv/bin/python -m pip install -r requirements.txt                # macOS/Linux

# Run the application
venv\Scripts\python.exe main.py                                   # Windows
venv/bin/python main.py                                           # macOS/Linux

# View help and CLI options
venv\Scripts\python.exe main.py --help                            # Windows
venv/bin/python main.py --help                                    # macOS/Linux</code></pre>


<h3>3. Install Dependencies</h3>
<pre><code>pip install -r requirements.txt</code></pre>


<h3>4. Setup WebODM</h3>
<p><strong>Install <a href="https://docs.docker.com/desktop/">Docker Desktop</a> first</strong></p>
<pre><code># Clone and start WebODM
git clone https://github.com/OpenDroneMap/WebODM --depth 1
cd WebODM
./webodm.sh start</code></pre>
<p>Create an account at <a href="http://localhost:8000">http://localhost:8000</a></p>


<h3>5. Configure Application</h3>
<pre><code>nano config/config.yaml      # Linux/macOS
notepad config/config.yaml   # Windows</code></pre>


<h3>6. Run Pipeline</h3>

<p><strong>GUI Mode (Recommended):</strong></p>
<pre><code>python main.py
<br>
# OR
<br>
python main.py --gui</code></pre>


<p><strong>CLI Mode:</strong></p>
<pre><code># View all CLI options and examples
python main.py --help

<br>
# Quick example - process drone images
python main.py --input ./drone_images --output ./results</code></pre>

<h3>7. View Results</h3>
<p><strong>GUI:</strong> Click "View Results" button to browse processed files</p>
<p><strong>CLI:</strong> Check your output directory (Determined In Your <code>config.yaml</code>) for DSM, DTM, CHM, and analysis files (formatted like <code>YYYYMMDD_HHMMSS/</code>)</p>
<br>


<img src="https://github.com/user-attachments/assets/2770954d-c025-4fbc-bb42-a33b38385cad" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/2770954d-c025-4fbc-bb42-a33b38385cad" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/2770954d-c025-4fbc-bb42-a33b38385cad" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/2770954d-c025-4fbc-bb42-a33b38385cad" alt="Monkeys With A Drone" width="55" height="59"> 

----------------------------------------------

<img src="https://github.com/user-attachments/assets/a2c98a65-196d-490f-85bf-7d0dbd0e3dfe" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/a2c98a65-196d-490f-85bf-7d0dbd0e3dfe" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/a2c98a65-196d-490f-85bf-7d0dbd0e3dfe" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/a2c98a65-196d-490f-85bf-7d0dbd0e3dfe" alt="Monkeys With A Drone" width="55" height="59"> 



<h3>🔍 The Breakdown:</h3> <h4>Architecture Diagram</h4>

<img alt="image" src="https://github.com/user-attachments/assets/5a408b2e-bc16-40a5-8da3-4df83a013cdc"><br>

The Process Will Be Initialized With A Raw Digital Aerial Image-Set As One Of The Main Inputted Arguments--With The Other Being A Provided Environmental Tag For Fine-Tuning Of Parameters For The WebODM Software.

The System Can Be Accessed Through Either CLI Or Our Modern PyQt5-Based GUI Interface. The GUI Provides Drag-and-Drop Functionality For Image Sets, Real-Time Progress Visualization, Environment Selection, And Parameter Customization Through An Intuitive Settings Interface.

After The Setup Script Initializes The Environment, Our `main.py` Launches The GUI Interface Or Pipeline Backend Based On The Context. The `PipelineWorker` Class (A QThread Subclass) Manages The Execution Of Our 3-Stage Pipeline. In Our Architecture, There Are Several Key Components:

<h6>Core Components</h6>

A Logger Class `LoggerSetup`: Provides Detailed, Timestamped Logs Across All Pipeline Stages. Allows Users And Developers To Know Who, What, Where, And Why Specific Operations Are Going On.

A Config Loader `ConfigLoader`: For Our Tunable Parameters For Our User Through A YAML-Formatted Settings File. Applied To Allow Users Freedom To Change Specific Parameters Throughout Codebase's Lifetime.

A File Handler `FileHandler`: Orchestrates File Operations And Directory Management Throughout Runtime. Mainly Being Utilized To Allow A More Modifiable, Debuggable, And Dynamic Means Of File Management Than Simple Operations In-Line.

<h6>Stage-Specific Components</h6>
A Batch Image Processor `BatchProcessor`: Preprocesses And Validates Raw Drone Imagery For Usage In Point-Cloud Generation With Multiple Worker Threads. Performs Quality Control Checks Including Resolution, Blur Detection, And Brightness Assessment.

A API Interfacer With WebODM `WebODMClient`: Interfaces With WebODM For Our Point-Cloud Generation, Including Adaptive Parameter Tuning Based On Environmental Conditions. Manages The Asynchronous Processing Of Image Sets Through A REST API And Provides Progress Monitoring. As Well As Post-Processes WebODM Point-Cloud Outputs To Generate Canopy Height Models (CHMs) By Computing The Difference Between Digital Surface Models (DSMs) And Digital Terrain Models (DTMs). This Layer Converts Raw Point-Cloud Data Into Forest-Specific Metrics.

A Gap Detector `GapDetector`: Analyzes The Canopy Height Models To Automatically Identify, Measure, And Characterize Forest Gaps. The Gap Detection Algorithm Uses Configurable Height Thresholds And Morphological Operations To Create Vector Polygons Of Gap Areas With Associated Metrics.

<h6>Stage 1: Preprocessing Digital Aerial Photographs</h6>

The Pipeline Begins By Creating Timestamped Output Directories Through The `FileHandler`. In Stage 1, The System Collects All Digital Aerial Photographs From The Input Directory And Passes Them Through The `BatchProcessor`. This Component: <br>


* Validates Image Formats Against User-Configured Acceptable Types<br>
* Checks Resolution Against Minimum Requirements<br>
* Applies Blur Detection Algorithms To Filter Out Blurry Images<br>
* Assesses Image Brightness To Ensure Adequate Lighting<br>
* Processes Images In Parallel Using Multiple Worker Threads For Efficiency<br>
* Outputs A Collection Of Valid Images Ready For Point Cloud Generation<br>


The GUI Displays Real-Time Progress During This Stage And Indicates Any Issues With Specific Images.

<h6>Stage 2: WebODM Point-Cloud Generation</h6>

With A Valid Image Set, The Pipeline Proceeds To WebODM Processing. The `WebODMClient` Component: <br>

* Establishes A Connection With The Running WebODM Instance<br>
* Creates A Project And Task With Environment-Specific Parameters (Sunny, Rainy, Foggy, Night)<br>
* Uploads Images And Initializes Processing With Optimized Settings<br>
* Asynchronously Polls The WebODM API For Task Status And Progress<br>
* Downloads Generated Assets Including DSM, DTM And Orthophoto Files<br>
* Generates A Canopy Height Model (CHM) By Computing DSM-DTM Difference<br>
* Creates Timestamped Output Directories For All WebODM Products<br>


This Stage Features Robust Error Handling And Progress Updates, With The GUI Reflecting The Real-Time Status Of The WebODM Processing Tasks.


<h6>Stage 3: Gap Detection and Geospatial Analysis</h6>

Once The Point Cloud And CHM Are Generated, The `GapDetector` Module Performs Advanced Analysis:<br>

* Loads And Processes The CHM To Identify Areas Below User-Specified Tree Height Thresholds<br>
* Applies Configurable Morphological Operations (Dilation, Erosion, Smoothing) To Refine Gap Identification<br>
* Filters Gaps By Size Parameters To Focus On Ecologically Significant Openings<br>
* Generates Vector Polygons For Each Identified Gap With Rich Metadata<br>
* Calculates Gap Metrics Including Area, Perimeter, And Shape Characteristics<br>
* Creates Visualizations Of Gaps Overlaid On The CHM Or Orthophoto<br>
* Exports Results To GIS-Compatible Formats (GeoJSON, Shapefiles)<br>
* Generates Statistical Summaries Of Gap Distribution And Characteristics<br>

The GUI Shows Progress During This Stage And Visualizes Results Upon Completion.


<h6>Stage 4: Output Packaging</h6>
In The Final Stage, The Pipeline Organizes All Outputs Into A Structured Format:<br>

* Creates A Comprehensive Results Package In The Designated Output Directory<br>
* Generates A Summary YAML File With Pipeline Statistics And Metadata<br>
* Provides Direct Access To Vector Layers For Further GIS Analysis<br>
* Includes Quality Reports And Visualizations For Quick Assessment<br>
* All Results Are Accessible Through The Result Viewer In The GUI<br>


The Output Is Organized In Timestamped Folders For Clear Tracking Of Different Processing Runs.


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
