#TODO
#Ask Aydin to redo some letter pictures
#add in not a word label

import main
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QProgressBar
)

from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from FingerSpelling import Ui_MainWindow
import sys
import cv2
import mediapipe as mp
import enchant
import time
from smallWordList import word_list
import random
import os

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
MAX_HANDS = 1  # @param {type: "integer"}
min_detection_confidence = 0.6  # @param {type:"slider", min:0, max:1, step:0.01}
min_tracking_confidence = 0.5  # @param {type:"slider", min:0, max:1, step:0.01}

class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.winLabel.hide()
        self.loseLabel.hide()
        self.Play_btn.hide()
        self.winCond = False
        self.J_btn.hide()
        self.Z_btn.hide()
        self.Q_btn.hide()
        self.P_btn.hide()
        self.N_btn.hide()
        self.T_btn.hide()
        self.notWord.hide()
        self.notEnough.hide()
        self.Worker = Worker()
        self.Worker.start()
        self.Worker.imageUpdate.connect(self.ImageUpdateSlot)
        self.Worker.letter.connect(self.paintCanvas)
        self.Worker.progress.connect(self.updateProgressBar)
        self.cursorRow = 1
        self.cursorColumn = 1
        self.Enter.clicked.connect(self.enterPressed)
        self.Delete.clicked.connect(self.deletePressed)
        self.Play_btn.clicked.connect(self.newGame)
        #self.targetWord = str(random.choice(word_list)).upper()
        self.targetWord = "LABOR"
        self.create_alphabet_buttons()

    def newGame(self):
        #clear all the letters from the board
        self.winLabel.hide()
        self.loseLabel.hide()
        self.Play_btn.hide()
        self.winCond = False
        for i in range(1, 7):
            for j in range(1, 6):
                attribute_name = f"row{i}_{j}"
                # Check if the attribute exists
                if hasattr(self, attribute_name):
                    widget = getattr(self, attribute_name)
                    widget.setText("")
                    widget.setStyleSheet("background-color:rgb(0,0,0); color:rgb(255,255,255); border: 1px solid gray;")

        letters = [chr(65 + i) for i in range(26)]  # A-Z letters

        for i, letter in enumerate(letters):

            attribute_name = f"{letter}_btn"
            widget = getattr(self, attribute_name)
            widget.setStyleSheet("background-color:rgb(115, 115, 115); color:rgb(255, 255, 255)")

        #select new word
        self.targetWord = str(random.choice(word_list)).upper()
        self.cursorRow = 1
        self.cursorColumn = 1

    def create_alphabet_buttons(self):
        letters = [chr(65 + i) for i in range(26)]  # A-Z letters

        for i, letter in enumerate(letters):

            # Connect each button to the same slot, passing the letter as an argument
            # Using lambda with default argument to avoid late binding issues
            attribute_name = f"{letter}_btn"
            widget = getattr(self, attribute_name)
            widget.clicked.connect(lambda checked, l=letter: self.handle_button_click(l))

    def handle_button_click(self, letter):
        """Single slot that handles all button clicks"""
        #self.result_label.setText(f"You clicked: {letter}")
        #print(f"Button '{letter}' was clicked")
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to the image (assuming it's in the same directory)
        image_path = os.path.join(current_dir, r"Letters/" + str(letter).lower() + ".jpg")
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            print(f"Failed to load image: {image_path}")
        else:
            # Set the pixmap onto the label
            self.helpPic.setScaledContents(True)
            self.helpPic.setPixmap(pixmap)

    def ImageUpdateSlot(self, Image):
        self.webCam.setPixmap(QPixmap.fromImage(Image))

    def paintCanvas(self, prediction):
        if self.winCond:
            pass
        else:
            if self.cursorColumn < 6:
                attribute_name = f"row{self.cursorRow}_{self.cursorColumn}"
                # Check if the attribute exists
                if hasattr(self, attribute_name):
                    widget = getattr(self, attribute_name)
                    widget.setText(prediction)
                    widget.setStyleSheet("color:rgb(255,255,255); border: 1px solid gray;")
                    self.cursorColumn += 1

                else:
                    # Optional: Handle the case when the widget doesn't exist
                    print(f"Widget {attribute_name} not found")

    #TODO
    # def updatePrediction(self, prediction):
    #     self.signLetter("The Letter you are signing is: " + str(prediction))

    def enterPressed(self):
        print("Enter Clicked")
        guess = ""
        if self.cursorColumn == 6:
            for i in range(1,6):
                attribute_name = f"row{self.cursorRow}_" + str(i)
                widget = getattr(self, attribute_name)
                guess += widget.text()

            print(guess)
            if(self.isValidWord(guess)):
                #Evaluate Guess here
                print("Evaluating")
                results, self.winCond = self.check_word(guess)
                print(results)
                colorGuide = [0, 0, 0, 0, 0]
                for i in results["correct_positions"]:
                    colorGuide[i[1]] = 2

                for j in results["present_letters"]:
                    colorGuide[j[1]] = 1

                for k in range(1, 6):
                    attribute_name = f"row{self.cursorRow}_" + str(k)
                    widget = getattr(self, attribute_name)

                    print(widget.text())
                    attribute_name = f"{widget.text()}_btn"
                    letterBtn = getattr(self, attribute_name)

                    if colorGuide[k-1] == 2:
                        widget.setStyleSheet("background-color:rgb(108, 169, 101); border: 0px; color:rgb(255,255,255)")
                        letterBtn.setStyleSheet("background-color:rgb(108, 169, 101); color:rgb(255,255,255)")

                    elif colorGuide[k-1] == 1:
                        widget.setStyleSheet("background-color:rgb(200, 182, 83); border: 0px; color:rgb(255,255,255)")
                        letterBtn.setStyleSheet("background-color:rgb(200, 182, 83); color:rgb(255,255,255)")

                    else:
                        widget.setStyleSheet("background-color:rgb(120, 124, 127); border: 0px; color:rgb(255,255,255)")
                        letterBtn.setStyleSheet("background-color:rgb(51, 51, 51); color:rgb(255,255,255)")

                    widget.repaint()
                    letterBtn.repaint()
                    time.sleep(1)

                if self.winCond:
                    print("YOU WIN!")
                    self.Play_btn.show()
                    self.winLabel.show()

                elif self.cursorColumn == 6 and self.cursorRow == 6:
                    print("YOU LOSE!")
                    self.Play_btn.show()
                    self.loseLabel.show()

                self.cursorRow += 1
                self.cursorColumn = 1
            else:
                print("Not a Valid Word")
                self.notWord.show()
                self.notWord.repaint()
                #TODO
                # Add in Qtimer call to notWord label for a determined amount of time
                # Qtimer.singleShot(duration_ms, function call to hide_label)


        else:
            print("Not Enough Letters")
            #TODO
            # Add in Qtimer call to  notEnough label for a determined amount of time


    def deletePressed(self):
        self.notWord.hide()
        column = self.cursorColumn - 1
        if column > 0:
            self.cursorColumn -= 1
            attribute_name = f"row{self.cursorRow}_" + str(column)
            widget = getattr(self, attribute_name)
            widget.setText("")
        else:
            self.cursorColumn = 1

    def isValidWord(self, guess):
        dict = enchant.Dict("en_US")
        return(dict.check(guess))

    def updateProgressBar(self, percent):
        self.submitBar.setValue(percent)

    # def check_word(self, guess):
    #     winCond = False
    #
    #     if len(guess) != 5 or len(self.targetWord) != 5:
    #         return "Both words must be 5 letters long"
    #
    #     if guess == self.targetWord:
    #         winCond = True
    #
    #     result = {
    #         "correct_positions": [],  # Letters in the correct position
    #         "present_letters": []  # Letters present but in wrong position
    #     }
    #
    #     # Check for correct positions
    #     for i in range(5):
    #         if guess[i] == self.targetWord[i]:
    #             result["correct_positions"].append((guess[i], i))
    #
    #     # Check for letters present but in wrong position
    #     remaining_target = list(self.targetWord)
    #     for i, letter in enumerate(guess):
    #         # Skip letters already found in correct position
    #         if (letter, i) in result["correct_positions"]:
    #             if letter in remaining_target:
    #                 remaining_target.remove(letter)
    #             continue
    #
    #         if letter in remaining_target:
    #             result["present_letters"].append((letter, i))
    #             remaining_target.remove(letter)
    #
    #     return result, winCond
    def check_word(self, guess):
        winCond = False

        if len(guess) != 5 or len(self.targetWord) != 5:
            return "Both words must be 5 letters long"

        if guess == self.targetWord:
            winCond = True

        result = {
            "correct_positions": [],  # Letters in the correct position
            "present_letters": []  # Letters present but in wrong position
        }

        # First pass: mark correct positions
        remaining_target = list(self.targetWord)
        for i in range(5):
            if guess[i] == self.targetWord[i]:
                result["correct_positions"].append((guess[i], i))
                # Mark this letter as used in the target word
                remaining_target.remove(guess[i])

        # Second pass: check for letters in wrong positions
        for i in range(5):
            letter = guess[i]
            # Skip letters already found in correct position
            if any(pos == i for _, pos in result["correct_positions"]):
                continue

            # If the letter exists in remaining_target, it's in the wrong position
            if letter in remaining_target:
                result["present_letters"].append((letter, i))
                remaining_target.remove(letter)

        return result, winCond

class Worker(QThread):
    imageUpdate = pyqtSignal(QImage)
    letter = pyqtSignal(str)
    progress = pyqtSignal(int)

    def run(self):
        self.ThreadActive = True
        testflag = 0
        predictionList = []
        notLetterCount = 0

        Capture = cv2.VideoCapture(0)

        with mp_hands.Hands(
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=min_tracking_confidence,
                max_num_hands=MAX_HANDS
        ) as hands:
            while self.ThreadActive:
                ret, frame = Capture.read()
                if ret:
                    Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    FlippedImage = cv2.flip(Image, 1)


                    FlippedImage.flags.writeable = False
                    results = hands.process(FlippedImage)

                    # Draw the hand annotations on the image
                    FlippedImage.flags.writeable = True
                    FlippedImage = cv2.cvtColor(FlippedImage, cv2.COLOR_RGB2BGR)

                    try:
                        FlippedImage, prediction = main.recognize_gesture(FlippedImage, results)
                    except Exception as error:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        print(f"{error}, line {exc_tb.tb_lineno}")

                    #Test Code for painting the canvas
                    # if testflag == 0 and prediction.isalpha():
                    #     print(prediction)
                    #     self.letter.emit(prediction)

                    predictionsLength = len(predictionList)
                    if prediction.isalpha():
                        predictionList.append(prediction)

                    else:
                        notLetterCount += 1
                        if notLetterCount > 50:
                            notLetterCount = 0
                            predictionList.clear()

                    if predictionsLength > 100:
                        predictionList = predictionList[50:]
                        uniquePredictions = set(predictionList)
                        letterPrediction = prediction
                        count = 0
                        for letter in uniquePredictions:
                            if predictionList.count(letter) > 30 and predictionList.count(letter) > count:
                                count = predictionList.count(letter)
                                letterPrediction = letter
                        print(letterPrediction)
                        self.letter.emit(letterPrediction)
                        predictionList.clear()

                    ConvertToQtFormat = QImage(FlippedImage.data, FlippedImage.shape[1], FlippedImage.shape[0], QImage.Format_RGB888)
                    Pic = ConvertToQtFormat.scaled(300,300, Qt.KeepAspectRatio)

                    self.progress.emit(predictionsLength)
                    self.imageUpdate.emit(Pic)

                    # testflag += 1
                    # if testflag == 100:
                    #     testflag = 0

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
