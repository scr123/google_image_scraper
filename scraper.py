#!/usr/bin/env python3

"""
__author__ = "Sean Crutchlow"
__copyright__ = "Copyright (c) 2022 Sean Crutchlow"
__credits__ = ["Sean Crutchlow"]
__version__ = "1.0"
__maintainer__ = "Sean Crutchlow"
__email__ = "sean.GH1231@gmail.com"
"""

import argparse
import cv2
import os
import time
import urllib.request

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tqdm import tqdm

from webdriver_manager.chrome import ChromeDriverManager


def parse_args():
    """
    Parse program arguments
    """

    # Create parser object
    parser = argparse.ArgumentParser(
        description='Scrapes Google Images')

    # Populate parser arguments
    parser.add_argument("-q", "--query",
                        help='Image search query', required=True)

    parser.add_argument("-t", "--time_sleep",
                        help='Time to sleep in seconds between actions that require a wait',
                        type=float, required=True)

    parser.add_argument("-o", "--output_directory",
                        help='Output directory', required=True)

    parser.add_argument("-n", "--num_images",
                        help='Output directory',
                        type=int, required=True)

    parser.add_argument("-f", "--image_format",
                        help='Output image formats [jpg, jpeg, png, tiff]',
                        choices=['jpg', 'jpeg', 'png', 'tiff'],
                        required=False)

    parser.add_argument("-s", "--size_images",
                        help='Image sizes [large, medium, icon]',
                        choices=['large', 'medium', 'icon'],
                        required=False)

    parser.add_argument("-r", "--resize",
                        help='Resize scraped images',
                        nargs='+', type=int,
                        required=False)

    # Parse arguments
    args = parser.parse_args()

    # Assert argument constraints
    assert len(args.query) > 0, "Query expects a non-empty string"

    assert args.time_sleep > 0.0, "Time sleep expects a float greater than 0.0"

    assert os.path.isdir(
        args.output_directory) and os.path.exists(args.output_directory), \
        "Output directory expects a valid path to a directory"

    assert args.num_images > 0, "Number of images expects an integer greater than 0"

    if args.resize is not None:
        assert len(args.resize) == 2, "Resize expects a width & height"

    return args.query, args.time_sleep, args.output_directory, args.num_images, \
        args.image_format, args.size_images, args.resize


def generate_driver():
    """
    Generates webdriver object
    """

    # Construct options & add arguments that will be pass to webdriver
    options = Options()
    options.add_argument("incognito")
    options.add_argument("headless")
    options.add_argument("disable-gpu")

    # Construct webdriver object with options & install if not found
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    return driver


def submit_query(driver, query):
    """
    Submit query for images

    :param      driver:  The driver
    :type       driver:  WebDriver
    :param      query:   The query
    :type       query:   str
    """
    # Get webpage
    driver.get('https://images.google.com/')

    # Find search box
    box = driver.find_element(By.XPATH, '//*[@id="sbtc"]/div/div[2]/input')

    # Type query
    box.send_keys(query)

    # Enter query
    box.send_keys(Keys.ENTER)


def apply_size_filter(driver, size):
    """
    Apply size enumeration filter

    :param      driver:  The driver
    :type       driver:  WebDriver
    :param      size:    The size
    :type       size:    str
    """

    # Click on 'Tools'
    driver.find_element(
        By.XPATH, '//*[@id="yDmH0d"]/div[2]/c-wiz/div[1]/div/div[1]/div[2]/div[2]/div').click()

    # Click on 'Size'
    driver.find_element(
        By.XPATH, '//*[@id="yDmH0d"]/div[2]/c-wiz/div[2]/div[2]/c-wiz[1]/div/div/div[1]/div/div[1]/div/div[1]').click()

    # Click on one of the following filters ['large', 'medium', 'icon']
    if size == 'large':
        driver.find_element(
            By.XPATH, '//*[@id="yDmH0d"]/div[2]/c-wiz/div[2]/div[2]/c-wiz[1]/div/div/div[3]/div/a[2]/div/span').click()
    elif size == 'medium':
        driver.find_element(
            By.XPATH, '//*[@id="yDmH0d"]/div[2]/c-wiz/div[2]/div[2]/c-wiz[1]/div/div/div[3]/div/a[3]/div/span').click()
    else:
        driver.find_element(
            By.XPATH, '//*[@id="yDmH0d"]/div[2]/c-wiz/div[2]/div[2]/c-wiz[1]/div/div/div[3]/div/a[4]/div/span').click()


def scroll(driver, time_sleep, num_images):
    """
    Scroll

    :param      driver:      The driver
    :type       driver:      WebDriver
    :param      time_sleep:  The sleep duration
    :type       time_sleep:  float
    :param      num_images:  The number images
    :type       num_images:  int
    """

    # Store current scroll height
    curr_height = driver.execute_script('return document.body.scrollHeight')

    # Store current number of images
    curr_num_images = driver.execute_script('return document.images.length')

    # Scroll as long as current number
    while curr_num_images < num_images:
        driver.execute_script('\
        window.scrollTo(0,document.body.scrollHeight)')

        time.sleep(time_sleep * 4)

        height = driver.execute_script('\
        return document.body.scrollHeight')

        # Click 'Show more results' if button exists
        try:
            driver.find_element(
                By.XPATH, '//*[@id="islmp"]/div/div/div/div[1]/div[2]/div[2]/input').click()
            time.sleep(time_sleep)

        except:
            pass

        # Check if all images are viewed and scrolling cannot go further
        if height == curr_height:
            break

        # Update current height
        curr_height = height

        # Update current number of images after scrolling
        curr_num_images = driver.execute_script(
            'return document.images.length')

    return curr_num_images


def process_img(filepath, extension, size):
    """
    Processes image

    :param      filepath:   The filepath
    :type       filepath:   str
    :param      extension:  The image extension
    :type       extension:  str
    :param      size:       The size
    :type       size:       list(int)
    """

    # Resize image if applicable
    if size is not None:
        # Unpack size
        width, height = size

        # Read image
        img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)

        # Resize image
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

    # Write image, and change file extension if applicable
    if extension is not None:
        cv2.imwrite(filepath.split('.')[0] + '.' + extension, img)
        os.remove(filepath)
    else:
        cv2.imwrite(filepath, img)


def save_img(driver, query, time_sleep, output_dir, idx, input_formats, output_format, output_size):
    """
    Saves an image.

    :param      driver:         The driver
    :type       driver:         WebDriver
    :param      query:          The query
    :type       query:          str
    :param      time_sleep:     The sleep duration
    :type       time_sleep:     float
    :param      output_dir:     The output directory
    :type       output_dir:     str
    :param      idx:            The index
    :type       idx:            int
    :param      input_formats:  The input formats
    :type       input_formats:  list(str)
    :param      output_format:  The output format
    :type       output_format:  str
    :param      output_size:    The output size
    :type       output_size:    list(int)
    """
    try:
        # Click on the image corresponding to index 'idx'
        driver.find_element(By.XPATH,
                            '//*[@id="islrg"]/div[1]/div[' +
                            str(idx) + ']/a[1]/div[1]/img').click()

        # # Sleep after clicking image
        time.sleep(time_sleep)

        # Get URL for image
        src = driver.find_element(
            By.XPATH, '//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[3]/div/a/img').get_attribute('src')

        try:
            # If source URL exists for image
            if src != None:
                # Cast as string
                src = str(src)

                # Check that the source image uses an image format supported by cv2,
                # and trim the URL to the image only
                out = [(src.split(f)[0] + f, f)
                       for f in input_formats if f in src]

                # If no supported image format found, return (Note: expect only
                # 1)
                if len(out) != 1:
                    return

                # Unpack modified URL and file extension
                url, ext = out[0]

                # Remove whitespace in query
                query = query.replace(' ', '_')

                # Construct filepath for writing to disk
                filepath = os.path.join(os.path.abspath(
                    output_dir), query + '_' + str(idx) + ext)

                # Retrieve URL
                urllib.request.urlretrieve(src, filepath)

                # Process image if applicable
                process_img(filepath, output_format, output_size)
        except:
            pass
    except:
        pass


def main():
    """
    Main
    """

    # Parse arguments
    query, time_sleep, output_dir, num_images, output_format, size_enum, output_size = parse_args()

    # File formats for cv2.imread() -
    #    https://docs.opencv.org/4.5.5/d4/da8/group__imgcodecs.html#ga288b8b3da0892bd651fce07b3bbd3a56
    input_formats = ['.bmp', '.dib', '.jpeg', '.jpg', '.jp2', '.png', '.webp', '.pbm',
                     '.pgm', '.ppm', '.pxm', '.pnm', '.pfm', '.sr', '.ras', '.tiff',
                     '.exr', '.hdr', '.pic']

    # Generate browser
    driver = generate_driver()

    # Submit image query
    submit_query(driver, query)

    # Apply image size filter if specified
    if size_enum is not None:
        apply_size_filter(driver, size_enum)

    # Scrolls down until number of images for query is met, or max number of
    # images are discovered
    num_discovered_images = scroll(driver, time_sleep, num_images)

    # Iterate over image indices for query
    for i in tqdm(range(1, min(num_discovered_images, num_images) + 1)):
        save_img(driver, query, time_sleep, output_dir, i, input_formats,
                 output_format, output_size)

    # Close driver
    driver.close()


if __name__ == "__main__":
    main()
