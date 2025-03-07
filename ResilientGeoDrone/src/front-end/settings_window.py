from pathlib import Path
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QFormLayout,
                           QSpinBox, QLineEdit, QComboBox, QPushButton,
                           QDoubleSpinBox, QListWidget, QHBoxLayout,
                           QFileDialog, QMessageBox, QGroupBox, QLabel,
                           QCheckBox, QInputDialog)
from PyQt5.QtCore import Qt
import yaml
import os



"""

    Desc: This Module Provides A Settings Window For The User To Adjust
    The Configuration Parameters Of The Pipeline. The Settings Window
    Will Allow The User To Adjust Preprocessing, Point Cloud, And Geospatial
    Configuration Parameters. The Window Is Formatted As A Tabbed Widget
    With Each Tab Representative Of A Configuration Section. 


"""
class SettingsWindow(QWidget):

    """
    
        Desc: Initializes Our Settings Window With A Configuration Path
        For Loading Of Our Configuration Parameters. The Settings Window
        Will Allow The User To Adjust Preprocessing, Point Cloud, And
        Geospatial Configuration Parameters. The Intializer Also
        Establishes Two Buttons For Saving And Resetting The Settings.
        Our Window Is Layed Out In A Vertical Layout With Tabs For Each
        Configuration Section.

        Preconditions:
            1. config_path: Path To Configuration File
            2. config_path Must Be A Valid Path
        
        Postconditions:
            1. Set Our Configuration Path
            2. Load Our Configuration Parameters
            3. Create A Tabbed Widget For Each Configuration Section
            4. Add Buttons For Saving And Resetting The Settings
            5. Set-Up A Vertical Layout For Our Window
    
    """
    def __init__(self, config_path = Path(__file__).parent.parent.parent / "config/config.yaml"):
        # Initialize QWidget Superclass
        super().__init__()

        # Set-Up Our Config Path
        self.config_path = config_path
        self.env_widgets = {}

        # Set-Up Our Pop-Up Window
        self.setWindowTitle("Settings")
        self.setMinimumSize(800, 600)

        # Load Current Config
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Set-Up A Vertical Layout (Make Our Overall Settings In A Stacked Order)
        layout = QVBoxLayout(self)
        
        # Create Our Top Tab Widgets
        tabs = QTabWidget()
        self.add_preprocessing_tab(tabs)
        self.add_point_cloud_tab(tabs)
        self.add_geospatial_tab(tabs)
        layout.addWidget(tabs)

        # Buttons Formatting
        buttons_layout = QHBoxLayout()

        save_btn = QPushButton("Save Settings")
        reset_btn = QPushButton("Reset to Defaults")

        # Connect Them To Their Function
        save_btn.clicked.connect(self.save_settings)
        reset_btn.clicked.connect(self.reset_settings)

        # Add The Buttons To The Layout
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(reset_btn)

        # Add The Buttons Layout To The Main Layout
        layout.addLayout(buttons_layout)


    """
    
        Desc: Function Adds A Tab For Preprocessing Settings. The Tab
        Will Allow The User To Adjust The Supported Image Formats, Minimum
        Resolution, Blur Threshold, Brightness Range, And Maximum Workers
        For Preprocessing Images. The Parts Are All Formatted In A 2-Column
        Layout For Easy User Access. It Also Provides Buttons For The Adding
        And Removing Of Supported Image Formats.

        Preconditions:
            1. tabs: QTabWidget Object
        
        Postconditions:
            1. Add A Tab For Preprocessing Settings To The Tab Widget
            2. Add Supported Image Formats, Minimum Resolution, Blur Threshold, Brightness Range, And Maximum Workers To The Tab
    
    """
    def add_preprocessing_tab(self, tabs):
        # Create A Tab For Preprocessing
        tab = QWidget()

        # Create A Form Layout
        layout = QFormLayout(tab)

        # Supported Formats Of Image
        formats_group = QGroupBox("Supported Formats")
        formats_layout = QVBoxLayout()

        # Create A List Widget
        self.formats_list = QListWidget()
        # Add The Supported Formats To The List
        self.formats_list.addItems(self.config['preprocessing']['supported_formats'])

        # Create Buttons For Adding And Removing Image Formats (.png, .jpg, ...)
        format_buttons = QHBoxLayout()
        add_format_btn = QPushButton("Add")
        remove_format_btn = QPushButton("Remove")
        
        # Connect The Buttons To Their Functions
        add_format_btn.clicked.connect(self.add_format)
        remove_format_btn.clicked.connect(self.remove_format)

        # Add The Buttons To Our Layout
        format_buttons.addWidget(add_format_btn)
        format_buttons.addWidget(remove_format_btn)

        # Add Widgets To The Layout For The Row
        formats_layout.addWidget(self.formats_list)

        # Add The Buttons Layout To The Layout Of The Image Formats
        formats_layout.addLayout(format_buttons)
        formats_group.setLayout(formats_layout)

        # Add The Formats Group To The Main Layout
        layout.addRow(formats_group)

        # Now Set-Up For Our Resolution Row
        res_group = QGroupBox("Minimum Resolution")
        res_layout = QFormLayout()

        # Create Spin Boxes For Width And Height
        self.width = QSpinBox()
        self.height = QSpinBox()

        # Set The Range Of The Spin Boxes
        self.width.setRange(0, 10000)
        self.height.setRange(0, 10000)

        # Set The Default Values
        self.width.setValue(self.config['preprocessing']['min_resolution'][0])
        self.height.setValue(self.config['preprocessing']['min_resolution'][1])

        # Add The Spin Boxes To The Layout
        res_layout.addRow("Width:", self.width)
        res_layout.addRow("Height:", self.height)

        # Add The Row To The Group
        res_group.setLayout(res_layout)
        layout.addRow(res_group)

        # Set-Up Processing Settings Row
        proc_group = QGroupBox("Processing Settings")
        proc_layout = QFormLayout()

        # Create Spin Boxes For Blur, Brightness, And Max Workerss
        self.blur = QSpinBox()
        self.blur.setRange(0, 1000)

        self.blur.setValue(self.config['preprocessing']['blur_threshold'])
        proc_layout.addRow("Blur Threshold:", self.blur)

        self.bright_min = QSpinBox()
        self.bright_max = QSpinBox()
        self.bright_min.setRange(0, 255)
        self.bright_max.setRange(0, 255)

        self.bright_min.setValue(self.config['preprocessing']['brightness_range'][0])
        self.bright_max.setValue(self.config['preprocessing']['brightness_range'][1])

        proc_layout.addRow("Min Brightness:", self.bright_min)
        proc_layout.addRow("Max Brightness:", self.bright_max)

        self.max_workers = QSpinBox()
        self.max_workers.setRange(1, 32)

        self.max_workers.setValue(self.config['preprocessing']['max_workers'])
        proc_layout.addRow("Max Workers:", self.max_workers)

        # Add The Processing Settings Row To The Group
        proc_group.setLayout(proc_layout)
        layout.addRow(proc_group)

        # Finally Implement Our Tab To The Main Tab
        tabs.addTab(tab, "Preprocessing")


    """

        Desc: Function Adds A Tab For Point Cloud Settings. The Tab
        Will Allow The User To Adjust The WebODM Connection Settings
        And Environment Settings For Point Cloud Generation. The Tab
        Will Also Allow The User To Adjust The Quality, Min Features,
        Matcher, And Max Concurrency For Each Environment. The Tab
        Will Also Allow The User To Adjust The Point Cloud Quality,
        Mesh Quality, And Ignore GSD For Foggy Environments.

        Preconditions:
            1. tabs: QTabWidget Object
        
        Postconditions:
            1. Add A Tab For Point Cloud Settings To The Tab Widget
            2. Add WebODM Connection Settings And Environment Settings To The Tab

    """
    def add_point_cloud_tab(self, tabs):
        # Create A Tab For Point Cloud
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Set-Up WebODM Connection Settings Group
        webodm_group = QGroupBox("WebODM Connection")
        webodm_layout = QFormLayout()

        # Create A Entry For Our Port And Host Name For WebODM API 
        self.host = QLineEdit(self.config['point_cloud']['webodm']['host'])
        self.port = QSpinBox()
        self.port.setRange(0, 65535)

        self.port.setValue(self.config['point_cloud']['webodm']['port'])

        # Ask The Authentication Information For Their WebODM Session
        self.username = QLineEdit(self.config['point_cloud']['webodm']['username'])
        self.password = QLineEdit(self.config['point_cloud']['webodm']['password'])

        # Censor The Password
        self.password.setEchoMode(QLineEdit.Password)

        # Ask For The Timeout For The WebODM Session (For API Access Key)
        self.timeout = QSpinBox()
        self.timeout.setRange(0, 86400)
        
        self.timeout.setValue(self.config['point_cloud']['webodm']['timeout'])

        # Add The Widgets To The Layout In A Row Format
        webodm_layout.addRow("Host:", self.host)
        webodm_layout.addRow("Port:", self.port)
        webodm_layout.addRow("Username:", self.username)
        webodm_layout.addRow("Password:", self.password)
        webodm_layout.addRow("Timeout (s):", self.timeout)

        # Add The Layout To The Group
        webodm_group.setLayout(webodm_layout)
        layout.addWidget(webodm_group)

        # Environment Settings Group
        env_group = QGroupBox("Environment Settings")
        env_layout = QVBoxLayout()

        self.env_tabs = QTabWidget()
        for env in ['sunny', 'rainy', 'foggy', 'night']:

            # Add Dictionary Element
            self.env_widgets[env] = {}

            env_tab = QWidget()
            tab_layout = QFormLayout(env_tab)

            # Feature Settings
            feature_group = QGroupBox("Feature Settings")
            feature_layout = QFormLayout()

            # Get Values They Could Pick For Quality
            quality = QComboBox()
            quality.addItems(['ultra', 'high', 'medium', 'low'])

            quality.setCurrentText(self.config['point_cloud']['webodm']['environments'][env]['feature_quality'])

            # Store In Dynamic Dictionary For Later Use
            self.env_widgets[env]['quality'] = quality

            # Add The Quality To The Layout
            feature_layout.addRow("Quality:", quality)

            # Set-Up Min Features, Matcher, And Max Concurrency
            min_features = QSpinBox()
            min_features.setRange(1000, 20000)

            min_features.setValue(self.config['point_cloud']['webodm']['environments'][env]['min_num_features'])

            # Store In Dynamic Dictionary For Later Use
            self.env_widgets[env]['min_features'] = min_features

            # Add The Min Features To The Layout
            feature_layout.addRow("Min Features:", min_features)

            # Set-Up Matcher Parameter
            matcher = QComboBox()
            matcher.addItems(['bfmatcher', 'flann'])

            matcher.setCurrentText(self.config['point_cloud']['webodm']['environments'][env]['matcher_type'])
            
            # Store In Dynamic Dictionary For Later Use
            self.env_widgets[env]['matcher'] = matcher

            # Add The Matcher To The Layout
            feature_layout.addRow("Matcher:", matcher)

            # Add The Feature Layout To The Group
            feature_group.setLayout(feature_layout)
            tab_layout.addWidget(feature_group)

            # Quality Settings
            quality_group = QGroupBox("Quality Settings")
            quality_layout = QFormLayout()

            # Set-Up Point Cloud Quality
            point_cloud_quality = QComboBox()
            point_cloud_quality.addItems(['ultra', 'high', 'medium', 'low'])

            point_cloud_quality.setCurrentText(self.config['point_cloud']['webodm']['environments'][env]['point_cloud_quality'])

            # Store In Dynamic Dictionary For Later Use
            self.env_widgets[env]['pc_quality'] = point_cloud_quality

            # Add The Point Cloud Quality To The Layout
            quality_layout.addRow("Point Cloud:", point_cloud_quality)

            # Set-Up Mesh Quality
            mesh_quality = QComboBox()
            mesh_quality.addItems(['ultra', 'high', 'medium', 'low'])

            mesh_quality.setCurrentText(self.config['point_cloud']['webodm']['environments'][env]['mesh_quality'])

            # Store In Dynamic Dictionary For Later Use
            self.env_widgets[env]['mesh_quality'] = mesh_quality

            # Add The Mesh Quality To The Layout
            quality_layout.addRow("Mesh:", mesh_quality)

            # Add The Quality Layout To The Group
            quality_group.setLayout(quality_layout)
            tab_layout.addWidget(quality_group)

            # Processing Settings
            proc_group = QGroupBox("Processing Settings")
            proc_layout = QFormLayout()

            # Set-Up Max Concurrency
            max_concurrency = QSpinBox()
            max_concurrency.setRange(1, 16)

            max_concurrency.setValue(self.config['point_cloud']['webodm']['environments'][env]['max_concurrency'])

            # Store In Dynamic Dictionary For Later Use
            self.env_widgets[env]['concurrency'] = max_concurrency

            # Add The Max Concurrency To The Layout
            proc_layout.addRow("Max Concurrency:", max_concurrency)

            # If The Environment Is Foggy, Add The Ignore GSD Checkbox
            if env == 'foggy':
                ignore_gsd = QCheckBox()
                ignore_gsd.setChecked(self.config['point_cloud']['webodm']['environments'][env].get('ignore_gsd', False))

                # Store In Dynamic Dictionary For Later Use
                self.env_widgets[env]['ignore_gsd'] = ignore_gsd

                # Add The Ignore GSD To The Layout
                proc_layout.addRow("Ignore GSD:", ignore_gsd)
            
            # Add The Processing Layout To The Group
            proc_group.setLayout(proc_layout)
            tab_layout.addWidget(proc_group)

            # Add The Environment Layout To The Tab
            env_tab.setLayout(tab_layout)
            self.env_tabs.addTab(env_tab, env.capitalize())

        # Add The Environment Layout To The Group
        env_group.setLayout(env_layout)
        layout.addWidget(self.env_tabs)

        # Add The Environment Group To The Main Layout
        tabs.addTab(tab, "Point Cloud")


    """
    
        Desc: Function Adds A Tab For Geospatial Settings. The Tab
        Will Allow The User To Adjust The QGIS Path, Analysis Settings,
        Terrain Settings, And Output Settings. The Tab Will Allow The
        User To Adjust The Min Tree Height, Canopy Threshold, Slope
        Threshold, Roughness Threshold, Output Formats, And Resolution.

        Preconditions:
            1. tabs: QTabWidget Object

        Postconditions:
            1. Add A Tab For Geospatial Settings To The Tab Widget
            2. Add QGIS Path, Analysis Settings, Terrain Settings, And Output Settings To The Tab
    
    """
    def add_geospatial_tab(self, tabs):
        # Create A Tab For Geospatial Settings
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Set-Up QGIS Settings Group
        qgis_group = QGroupBox("QGIS Settings")
        qgis_layout = QHBoxLayout()

        # Create A Line Edit For The QGIS Path
        self.qgis_path = QLineEdit(self.config['geospatial']['qgis_path'])
        browse_btn = QPushButton("Browse...")

        # Connect The Button To The Function
        browse_btn.clicked.connect(self.browse_qgis)

        # Add The Widgets To The Layout
        qgis_layout.addWidget(self.qgis_path)
        qgis_layout.addWidget(browse_btn)

        # Add The Layout To The Group
        qgis_group.setLayout(qgis_layout)

        # Add The Group To The Main Layout
        layout.addWidget(qgis_group)

        # Set-Up Analysis Settings Group
        analysis_group = QGroupBox("Analysis Settings")
        analysis_layout = QFormLayout()

        # Set-Up Min Tree Height And Canopy Threshold
        self.tree_height = QDoubleSpinBox()
        self.tree_height.setRange(0, 100)

        self.tree_height.setValue(self.config['geospatial']['analysis']['min_tree_height'])

        # Create A Double Spin Box For The Canopy Threshold
        analysis_layout.addRow("Min Tree Height (m):", self.tree_height)

        self.canopy = QDoubleSpinBox()
        self.canopy.setRange(0, 1)
        self.canopy.setSingleStep(0.1)

        self.canopy.setValue(self.config['geospatial']['analysis']['canopy_threshold'])
        analysis_layout.addRow("Canopy Threshold:", self.canopy)

        # Set-Up Terrain Settings Group
        terrain_group = QGroupBox("Terrain Analysis")
        terrain_layout = QFormLayout()

        # Set-Up Slope And Roughness Thresholds
        self.slope = QDoubleSpinBox()
        self.slope.setRange(0, 90)

        self.slope.setValue(self.config['geospatial']['analysis']['terrain']['slope_threshold'])

        # Create A Double Spin Box For The Roughness Threshold
        analysis_layout.addRow("Slope Threshold (°):", self.slope)

        self.roughness = QDoubleSpinBox()
        self.roughness.setRange(0, 1)
        self.roughness.setSingleStep(0.1)

        self.roughness.setValue(self.config['geospatial']['analysis']['terrain']['roughness_threshold'])

        # Add The Roughness Threshold To The Layout
        terrain_layout.addRow("Roughness Threshold:", self.roughness)

        # Add The Terrain Layout To The Group
        terrain_group.setLayout(terrain_layout)
        analysis_layout.addRow(terrain_group)

        # Add The Analysis Layout To The Group
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)

        # Set-Up Output Settings Group
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout()

        # Set-Up Output Formats And Resolution
        self.geo_formats_list = QListWidget()
        self.geo_formats_list.addItems(self.config['geospatial']['output']['formats'])

        # Add The Output Formats To The Layout
        output_layout.addRow("Output Formats:", self.geo_formats_list)

        self.resolution = QDoubleSpinBox()
        self.resolution.setRange(0.01, 1.0)
        self.resolution.setSingleStep(0.1)

        self.resolution.setValue(self.config['geospatial']['output']['resolution'])
        output_layout.addRow("Resolution (m/px):", self.resolution)

        # Add The Output Layout To The Group
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Add The Group To The Main Layout
        tabs.addTab(tab, "Geospatial")


    """
    
        Desc: Function Adds A Format To The Supported Image Formats List
        When The User Clicks The Add Button. The Function Will Prompt
        The User For A Format And Add It To The List. 

        Preconditions:
            1. None

        Postconditions:
            1. Add A Format To The Supported Image Formats List
    
    """
    def add_format(self):
        # Add A Format To The Supported Formats
        text, ok = QInputDialog.getText(self, "Add Format", "Enter format (e.g., .jpg):")
        if ok and text:
            self.formats_list.addItem(text)


    """
    
        Desc: Function Removes A Format From The Supported Image Formats
        List When The User Clicks The Remove Button. The Function Will
        Remove The Selected Format From The List.

        Preconditions:
            1. None

        Postconditions:
            1. Remove A Format From The Supported Image Formats
    
    """
    def remove_format(self):
        # Remove A Format From The Supported Formats
        row = self.formats_list.currentRow()
        if row >= 0:
            self.formats_list.takeItem(row)


    """
    
        Desc: Function Allows The User To Browse For The QGIS Executable
        When The User Clicks The Browse Button. The Function Will Open
        A File Dialog For The User To Select The QGIS Executable.

        Preconditions:
            1. None

        Postconditions:
            1. Open A File Dialog For The User To Select The QGIS Executable
    
    """
    def browse_qgis(self):
        # Browse For The QGIS Path
        path = QFileDialog.getOpenFileName(self, "Select QGIS Executable", filter="QGIS Executable (*.exe)")
        if path[0]:
            self.qgis_path.setText(path[0])


    """
    
        Desc: Function Saves The Settings To The Configuration File
        When The User Clicks The Save Settings Button. The Function
        Will Save The Specified Settings To The Configuration File,
        Including Preprocessing, Point Cloud, And Geospatial Settings.
        These Include Supported Formats, Minimum Resolution, Blur
        Threshold, Brightness Range, Maximum Workers, WebODM Connection
        Settings, Environment Settings, QGIS Path, Analysis Settings,
        Terrain Settings, And Output Settings. 

        Preconditions:
            1. None

        Postconditions:
            1. Save The Settings To The Configuration File
    
    """
    def save_settings(self):
        try:
            # Update Preprocessing Settings
            self.config['preprocessing']['supported_formats'] = [
                self.formats_list.item(i).text() 
                for i in range(self.formats_list.count())
            ]
            self.config['preprocessing']['min_resolution'] = [
                self.width.value(),
                self.height.value()
            ]
            self.config['preprocessing']['blur_threshold'] = self.blur.value()
            self.config['preprocessing']['brightness_range'] = [
                self.bright_min.value(),
                self.bright_max.value()
            ]
            self.config['preprocessing']['max_workers'] = self.max_workers.value()

            # Update Point Cloud Settings
            webodm = self.config['point_cloud']['webodm']
            webodm['host'] = self.host.text()
            webodm['port'] = self.port.value()
            webodm['username'] = self.username.text()
            webodm['password'] = self.password.text()
            webodm['timeout'] = self.timeout.value()

            # Update Environment Settings
            for env in ['sunny', 'rainy', 'foggy', 'night']:                
                
                env_config = webodm['environments'][env]
                env_config['feature_quality'] = self.env_widgets[env]['quality'].currentText()
                env_config['min_num_features'] = self.env_widgets[env]['min_features'].value()
                env_config['matcher_type'] = self.env_widgets[env]['matcher'].currentText()
                env_config['point_cloud_quality'] = self.env_widgets[env]['pc_quality'].currentText()
                env_config['mesh_quality'] = self.env_widgets[env]['mesh_quality'].currentText()
                env_config['max_concurrency'] = self.env_widgets[env]['concurrency'].value()
                
                if env == 'foggy':
                    env_config['ignore_gsd'] = self.env_widgets[env]['ignore_gsd'].isChecked()

            # Update Geospatial Settings
            self.config['geospatial']['qgis_path'] = self.qgis_path.text()
            self.config['geospatial']['analysis']['min_tree_height'] = self.tree_height.value()
            self.config['geospatial']['analysis']['canopy_threshold'] = self.canopy.value()
            self.config['geospatial']['analysis']['terrain']['slope_threshold'] = self.slope.value()
            self.config['geospatial']['analysis']['terrain']['roughness_threshold'] = self.roughness.value()
            self.config['geospatial']['output']['formats'] = [
                self.geo_formats_list.item(i).text() 
                for i in range(self.geo_formats_list.count())
            ]
            self.config['geospatial']['output']['resolution'] = self.resolution.value()

            # Save To File
            with open(self.config_path, 'w') as f:
                yaml.safe_dump(self.config, f, default_flow_style=False)
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")


    """
    
        Desc: Function Resets The Settings To The Default Configuration
        When The User Clicks The Reset Settings Button. The Function
        Will Reset The Configuration To The Default Configuration File
        And Reinitialize All Widgets.

        Preconditions:
            1. None

        Postconditions:
            1. Reset The Settings To The Default Configuration
            2. Reset Widgets To Default State
    
    """
    def reset_settings(self):
        try:
            # Load Default Config
            default_config_file = Path(__file__).parent.parent.parent / "config/default_config.yaml"

            # Now Add Changes
            with open(default_config_file, 'r') as f:
                self.config = yaml.safe_load(f)

            # Reinitialize all widgets
            self.__init__(self.config_path)
            QMessageBox.information(self, "Success", "Settings reset to defaults!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset settings: {str(e)}")