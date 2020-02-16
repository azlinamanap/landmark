# LANDMARK

This app was developed for the final two-week project of the Next Academy Full Stack Web Development 10-week bootcamp. The theme given was **Education**, so our team decided to think out of the box and make an app with the lofty goal of *educating society*. In a nutshell, this app takes in a photo of a landmark and returns information about it.

### How it works

- Takes in a photo via upload on mobile
- Uploads the photo to Amazon S3 and stores the image in the server database
- Sends the photo to the Google Vision API for landmark detection and returns information about the landmark such as name, location and general info
- Stores the information into the server database
- Images are then viewable as posts with the associated information based on the name of the landmark

### Usage

A working version can be accessed [here](https://landmarkit.netlify.com/), however the functionality is currently incomplete as the Google API Keys have been taken down to prevent excess API calls and unnecessary charges.

