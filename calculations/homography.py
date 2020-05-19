# import the necessary packages
import numpy as np
import cv2


def four_point_transform(image, pts):
	"""
	Performs a perspective transformation to obtain a bird's-eye view of a given image.
	Source: https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/

	Args:
		image (np.array): Tensor of the image to be transformed.
		pts (np.array): 4*2 array of rectangular coordinates with which to calibrate the bird's-eye view with.

	Returns:
		warped (np.array): Image of the bird's-eye view. Unused but could be visualised.
		M (np.array): 3*3 homography matrix. This allows the translation of any given point to the transformed perspective.
	"""
	
	# NOTE: Very specific ordering of points. 
	(tl, tr, br, bl) = pts

	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))

	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))

	# Now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view"
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")

	M = cv2.getPerspectiveTransform(pts, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

	return warped, M