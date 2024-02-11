import os
import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QRadioButton, QHBoxLayout, QButtonGroup, QCheckBox, QGroupBox, QMessageBox, QDesktopWidget
from PyQt5.QtCore import Qt

# Define the directory to save GIFs
gif_directory = "GIFs"

# Ensure the GIF directory exists
if not os.path.exists(gif_directory):
    os.makedirs(gif_directory)

# Global variable to store the selected FPS, scale and time
selected_fps = 20
selected_scale = "600"  # Default scale
selected_time = None  # Default time, meaning no time limit

# Global variable to store the override GIF option
override_gif = True

def video_to_gif(video_path):
    global selected_fps, override_gif, selected_scale, selected_time
    output_gif = os.path.join(gif_directory, f"{os.path.splitext(os.path.basename(video_path))[0]}.gif")
    
    scale_filter = f"scale={selected_scale}:-1:flags=lanczos," if selected_scale else ""
    time_option = ['-t', selected_time] if selected_time else []

    if os.path.exists(output_gif) and not override_gif:
        # Show confirmation dialog
        reply = QMessageBox.question(None, "Confirm Overwrite", "File already exists. Do you want to overwrite?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.No:
            return None  # Do not overwrite the file
    
    # Proceed with ffmpeg command, including '-y' to overwrite since user confirmed
    ffmpeg_command = [
        'ffmpeg', '-y',
        *time_option,
        '-i', video_path, '-vf',
        f"fps={selected_fps},{scale_filter}split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        '-loop', '0', output_gif
    ]
    
    subprocess.run(ffmpeg_command)
    return output_gif

class DropLabel(QLabel):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                padding: 5px;
                font-size: 36px; /* Increased font size */
            }
        """)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            video_path = url.toLocalFile()
            if video_path.endswith(('.mp4', '.webm', '.avi', '.mov', '.flv', '.mkv', '.mpeg', '.wmv')):
                gif_path = video_to_gif(video_path)
                if gif_path:
                    self.setText(f"Converted to GIF: \n{os.path.basename(gif_path)}")
                else:
                    self.setText(f"Conversion canceled.")
            else:
                self.setText("Invalid file type. \nPlease drag a supported video file.")

def fps_changed(fps):
    global selected_fps
    selected_fps = fps

def scale_changed(scale):
    global selected_scale
    selected_scale = None if scale == "None" else scale

def time_changed(time):
    global selected_time
    selected_time = None if time == "None" else time

def override_changed(state):
    global override_gif
    override_gif = state == Qt.Checked

def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle('Video to GIF Converter')

    # Set initial size
    initialWidth = 500  # Assuming 500 is the current width you're satisfied with
    window.resize(initialWidth, initialWidth)  # Set height equal to twice the current width

    # Centering the window
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    window.move(qr.topLeft())

    main_layout = QVBoxLayout()
    label = DropLabel('Drag and Drop Video Files Here', window)
    main_layout.addWidget(label)

    # Create a horizontal layout for FPS options and the override toggle
    options_layout = QHBoxLayout()

    # Group Box for FPS Radio Buttons
    fps_group_box = QGroupBox("FPS Options")
    fps_layout = QHBoxLayout()
    fps_group = QButtonGroup(fps_group_box)
    fps_options = {20: "20 FPS", 10: "10 FPS", 8: "8 FPS"}
    for fps, text in fps_options.items():
        radio_btn = QRadioButton(text)
        fps_layout.addWidget(radio_btn)
        fps_group.addButton(radio_btn, fps)
        radio_btn.toggled.connect(lambda checked, fps=fps: fps_changed(fps) if checked else None)

    fps_group.button(20).setChecked(True)
    fps_group_box.setLayout(fps_layout)
    options_layout.addWidget(fps_group_box)

    # Inside the main function, after setting up the override GIF checkbox

    # Scale Options
    scale_group_box = QGroupBox("Scale Options")
    scale_group_box.setToolTip("Select the scale for the GIF. 'None' means no scaling.")
    scale_layout = QHBoxLayout()
    scale_group = QButtonGroup(window)  # Ensure the parent is set correctly
    scale_options = {"600": "600", "480": "480", "None": "None"}
    for scale, text in scale_options.items():
        radio_btn = QRadioButton(text)
        scale_layout.addWidget(radio_btn)
        scale_group.addButton(radio_btn)
        radio_btn.toggled.connect(lambda checked, scale=scale: scale_changed(scale) if checked else None)
        if scale == "600":  # Set default selection for scale
            radio_btn.setChecked(True)

    scale_group_box.setLayout(scale_layout)
    options_layout.addWidget(scale_group_box)

    # Time Options
    time_group_box = QGroupBox("Time Options")
    time_group_box.setToolTip("Select the maximum duration for the GIF. 'None' means the full video.")
    time_layout = QHBoxLayout()
    time_group = QButtonGroup(window)  # Ensure the parent is set correctly
    time_options = {None: "None", "10": "10 sec", "5": "5 sec"}
    for time, text in time_options.items():
        radio_btn = QRadioButton(text)
        time_layout.addWidget(radio_btn)
        time_group.addButton(radio_btn)
        radio_btn.toggled.connect(lambda checked, time=time: time_changed(time) if checked else None)
        if time == "None":  # Set default selection for time
            radio_btn.setChecked(True)

    time_group_box.setLayout(time_layout)
    options_layout.addWidget(time_group_box)

    # Override GIF Checkbox
    override_checkbox = QCheckBox("Override Existing GIF")
    override_checkbox.setToolTip("Uncheck if you want to be asked about overwriting existing GIFs.")
    override_checkbox.setChecked(True)  # Default checked
    override_checkbox.stateChanged.connect(override_changed)
    options_layout.addWidget(override_checkbox)

    main_layout.addLayout(options_layout)

    window.setLayout(main_layout)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
