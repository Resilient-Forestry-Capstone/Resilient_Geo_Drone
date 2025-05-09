# ResilientGeoDrone - A Point Cloud Forestry Analysis Tool
3-Staged Python Script Which Utilizes Provided Digital Aerial Photogrammetry To Create High Quality Point Clouds For Use In Geospatial Analysis Of Forest Canopies.

Program Uses _**QGIS**_ And _**WebODM**_ As Two Main Software Facillitators For The Point Cloud And Geospatial Analysis. Because Of The External Dependency To Interface With The _**QGIS**_ API We Utilize `Window`'s .bat Files For Linking.


----------------------------------------------


<h3>📑 Table of Contents</h3>


1. [🔍 The Breakdown](#the-breakdown)
   - [Architecture Diagram](#architecture-diagram)
   - [Core Components](#core-components)
   - [Stage-Specific Components](#stage-specific-components)
2. [🌟 Features](#features)
3. [🏗️ Additional Documents](#additionalDocuments)




----------------------------------------------

<img src="https://github.com/user-attachments/assets/d9dd1c40-ff1c-4ada-ac22-f3dc500c63c3" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/d9dd1c40-ff1c-4ada-ac22-f3dc500c63c3" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/d9dd1c40-ff1c-4ada-ac22-f3dc500c63c3" alt="Monkeys With A Drone" width="55" height="59"> <img src="https://github.com/user-attachments/assets/d9dd1c40-ff1c-4ada-ac22-f3dc500c63c3" alt="Monkeys With A Drone" width="55" height="59">

<h3 id="the-breakdown">🔍 The Breakdown:</h3>

<h4>Architecture Diagram</h4>

![image](https://github.com/user-attachments/assets/3ba7e594-e03c-4020-aa2b-ba5eda7621da)

<br>The Process Is Now Initialized Through A Modern User Interface Allowing Drag-And-Drop Functionality For Image Processing Through The MainClientWindow Class. The Current Architecture Retains The Core Environmental Parameter System For ___WebODM___ Software Integration, But Now Operates Through An Event-Driven Qt-Based Interface Rather Than Pure Command Line Execution.

Our External Dependency Management Still Employs A Custom .bat Script Which Configures The Necessary Environment, But Now The System Primarily Launches The GUI Interface Via MainClientWindow Rather Than Immediately Starting Pipeline Processing As We Deprecated Our Previous Usage Of ___QGIS___. This UI-First Approach Provides A More User-Friendly Experience While Maintaining The Technical Processing Power Of The Original System.

The Pipeline Architecture Has Been Significantly Enhanced With Multi-Threaded Execution Through The `PipelineWorker` Class Which Inherits From _QThread_, Allowing Long-Running Operations To Execute Without Blocking The User Interface. The Core Components Have Been Maintained But With Expanded Capabilities:

<h6>Core Components</h6>
A Logger Class (`LoggerSetup`): Enhanced To Track UI Events And Thread Operations In Addition To Pipeline Events
A Config Loader (`ConfigLoader`): Expanded With UI-Configurable Parameters Through A Settings Dialog Interface
A File Handler (`FileHandler`): Now Manages Both Input Directories From Drag-And-Drop Events And Structured Output Directory Hierarchies
<h6>Stage-Specific Components</h6> <h6>Stage 1: Image Preprocessing With Progress Updates</h6>
The Preprocessing Stage Has Been Enhanced With A Modern Batch Image Processor That Spawns Multiple Worker Threads Using Python's `ThreadPoolExecutor`. This Implementation Provides Significant Performance Improvements Through Parallel Processing While Maintaining Thread-Safety For Image Validation Operations. The `BatchProcessor` Now Emits Progress Signals That Update The User Interface In Real-Time, Providing Feedback On Image Quality Assessment Including Resolution Checks, Blur Detection, Brightness Evaluation, And Contrast Analysis.

Each Image Is Processed Through An `ImageValidator` Component That Applies Configurable Thresholds For Quality Metrics. These Parameters Are User-Adjustable Through The Settings Dialog, With Configurations Persisted In The YAML Configuration File. When Image Validation Fails Due To Resolution, Blur Or Other Quality Issues, The System Now Clearly Reports These Failures In The UI Rather Than Silently Rejecting Files.

<h6>Stage 2: WebODM Point-Cloud Generation With Live Progress</h6>

The ___WebODM___ Integration Has Been Completely Refactored From A Blocking Synchronous Implementation To A Signal-Based Asynchronous System. The `WebODMClient` Component Now Connects To WebODM Using Configurable Connection Parameters (Username, Password, Host, Port) And Features A Reliable Authentication System With Token-Based Session Management.

As ___WebODM___ Processing Is Time-Intensive, The System Implements A Sophisticated Progress Tracking Mechanism. This Is Accomplished By Continuously Polling The WebODM API For Task Status, Then Emitting Progress Signals (progress_updated_status) That Update The UI Progress Bar With Detailed Status Messages.

During Processing, The ___WebODM___ Client Creates Projects, Uploads Images, Configures Processing Parameters Based On Environmental Conditions (Sunny, Rainy, Foggy), And Monitors Task Execution. Upon Completion, It Downloads Multiple Assets Including Digital Surface Models (DSM), Digital Terrain Models (DTM), Orthophotos, Point Cloud Files (.laz), And Generated Reports. All Of These Assets Are Saved In A Timestamped Output Directory Structure.

<h6>Stage 3: Canopy Height Model And Gap Analysis</h6>
The Final Stage Implements Enhanced Analysis Features Through The Integration Of The New `GapDetector` Component. This Component Performs Advanced Geospatial Analytics On The Generated Point Clouds.

The System Generates Canopy Height Models (CHM) By Computing The Difference Between DSM And DTM, With Sophisticated Handling Of NoData Values. When DSM And DTM Have Different Resolutions, The System Resamples Them Using Bilinear Interpolation To Ensure Proper Alignment Before CHM Generation. This Process Uses The Rasterio Library For Geospatial Transformations And Properly Preserves Coordinate Reference Systems (CRS) And Geospatial Metadata.

The Gap Detector Then Applies Configurable Height Thresholds To Identify Forest Canopy Gaps. It Uses Connected Component Analysis To Delineate Individual Gaps And Calculates Various Metrics For Each Gap Including Area, Perimeter, Circularity, And Centroid Coordinates. These Gaps Are Vectorized Into Polygons And Stored In _GeoDataFrame_ Format With Associated Metrics.

The Analysis Produces Multiple Output Products:

Canopy Height Model _GeoTIFF_ Files
Gap Vector Files (_GeoPackage_ Format)
CSV Reports With Gap Metrics
Summary Statistics Text Files
Visualizations Of Gaps Overlaid On Orthophotos
Detailed Gap Analysis Reports
<h6>Results Viewing And Exploration</h6>

The Final Results Can Be Explored Through The `ResultsViewerWidget`, A Specialized Component For Interactive Visualization Of Generated Outputs. This Viewer Provides Access To DSM, DTM, Orthophotos, CHM, And Generated Reports. It Supports Basic GIS Functionality Including Layer Toggling, Distance Measurement, And Attribute Examination.

<h6>Exception Handling And Resilience</h6>
The System Now Implements Comprehensive Exception Handling At Each Stage, Providing User-Friendly Feedback When Issues Occur Rather Than Crashing. Failed Stages Are Clearly Reported With Detailed Messages In The User Interface. This Robust Error Handling Strategy Includes:

Validation Exceptions For Invalid Images
Connection Exceptions For WebODM Communication Issues
Processing Exceptions For Point Cloud Generation Failures
Analysis Exceptions For Gap Detection Problems
This Architecture Evolution Represents A Significant Enhancement In Both User Experience And Technical Capability While Maintaining The Core Processing Pipeline That Made The Original System Effective.

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



----------------------------------------------


<h3 id="additionalDocuments">🏗️ Additional Documents:</h3>

<h4>User Resources & Documentation</h4>
<a href="https://colab.research.google.com/drive/1jcTHM3HCaJ1qFnkUvrGkAXTe_YUrozMf?usp=sharing" target="_blank">Documentation</a><br>
<a href="https://colab.research.google.com/drive/1jNO7_kG1UmCKrqQNBmvPGhgTCfkMYllN?usp=sharing" target="_blank">User Manual</a><br><br>

<h4>Technical & Project Documentation</h4>
<a href="https://docs.google.com/document/d/1Bqws8frZD-5I0rI0Xwkueb98Aeva9kvB/edit?usp=sharing&ouid=113497198781082727325&rtpof=true&sd=true">Project Document</a><br>
<a href="https://docs.google.com/document/d/1ZxcAY7KImUwXDi1PurcVOaRES5GLi2UW/edit?usp=sharing&ouid=113497198781082727325&rtpof=true&sd=true">Scope Document</a><br>
<a href="https://docs.google.com/document/d/1nacwGeTUOO5oRy9UE1OUEOxUP9ydSuve/edit?usp=sharing&ouid=113497198781082727325&rtpof=true&sd=true">Design Document</a>

