from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.FileSystem import FileSystem
import zipfile

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """

    browser.configure( # slows everything down
        slowmo=0,
    )

    open_robot_order_website()
    order_looper()
    archive_receipts()

    
def open_robot_order_website():
    """Opens the website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    
def close_annoying_modal():
    """Commits actions that have to be done on page like clicking and inputting text"""
    page = browser.page()
    page.click("text=OK")
    
def fill_the_form(order):
    """Fills the form"""
    page = browser.page()
    page.select_option("#head", order["Head"])
    page.click(f"#id-body-{order['Body']}")
    page.fill(".form-control", order["Legs"])
    page.fill("#address", order["Address"])
    page.click("text=Preview")
    page.click("#order")
    while page.locator('.alert-danger').is_visible():
        page.click("#order")
    store_receipt_as_pdf(order["Order number"])
    screenshot_robot(order["Order number"])
    page.click("#order-another")
    
def store_receipt_as_pdf(order_number):
    """Saves order receipt as pdf"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt_html, f'output/receipt_{order_number}.pdf')

def screenshot_robot(order_number):
    page = browser.page()
    page.locator('#robot-preview').screenshot(path= f'output/screenshot_{order_number}.png')
    embed_screenshot_to_receipt(f'output/screenshot_{order_number}.png', f'output/receipt_{order_number}.pdf')

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()

    pdf.add_files_to_pdf(
        files = [
            pdf_file,
            f"{screenshot}:align=center"
        ],
        target_document = pdf_file
    )

def archive_receipts():
    with zipfile.ZipFile("output/receipts.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        lib = FileSystem()
        files = lib.find_files("output/receipt_*.pdf")
        file_paths_names = [(file.path, file.name) for file in files]

        for (path,name) in file_paths_names:
            zipf.write(path, name)



def order_looper():
    """Loops through each order and calls the form filler"""
    close_annoying_modal()
    for row in get_orders():
        fill_the_form(row)
        close_annoying_modal()

def get_orders():
    """Gets order file"""
    http = HTTP()
    http.download(url = "https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    orders = library.read_table_from_csv("orders.csv")
    return orders