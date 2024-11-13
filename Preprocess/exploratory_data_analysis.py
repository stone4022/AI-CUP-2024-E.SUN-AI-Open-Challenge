import os
import fitz
from natsort import natsorted


def save_page_as_image(page, output_folder, pdf_file_name, page_num):
    """
    Save a PDF page as an image.

    :param page: PDF page object
    :param output_folder: Folder to save the image
    :param pdf_file_name: PDF file name (without path)
    :param page_num: Page number
    """
    # Render the page as an image
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Resolution can be adjusted
    pdf_base_name = os.path.splitext(os.path.basename(pdf_file_name))[0]

    # Define the path for saving the image
    image_filename = f"{pdf_base_name}_page_{page_num + 1}.png"
    image_path = os.path.join(output_folder, image_filename)

    # Save the image to the specified folder
    pix.save(image_path)


def analyze_pdf(file_path, output_folder):
    """
    Analyze a PDF and categorize pages as text-only, image-only, or mixed content.

    :param file_path: PDF file path
    :param output_folder: Folder for saving images
    :return: Dictionary containing categorized pages
    """
    doc = fitz.open(file_path)

    analysis = {
        "pure_text_pages": [],    # Text-only pages
        "pure_image_pages": [],   # Image-only pages
        "mixed_pages": []         # Pages with both images and text
    }

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = page.get_text()
        images = page.get_images(full=True)

        # Save the entire page as an image if it contains images
        # if images:
        #     save_page_as_image(page, output_folder, file_path, page_num)

        # Classify the page based on its content
        if text and not images:
            analysis["pure_text_pages"].append(page_num + 1)  # Text-only page
        elif images and not text:
            analysis["pure_image_pages"].append(page_num + 1)  # Image-only page
        elif text and images:
            analysis["mixed_pages"].append(page_num + 1)  # Mixed content page

    doc.close()
    return analysis


def analyze_pdfs_in_folder(folder_path, output_folder):
    """
    Analyze all PDF files in a folder and classify each page by content type.

    :param folder_path: Path to the folder containing PDF files
    :param output_folder: Folder for saving images
    :return: Dictionary of analysis results and a summary of the folder
    """
    pdf_files = [os.path.join(folder_path, f)
                 for f in os.listdir(folder_path) if f.endswith('.pdf')]

    all_results = {}
    total_text_pages = 0
    total_image_pages = 0
    total_mixed_pages = 0
    pure_image_pdfs = []
    mixed_pdfs = []

    for pdf_file in pdf_files:
        result = analyze_pdf(pdf_file, output_folder)
        all_results[pdf_file] = result

        total_text_pages += len(result["pure_text_pages"])
        total_image_pages += len(result["pure_image_pages"])
        total_mixed_pages += len(result["mixed_pages"])

        if len(result["pure_image_pages"]) > 0:
            pure_image_pdfs.append(pdf_file.replace("\\", "/"))

        if len(result["mixed_pages"]) > 0:
            mixed_pdfs.append(pdf_file.replace("\\", "/"))

    folder_summary = {
        "total_pure_text_pages": total_text_pages,
        "total_pure_image_pages": total_image_pages,
        "total_mixed_pages": total_mixed_pages,
        "pure_image_pdfs": pure_image_pdfs,
        "mixed_pdfs": mixed_pdfs
    }

    return all_results, folder_summary


def analyze_pdfs_in_multiple_folders(folder_paths, output_folder_base):
    """
    Analyze PDF files across multiple folders.

    :param folder_paths: List of folder paths
    :param output_folder_base: Base folder path for saving images
    :return: Dictionary of analysis results for all folders
    """
    all_folder_results = {}

    for folder_path in folder_paths:
        if os.path.exists(folder_path):
            folder_name = os.path.basename(folder_path)
            output_folder = os.path.join(output_folder_base, folder_name)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            folder_result, folder_summary = analyze_pdfs_in_folder(
                folder_path, output_folder)
            all_folder_results[folder_path] = {
                "results": folder_result,
                "summary": folder_summary
            }
        else:
            print(f"Folder does not exist: {folder_path}")

    return all_folder_results


# File paths for the dataset (replace with the original dataset source from the official source)
folder_paths = ['datasets/reference/finance', 'datasets/reference/insurance']
output_folder_base = 'figures'
result = analyze_pdfs_in_multiple_folders(folder_paths, output_folder_base)

# Display results
for folder, folder_data in result.items():

    # Initialize counters (to count the number of PDF files)
    total_pure_image_pdfs = 0
    total_mixed_pdfs = 0
    pure_image_pdf_list = []
    mixed_pdf_list = []

    print(f"\nFolder: {folder}")
    print(f"Total text-only pages: {folder_data['summary']['total_pure_text_pages']}")
    print(f"Total image-only pages: {folder_data['summary']['total_pure_image_pages']}")
    print(f"Total mixed-content pages: {folder_data['summary']['total_mixed_pages']}")

    # If the folder contains PDF files with image-only pages
    if 'pure_image_pdfs' in folder_data['summary'] and folder_data['summary']['pure_image_pdfs']:
        sorted_pure_image_pdfs = natsorted(folder_data['summary']['pure_image_pdfs'])
        total_pure_image_pdfs += len(sorted_pure_image_pdfs)  # Sum the count of image-only PDFs
        pure_image_pdf_list.extend([os.path.splitext(os.path.basename(pdf))[0] for pdf in sorted_pure_image_pdfs])

    # If the folder contains PDF files with mixed-content pages
    if 'mixed_pdfs' in folder_data['summary'] and folder_data['summary']['mixed_pdfs']:
        sorted_mixed_pdfs = natsorted(folder_data['summary']['mixed_pdfs'])
        total_mixed_pdfs += len(sorted_mixed_pdfs)  # Sum the count of mixed-content PDFs
        mixed_pdf_list.extend([os.path.splitext(os.path.basename(pdf))[0] for pdf in sorted_mixed_pdfs])

    # Display total count results after the loop
    print(f"Total image-only PDF files: {total_pure_image_pdfs}")
    print(f"Total mixed-content PDF files: {total_mixed_pdfs}")
    print(f"Image-only PDF file list: {pure_image_pdf_list}")
    print(f"Mixed-content PDF file list: {mixed_pdf_list}")

