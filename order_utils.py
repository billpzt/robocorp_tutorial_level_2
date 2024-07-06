import os
from robocorp import browser
from RPA.Tables import Tables
from RPA.PDF import PDF


def fill_order_form(individual_order: dict):
    """Fills the form with the data from the individual order."""
    page = browser.page()
    page.select_option("#head", individual_order["Head"])  # 1. Choose head
    body_locator = f'#id-body-{individual_order["Body"]}'
    page.set_checked(body_locator, checked=True)  # 2. Choose a body
    legs_locator = "//div[3]/input"
    page.fill(legs_locator, individual_order["Legs"])  # 3. Choose legs
    page.fill("#address", individual_order["Address"])  # 4. Enter shipping address


def return_csv_data():
    """Reads the CSV file and fills the form with all the data."""
    csv = Tables()
    table = csv.read_table_from_csv("orders.csv", header=True)
    return table


def preview_robot_order() -> None:
    """Clicks the Preview button on the page"""
    page = browser.page()
    page.click("text=Preview")


def collect_order_screenshot() -> None:
    """Takes a screenshot of the page"""
    page = browser.page()
    page.screenshot(path="./output/robot_order.png")


def submit_order() -> None:
    """Submits the order and retry if server error."""
    page = browser.page()
    page.click("#order")
    error_message = page.query_selector(".alert-danger")
    while error_message:
        print("Error found on page, trying to order again")
        page.click("#order")  # Retry if server error
        if page.query_selector("#order-another"):
            break


def store_receipt_as_pdf(order_number) -> str:
    """
    Saves the order receipt as a PDF file
    and returns the filename to be used in another method.
    """
    # Get current working directory
    cwd = os.getcwd()
    # Create an absolute path for the PDF file
    pdf_filename_path = os.path.join(cwd, "output", f"order_{order_number}.pdf")

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(pdf_filename_path), exist_ok=True)

    # Get the current page and the order receipt HTML
    page = browser.page()
    order_receipt_html = page.locator("#receipt").inner_html()

    # Convert HTML to PDF
    pdf = PDF()
    pdf.html_to_pdf(order_receipt_html, pdf_filename_path)
    print(f"PDF path: {pdf_filename_path}")
    return pdf_filename_path


def screenshot_robot(order_number) -> str:
    """
    Takes a screenshot of the robot image
    and returns the filename to be used in another method.
    """
    # Get current working directory
    cwd = os.getcwd()
    # Create an absolute path for the screenshot file
    robot_screenshot_filename_path = os.path.join(
        cwd, "output", f"robot_{order_number}.png"
    )

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(robot_screenshot_filename_path), exist_ok=True)

    # Get the current page and take a screenshot
    page = browser.page()
    picture_locator_id = "#robot-preview-image"
    page.locator(picture_locator_id).screenshot(path=robot_screenshot_filename_path)
    print(f"Screenshot path: {robot_screenshot_filename_path}")
    return robot_screenshot_filename_path


def embed_screenshot_to_receipt(screenshot, pdf_file) -> None:
    pdf = PDF()
    files = [pdf_file, screenshot]
    print(files)
    pdf.add_files_to_pdf(files=files, target_document=pdf_file)


def click_to_order_another() -> None:
    page = browser.page()
    page.click("#order-another")


def close_annoying_modal() -> None:
    modal_locator = ".modal-dialog"
    page = browser.page()
    if page.is_visible(modal_locator):
        page.click("text=OK")  # Give up rights


def process_one_order(order) -> None:
    close_annoying_modal()
    order_num = order["Order number"]
    fill_order_form(order)
    preview_robot_order()
    collect_order_screenshot()
    submit_order()
    pdf_path = store_receipt_as_pdf(order_number=order_num)
    robot_screenshot_path = screenshot_robot(order_number=order_num)
    embed_screenshot_to_receipt(robot_screenshot_path, pdf_path)
    click_to_order_another()
