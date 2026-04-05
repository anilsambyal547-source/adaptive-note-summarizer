# utils/ocr_processor.py — Image/scanned PDF text extraction
# Primary: Gemini Vision | Fallback: OpenCV preprocessing + Tesseract
import io
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Structured result from OCR processing."""
    text: str = ""
    method: str = "none"
    warnings: list[str] = field(default_factory=list)
    success: bool = False


def _preprocess_image_cv(image_bytes: bytes) -> bytes:
    """Apply OpenCV preprocessing: grayscale, CLAHE contrast, deskew."""
    try:
        import cv2
        import numpy as np

        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return image_bytes

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # CLAHE for adaptive contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Deskew via Hough lines
        edges = cv2.Canny(enhanced, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100,
                                minLineLength=100, maxLineGap=10)
        if lines is not None and len(lines) > 0:
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                if abs(angle) < 15:  # Only consider near-horizontal lines
                    angles.append(angle)
            if angles:
                median_angle = np.median(angles)
                if abs(median_angle) > 0.5:
                    h, w = enhanced.shape
                    center = (w // 2, h // 2)
                    matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    enhanced = cv2.warpAffine(enhanced, matrix, (w, h),
                                              flags=cv2.INTER_CUBIC,
                                              borderMode=cv2.BORDER_REPLICATE)

        # Binarize for OCR
        enhanced = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        _, buf = cv2.imencode(".png", enhanced)
        return buf.tobytes()

    except ImportError:
        logger.warning("OpenCV not available — skipping preprocessing")
        return image_bytes
    except Exception as exc:
        logger.warning("Image preprocessing failed: %s", exc)
        return image_bytes


def extract_text_with_vision(image_bytes: bytes, model) -> OCRResult:
    """Use Gemini Vision to extract text from an image."""
    try:
        import PIL.Image

        img = PIL.Image.open(io.BytesIO(image_bytes))
        prompt = (
            "Extract ALL text from this image exactly as written. "
            "Preserve formatting, line breaks, and structure. "
            "If the image contains handwritten text, do your best to transcribe it. "
            "Return only the extracted text, nothing else."
        )
        response = model.generate_content([prompt, img])
        if response and response.text and len(response.text.strip()) > 10:
            return OCRResult(
                text=response.text.strip(),
                method="gemini_vision",
                success=True,
            )
        return OCRResult(warnings=["Gemini Vision returned insufficient text"])
    except Exception as exc:
        logger.warning("Gemini Vision OCR failed: %s", exc)
        return OCRResult(warnings=[f"Gemini Vision failed: {exc}"])


def extract_text_with_tesseract(image_bytes: bytes) -> OCRResult:
    """Preprocess image with OpenCV, then run Tesseract OCR."""
    try:
        import pytesseract
        import PIL.Image

        processed = _preprocess_image_cv(image_bytes)
        img = PIL.Image.open(io.BytesIO(processed))
        text = pytesseract.image_to_string(img, lang="eng")

        if text and len(text.strip()) > 10:
            return OCRResult(text=text.strip(), method="tesseract_ocr", success=True)
        return OCRResult(warnings=["Tesseract returned insufficient text"])

    except ImportError:
        return OCRResult(warnings=["Tesseract/pytesseract not installed"])
    except Exception as exc:
        logger.warning("Tesseract OCR failed: %s", exc)
        return OCRResult(warnings=[f"Tesseract OCR failed: {exc}"])


def extract_text_from_image(image_bytes: bytes, model=None) -> OCRResult:
    """
    Extract text from an image.
    Strategy: Gemini Vision (primary) → OpenCV + Tesseract (fallback) → error.
    """
    all_warnings: list[str] = []

    # 1. Try Gemini Vision
    if model is not None:
        result = extract_text_with_vision(image_bytes, model)
        if result.success:
            return result
        all_warnings.extend(result.warnings)

    # 2. Fallback to Tesseract
    result = extract_text_with_tesseract(image_bytes)
    if result.success:
        result.warnings = all_warnings + result.warnings
        return result
    all_warnings.extend(result.warnings)

    # 3. Nothing worked
    return OCRResult(
        text="",
        method="none",
        warnings=all_warnings,
        success=False,
    )


def extract_text_from_scanned_pdf(
    pdf_bytes: bytes, model=None, progress_callback=None
) -> OCRResult:
    """
    Convert a scanned PDF to images and extract text from each page.
    Uses pdf2image for conversion, then the image pipeline.
    """
    try:
        from pdf2image import convert_from_bytes

        images = convert_from_bytes(pdf_bytes, dpi=300)
    except ImportError:
        return OCRResult(warnings=["pdf2image not installed — cannot process scanned PDF"])
    except Exception as exc:
        return OCRResult(warnings=[f"PDF to image conversion failed: {exc}"])

    all_text: list[str] = []
    all_warnings: list[str] = []
    method = "none"
    total = len(images)

    for i, img in enumerate(images):
        if progress_callback:
            progress_callback(i, total)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        page_bytes = buf.getvalue()

        page_result = extract_text_from_image(page_bytes, model=model)
        if page_result.success:
            all_text.append(f"--- Page {i + 1} ---\n{page_result.text}")
            method = page_result.method
        all_warnings.extend(page_result.warnings)

    if progress_callback:
        progress_callback(total, total)

    combined = "\n\n".join(all_text)
    return OCRResult(
        text=combined,
        method=method,
        warnings=all_warnings,
        success=bool(combined.strip()),
    )
