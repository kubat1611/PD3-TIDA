import sys
import os
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QSlider,QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from mutagen.mp3 import MP3


class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Player")
        self.setFixedSize(500, 200)

        self.player = QMediaPlayer()
        self.songs = [f for f in os.listdir() if f.endswith(".mp3")]
        self.current_index = 0
        self.shuffle = False
        self.loop = False
        self.paused = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)

        self.player.mediaStatusChanged.connect(self.handle_media_status)

        self.init_ui()
        self.load_song()

    def init_ui(self):
        self.setStyleSheet("""
            #time {
            font-size: 32px;
            }
            #top_container, #bottom_container {
            background-color: #272727;
            }
            QLabel {
            color: #00ff00;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        top_container = QWidget()
        top_container.setObjectName("top_container")
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        left_box = QWidget()
        left_box.setObjectName("top_left")
        left_layout = QVBoxLayout()
        self.time_label = QLabel("00:00")
        self.time_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.time_label.setObjectName("time")
        left_layout.addWidget(self.time_label)
        left_box.setLayout(left_layout)
        top_layout.addWidget(left_box, 1)

        right_box = QWidget()
        right_layout = QVBoxLayout()

        self.song_label = QLabel("Song: ---")

        rate_box = QWidget()
        rate_layout = QHBoxLayout()
        self.bitrate_label = QLabel("BITRATE: --- kbps")
        self.mixrate_label = QLabel("MIXRATE: --- kHz")
        rate_layout.addWidget(self.bitrate_label)
        rate_layout.addWidget(self.mixrate_label)
        rate_box.setLayout(rate_layout)

        sound_box = QWidget()
        sound_layout = QHBoxLayout()
        volume_label = QLabel("VOLUME:")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        sound_layout.addWidget(volume_label)
        sound_layout.addWidget(self.volume_slider)
        sound_box.setLayout(sound_layout)

        right_layout.addWidget(self.song_label)
        right_layout.addWidget(rate_box)
        right_layout.addWidget(sound_box)

        right_box.setLayout(right_layout)
        top_layout.addWidget(right_box, 2)

        top_container.setLayout(top_layout)

        bottom_container = QWidget()
        bottom_container.setObjectName("bottom_container")
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)

        bottom_left = QWidget()
        left_layout = QHBoxLayout()
        left_layout.setAlignment(Qt.AlignCenter)
        self.prev_btn = QPushButton("⏮")
        self.play_btn = QPushButton("▶")
        self.pause_btn = QPushButton("⏸")
        self.restart_btn = QPushButton("⟲")
        self.next_btn = QPushButton("⏭")

        for btn in [self.prev_btn, self.play_btn, self.pause_btn, self.restart_btn, self.next_btn]:
            btn.setFixedSize(32, 32)
            left_layout.addWidget(btn)

        self.prev_btn.clicked.connect(self.prev_song)
        self.play_btn.clicked.connect(self.play_song)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.restart_btn.clicked.connect(self.restart_song)
        self.next_btn.clicked.connect(self.next_song)

        bottom_left.setLayout(left_layout)

        bottom_right = QWidget()
        right_layout = QHBoxLayout()
        right_layout.setAlignment(Qt.AlignLeft)
        self.shuffle_btn = QPushButton("SHUFFLE")
        self.loop_btn = QPushButton("🔁")
        self.shuffle_btn.clicked.connect(self.toggle_shuffle)
        self.loop_btn.clicked.connect(self.toggle_loop)
        right_layout.addWidget(self.shuffle_btn)
        right_layout.addWidget(self.loop_btn)
        bottom_right.setLayout(right_layout)

        bottom_layout.addWidget(bottom_left, 1)
        bottom_layout.addWidget(bottom_right, 1)
        bottom_container.setLayout(bottom_layout)

        main_layout.addWidget(top_container, 4)
        main_layout.addWidget(bottom_container, 1)

        self.setLayout(main_layout)

    def load_song(self):
        if not self.songs:
            self.song_label.setText("No MP3s Found")
            return
        song = self.songs[self.current_index]
        display_name = song
        if len(display_name) > 43:
            display_name = display_name[:40] + "..."
        self.song_label.setText(f"Song: {display_name}")
        audio = MP3(song)
        self.bitrate_label.setText(f"BITRATE: {audio.info.bitrate // 1000} kbps")
        self.mixrate_label.setText(f"MIXRATE: {int(audio.info.sample_rate / 1000)} kHz")
        url = QUrl.fromLocalFile(os.path.abspath(song))
        content = QMediaContent(url)
        self.player.setMedia(content)

    def play_song(self):
        if self.paused:
            self.player.play()
            self.timer.start(1000)
            self.paused = False
        elif self.player.state() == QMediaPlayer.PlayingState:
            return
        else:
            self.restart_song()

    def toggle_pause(self):
        if not self.paused:
            self.player.pause()
            self.timer.stop()
            self.paused = True
        else:
            self.player.play()
            self.timer.start(1000)
            self.paused = False

    def restart_song(self):
        self.load_song()
        self.player.setPosition(0)
        self.player.play()
        self.timer.start(1000)

    def next_song(self):
        if not self.loop:
            self.current_index = (
                random.randint(0, len(self.songs) - 1) if self.shuffle
                else (self.current_index + 1) % len(self.songs)
            )
        self.restart_song()

    def prev_song(self):
        if not self.loop:
            self.current_index = (self.current_index - 1) % len(self.songs)
        self.restart_song()

    def toggle_shuffle(self):
        if not self.shuffle:
            self.shuffle = True
            self.loop = False  # Disable loop if shuffle is enabled
            self.shuffle_btn.setStyleSheet("background-color: lightgreen;")
            self.loop_btn.setStyleSheet("")
        else:
            self.shuffle = False
            self.shuffle_btn.setStyleSheet("")
    
    def toggle_loop(self):
        if not self.loop:
            self.loop = True
            self.shuffle = False  # Disable shuffle if loop is enabled
            self.loop_btn.setStyleSheet("background-color: lightgreen;")
            self.shuffle_btn.setStyleSheet("")
        else:
            self.loop = False
            self.loop_btn.setStyleSheet("")

    def update_time(self):
        pos = self.player.position() // 1000
        minutes = pos // 60
        seconds = pos % 60
        self.time_label.setText(f"{minutes:02}:{seconds:02}")

    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            if self.loop:
                self.restart_song()
            else:
                self.next_song()

    def set_volume(self, val):
        self.player.setVolume(val)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MusicPlayer()
    window.show()
    sys.exit(app.exec_())
