# ROV Vision

This repository contains all the image processing and autonomy code for the ROV

See the [Vision18-19](https://github.com/CWRUbotixROV/rov-vision/tree/Vision18-19) branch for last year's code

# General Directory Structure

- `root`
    - `Autonomy`
        - **Note:** Contains all the code to handle tasks that involve autonomy for the ROV.
    - `Documentation`
        - **Note:** Any reference materials that would be useful for using something in this repository.  These should likely be Markdown files unless there's a good reason not to do that.
        - `Resources`
            - **Note:** this folder should contain images or other resources linked by the documents at the root of the Documentation folder.
            - `Images`
    - `Vision`
        - **Note:** Contains all the static image processing code.  Each task should have it's own folder/module.  Any images used for testing should have their own sub-folder under the module folder

