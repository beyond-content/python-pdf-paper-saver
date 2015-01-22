from random import randint
from unittest import TestCase
from cStringIO import StringIO

from hamcrest import *
from reportlab.lib.colors import black, getAllNamedColors
from reportlab.lib.units import mm

from reportlab.pdfgen.canvas import Canvas
from PyPDF2 import PdfFileWriter, PdfFileReader
from rect.packer import pack


class ColoredPDFPage(object):
    def __init__(self, width, height, background_color=None, text=None, size_unit=mm):
        super(ColoredPDFPage, self).__init__()
        self.width = width * size_unit
        self.height = height * size_unit
        self.background_color = background_color
        self.text = "%s x %s" % (width, height) if text is None else text

    @property
    def pagesize(self):
        return self.width, self.height

    @classmethod
    def create_randomly_sized_and_colored_page(cls, min_width, max_width, min_height, max_height, extra_text):
        colors_and_names = getAllNamedColors().items()
        width = randint(min_width, max_width)
        height = randint(min_height, max_height)
        color_name, color = colors_and_names[randint(0, len(colors_and_names) - 1)]
        text = "%s [Size: %d x %d][Color: %s] " % (extra_text, width, height, color_name)
        return cls(width, height, background_color=color, text=text).to_page()

    def to_page(self):
        stream = StringIO()
        c = Canvas(stream, pagesize=self.pagesize)
        if self.background_color:
            c.setFillColor(self.background_color)
            c.rect(0, 0, self.width, self.height, stroke=0, fill=1)
        if self.text:
            c.setFillColor(black)
            c.drawString(10, 10, self.text)
        c.save()
        stream.seek(0)
        return PdfFileReader(stream).pages[0]


class BaseTestCase(TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.source_pdf = StringIO()
        self.create_randomly_sized_pdf_pages()

    def create_randomly_sized_pdf_pages(self):
        writer = PdfFileWriter()
        for id in range(0, 100):
            page = ColoredPDFPage.create_randomly_sized_and_colored_page(40, 210, 40, 297, extra_text="#%d" % id)
            writer.addPage(page)
        writer.write(self.source_pdf)

    def test_expected_page_count(self):
        reader = PdfFileReader(self.source_pdf)
        assert_that(reader.numPages, equal_to(100), "Expected page count")

    def test_pack_pages(self):
        canvas = (306, 303)
        rects = [(100, 200), (200, 300)]
        pack(canvas, rects, 3)


