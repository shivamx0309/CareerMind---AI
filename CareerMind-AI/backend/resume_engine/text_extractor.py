
import pymupdf


def extract_text_from_pdf(file_path: str) -> dict:
    """
    Extract text from a PDF document page by page.

    Args:
        file_path: Absolute or relative path to the PDF.

    Returns:
        Dictionary containing extracted text and metadata.
    """

    document = None

    try:
        document = pymupdf.open(file_path)

        if document.is_encrypted:
            raise ValueError("Password-protected PDFs are not supported.")

        if document.page_count == 0:
            raise ValueError("PDF contains no pages.")

        pages = []
        full_text_parts = []
        links = []

        for page_number, page in enumerate(document, start=1):
            page_text = page.get_text("text")

            # Extract hyperlink annotations if present
            for link in page.get_links():
                if "uri" in link and link["uri"]:
                    links.append(link["uri"])

            # Normalize whitespace while preserving line structure.
            cleaned_lines = [
                line.strip()
                for line in page_text.splitlines()
                if line.strip()
            ]

            cleaned_text = "\n".join(cleaned_lines)

            pages.append({
                "page_number": page_number,
                "text": cleaned_text,
                "character_count": len(cleaned_text),
            })

            full_text_parts.append(cleaned_text)

        full_text = "\n\n".join(
            text for text in full_text_parts if text
        )

        return {
            "page_count": document.page_count,
            "pages": pages,
            "full_text": full_text,
            "character_count": len(full_text),
            "extraction_status": (
                "completed" if full_text.strip() else "no_text_found"
            ),
            "links": links,
        }

    except ValueError:
        raise

    except Exception as exc:
        raise ValueError(
            "Unable to extract text from the PDF."
        ) from exc

    finally:
        if document is not None:
            document.close()

