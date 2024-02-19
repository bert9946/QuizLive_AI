def crop_image(image):
	h, w = image.shape[:2]
	return image[int(h*.265):int(h*.93), int(w*0.15):int(w*0.87)]
