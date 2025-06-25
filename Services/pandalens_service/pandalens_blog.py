from docx import Document
from docx.shared import Inches
from Utilities import file_utility, time_utility, logging_utility
from Services.pandalens_service import pandalens_const

_logger = logging_utility.setup_logger(__name__)


def create_blog_in_word(intro, conclusion, selected_moments, enhanced_summaries, ignored_moments):
    """
    Create a travel blog Word document with enhanced coherent summaries.

    Args:
        intro: Introduction text
        conclusion: Conclusion text
        selected_moments: List of moment dictionaries
        enhanced_summaries: Optional list of rewritten summaries for each moment
        ignored_moments: Optional list of ignore moments
    """

    _logger.debug("[BLOG] Creating blog in Word document: Total moments: {moment_count}",
                  moment_count=len(selected_moments))

    # Create a new Document
    doc = Document()

    # Intro
    doc.add_heading('My Blog', 0)
    doc.add_paragraph(intro)

    # Body
    doc.add_heading('Memorable Moments', 0)

    img_folder = file_utility.get_path_from_project_root(pandalens_const.SEQUENCE_PATH_TO_IMAGES_FROM_PROJECT_ROOT)
    # Add moments with enhanced summaries
    for i, selected_moment in enumerate(selected_moments):
        img_name = selected_moment.get(pandalens_const.DB_MOMENT_FILENAME_KEY)
        if img_name:  # Add image if available
            img_path = file_utility.get_path_with_filename(img_folder, img_name)
            doc.add_picture(img_path, width=Inches(4))

        # Use enhanced summary if available, otherwise use original
        ori_summary = selected_moment[pandalens_const.DB_MOMENT_SUMMARY_KEY]
        summary = enhanced_summaries[i] if enhanced_summaries and i < len(enhanced_summaries) else ori_summary

        # Add the moment content
        doc.paragraph = doc.add_paragraph("\n" + summary + "\n")

    # Keep photos of ignored moments
    if len(ignored_moments) > 0:
        doc.add_heading('Additional Photos', 0)
        paragraph = doc.add_paragraph()
        for ignore_moment in ignored_moments:
            img_name = ignore_moment.get(pandalens_const.DB_MOMENT_FILENAME_KEY)
            if img_name:  # Add image if available
                run = paragraph.add_run()
                img_path = file_utility.get_path_with_filename(img_folder, img_name)
                run.add_picture(img_path, width=Inches(2))

    # Conclusion
    doc.add_heading('Summary', 0)
    doc.add_paragraph(conclusion)

    # Save the document
    pandalens_blog_root = file_utility.get_path_from_project_root(
        pandalens_const.SEQUENCE_PATH_TO_BLOGS_FROM_PROJECT_ROOT)

    current_date = time_utility.get_date_string("%Y%m%d_%H%M")
    doc.save(file_utility.get_path_with_filename(pandalens_blog_root, f'blog-{current_date}.docx'))
