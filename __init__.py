from PySide6 import QtWidgets, QtGui, QtCore
import substance_painter.ui
import substance_painter.event
import substance_painter.export
import substance_painter.project
import substance_painter.textureset
import os
import sys
import importlib.util

_plugin_folder = os.path.dirname(os.path.abspath(__file__))
_version_file = os.path.join(_plugin_folder, "version.txt")

VERSION_CODE = "1.0.1"  # VERSION_FOR_GITHUB_ACTION - Update this when releasing

def read_version():
    try:
        with open(_version_file, "r") as f:
            return f.read().strip()
    except:
        return VERSION_CODE

VERSION = read_version()

_updater_spec = importlib.util.spec_from_file_location("updater", os.path.join(_plugin_folder, "updater.py"))
updater = importlib.util.module_from_spec(_updater_spec)
sys.modules["updater"] = updater
_updater_spec.loader.exec_module(updater)

plugin_widgets = []
output_path = ""
texture_sizes_index = 2
texture_sizes = ["128x128", "256x256", "512x512", "1024x1024", "2048x2048", "4096x4096"]

padding_modes = ["No padding (passthrough)", "Dilation infinite", "Dilation + transparent", "Dilation + default background color", "Dilation + diffusion"]
padding_algorithms = ["passthrough", "infinite", "transparent", "color", "diffusion"]
padding_index = 1

# Custom export buttons storage
custom_export_buttons = []
custom_export_layout = None
path_indicator = None
log_label = None

def validate_path(path):
    """Validate if path is valid and exists, returns (is_valid, error_message)"""
    if not path or path.strip() == "":
        return (False, None)
    # Normalize path
    normalized = os.path.normpath(path)
    # Check if directory exists
    if os.path.isdir(normalized):
        return (True, None)
    else:
        return (False, "Directory does not exist :\ncheck directory is not D://.......texture.tif or D://.....D://")

def update_path_indicator(path):
    """Update the path indicator color and log label based on validation"""
    global path_indicator, log_label
    is_valid, error_msg = validate_path(path)
    if path_indicator:
        if is_valid:
            path_indicator.setStyleSheet("background-color: #4CAF50; border-radius: 8px;")
        else:
            path_indicator.setStyleSheet("background-color: #F44336; border-radius: 8px;")
    if log_label:
        if is_valid or error_msg is None:
            log_label.setText("")
            log_label.setVisible(False)
        else:
            log_label.setText(f"Error: {error_msg}")
            log_label.setVisible(True)

# Available presets
ENFUSION_PRESETS = ["GLOBAL_MASK", "VFX", "MCR", "NMO", "BCR"]
def textureSize(size):
    if size == "128x128":
        return 7
    elif size == "256x256":
        return 8
    elif size == "512x512":
        return 9
    elif size == "1024x1024":
        return 10
    elif size == "2048x2048":
        return 11
    elif size == "4096x4096":
        return 12

def export_isolate(groupLayer):
        # get name of TextureSet
        stack = substance_painter.textureset.get_active_stack()
        # get root layer nodes
        rootLayer = substance_painter.layerstack.get_root_layer_nodes(stack)

        # Dictionary mapping layer names to their corresponding texture set identifiers
        layer_map = {
            "Global": "$textureSet_GLOBAL_MASK",
            "VFX": "$textureSet_VFX",
            "MCR": "$textureSet_MCR",
            "NMO": "$textureSet_NMO",
            "BCR": "$textureSet_BCR"
        }

        # Helper function to set visibility
        def set_visible(node, is_visible):
            substance_painter.layerstack.Node.set_visible(node, is_visible)
            
        # First hide all layers
        for node in rootLayer:
            set_visible(node, False)
        
        if groupLayer in layer_map:
            print(f"Exporting {groupLayer}"+" in " + layer_map[groupLayer])
            # Show the selected layer
            for node in rootLayer:
                group = substance_painter.layerstack.Node.get_name(node)
                if group == groupLayer:
                    set_visible(node, True)
                    export_enfution(output_path_input.text(), layer_map[groupLayer], size_dropdown.currentText(), padding_dropdown.currentIndex())                    
                else:
                    set_visible(node, False)
                    

def export_enfution(output_path, maps, selected_size, selected_padding_index):
    saveData(output_path)
    if not substance_painter.project.is_open():
        return

    stack = substance_painter.textureset.get_active_stack()
    material = stack.material()

    # Use the provided output path or the project file path
    if output_path:
        Path = output_path
    else:
        Path = substance_painter.project.file_path()
        Path = os.path.dirname(Path) + "/"

    padding_algo = padding_algorithms[selected_padding_index]
    padding_params = {"paddingAlgorithm": padding_algo, "sizeLog2": textureSize(selected_size)}
    # Add dilation distance for algorithms that need it (transparent, color, diffusion)
    if padding_algo in ["transparent", "color", "diffusion"]:
        padding_params["dilationDistance"] = dilation_spinbox.value()

    # Inline export preset (Enfusion_template)
    enfusion_preset = {
        "name": "Enfusion_template",
        "maps": [
            {
                "fileName": "$textureSet_GLOBAL_MASK",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "basecolor"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "basecolor"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "basecolor"}
                ],
                "parameters": {"fileFormat": "tif", "bitDepth": "8", "dithering": False}
            },
            {
                "fileName": "$textureSet_VFX",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "basecolor"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "basecolor"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "basecolor"}
                ],
                "parameters": {"fileFormat": "tif", "bitDepth": "8", "dithering": False}
            },
            {
                "fileName": "$textureSet_MCR",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "basecolor"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "basecolor"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "basecolor"},
                    {"destChannel": "A", "srcChannel": "L", "srcMapType": "documentMap", "srcMapName": "roughness"}
                ],
                "parameters": {"fileFormat": "tif", "bitDepth": "8", "dithering": False}
            },
            {
                "fileName": "$textureSet_NMO",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "virtualMap", "srcMapName": "Normal_DirectX"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "virtualMap", "srcMapName": "Normal_DirectX"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "virtualMap", "srcMapName": "Normal_DirectX"}
                ],
                "parameters": {"fileFormat": "tif", "bitDepth": "8", "dithering": False}
            },
            {
                "fileName": "$textureSet_BCR",
                "channels": [
                    {"destChannel": "R", "srcChannel": "R", "srcMapType": "documentMap", "srcMapName": "basecolor"},
                    {"destChannel": "G", "srcChannel": "G", "srcMapType": "documentMap", "srcMapName": "basecolor"},
                    {"destChannel": "B", "srcChannel": "B", "srcMapType": "documentMap", "srcMapName": "basecolor"},
                    {"destChannel": "A", "srcChannel": "L", "srcMapType": "documentMap", "srcMapName": "roughness"}
                ],
                "parameters": {"fileFormat": "tif", "bitDepth": "8", "dithering": False}
            }
        ]
    }

    config = {
        "exportShaderParams": False,
        "exportPath": Path,
        "exportList": [{"rootPath": str(stack),
            "filter" : {
            "outputMaps" : [maps]
            }}],
        "exportPresets": [enfusion_preset],
        "defaultExportPreset": "Enfusion_template",
        "exportParameters": [
            {
                "parameters": padding_params
            }
        ]
    }
    export_list = substance_painter.export.list_project_textures(config)
    print(export_list)
    substance_painter.export.export_project_textures(config)   


def export_all():
        # get name of TextureSet
        stack = substance_painter.textureset.get_active_stack()
        # get root layer nodes
        rootLayer = substance_painter.layerstack.get_root_layer_nodes(stack)
        
        # Dictionary mapping layer names to their corresponding texture set identifiers
        layer_map = {
            "Global": "$textureSet_GLOBAL_MASK",
            "VFX": "$textureSet_VFX",
            "MCR": "$textureSet_MCR",
            "NMO": "$textureSet_NMO",
            "BCR": "$textureSet_BCR"
        }
        
        # Helper function to set visibility
        def set_visible_and_export(node, is_visible):
            substance_painter.layerstack.Node.set_visible(node, is_visible)
            
        # First hide all layers
        for node in rootLayer:
            set_visible_and_export(node, False)
            
        # Then process each layer one by one
        for node in rootLayer:
            group = substance_painter.layerstack.Node.get_name(node)
            
            if group in layer_map:
                print(f"Exporting {group}")
                set_visible_and_export(node, True)
                export_enfution(output_path_input.text(), layer_map[group], size_dropdown.currentText(), padding_dropdown.currentIndex())
                set_visible_and_export(node, False)
            else:
                print(f"Skipping {group} - not in supported layers")


def show_message_box(message):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setText(message)
        msg_box.setWindowTitle("Error")
        msg_box.setIcon(QtWidgets.QMessageBox.Warning)
        msg_box.exec_()
    

def logX():
    for shelf in substance_painter.resource.Shelves.all():
        export_presets_dir = f"{shelf.path()}/export-presets"
        #print(shelf)
        if not os.path.isdir(export_presets_dir):
            continue
        for filename in os.listdir(export_presets_dir):
            if not filename.endswith(".spexp"):
                continue
            name = os.path.splitext(filename)[0]
            export_preset_id = substance_painter.resource.ResourceID(context=shelf.name(), name=name)
            export_preset = substance_painter.resource.Resource.retrieve(export_preset_id)[0]
            #print(export_preset.gui_name())
    # my_shelf = substance_painter.resource.Shelf("export") 
    # all_shelf_resources = my_shelf.resources() 
    # print(substance_painter)
    # for resource in all_shelf_resources: 
    #     print(resource.identifier().name) 
    #print("The name of the project is now: '{0}'".format(substance_painter.project.name())) 
    metadata = substance_painter.project.Metadata("PluginSaveData")
    save = ["testsavedata", 2]
    metadata.set("plugin_save_data", save)
    
    print("Save Data", metadata.get("plugin_save_data"))
    

def saveData(path):
    if not substance_painter.project.is_open():
        return
    global size_dropdown, padding_dropdown
    metadata = substance_painter.project.Metadata("PluginSaveData")
    PluginSaveData = [path, size_dropdown.currentIndex(), padding_dropdown.currentIndex()]
    metadata.set("plugin_save_data", PluginSaveData)
    print("Save Data", metadata.get("plugin_save_data"))

def my_callback(*args, **kwargs):
    global output_path, output_path_input, texture_sizes_index, padding_index, size_dropdown, padding_dropdown
    print(f'Callback: {substance_painter.project.file_path()}')

    metadata = substance_painter.project.Metadata("PluginSaveData")
    PluginSaveData = metadata.get("plugin_save_data")
    if not PluginSaveData:
        return

    output_path = PluginSaveData[0]
    texture_sizes_index = PluginSaveData[1]
    
    if len(PluginSaveData) > 2:
        padding_index = PluginSaveData[2]

    print(PluginSaveData)
    output_path_input.setText(output_path)
    size_dropdown.setCurrentIndex(texture_sizes_index)
    padding_dropdown.setCurrentIndex(padding_index)
    
def saveTriggered(*args, **kwargs):
    print("S A V E")

def get_root_layer_names():
    """Get all root layer names from current project"""
    if not substance_painter.project.is_open():
        return []
    try:
        stack = substance_painter.textureset.get_active_stack()
        rootLayer = substance_painter.layerstack.get_root_layer_nodes(stack)
        return [substance_painter.layerstack.Node.get_name(node) for node in rootLayer]
    except:
        return []

def export_custom(group_name, preset_name):
    """Export a specific group with a specific preset"""
    if not substance_painter.project.is_open():
        return
    
    stack = substance_painter.textureset.get_active_stack()
    rootLayer = substance_painter.layerstack.get_root_layer_nodes(stack)
    
    # Hide all layers first
    for node in rootLayer:
        substance_painter.layerstack.Node.set_visible(node, False)
    
    # Show only the target layer and export
    for node in rootLayer:
        if substance_painter.layerstack.Node.get_name(node) == group_name:
            substance_painter.layerstack.Node.set_visible(node, True)
            maps = f"$textureSet_{preset_name}"
            export_enfution(output_path_input.text(), maps, size_dropdown.currentText(), padding_dropdown.currentIndex())
            break

class CustomExportDialog(QtWidgets.QDialog):
    """Dialog for creating custom export buttons"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Custom Export")
        self.setMinimumWidth(300)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Group layer selection
        group_label = QtWidgets.QLabel("Select Group Layer:")
        self.group_combo = QtWidgets.QComboBox()
        layer_names = get_root_layer_names()
        self.group_combo.addItems(layer_names if layer_names else ["No layers found"])
        
        # Preset selection
        preset_label = QtWidgets.QLabel("Select Enfusion Preset:")
        self.preset_combo = QtWidgets.QComboBox()
        self.preset_combo.addItems(ENFUSION_PRESETS)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        create_btn = QtWidgets.QPushButton("Create")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        create_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        
        # Add to layout
        layout.addWidget(group_label)
        layout.addWidget(self.group_combo)
        layout.addWidget(preset_label)
        layout.addWidget(self.preset_combo)
        layout.addLayout(button_layout)
    
    def get_selection(self):
        return self.group_combo.currentText(), self.preset_combo.currentText()

def show_custom_export_dialog():
    """Show dialog and create custom export button"""
    global custom_export_layout, custom_export_buttons
    
    dialog = CustomExportDialog()
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        group_name, preset_name = dialog.get_selection()
        if group_name and group_name != "No layers found":
            # Create container for button row
            row_widget = QtWidgets.QWidget()
            row_layout = QtWidgets.QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            # Create export button
            btn_text = f"{group_name} → {preset_name}"
            new_btn = QtWidgets.QPushButton(btn_text)
            new_btn.clicked.connect(lambda checked=False, g=group_name, p=preset_name: export_custom(g, p))
            
            # Create delete button
            del_btn = QtWidgets.QPushButton("-")
            del_btn.setFixedWidth(30)
            del_btn.clicked.connect(lambda checked=False, w=row_widget: remove_custom_export(w))
            
            row_layout.addWidget(new_btn)
            row_layout.addWidget(del_btn)
            
            # Add to layout and storage
            custom_export_layout.addWidget(row_widget)
            custom_export_buttons.append({"widget": row_widget, "group": group_name, "preset": preset_name})

def remove_custom_export(row_widget):
    """Remove a custom export button"""
    global custom_export_buttons
    
    # Remove from layout
    row_widget.setParent(None)
    row_widget.deleteLater()
    
    # Remove from storage
    custom_export_buttons = [b for b in custom_export_buttons if b.get("widget") != row_widget]

def start_plugin():
    # Create a docked widget
    dev_label = QtWidgets.QLabel("Dev Tools")
    customExport_label = QtWidgets.QLabel("Custom Export")
    plugin_widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()
    plugin_widget.setLayout(layout)
    plugin_widget.setWindowTitle("Hello Export") 
    
    substance_painter.event.DISPATCHER.connect(substance_painter.event.ProjectOpened, my_callback)
    #substance_painter.event.DISPATCHER.connect(substance_painter.event.ProjectSaved, saveTriggered)
    # Create a dropdown for selecting the texture size
    global size_dropdown
    size_label = QtWidgets.QLabel("Texture Size:")
    size_dropdown = QtWidgets.QComboBox()
    size_dropdown.addItems(texture_sizes)
    
    #size_dropdown.activated.conext(saveData(size_dropdown.currentIndex()))
    
    global output_path_input, path_indicator
    
    # Create horizontal layout for path input with indicator and browse button
    path_layout = QtWidgets.QHBoxLayout()
    
    # Path indicator (colored circle)
    path_indicator = QtWidgets.QLabel()
    path_indicator.setFixedSize(16, 16)
    path_indicator.setStyleSheet("background-color: #F44336; border-radius: 8px;")
    
    # Path input field
    output_path_input = QtWidgets.QLineEdit()
    output_path_input.setPlaceholderText("Output Path")
    
    def on_path_changed(text):
        saveData(text)
        update_path_indicator(text)
    
    output_path_input.textChanged.connect(on_path_changed)
    output_path_input.setText(output_path)
    
    # Browse button
    def browse_folder():
        folder = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Output Folder", output_path_input.text())
        if folder:
            output_path_input.setText(folder)
            update_path_indicator(folder)
    
    bt_browse = QtWidgets.QPushButton("...")
    bt_browse.setFixedWidth(30)
    bt_browse.clicked.connect(browse_folder)
    
    path_layout.addWidget(path_indicator)
    path_layout.addWidget(output_path_input)
    path_layout.addWidget(bt_browse)
    
    # Log label for error messages
    global log_label
    log_label = QtWidgets.QLabel("")
    log_label.setStyleSheet("background-color: #1a1a1a; color: white; padding: 6px; border-radius: 4px;")
    log_label.setWordWrap(True)
    log_label.setVisible(False)
    
    # Initial validation
    update_path_indicator(output_path)

    global padding_dropdown, dilation_spinbox
    padding_label = QtWidgets.QLabel("Padding Type:")
    padding_dropdown = QtWidgets.QComboBox()
    padding_dropdown.addItems(padding_modes)
    
    # Dilation pixels input with slider
    dilation_label = QtWidgets.QLabel("Dilation (pixels):")
    dilation_layout = QtWidgets.QHBoxLayout()
    
    dilation_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    dilation_slider.setRange(0, 256)
    dilation_slider.setValue(16)
    dilation_slider.setEnabled(False)
    
    dilation_spinbox = QtWidgets.QSpinBox()
    dilation_spinbox.setRange(0, 256)
    dilation_spinbox.setValue(16)
    dilation_spinbox.setFixedWidth(50)
    dilation_spinbox.setEnabled(False)
    
    # Sync slider and spinbox
    dilation_slider.valueChanged.connect(dilation_spinbox.setValue)
    dilation_spinbox.valueChanged.connect(dilation_slider.setValue)
    
    dilation_layout.addWidget(dilation_slider)
    dilation_layout.addWidget(dilation_spinbox)
    
    # Show/hide dilation input based on padding type
    def on_padding_changed(index):
        algo = padding_algorithms[index]
        # Enable dilation for transparent, color, diffusion
        enabled = algo in ["transparent", "color", "diffusion"]
        dilation_spinbox.setEnabled(enabled)
        dilation_slider.setEnabled(enabled)
        saveData(output_path_input.text())
    
    padding_dropdown.currentIndexChanged.connect(on_padding_changed)
    

    # Create a button to trigger the export
    bt_export_mask = QtWidgets.QPushButton("Global")
    bt_export_mask.setFixedHeight(80)
    bt_export_vfx = QtWidgets.QPushButton("VFX")
    bt_export_vfx.setFixedHeight(80)
    bt_export_mcr = QtWidgets.QPushButton("MCR")
    bt_export_mcr.setFixedHeight(80)
    bt_export_nmo = QtWidgets.QPushButton("NMO")
    bt_export_bcr = QtWidgets.QPushButton("BCR")
    bt_export_bcr.setFixedHeight(80)

    ##bt_export_isolate = QtWidgets.QPushButton("Export Selection")
    #bt_export_all = QtWidgets.QPushButton("Export All")
    bt_logX = QtWidgets.QPushButton("LogX")

    # Connect the button to the export_textures function with the output path as an argument
    bt_export_mask.clicked.connect(lambda: export_isolate("Global"))
    bt_export_vfx.clicked.connect(lambda: export_isolate("VFX"))
    bt_export_mcr.clicked.connect(lambda: export_isolate("MCR"))
    bt_export_nmo.clicked.connect(lambda: export_isolate("NMO"))
    bt_export_bcr.clicked.connect(lambda: export_isolate("BCR"))

    ##bt_export_isolate.clicked.connect(export_isolate)
    #bt_export_all.clicked.connect(export_all)
    bt_logX.clicked.connect(lambda: logX())    

    # Add the label, input field, and button to the layout
    # layout.addWidget(label)
    layout.addLayout(path_layout)
    layout.addWidget(log_label)
    layout.addWidget(size_label)
    layout.addWidget(size_dropdown)
    layout.addWidget(padding_label)
    layout.addWidget(padding_dropdown)
    layout.addWidget(dilation_label)
    layout.addLayout(dilation_layout)
    
    # Create grid layout for export buttons (2 columns)
    export_grid = QtWidgets.QGridLayout()
    export_grid.addWidget(bt_export_mask, 0, 0)
    export_grid.addWidget(bt_export_vfx, 0, 1)
    export_grid.addWidget(bt_export_mcr, 1, 0)
    export_grid.addWidget(bt_export_bcr, 1, 1)
    export_grid.addWidget(bt_export_nmo, 2, 0, 1, 2)  # span 2 columns
    layout.addLayout(export_grid)

    # Custom Export section
    layout.addWidget(customExport_label)
    
    # Create horizontal layout for Custom Export header with + button
    custom_header_layout = QtWidgets.QHBoxLayout()
    bt_add_custom = QtWidgets.QPushButton("+")
    bt_add_custom.setFixedWidth(30)
    bt_add_custom.clicked.connect(show_custom_export_dialog)
    custom_header_layout.addWidget(bt_add_custom)
    custom_header_layout.addStretch()
    layout.addLayout(custom_header_layout)
    
    # Container for custom export buttons
    global custom_export_layout
    custom_export_layout = QtWidgets.QVBoxLayout()
    layout.addLayout(custom_export_layout)
    
    # Version Update section
    version_label = QtWidgets.QLabel(f"Version: {VERSION}")
    version_label.setStyleSheet("color: #888; font-size: 10px;")
    
    global update_status_label, bt_version
    update_status_label = QtWidgets.QLabel("")
    update_status_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
    
    bt_version = QtWidgets.QPushButton("Version Manager")
    bt_version.setFixedHeight(30)
    
    all_releases_data = []
    
    def show_version_dialog():
        global all_releases_data
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Version Manager")
        dialog.setMinimumWidth(400)
        dialog_layout = QtWidgets.QVBoxLayout(dialog)
        
        current_info = QtWidgets.QLabel(f"Current Version: {VERSION}")
        current_info.setStyleSheet("font-weight: bold;")
        dialog_layout.addWidget(current_info)
        
        status_info = QtWidgets.QLabel()
        if all_releases_data:
            latest = all_releases_data[0]
            cmp = updater.compare_versions(VERSION, latest['tag'])
            if cmp < 0:
                status_info.setText(f"Update available: {latest['tag']}")
                status_info.setStyleSheet("color: #FF9800;")
            else:
                status_info.setText("Up to date")
                status_info.setStyleSheet("color: #4CAF50;")
        else:
            status_info.setText("Unable to check updates")
            status_info.setStyleSheet("color: #F44336;")
        dialog_layout.addWidget(status_info)
        
        dialog_layout.addWidget(QtWidgets.QLabel(""))
        
        update_btn = QtWidgets.QPushButton("Update to Latest")
        update_btn.setFixedHeight(40)
        
        revert_label = QtWidgets.QLabel("Revert to version:")
        revert_combo = QtWidgets.QComboBox()
        revert_combo.addItem("Select version...", {"url": None, "tag": None})
        for rel in all_releases_data:
            revert_combo.addItem(f"{rel['tag']} - {rel['date']}", {"url": rel['zip_url'], "tag": rel['tag']})
        
        dialog_layout.addWidget(update_btn)
        dialog_layout.addWidget(revert_label)
        dialog_layout.addWidget(revert_combo)
        
        def on_update():
            if not all_releases_data:
                return
            latest = all_releases_data[0]
            if updater.compare_versions(VERSION, latest['tag']) >= 0:
                return
            plugin_folder = updater.get_plugin_folder()
            success = updater.download_and_extract(latest['zip_url'], plugin_folder, latest['tag'])
            dialog.close()
            if success:
                msg = QtWidgets.QMessageBox()
                msg.setWindowTitle("Update Successful")
                msg.setText("Update successful. Please disable and re-enable the plugin to apply changes.")
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.exec_()
            else:
                msg = QtWidgets.QMessageBox()
                msg.setWindowTitle("Update Failed")
                msg.setText("Failed to download update. Please try again.")
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.exec_()
        
        def on_revert(index):
            if index <= 0:
                return
            reply = QtWidgets.QMessageBox.question(
                None, "Confirm Revert",
                f"Revert to {revert_combo.currentText()}?\nThis will replace plugin files.",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                data = revert_combo.currentData()
                zip_url = data["url"]
                tag = data["tag"]
                plugin_folder = updater.get_plugin_folder()
                success = updater.download_and_extract(zip_url, plugin_folder, tag)
                dialog.close()
                if success:
                    msg = QtWidgets.QMessageBox()
                    msg.setWindowTitle("Revert Successful")
                    msg.setText("Revert successful. Please disable and re-enable the plugin to apply changes.")
                    msg.setIcon(QtWidgets.QMessageBox.Information)
                    msg.exec_()
                else:
                    msg = QtWidgets.QMessageBox()
                    msg.setWindowTitle("Revert Failed")
                    msg.setText("Failed to download version. Please try again.")
                    msg.setIcon(QtWidgets.QMessageBox.Warning)
                    msg.exec_()
                revert_combo.setCurrentIndex(0)
        
        update_btn.clicked.connect(on_update)
        revert_combo.currentIndexChanged.connect(on_revert)
        
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        dialog_layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def on_check_updates():
        global all_releases_data
        has_update, latest_tag, latest_info, all_releases = updater.check_for_updates(VERSION)
        all_releases_data = all_releases
        if not all_releases:
            update_status_label.setText("Unable to check updates")
            update_status_label.setStyleSheet("color: #F44336; font-size: 10px;")
            return
        
        if has_update:
            update_status_label.setText(f"Update available: {latest_tag}")
            update_status_label.setStyleSheet("color: #FF9800; font-size: 10px;")
        else:
            update_status_label.setText("Up to date")
            update_status_label.setStyleSheet("color: #4CAF50; font-size: 10px;")
    
    bt_version.clicked.connect(show_version_dialog)
    
    layout.addWidget(version_label)
    layout.addWidget(bt_version)
    layout.addWidget(update_status_label)
    
    # Auto-check for updates on startup
    on_check_updates()

    # Add the docked widget to the UI
    substance_painter.ui.add_dock_widget(plugin_widget)

    # Store the widget for proper cleanup later when stopping the plugin
    plugin_widgets.append(plugin_widget) 

def close_plugin():
    # Remove all widgets that have been added to the UI
    for widget in plugin_widgets:
        substance_painter.ui.delete_ui_element(widget)
    plugin_widgets.clear()

if __name__ == "__main__":
    start_plugin()