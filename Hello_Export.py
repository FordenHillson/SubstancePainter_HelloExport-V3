from PySide2 import QtWidgets, QtGui
import substance_painter.ui
import substance_painter.export
import substance_painter.project
import substance_painter.textureset
import os

plugin_widgets = []
output_path = ""


def export_enfution(output_path, maps):
    if not substance_painter.project.is_open():
        return

    stack = substance_painter.textureset.get_active_stack()
    material = stack.material()

    export_preset = substance_painter.resource.ResourceID(
        context="your_assets",
        name="Enfusion_template"
    )
    resolution = material.get_resolution()

    # Use the provided output path or the project file path
    if output_path:
        Path = output_path
    else:
        Path = substance_painter.project.file_path()
        Path = os.path.dirname(Path) + "/"

    #project_output_directory = substance_painter.project.get_output_path()
    config = {
        "exportShaderParams": False,
        "exportPath": Path,
        "exportList": [{"rootPath": str(stack),
            "filter" : {
            "outputMaps" : [maps]
            }}],
        "exportPresets": [{"name": "default", "maps": []}],  # Specify the desired map name (e.g., "Diffuse")
        "defaultExportPreset": export_preset.url(),
        "exportParameters": [
            {
                "parameters": {"paddingAlgorithm": "infinite"}
            }
        ]
    }
    export_list = substance_painter.export.list_project_textures(config)
    print(export_list)
    substance_painter.export.export_project_textures(config)
    

def logX():
    for shelf in substance_painter.resource.Shelves.all():
        export_presets_dir = f"{shelf.path()}/export-presets"
        print(shelf)
        if not os.path.isdir(export_presets_dir):
            continue
        for filename in os.listdir(export_presets_dir):
            if not filename.endswith(".spexp"):
                continue
            name = os.path.splitext(filename)[0]
            export_preset_id = substance_painter.resource.ResourceID(context=shelf.name(), name=name)
            export_preset = substance_painter.resource.Resource.retrieve(export_preset_id)[0]
            print(export_preset.gui_name())
    # my_shelf = substance_painter.resource.Shelf("export") 
    # all_shelf_resources = my_shelf.resources() 
    # print(substance_painter)
    # for resource in all_shelf_resources: 
    #     print(resource.identifier().name) 
    #print("The name of the project is now: '{0}'".format(substance_painter.project.name())) 
    metadata = substance_painter.project.Metadata("PluginSaveData")
    metadata.set("plugin_save_data", "testsavedata")
    

def saveData(path):
    metadata = substance_painter.project.Metadata("PluginSaveData")
    metadata.set("plugin_save_data", path)
    print("Save Data", metadata.get("plugin_save_data"))

def start_plugin():
    # Create a docked widget
    dev_label = QtWidgets.QLabel("Dev Tools")
    plugin_widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()
    plugin_widget.setLayout(layout)
    plugin_widget.setWindowTitle("Hello Export") 
    
    
    metadata = substance_painter.project.Metadata("PluginSaveData")
    
    # Add a label with the text "Hello"
    # label = QtWidgets.QLabel("Hello")

    # Create an input field for the output path
    output_path_input = QtWidgets.QLineEdit()
    output_path_input.setPlaceholderText("Output Path")
    output_path_input.setText(metadata.get("plugin_save_data"))
    output_path_input.textChanged.connect(lambda text = output_path_input.text(): saveData(text))
    

    # Create a button to trigger the export
    bt_export_mask = QtWidgets.QPushButton("Global Mask")
    bt_export_vfx = QtWidgets.QPushButton("VFX")
    bt_export_mcr = QtWidgets.QPushButton("MCR")
    bt_export_nmo = QtWidgets.QPushButton("NMO")
    bt_logX = QtWidgets.QPushButton("LogX")

    # Connect the button to the export_textures function with the output path as an argument
    bt_export_mask.clicked.connect(lambda: export_enfution(output_path_input.text(), "$textureSet_GLOBAL_MASK"))
    bt_export_vfx.clicked.connect(lambda: export_enfution(output_path_input.text(), "$textureSet_VFX"))
    bt_export_mcr.clicked.connect(lambda: export_enfution(output_path_input.text(), "$textureSet_MCR"))
    bt_export_nmo.clicked.connect(lambda: export_enfution(output_path_input.text(), "$textureSet_NMO"))
    bt_logX.clicked.connect(lambda: logX())

    # Add the label, input field, and button to the layout
    # layout.addWidget(label)
    layout.addWidget(output_path_input)
    layout.addWidget(bt_export_mask)
    layout.addWidget(bt_export_vfx)
    layout.addWidget(bt_export_mcr)
    layout.addWidget(bt_export_nmo)
    
    layout.addWidget(dev_label)
    layout.addWidget(bt_logX)
    
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
