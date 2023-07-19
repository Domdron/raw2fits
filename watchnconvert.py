import time
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Assuming the convert_raw_to_fits function is defined in a module named 'conversion_module'
from raw2fits import convert_raw_to_fits

class FileHandler(FileSystemEventHandler):
    """
    FileHandler is a class that inherits from FileSystemEventHandler.
    It overrides the on_created method to perform actions when a new file is detected.

    For each of the parameters of the convert_raw_to_fits function, which is used to do
    the conversion to FITS, this class has an attribute of the same name.
    """
        
    def __init__(self, file_extension, pixel_size, downscale_factor, output_file_path):
        self.file_extension = file_extension
        self.pixel_size = pixel_size
        self.downscale_factor = downscale_factor
        self.output_file_path = output_file_path

    def on_created(self, event):
        if event.src_path.endswith(self.file_extension):
            print(f'New file detected: {event.src_path}')
            convert_raw_to_fits(event.src_path, self.pixel_size, self.downscale_factor, self.output_file_path)

def watch_directory(directory, file_extension, pixel_size, downscale_factor, output_file_path):
    """
    This function sets up a watchdog observer to watch a directory for new files with a specific extension.
    When a new file with the specified extension is detected in the directory, it is automatically converted
    using the convert_raw_to_fits function. This function runs indefinitely until interrupted.

    Args: (see convert_raw_to_fits for more details)
        directory (str): The directory to watch.
        file_extension (str): The file extension to watch for.
        
        For pixel_size, downscale_factor, output_file_path: see convert_raw_to_fits for more details.

    Side Effects:
        - Starts an infinite loop that watches for new files in the specified directory.
        - Automatically converts new files with the specified extension using the convert_raw_to_fits function.
        - The converted files are saved in the same directory.
        - This function will continue to run and monitor the directory until the program is manually stopped.
    """
    event_handler = FileHandler(file_extension, pixel_size, downscale_factor, output_file_path)
    observer = Observer()
    observer.schedule(event_handler, path=directory, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Watch a directory for new files with a specific extension and convert them.')
    parser.add_argument('--directory', default='.', help='Directory to watch. Defaut = "."')
    parser.add_argument('--file_extension', default='.ORF', help='File extension to watch for. Default = ".ORF"')
    parser.add_argument('--pixel_size', default=3.75, type=float, help='Set the PIXSIZE1 header of the converted FITS file to this value. Default = 3.75')
    parser.add_argument('--downscale_factor', default=4, type=int, help='The converted image will be shrunk by this factor in each dimension. Defaut = 4')
    parser.add_argument('--output_file_path', help='FITS file to write converted images to; will be overwritten with each conversion. If none is given, output is written to <input-file-basename>.fits. Default = None')
    args = parser.parse_args()

    watch_directory(args.directory, args.file_extension, args.pixel_size, args.downscale_factor, args.output_file_path)
