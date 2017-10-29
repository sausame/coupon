#!/usr/bin/env python
# -*- coding:utf-8 -*-

# TODO: will use bokeh instead in future

import os
import pdfkit
import pytesseract
import shutil

from wand.image import Image
from wand.color import Color
from utils import runCommand

try:
    import Image
except ImportError:
    from PIL import Image

class ImageKit:

    @staticmethod
    def init(configFile):
        pass

    @staticmethod
    def fromHtml(htmlFile, imgFile=None, start=(0,0), size=None, resize=None, resolution=300, pageSize=None):

        htmlFile = os.path.realpath(htmlFile)

        pos = htmlFile.rfind('.html')

        if pos is not 0:
            prefix = htmlFile[:pos]
        else:
            prefix = htmlFile

        if imgFile is None:
            imgFile = prefix + '.png'

        pdfFolder = prefix + '-pdfs'

        if not os.path.exists(pdfFolder):
            os.mkdir(pdfFolder, 0755)

        pdfFile = os.path.join(pdfFolder, 'temp.pdf')

        options = {'quiet': '',    
                'margin-top': '0.0in',
                'margin-right': '0.0in',
                'margin-bottom': '0.0in',
                'margin-left': '0.0in'}

        if pageSize is not None:

            options['page-width'] = pageSize[0]
            options['page-height'] = pageSize[1]

        pdfkit.from_file(htmlFile, pdfFile, options=options)

        outFile = os.path.join(pdfFolder, 'output.pdf')

        try:
            # Only parse first page
            ret = runCommand('/usr/bin/pdftk {} cat 1 output {}'.format(pdfFile, outFile))

            with Image(filename=outFile, resolution=resolution) as img:

                if size is None:
                    size = (img.width - start[0], img.height - start[1])

                with Image(width=size[0], height=size[1], background=Color('white')) as bg:

                    bg.composite(img, start[0], start[1])
                    if resize is not None:
                        bg.resize(resize[0], resize[1])

                    bg.save(filename=imgFile)
        except Exception as e:
            print e
            return None

        finally:
            shutil.rmtree(pdfFolder)

        return imgFile

    @staticmethod
    def getText(path, lang='eng', config='-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz -psm 6'):

        image = Image.open(path)
        text = pytesseract.image_to_string(image, lang=lang, config=config)
        return text

    @staticmethod
    def saveCapture(driver, element, path):

        # now that we have the preliminary stuff out of the way time to get that image :D
        location = element.location
        size = element.size

        # saves screenshot of entire page
        driver.save_screenshot(path)

        # uses PIL library to open image in memory
        image = Image.open(path)

        left = int(location['x'])
        top = int(location['y'])
        right = int(location['x'] + size['width'])
        bottom = int(location['y'] + size['height'])

        image = image.crop((left, top, right, bottom))  # defines crop points
        image.save(path, 'png')  # saves new cropped image

