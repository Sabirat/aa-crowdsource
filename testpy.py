from app import app
from flask import render_template
from flask import Flask, request
from random import randint
from flaskext.mysql import MySQL

from selenium import webdriver

from PIL import Image
from pytesseract import image_to_string
from PIL import ImageFilter
#from selenium.webdriver.common.keys import Keys
#from selenium.webdriver.support.wait import WebDriverWait
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support import expected_conditions as EC

imgCropped = Image.open("app/static/images/img2.jpg")
#imgCropped.filter(ImageFilter.SHARPEN)

#gray = im.convert('L')
#bw = gray.point(lambda x: 0 if x<150 else 250, '1')
#cleaned_image_name ='_cleaned.jpg'
#bw.save(cleaned_image_name)

print(imgCropped)

print(image_to_string(imgCropped))










