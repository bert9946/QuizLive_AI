import io
import numpy as np
from PIL import Image

import Vision
from Quartz import CIImage
from AppKit import NSBitmapImageRep, NSImage
from Foundation import NSData


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

def detect_text(ci_image):

    # Create a new image-request handler.
    request_handler = Vision.VNImageRequestHandler.alloc().initWithCIImage_options_(
        ci_image, None
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


"""Create a CIImage from a numpy array"""
"""from: https://gist.github.com/RhetTbull/1c34fc07c95733642cffcd1ac587fc4c?permalink_comment_id=4945454#gistcomment-4945454"""

def createNSImageFromNumpyArray(numpy_array):
    image = Image.fromarray(numpy_array)
    data = io.BytesIO()
    image.save(data, "JPEG")
    nsdata = NSData.dataWithBytes_length_(data.getvalue(), len(data.getvalue()))
    rep = NSBitmapImageRep.imageRepWithData_(nsdata)
    nsimage = NSImage.alloc().initWithSize_((rep.pixelsWide(), rep.pixelsHigh()))
    nsimage.addRepresentation_(rep)
    return nsimage

def convertNSImageToCIImage(nsimage):
    imageData = nsimage.TIFFRepresentation()
    bitmap = NSBitmapImageRep.alloc().initWithData_(imageData)
    ciimage = CIImage.alloc().initWithBitmapImageRep_(bitmap)
    return ciimage

def image2text(numpy_array: np.ndarray) -> str:
    nsi = createNSImageFromNumpyArray(numpy_array)
    cii = convertNSImageToCIImage(nsi)
    results = detect_text(cii)
    text = '\n'.join([i[0] for i in results])
    return text