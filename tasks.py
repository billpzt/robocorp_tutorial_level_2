import os
from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Archive import Archive

import order_utils as ut


@task
def order_robots_from_RobotSpareBin():
    """
    Cleans up the output directory from previous runs.
    Orders robots from the RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    Cleans up the output directory.
    """
    cleanup()
    open_robot_order_website()
    download_csv_file()
    ut.close_annoying_modal()
    orders = ut.return_csv_data()
    process_all_orders(orders)
    archive_receipts()
    cleanup()


def open_robot_order_website():
    main_url = "https://robotsparebinindustries.com/#/robot-order"
    browser.goto(main_url)


def download_csv_file():
    """Downloads the CSV file with the orders."""
    csv_url = "https://robotsparebinindustries.com/orders.csv"
    http = HTTP()
    http.download(csv_url, overwrite=True)


def process_all_orders(orders_table):
    for order in orders_table:
        ut.process_one_order(order)


def archive_receipts():
    """Creates a ZIP archive of the receipts."""
    lib = Archive()
    lib.archive_folder_with_zip(
        folder="./output", archive_name="./output/receipts.zip", include="*.pdf"
    )


def cleanup():
    """Cleans up the output directory."""
    for file in os.listdir("./output"):
        if file.endswith(".pdf") or file.endswith(".png"):
            os.remove(os.path.join("./output", file))
