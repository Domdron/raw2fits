import os
import rawpy
import numpy as np
from astropy.io import fits
from scipy.ndimage import zoom
import time


def convert_raw_to_fits(raw_file_path, pixel_size, downscale_factor, output_file_path = None):
    """
    Convert a RAW image file to a FITS file.

    This function reads a RAW image file, converts it to an RGB image, 
    then converts that image to a numpy array, and finally writes that 
    data to a new FITS file. The FITS file is saved with the same base 
    name as the input file but with a ".fits" extension. A 'PIXSIZE1' 
    keyword is added to the FITS file header, with its value set to the 
    provided pixel size.

    Parameters:
    raw_path (str): The path to the RAW file to convert.
    pixel_size (float): The pixel size of the camera sensor, in micrometers.
    downscale_factor (int): The factor by which to downscale the converted image.
    output_file_path (str): The path to the output FITS file. If not provided, a new FITS file 
        is created in the same directory as the input file with the same base name as the input
        file.

    Side Effects:
    A new FITS file is created either as specified by output_file_path, or in the same directory 
    and with the same base name as the input file. 
    If a file with the same name already exists, it will be overwritten.

    Example usage:
    convert_raw_to_fits('path_to_your_file.RAW', 5.0, 2, './output.fits')
    """

    # Determine the FITS file path
    if(output_file_path is None):
        base_name = os.path.splitext(raw_file_path)[0]
        output_file_path = base_name + '.fits'

   # Read and process the raw file
    rgb = read_and_process_image(raw_file_path)

    # Convert the RGB image to grayscale
    grayscale = np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

    # Get the actual shape of the grayscale image
    actual_shape = grayscale.shape

    # Reshape the image data to match the actual shape
    reshaped_image = grayscale.reshape(actual_shape)

    # Downscale the image
    downscaled_image = zoom(reshaped_image, 1 / downscale_factor)

    # Normalize the image data to the range 0-65535 (16-bit range)
    downscaled_image = ((downscaled_image - downscaled_image.min()) / (downscaled_image.max() - downscaled_image.min())) * 65535

    # Convert the data to 16-bit integers
    downscaled_image = downscaled_image.astype(np.uint16)

    # Create a FITS file
    hdu = fits.PrimaryHDU(downscaled_image)

    # Set PIXELSIZE1 header
    hdu.header['PIXSIZE1'] = pixel_size * downscale_factor

    # Write the FITS file
    hdu.writeto(output_file_path, overwrite=True)

    print(f'Wrote {output_file_path}')



def read_and_process_image(raw_file_path, retries=20, delay=2):
    """
    Read and process an image file using rawpy. If an error occurs during reading,
    the operation is retried a specified number of times.

    Parameters:
    raw_file_path (str): The path to the raw image file.
    retries (int): The number of times to retry reading the file if an error occurs. Default is 3.
    delay (int): The delay in seconds between retries. Default is 1.

    Returns:
    np.ndarray: The processed image data.
    """
    for i in range(retries):
        try:
            with rawpy.imread(raw_file_path) as raw:
                rgb = raw.postprocess()
            return rgb
        except rawpy._rawpy.LibRawIOError:
            if i < retries - 1:  # i is zero indexed
                time.sleep(delay)
                continue
            else:
                raise    