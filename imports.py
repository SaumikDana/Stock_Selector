import os
import sys
import yfinance as yf  
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as si
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from scipy.interpolate import griddata
import matplotlib.ticker as mticker
import requests
from bs4 import BeautifulSoup
import math
from IPython.display import display
from selenium import webdriver
import time
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run in headless mode
driver = webdriver.Chrome(options=options)
import ta
import re
