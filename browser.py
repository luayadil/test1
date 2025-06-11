import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit,
                           QToolBar, QPushButton, QVBoxLayout, QWidget)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap
import os
from datetime import datetime

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Simple Web Browser')
        self.setGeometry(100, 100, 1024, 768)

        # Create the web view
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('http://www.google.com'))

        # Create navigation bar
        navtb = QToolBar()
        self.addToolBar(navtb)

        # Back Button
        back_btn = QPushButton('Back', self)
        back_btn.clicked.connect(self.browser.back)
        navtb.addWidget(back_btn)

        # Forward Button
        forward_btn = QPushButton('Forward', self)
        forward_btn.clicked.connect(self.browser.forward)
        navtb.addWidget(forward_btn)

        # Reload Button
        reload_btn = QPushButton('Reload', self)
        reload_btn.clicked.connect(self.browser.reload)
        navtb.addWidget(reload_btn)

        # Screenshot Button
        screenshot_btn = QPushButton('Screenshot', self)
        screenshot_btn.clicked.connect(self.take_screenshot)
        navtb.addWidget(screenshot_btn)

        # URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.url_bar)

        # Update URL bar when URL changes
        self.browser.urlChanged.connect(self.update_url)

        # Set browser as central widget
        self.setCentralWidget(self.browser)

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())

    def take_screenshot(self):
        # Create screenshots directory if it doesn't exist
        if not os.path.exists('screenshots'):
            os.makedirs('screenshots')
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screenshots/screenshot_{timestamp}.png'
        
        # Capture the webpage view
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(self.browser.winId())
        screenshot.save(filename)

def main():
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 