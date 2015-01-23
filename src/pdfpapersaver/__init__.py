from PyPDF2 import PdfFileReader, PdfFileWriter
from rect import Rect
from rect.packer import pack
from reportlab.lib import pagesizes
from reportlab.lib.units import mm

__version__ = "0.1.0"


class PDFPagePacker(object):
    def __init__(self, pdf_file, canvas_size=pagesizes.A4, padding=5 * mm):
        super(PDFPagePacker, self).__init__()
        self.pdf_file = pdf_file
        self.canvas_size = canvas_size
        self.inner_canvas_size = canvas_size[0] - 4 * padding, canvas_size[1] - 4 * padding
        self.padding = padding
        self.reader = PdfFileReader(self.pdf_file)
        self.rects = list()
        self.create_rect_page_dictionary()

    @property
    def page_count(self):
        return self.reader.numPages

    def create_rect_page_dictionary(self):
        for page in self.reader.pages:
            rect = Rect([page.mediaBox.getWidth(), page.mediaBox.getHeight()])
            rect.page = page
            self.rects.append(rect)

    def pack(self):
        def place_rects_and_append_to_pages(rects_to_place):
            pages_to_place = [rect.page for rect in rects_to_place]
            placed_rects = pack(self.inner_canvas_size, rects_to_place, self.padding)
            for rect, page in zip(placed_rects, pages_to_place):
                rect.page = page
            if placed_rects:
                pages.append(placed_rects)

        items_to_place = list(self.rects)
        rects_to_place = []
        pages = []
        while items_to_place:
            try:
                rect = items_to_place[0]
                rects_to_place.append(rect)
                pack(self.inner_canvas_size, rects_to_place, self.padding)
                items_to_place.pop(0)
            except ValueError, e:
                if e.message == "Pack size too small.":
                    rects_to_place.pop()
                    place_rects_and_append_to_pages(rects_to_place)
                    rects_to_place = []
                else:
                    raise
        place_rects_and_append_to_pages(rects_to_place)
        return pages

    def get_packed_file(self, packed_file):
        writer = PdfFileWriter()
        scale = 1.0
        for rects in self.pack():
            page = writer.addBlankPage(*self.canvas_size)
            for rect in rects:
                y = self.canvas_size[1] - rect.top - 2 * self.padding
                x = rect.left + 2 * self.padding
                page.mergeScaledTranslatedPage(rect.page, scale, x, y)
        writer.write(packed_file)