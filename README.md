# ROV Vision

This repository contains all the image processing and autonomy code for the ROV

See the [Vision18-19](https://github.com/CWRUbotixROV/rov-vision/tree/Vision18-19) branch for old code

# General Directory Structure

- `root`
    - `autonomy`
        - **Note:** Contains all the code to handle tasks that involve autonomy for the ROV.
    - `documentation`
        - **Note:** Any reference materials that would be useful for using something in this repository.  These should likely be Markdown files unless there's a good reason not to do that.
    - `images`
        - **Note:** Contains all images used for testing vision code. Use separate folders for different datasets.
    - `vision`
        - **Note:** Contains all the static image processing code.  Each task should have it's own folder/module. See [this](documentation/vision.md) for documentation.

