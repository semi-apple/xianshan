import cv2 as cv
import pytesseract
# set tesseract path for detection based on the location of tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'.\Tesseract-OCR\tesseract.exe'
from client import Client
import pygetwindow as gw
import numpy as np
import sys

def is_image_opened(image_path):
    """
    Check if the image is currently opened in any window.
    
    :param image_path: Path to the image file.
    :return: True if the image is opened, False otherwise.
    """
    windows = gw.getWindowsWithTitle(image_path)
    return len(windows) > 0

class Extractor:
    def __init__(self, image_path):
        """
        Initialize the Extractor with the path to the image file.

        :param image_path: Path to the image file.
        """
        self.image_path = image_path
    
    def process(self):
        tables = []
        image = cv.imread(self.image_path)
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        _, binary = cv.threshold(gray, 150, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
        # Define coordinates for the left and right tables
        lx1, ly1, lx2, ly2 = 118, 45, 1115, 235
        rx1, ry1, rx2, ry2 = 1318, 45, 2315, 235
        # Extract left and right table regions
        left = binary[ly1:ly2, lx1:lx2]
        right = binary[ry1:ry2, rx1: rx2]
        tables.append(left)
        tables.append(right)
        
        return tables
    
    def extract(self):
        """
        Extract information from the processed tables and prepare the messages for sending.

        :return: List of messages extracted from the tables.
        """
        message = []
        tables = self.process()
        for i, binary in enumerate(tables):
            # Create a horizontal kernel for line detection
            kernel = cv.getStructuringElement(cv.MORPH_RECT, (10, 1))
            # horizontal = cv.morphologyEx(binary, cv.MORPH_OPEN, kernel)
            horizontal = cv.dilate(binary, kernel, iterations=2)
            # cv.imshow('Horizontal', horizontal)
            # cv.waitKey()
            # cv.destroyAllWindows()
            
            # Detect horizontal lines using Hough Line Transform
            lines = cv.HoughLinesP(horizontal, rho=1.0, theta=np.pi / 180, threshold=100, minLineLength=int(0.95 * binary.shape[1]), maxLineGap=70)
            lines_y = np.sort(lines[:,:,1], axis=None)
            list_y = list(lines_y)
            
            # Merge close y-coordinates to avoid redundant rows
            for i in range(len(list_y) - 1):
                if (list_y[i] - list_y[i + 1]) ** 2 <= (binary.shape[0] / 7) ** 2:
                    list_y[i + 1] = list_y[i]
                    
            # Remove duplicates and sort the list
            list_y = list(set(list_y))
            list_y.sort()
            # print(list_y)

            for i in range(len(list_y)):
                if i == len(list_y) - 1:
                    break
                # Extract each row based on y-coordinates
                temp = binary[list_y[i] + 2: list_y[i + 1] + 5,:]
                # Refine the extracted row using erosion and dilation
                kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 1))
                eroded = cv.erode(temp, kernel, iterations=1)
                dilated = cv.dilate(eroded, kernel, iterations=1)
                # cv.imshow('temp', dilated)
                # cv.waitKey()
                # cv.destroyAllWindows()
                
                # Perform OCR on the processed row
                custom_config = r'--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.'
                text = pytesseract.image_to_string(dilated, config=custom_config).strip()
                # print(text)
                
                # Define labels for the extracted data fields
                translate = ['dot', 'unit', 'current', 'scale'] 
                
                # Process the extracted text into fields
                text_list = text.split(' ')
                if len(text_list) == 3:
                    text_list.append('') # Add an empty scale field if missing
                    text_list[3] = text_list[2]
                    text_list[2] = text_list[1]
                    text_list[1] = ''
                    
                # Correct invalid numbers
                for i, word in enumerate(text_list):
                    if i > 1:
                        if word[0].isalpha() or (len(word) > 1 and word[1] == '.' and (word[0] == '6' or word[0] == '8')):
                            word = '0' + word[1:]
                    message.append(f'{translate[i]}: {word}')
                    # print(f'{translate[i]}: {word}', end='\t')
                # print()

            # return    
        return message

if __name__ == '__main__':
    image_path = 'test.png'
    
    if is_image_opened(image_path):
        print('Extracting...')
        extractor = Extractor(image_path)
        mess = extractor.extract()
        client = Client('127.0.0.1', 5000)
        client.send(mess)
        
    sys.exit(0)
    
        
        
    