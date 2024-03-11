import cv2 as cv
import numpy as np

import Vision


def image2text(numpy_array: np.ndarray) -> str:
    buffer = imageToBuffer(numpy_array)
    results = detect_text(buffer)
    text = '\n'.join([i[0] for i in results])
    return text

def detect_text(buffer):

    # Create a new image-request handler.
    request_handler = Vision.VNImageRequestHandler.alloc().initWithData_options_(
        buffer, None
    )
    results = []
    handler = make_request_handler(results)

    # Create a new request to recognize text.
    request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handler)
    request.setRecognitionLanguages_(['zh-Hant'])
    request.setRevision_(Vision.VNRecognizeTextRequestRevision3)
    request.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)

    # Perform the text-recognition request.
    error = request_handler.performRequests_error_([request], None)

    return results

def make_request_handler(results):
    """results: list to store results"""
    if not isinstance(results, list):
        raise ValueError("results must be a list")

    def handler(request, error):
        if error:
            print(f"Error! {error}")
        else:
            observations = request.results()
            for text_observation in observations:
                recognized_text = text_observation.topCandidates_(1)[0]
                results.append([recognized_text.string(), recognized_text.confidence()])

    return handler

def imageToBuffer(image:any) -> any:
    """
    Convert a numpy array image to bytes.

    Parameters
    ----------
    image : object
        The input image to be converted.

    Returns
    -------
    bytes
        The image data in bytes.
    """
    success, encoded_image = cv.imencode('.jpeg', image)  # Replace '.png' with the desired format
    return encoded_image.tobytes()