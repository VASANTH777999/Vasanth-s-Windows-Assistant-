# corrected_chat_ui_fixed.py
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit,
    QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
)
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer, QRect
import os
import logging
import config

# Setup logger
logger = logging.getLogger("Solix.GUI")

# ============================================
# Environment & Paths
# ============================================
Assistantname = config.ASSISTANTNAME
TempDirPath = config.TEMP_DIR
GraphicsDirPath = config.GRAPHICS_DIR

# Ensure directories exist (avoid crashes)
TempDirPath.mkdir(parents=True, exist_ok=True)
GraphicsDirPath.mkdir(parents=True, exist_ok=True)


# --- Utility functions ---
def AnswerModifier(Answer: str) -> str:
    """Remove empty lines from an answer text."""
    lines = Answer.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)


def QueryModifier(Query: str) -> str:
    """Normalize query: trim, lower, add punctuation appropriately and capitalize."""
    if not Query:
        return ""
    new_query = Query.lower().strip()
    question_words = [
        "how", "what", "who", "where", "when", "why", "which", "whose", "whom",
        "can you", "what's", "where's", "how's"
    ]
    last_char = new_query[-1] if new_query else ""
    is_question = any(new_query.startswith(q + " ") or q in new_query for q in question_words)
    punct = "?" if is_question else "."
    if last_char in ['.', '?', '!']:
        new_query = new_query[:-1] + punct
    else:
        new_query = new_query + punct
    return new_query.capitalize()


def safe_write(path: Path, text: str):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except Exception:
        # Warning: In production, log exceptions, here silently ignore
        pass


def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def SetMicrophoneStatus(Command: str):
    safe_write(TempDirPath / "Mic.data", Command)


def GetMicrophoneStatus() -> str:
    return safe_read(TempDirPath / "Mic.data")


def SetAssistantStatus(Status: str):
    safe_write(TempDirPath / "Status.data", Status)


def GetAssistantStatus() -> str:
    return safe_read(TempDirPath / "Status.data")


def MicButtonInitialized():
    SetMicrophoneStatus("False")


def MicButtonClosed():
    SetMicrophoneStatus("True")


def GraphicsDirectoryPath(filename: str) -> str:
    return str(GraphicsDirPath / filename)


def TempDirectoryPath(filename: str) -> str:
    return str(TempDirPath / filename)


def ShowTextToScreen(Text: str):
    safe_write(TempDirPath / "Responses.data", Text)


# --- ChatSection widget ---
class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 40, 40, 100)
        layout.setSpacing(5)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color: black;")
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        # default text color
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(QColor(Qt.blue))
        self.chat_text_edit.setCurrentCharFormat(text_color_text)

        # Animated GIF label
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        gif_path = GraphicsDirectoryPath("Jarvis.gif")
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(480, 270))
            self.gif_label.setMovie(movie)
            movie.start()
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        layout.addWidget(self.gif_label)

        # status label shown near gif
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        # Timer to poll Responses.data and Status.data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer)
        self.timer.start(200)  # 200 ms timer

        # scrollbar style for chat section
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: black;
                height: 10px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        self._old_chat_message = ""

    def _on_timer(self):
        self.loadMessages()
        self.SpeechRecogText()

    def loadMessages(self):
        messages = safe_read(TempDirPath / "Responses.data")
        if not messages or len(messages) <= 1:
            return
        if str(self._old_chat_message) == str(messages):
            return
        self.addMessage(message=messages, color='white')
        self._old_chat_message = messages

    def SpeechRecogText(self):
        messages = GetAssistantStatus()
        self.label.setText(messages)

    def addMessage(self, message: str, color: str = "white"):
        cursor = self.chat_text_edit.textCursor()
        fmt = QTextCharFormat()
        block_fmt = QTextBlockFormat()
        block_fmt.setTopMargin(10)
        block_fmt.setLeftMargin(10)
        fmt.setForeground(QColor(color))
        cursor.setBlockFormat(block_fmt)
        cursor.setCharFormat(fmt)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)
        # autoscroll to bottom
        self.chat_text_edit.verticalScrollBar().setValue(self.chat_text_edit.verticalScrollBar().maximum())


# --- Initial Screen ---
class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        gif_label = QLabel()
        gif_path = GraphicsDirectoryPath("Jarvis.gif")
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            max_gif_size_H = int(screen_width / 16 * 9)
            movie.setScaledSize(QSize(screen_width, max_gif_size_H))
            gif_label.setMovie(movie)
            movie.start()
        gif_label.setAlignment(Qt.AlignCenter)
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # microphone icon label
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True

        # set initial icon if present
        mic_on_path = GraphicsDirectoryPath("Mic_on.png")
        if os.path.exists(mic_on_path):
            pixmap = QPixmap(mic_on_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)

        # mouse click toggles mic
        self.icon_label.mousePressEvent = self.toggle_icon

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")

        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        self.setLayout(content_layout)

        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(500)

    def SpeechRecogText(self):
        messages = GetAssistantStatus()
        self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
        if os.path.exists(path):
            pixmap = QPixmap(path).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath("Mic_on.png"), 60, 60)
            MicButtonInitialized()
        else:
            self.load_icon(GraphicsDirectoryPath("Mic_off.png"), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled


# --- Message Screen (contains ChatSection) ---
class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        chat_section = ChatSection()
        layout.addWidget(chat_section)

        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


# --- Top bar (toolbar) ---
class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget: QStackedWidget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()
        self.draggable = True
        self.offset = None

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)
        layout.setContentsMargins(8, 6, 8, 6)

        # Title
        title_label = QLabel(f"{str(Assistantname).capitalize()} AI")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color: white; padding: 4px;")
        layout.addWidget(title_label)
        layout.addStretch(1)

        # Home button
        home_button = QPushButton("  Home")
        home_button.setStyleSheet("height:40px; background-color:white ; color: black")
        home_icon = QIcon(GraphicsDirectoryPath("Home.png")) if os.path.exists(GraphicsDirectoryPath("Home.png")) else QIcon()
        home_button.setIcon(home_icon)
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(home_button)

        # Chat button
        message_button = QPushButton("  Chat")
        message_icon = QIcon(GraphicsDirectoryPath("Chats.png")) if os.path.exists(GraphicsDirectoryPath("Chats.png")) else QIcon()
        message_button.setIcon(message_icon)
        message_button.setStyleSheet("height:40px; background-color:white ; color: black")
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(message_button)

        layout.addStretch(1)

        # Minimize, Maximize, Close buttons
        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirectoryPath('Minimize2.png')) if os.path.exists(GraphicsDirectoryPath('Minimize2.png')) else QIcon()
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet('background-color:white')
        minimize_button.clicked.connect(self.minimizeWindow)
        layout.addWidget(minimize_button)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png')) if os.path.exists(GraphicsDirectoryPath('Maximize.png')) else QIcon()
        self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.png')) if os.path.exists(GraphicsDirectoryPath('Minimize.png')) else QIcon()
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet('background-color:white')
        self.maximize_button.clicked.connect(self.maximizeWindow)
        layout.addWidget(self.maximize_button)

        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirectoryPath('Close.png')) if os.path.exists(GraphicsDirectoryPath('Close.png')) else QIcon()
        close_button.setIcon(close_icon)
        close_button.setStyleSheet('background-color:white')
        close_button.clicked.connect(self.closeWindow)
        layout.addWidget(close_button)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable and event.button() == Qt.LeftButton:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)


# --- Main window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        stacked_widget = QStackedWidget(self)

        initial_screen = InitialScreen()
        message_screen = MessageScreen()

        stacked_widget.addWidget(initial_screen)   # index 0
        stacked_widget.addWidget(message_screen)   # index 1

        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")

        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)


# --- Entry point ---
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()
