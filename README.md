This repository contains 2 tools:
1. raw2fits module which converts a given RAW image file to FITS.
2. watchnconvert which watches a directory for new RAW files and converts them as they appear.

# Requirements
Requires Python >= 3.9 and pip
```pip install -r requirements.txt```

# watchnconvert usage 
Run with default parameter values:
```python watchnconvert.py```

To see available parameters and their default values:
```python watchnconvert.py --help```

# Example use cases
This can then be used e.g. with the INDI CCD Simulator to make real photos available to consuming software such as KStars with cameras that aren't directly supported.

For example, one can use an EZ Share card and my [ezshare tool](https://github.com/Domdron/ezshare) to download images from an unsupported camera via WiFi, and then automatically convert them to FITS, which allows them to be used in the INDI CCD Simulator and therefore INDI clients apps.

## With INDI/KStars/EKOS:
1. In ezshare Typescript project start `npm run oly` to download images from an Olympus PEN camera (use `npm run start` with appropriate parameters for other cameras).
2. In this project directory, start 
```python watchnconvert.py --directory ../ezshare/raws/ --output_file ./latest.fits``` 
to auto-convert new images to `./latest.fits`
3. Make sure there are no other `.fits` files in this directory.
4. In INDI CCD Sim config, watch this project direcotry.
5. Now, triggering an image capture in EKOS will load the current content of `latest.fits`.

So the flow is generally:1
1. Capture image in camera.
2. Wait for image being downloaded and converted.
3. Trigger capture in EKOS (or other INDI clients) to load the image.

This implies of course that it's generally not suitable for automatic workflows, as one needs to trigger the camera, and do so before triggering the capture in EKOS. Except in some cases with some workarounds:

## Polar alignment

With a bit of trickery, one can use it e.g. for the polar alignment. The idea is to set the exposure lenght long enough to allow for steps 1. and 2. above to be completed before the alignment process tries to load the next image. 

But a problem here is that the CCD Simulator loads the image from disk at the beginngin of the exposure time, not at the end. However, if the plate solving fails for a captured image, it makes another capture and tries again. So we can exploit this by letting it intentionally fail for the first time, by giving it a non-solvable image (e.g. pure noise or black) to give us enough time to do steps 1. and 2. above before the 2nd capture in the 2nd and 3rd alignment step:

1. Set Exposure time to a value which is greater than the max. download time from the EZ Share card + some extra (>= 45 seconds in my case).
2. Slew mount to start location.
3. Make first capture and wait for it to be downloaded and converted.
4. Start Polar alignment. It will immediate make the first capture and load the image from step 2.
5. After completion of capture, while mount is slewing to the next position, `cp <path-to-noise.fits> ./latest.fits` to let plate solving fail, which makes time for capturing, downloading and converting a new image.
6. Capture new image in camera. It will be picked up automatically on the retried capture. Repeat from 5. for the third alignment step.
7. For the final adjustment step, just keep capturing; images will be picked up automatically.

One can probably streamline this by avoiding the purposeful failing and re-capturing (which makes each step take >= 90 seconds) by using manual slewing instead; but I haven't tried that yet.