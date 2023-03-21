import time
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from os.path import join as ospj

def gen_generic_text(style, text, spacer):
    par = Paragraph(text, style)
    spacer = Spacer(1, spacer)
    return [par, spacer]

def gen_heading1(styles, text):
    return gen_generic_text(styles["Heading1"], text, 4)

def gen_heading2(styles, text):
    return gen_generic_text(styles["Heading2"], text, 4)

def gen_content_line(styles, text):
    return gen_generic_text(styles["Normal"], text, 16)

def bus_basic_info(styles, line_number):
    elems = []
    operator = f"Operator: Egged"
    elems.extend(gen_heading2(styles, operator))
    return elems

def gen_intro(styles, line_number):
    intro = f"Bunching Report: Line {line_number}"
    return gen_heading1(styles, intro)

def gen_titled_image(styles, image, title, desc=None):
    elems = []
    elems.extend(gen_heading2(styles, title))
    if desc is not None:
        elems.extend(gen_content_line(styles, desc))
    elems.append(image)
    elems.append(Spacer(1, 16))
    return elems

def generate_bus_report(line_number, png_basedir):
    elems = []

    styles=getSampleStyleSheet()

    elems.extend(gen_intro(styles, line_number))
    elems.extend(bus_basic_info(styles, line_number))

    image_title_and_path = [
        # ("freq.png", "Bus Frequency"),
        ("route_journeys.png", "Bus Journeys"),
        ("bus_stop_bunching.png", "Bus Route Bunching", 
            "How bunched the bus is in the route until that station. This doesn't mean that it started bunching close to that station, just the current degree of bunching."),
        # ("test2.png", "Bus Route Bunching Difference", "The degree of bunching that each station contributes. Essentially, whether the buses bunched in the route before that station."),
        # ("bunching_in_day.png", "Bunching / Time in Day", "Coorelation of bunching to an hour in a weekday")
    ]

    for image_tpl in image_title_and_path:
        if len(image_tpl) == 3:
            desc = image_tpl[2]
        else:
            desc = None

        filename, title, *_ = image_tpl
        path = ospj(str(png_basedir), filename)
        img = Image(path, 450, 450)
        elems.extend(gen_titled_image(styles, img, title, desc))

    return elems


def generate_report(filename, png_basedir, line_number):
    doc = SimpleDocTemplate(filename, pagesize=letter,
                        rightMargin=72,leftMargin=72,
                        topMargin=72,bottomMargin=18)
    report_elems = generate_bus_report(line_number, png_basedir)
    doc.build(report_elems)

def main():
    generate_report("bus_report.pdf", "images", 1337)

if __name__ == "__main__":
    main()