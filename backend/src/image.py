import base64
import os
from pathlib import Path

from .errors import AccessError


# The folder of which all uploads from the frontend are stored
upload_folder = os.path.dirname(os.getcwd()) + '/frontend' + '/src' + '/images' + '/upload'


## Clear Folder ################################################################


def clear_user_images_uploads():
    """
    Clears the upload folder in frontend/src/images when called. Ignores the
    AAA.jpg file (must have at least one file in a folder for git sync).

    Parameters:
        None
    Returns:
        None
    """

    cleared_successfully = False

    for file in os.scandir(upload_folder):
        if Path(file).name != "AAA.jpg":
            os.remove(file.path)
            cleared_successfully = True

    return cleared_successfully


## Decode For Storage From The Frontend ########################################


def decode_data_url(data_url):
    """
    Given a base64 data URL from the frontend, decode and return the header and
    the payload.

    Parameters:
        <data_url>
            The data URL (expecting a string not a byte object).
    Returns:
        The header (content type) and the image (string).
    """

    # Split the data URL to get the content type and base64-encoded data
    content_type, encoded_data = data_url.split(",", 1)

    # Decode the Base64 data
    image_data = base64.b64decode(encoded_data)

    return content_type, image_data


def write_to_file(image_name, image_data):
    """
    Given an image file name and image data, write this combination into the 
    root > frontend > src > images > upload folder.

    Parameters:
        <image_name>
            The name that the file will be called (including its extension).
        <image_data>
            The raw image data.
    Exceptions:
        AccessError:
        - If for some reason the file cannot be written.
    Returns:
        True if the file is written successfully.
    """

    try:
        with open(upload_folder + "/" + image_name, "wb") as f:
            f.write(image_data)
            return True
    except:
        raise AccessError(description = "Error: cannot write image to file.")


def store_image_locally(image_type, event_id, incoming_image_data):
    """
    Converts an incoming image from the frontend (expecting a base64 string) and
    stores it locally into the correct local storage. The file name will be a
    combination of image type and the event ID. The image type is determined
    by one of the following (only):

    An image for an event will start with "event".
    An image for an event's seating plan will start with "seating".

    e.g. event1.jpg
         seating1.jpg

    Will save with the same image type as the original upload.

    Parameters:
        <image_type>
            A string matching of the types listed above, exactly.
        <event_id>
            The event ID that this image is associated with.
        <incoming_image_data>
            The base64 data URL data from the frontend (no prior conversion
            needed).
    Returns:
        A string of the name of the image.
    """

    # If there is no image
    if incoming_image_data == "":
        return incoming_image_data

    # Extract the content type and image data from the URL
    content_type, image_data = decode_data_url(incoming_image_data)

    # Debug: Writes the whole base64 data URL to a text file
    # with open(upload_folder + "/" + "temp.txt", "w") as f:
    #     f.write(incoming_image_data)

    # Get the image extension
    extension = get_image_type(content_type)

    # Combine image name with extension
    image_filename = image_type + event_id + extension

    # Write to file
    write_to_file(image_filename, image_data)

    return image_filename


## Encode For Display In The Frontend ##########################################


def encode_to_base64(image_filename):
    """
    Given a local image filename, convert it to a base64 data URL, ready to be
    sent to the frontend.

    Parameters:
        <image_filename>
            The name of the image locally (e.g. event1.jpeg).
    Returns:
        If a valid image exists, the base64 data URL as a string. Else, an
        empty string.
    """

    # If there is no image
    if image_filename == "":
        return image_filename

    # If it has not been converted already (first word of header is "data")
    if image_filename[0] != "d":
        data_url = ""

        with open(upload_folder + "/" + image_filename, "rb") as image_file:
            # Read the binary data from the image file
            binary_data = image_file.read()

            # Encode the binary data in Base64
            base64_data = base64.b64encode(binary_data).decode("utf-8")

            # Form the data URL by combining the content type and the base64 data
            # content_type = "image/jpeg"
            # Adjust this based on the actual image type
            content_type = "image/" + get_image_type(image_filename)

            data_url = f"data:{content_type};base64,{base64_data}"
    
        return data_url
    
    # Image has been converted already
    else:
        return image_filename


## Helper ######################################################################


def get_image_type(content_type):
    """
    Searches the header of the base64 data URL to find the image's file
    extension. (So far only works for the listed image types.)

    Parameters:
        <content_type>
            The header of the base64 data URL.
    Returns:
        The extension (with a prefix dot) as a string if successful, else
        returns an empty string.
    """

    if "jpeg" in content_type:
        return ".jpeg"

    if "jpg" in content_type:
        return ".jpg"

    if "png" in content_type:
        return ".png"

    if "bmp" in content_type:
        return ".bmp"

    if "gif" in content_type:
        return ".gif"

    return ""


if __name__ == '__main__':
    # clear_user_images_uploads()
    # print(os.path.dirname(os.getcwd()) + '/frontend' + '/src' + '/images' + '/upload')
    # store_image_locally('event', '1', image)
    # encode_to_base64(upload_folder + "/event1.jpeg")
    pass
