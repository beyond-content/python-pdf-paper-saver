from itertools import chain
from random import randint
from unittest import TestCase
from cStringIO import StringIO

from hamcrest import *
from rect import Rect
from reportlab.lib import pagesizes

from reportlab.lib.colors import black, getAllNamedColors
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from PyPDF2 import PdfFileWriter, PdfFileReader
from rect.packer import pack

from pdfpapersaver import PDFPagePacker


class ColoredPDFPage(object):
    def __init__(self, width, height, background_color=None, text=None, size_unit=mm):
        super(ColoredPDFPage, self).__init__()
        self.size_unit = size_unit
        self.width = width * self.size_unit
        self.height = height * self.size_unit
        self.background_color = background_color
        self.text = "%s x %s" % (width, height) if text is None else text
        self._page = None

    @property
    def pagesize(self):
        return self.width, self.height

    @property
    def page(self):
        self._page = self._page or self.to_page()
        return self._page

    @property
    def pdf_page_width(self):
        return self.page.mediaBox.getWidth()

    @property
    def pdf_page_height(self):
        return self.page.mediaBox.getHeight()

    @classmethod
    def create_randomly_sized_and_colored_page(cls, min_width, max_width, min_height, max_height, extra_text):
        colors_and_names = getAllNamedColors().items()
        width = randint(min_width, max_width)
        height = randint(min_height, max_height)
        color_name, color = colors_and_names[randint(0, len(colors_and_names) - 1)]
        # text = "%s [Size: %d x %d][Color: %s] " % (extra_text, width, height, color_name)
        text = extra_text
        return cls(width, height, background_color=color, text=text)

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

    def extract_stripped_text(self):
        return self.page.extractText().strip()

    def to_rect(self):
        return Rect([self.pdf_page_width, self.pdf_page_height])


class BaseTestCase(TestCase):
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.source_pdf = StringIO()
        self.colored_pages = []
        self.create_randomly_sized_pdf_pages()

    def create_randomly_sized_pdf_pages(self):
        writer = PdfFileWriter()
        for id in range(0, 100):
            max_width, max_height = [int(round(x / mm / 2)) for x in pagesizes.A4]
            colored_page = ColoredPDFPage.create_randomly_sized_and_colored_page(40, max_width,
                                                                                 40, max_height,
                                                                                 extra_text="#%d" % id,
            )
            writer.addPage(colored_page.page)
            self.colored_pages.append(colored_page)
        writer.write(self.source_pdf)

    def test_expected_page_count(self):
        reader = PdfFileReader(self.source_pdf)
        assert_that(reader.numPages, equal_to(100), "Expected page count")

    def test_colored_page_creation_results_in_the_correct_page_sizes_and_size(self):
        min_width, min_height = 50, 50
        max_width, max_height = 100, 200
        colored_page = ColoredPDFPage.create_randomly_sized_and_colored_page(min_width, max_width,
                                                                             min_height, max_height,
                                                                             "sometext!!")
        pdf_page_width = colored_page.pdf_page_width
        pdf_page_height = colored_page.pdf_page_height

        assert_that(colored_page.width, close_to(float(pdf_page_width), delta=0.001))
        assert_that(colored_page.height, close_to(float(pdf_page_height), delta=0.001))

        assert_that(pdf_page_height, less_than_or_equal_to(max_height * mm))
        assert_that(pdf_page_width, less_than_or_equal_to(max_width * mm))

        assert_that(pdf_page_height, greater_than_or_equal_to(min_height * mm))
        assert_that(pdf_page_width, greater_than_or_equal_to(min_width * mm))

        found_text = colored_page.extract_stripped_text()
        assert_that(found_text, contains_string("sometext!!"))

    def test_pack_pages(self):
        canvas = (306, 303)
        rects = [Rect([100, 200]), Rect([200, 300])]
        pack(canvas, rects, 3)

    def test_pack_pdf_pages(self):
        packer = PDFPagePacker(self.source_pdf)
        assert_that(packer.page_count, equal_to(100))
        assert_that(len(packer.rects), equal_to(100))
        pages = packer.pack()

        placed_rects = list(chain.from_iterable(pages))
        rect_count = len(placed_rects)
        assert_that(rect_count, equal_to(100))

        for r in placed_rects:
            assert_that(r.width, close_to(float(r.page.mediaBox.getWidth()), delta=0.001))
            assert_that(r.height, close_to(float(r.page.mediaBox.getHeight()), delta=0.001))

        packed_file = StringIO()
        packer.get_packed_file(packed_file)
        r = PdfFileReader(packed_file)
        assert_that(has_length(pages), r.numPages)

        f = file("/Users/jp/Desktop/mypdf_processed.pdf", "wb")
        packer.get_packed_file(f)
        f.close()
        return

        rects = [page.to_rect() for page in self.colored_pages]
        canvas = pagesizes.A4
        pack(canvas, rects, 1)
