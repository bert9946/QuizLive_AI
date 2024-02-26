# from https://yasoob.me/posts/how-to-use-vision-framework-via-pyobjc/
#   and https://github.com/RhetTbull/osxphotos/blob/main/osxphotos/text_detection.py
import Quartz
from Foundation import NSURL
import Vision


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

def detect_text(img_path: str):
    # Get the CIImage on which to perform requests.
    input_url = NSURL.fileURLWithPath_(img_path)
    input_image = Quartz.CIImage.imageWithContentsOfURL_(input_url)

    # Create a new image-request handler.
    request_handler = Vision.VNImageRequestHandler.alloc().initWithCIImage_options_(
        input_image, None
    )
    results = []
    handler = make_request_handler(results)


    # Create a new request to recognize text.
    request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handler)
    request.setRecognitionLanguages_(['zh-Hant'])
    request.setRevision_(Vision.VNRecognizeTextRequestRevision3)
    request.setRecognitionLevel_(0)
    # request.setUsesLanguageCorrection_(False)

    # Perform the text-recognition request.
    error = request_handler.performRequests_error_([request], None)

    return results