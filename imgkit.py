#!/usr/bin/env python
# -*- coding:utf-8 -*-

# TODO: will use bokeh instead in future

import os
import pdfkit
import shutil

from wand.image import Image
from wand.color import Color
from utils import runCommand

class ImageKit:

    @staticmethod
    def init(configFile):
        pass

    @staticmethod
    def fromHtml(htmlFile, imgFile=None, start=(0,0), size=None, resize=None, resolution=300):

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

        options = {'quiet': '' }
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

