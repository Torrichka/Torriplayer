import sys

from PySide6.QtCore import QStandardPaths, Qt, Slot
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import (QApplication, QDialog, QFileDialog,
    QMainWindow, QSlider, QStyle, QToolBar)
from PySide6.QtMultimedia import (QAudioOutput, QMediaFormat,
                                  QMediaPlayer)
from PySide6.QtMultimediaWidgets import QVideoWidget


def get_supported_mime_types():
    return list(map(
        lambda f: QMediaFormat(f).mimeType().name(),
        QMediaFormat().supportedFileFormats(QMediaFormat.ConversionMode.Decode)
    ))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Torriplayer')

        self.mime_types = []

        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)

        self.media_player.errorOccurred.connect(self._player_error)

        ## toolbar
        tool_bar = QToolBar()
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, tool_bar)

        # file
        file_menu = self.menuBar().addMenu("&File")
        icon = QIcon.fromTheme("document-open")
        open_action = QAction(
            icon, "&Open...", self,
            shortcut=QKeySequence.Open,
            triggered=self.open
        )
        icon = QIcon.fromTheme("application-exit")
        exit_action = QAction(
            icon, "&Exit", self,
            shortcut="Ctrl+Q",
            triggered=self.close
        )
        file_menu.addAction(open_action)
        file_menu.addAction(exit_action)
        tool_bar.addAction(open_action)

        style = self.style()

        # play
        play_menu = self.menuBar().addMenu("&Play")
        icon = QIcon.fromTheme("media-playback-start.png",
                               style.standardIcon(QStyle.SP_MediaPlay))
        play_action = QAction(
            icon, "Play", tool_bar,
            triggered=self.media_player.play
        )

        icon = QIcon.fromTheme("media-skip-backward-symbolic.svg",
                               style.standardIcon(QStyle.SP_MediaSkipBackward))
        self.previous_action = QAction(
            icon, "Previous", tool_bar,
            triggered=self.previous_clicked
        )

        icon = QIcon.fromTheme("media-playback-pause.png",
                               style.standardIcon(QStyle.SP_MediaPause))
        self.pause_action = QAction(
            icon, "Pause", tool_bar,
            triggered=self.media_player.pause
        )

        icon = QIcon.fromTheme("media-skip-forward-symbolic.svg",
                               style.standardIcon(QStyle.SP_MediaSkipForward))
        next_action = QAction(
            icon, "Next", tool_bar,
            triggered=self.next_clicked
        )

        icon = QIcon.fromTheme("media-playback-stop.png",
                               style.standardIcon(QStyle.SP_MediaStop))
        self.stop_action = QAction(
            icon, "Stop", tool_bar,
            triggered=self.stop_clicked
        )

        play_menu.addAction(play_action)
        play_menu.addAction(self.previous_action)
        play_menu.addAction(self.pause_action)
        play_menu.addAction(next_action)
        play_menu.addAction(self.stop_action)
        tool_bar.addAction(play_action)
        tool_bar.addAction(self.previous_action)
        tool_bar.addAction(self.pause_action)
        tool_bar.addAction(next_action)
        tool_bar.addAction(self.stop_action)

        volume_slider = QSlider()
        volume_slider.setOrientation(Qt.Horizontal)
        volume_slider.setMinimum(0)
        volume_slider.setMaximum(100)

        available_width = self.screen().availableGeometry().width()
        volume_slider.setFixedWidth(available_width / 10)
        volume_slider.setValue(self.audio_output.volume())
        volume_slider.setTickInterval(10)
        volume_slider.setTickPosition(QSlider.TicksBelow)
        volume_slider.setToolTip("Volume")
        volume_slider.valueChanged.connect(self.audio_output.setVolume)
        tool_bar.addWidget(volume_slider)

        video_widget = QVideoWidget()
        self.setCentralWidget(video_widget)
        self.media_player.playbackStateChanged.connect(self.update_buttons)
        self.media_player.setVideoOutput(video_widget)

        self.update_buttons(self.media_player.playbackState())

    def closeEvent(self, event):
        self.ensure_stopped()
        event.accept()

    @Slot()
    def open(self):
        self.ensure_stopped()
        file_dialog = QFileDialog(self)

        if not self.mime_types:
            self.mime_types = get_supported_mime_types()

        file_dialog.setMimeTypeFilters(self.mime_types)

        desktop_location = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        file_dialog.setDirectory(desktop_location)
        if file_dialog.exec() == QDialog.Accepted:
            url = file_dialog.selectedUrls()[0]
            self.media_player.setSource(url)
            self.media_player.play()

    @Slot()
    def stop_clicked(self):
        self.ensure_stopped()
    
    @Slot()
    def ensure_stopped(self):
        if self.media_player.playbackState() != QMediaPlayer.StoppedState:
            self.media_player.stop()

    @Slot()
    def previous_clicked(self):
        pass

    @Slot()
    def next_clicked(self):
        pass

    @Slot("QMediaPlayer::PlaybackState")
    def update_buttons(self, state):
        self.pause_action.setEnabled(state == QMediaPlayer.PlayingState)
        self.stop_action.setEnabled(state != QMediaPlayer.StoppedState)
        self.previous_action.setEnabled(self.media_player.position() > 0)

    @Slot("QMediaPlayer::Error", str)
    def _player_error(self, error, error_string):
        print(error_string, file=sys.stderr)
        self.statusBar().showMessage(error_string, 5000)


if __name__ == '__main__':
    app = QApplication()
    window = MainWindow()
    available_geometry = window.screen().availableGeometry()
    window.resize(available_geometry.width() / 2,
                    available_geometry.height() / 2)
    window.show()
    sys.exit(app.exec())