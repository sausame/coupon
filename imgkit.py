#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import pdfkit

from wand.image import Image
from wand.color import Color

class ImageKit:

    @staticmethod
    def init(configFile):
        pass

    @staticmethod
    def fromHtml(htmlFile, imgFile=None, start=(0,0), size=None, resolution=300):

        pos = htmlFile.rfind('.html')

        if pos is not 0:
            pdfFile = htmlFile[:pos]
        else:
            pdfFile = htmlFile

        if imgFile is None:
            imgFile = pdfFile + '.png'

        pdfFile += '.pdf'

        options = {'quiet': '' }
        pdfkit.from_file(htmlFile, pdfFile, options=options)

        with Image(filename=pdfFile, resolution=resolution) as img:
          with Image(width=img.width, height=img.height, background=Color('white')) as bg:
            bg.composite(img, start[0], start[1])
            if size is not None:
                bg.resize(size[0], size[1])
            bg.save(filename=imgFile)

        os.remove(pdfFile)

        return imgFile

