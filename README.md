# ResilientGeoDrone - A Point Cloud Forestry Analysis Tool
3-Staged Python Script Which Utilizes Provided Digital Aerial Photogrammetry To Create High Quality Point Clouds For Use In Geospatial Analysis Of Forest Canopies.

Program Uses _**QGIS**_ And _**WebODM**_ As Two Main Software Facillitators For The Point Cloud And Geospatial Analysis. Because Of The External Dependency To Interface With The _**QGIS**_ API We Utilize `Window`'s .bat Files For Linking.


----------------------------------------------

<h3>🏗️ Additional Documents:</h3>

<h4>User Resources & Documentation</h4>
<a href="https://colab.research.google.com/drive/1jcTHM3HCaJ1qFnkUvrGkAXTe_YUrozMf?usp=sharing" target="_blank">Documentation</a><br>
<a href="https://colab.research.google.com/drive/1jNO7_kG1UmCKrqQNBmvPGhgTCfkMYllN?usp=sharing" target="_blank">User Manual</a><br><br>

<h4>Technical & Project Documentation</h4>
<a href="https://docs.google.com/document/d/1Bqws8frZD-5I0rI0Xwkueb98Aeva9kvB/edit?usp=sharing&ouid=113497198781082727325&rtpof=true&sd=true">Project Document</a><br>
<a href="https://docs.google.com/document/d/1ZxcAY7KImUwXDi1PurcVOaRES5GLi2UW/edit?usp=sharing&ouid=113497198781082727325&rtpof=true&sd=true">Scope Document</a><br>
<a href="https://docs.google.com/document/d/1nacwGeTUOO5oRy9UE1OUEOxUP9ydSuve/edit?usp=sharing&ouid=113497198781082727325&rtpof=true&sd=true">Design Document</a>

----------------------------------------------


<h3>📑 Table of Contents</h3>


1. [🔍 The Breakdown](#the-breakdown)
   - [Architecture Diagram](#architecture-diagram)
   - [Core Components](#core-components)
   - [Stage-Specific Components](#stage-specific-components)
   - [Stage 1: Preprocessing Digital Aerial Photographs](#stage-1-preprocessing-digital-aerial-photographs)
   - [Stage 2: WebODM Point-Cloud Generation](#stage-2-webodm-point-cloud-generation)
   - [Stage 3: QGIS Geospatial Analysis](#stage-3-qgis-geospatial-analysis)
   - [Stage 4: Output Packaging](#stage-4-output-packaging)
2. [🌟 Features](#features)




----------------------------------------------

<img src="https://github.com/user-attachments/assets/d9dd1c40-ff1c-4ada-ac22-f3dc500c63c3" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/d9dd1c40-ff1c-4ada-ac22-f3dc500c63c3" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/d9dd1c40-ff1c-4ada-ac22-f3dc500c63c3" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/d9dd1c40-ff1c-4ada-ac22-f3dc500c63c3" alt="Monkeys With A Drone" width="55" height="59">

<h3 id="the-breakdown">🔍 The Breakdown:</h3>

<h4>Architecture Diagram</h4>

![image](https://github.com/user-attachments/assets/3ba7e594-e03c-4020-aa2b-ba5eda7621da)


<br>The Process Will Be Initialized With An Raw Digital Aerial Image-Set As One Of The Main Inputted Arguments--With The Other Being A Provided Environmental Tag For Fine-Tuning Of Parameters For The _**QGIS**_ And _**WebODM**_ Software. 

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


<h3 id="features">🌟 Features:</h3>

<h6>Home Window:</h6>
<img width="50%" height="50%" src="https://github.com/user-attachments/assets/e66b91c9-b936-42a7-9b8c-e9a0257b3bfd">

<h6>Settings Pop-Up Window:</h6>
<img width="50%" height="50%" src="https://github.com/user-attachments/assets/9cc59a39-0b22-4073-8c4f-ba6dcd4a3df0">

<h6>Settings' Logs Tab:</h6>
<img width="50%" height="50%" src="https://github.com/user-attachments/assets/6cc51cbf-2525-42b1-bfa9-8b1a193226b9">

<h6>Results Viewer Pop-Up Window:</h6>
<img width="50%" height="50%" src="https://github.com/user-attachments/assets/8f085e5b-9ea0-4ab3-81fa-a8b1f2efd57a">

<h6>Results Viewer .tif Colormap Modes:</h6>
<img width="50%" height="50%" src="https://github.com/user-attachments/assets/9b0f2355-0542-40c6-9693-e9bc7ad99f99">


<h6>Results Viewer .tif Inspector:</h6>
<img width="50%" height="50%" src="https://github.com/user-attachments/assets/4a9c430d-ead9-431f-a30f-45580147e5da">

<h6>Home Window Providing Image:</h6>
<img width="50%" height="50%" src="https://github.com/user-attachments/assets/912215bc-499e-4a85-b396-2834304cd2b2">

<h6>Home Window Running Pipeline:</h6>
<img width="50%" height="50%" src="https://github.com/user-attachments/assets/f5320b6a-9a64-44eb-9868-1658ce3c9ad3">

<h6>Home Window Completed Pipeline:</h6>
<img width="50%" height="50%" src="https://github.com/user-attachments/assets/a9b35483-5c80-4205-972e-aabfb1202380">




<img src="https://github.com/user-attachments/assets/8d00db25-670b-4312-85ac-ee926787047b" alt="Cornstarch <3" width="55" height="59"> <img src="https://github.com/user-attachments/assets/8d00db25-670b-4312-85ac-ee926787047b" alt="Cornstarch <3" width="55" height="59"> <img src="https://github.com/user-attachments/assets/8d00db25-670b-4312-85ac-ee926787047b" alt="Cornstarch <3" width="55" height="59"> <img src="https://github.com/user-attachments/assets/8d00db25-670b-4312-85ac-ee926787047b" alt="Cornstarch <3" width="55" height="59"> 

