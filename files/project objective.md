Project Objective:
We’re creating a lightweight web app that runs locally on your machine. Users will be able to input a request and multiple file paths, specify a current problem, and designate files for current bug and solution outputs. Once the info is submitted, the app gathers file contents, crafts a custom prompt for the OpenAI assistant, and processes the response to update local files and display a formatted popup. This tool is built with a Flask backend and a modern frontend (think React/HTML with Bootstrap/Tailwind for that slick vibe), ensuring smooth local execution without any cloud dependencies.

Module 1: User Interface (Frontend)

Description:
This module handles everything the user sees and interacts with. It's all about creating a clean, intuitive space where inputs are collected and feedback is provided.

Components & Details:

Input Fields:

Request: A mandatory field for the user’s core input.
Dynamic File Paths: A plus button allows the user to add up to 10 file paths. Each new file path is added as a new tab/field.
Current Problem: A mandatory field where users specify the problem they’re trying to solve.
Current Bug File Path & Solution File Path: Mandatory fields to set where the output data will be written.
Buttons & Interactions:

Plus Button: Dynamically adds new file path fields.
Submit Button: Gathers all input data and sends it to the backend for processing.
Popup Window: Once processing is done, a popup displays the generated prompt with a “copy” button and an “accept” button to close it.
UX Enhancements:

Loading indicators to show API call progress.
Validation ensuring all required fields are filled before submission.
A polished, responsive design for ease-of-use.
Module 2: Backend API Handling

Description:
This is the brains of the operation, connecting the frontend with the OpenAI API and managing data flows.

Steps & Details:

Data Reception:

Receive the form data (request, file paths, problem details) from the frontend.
File Content Extraction:

Read contents from the user-specified file paths.
Format these contents into a coherent prompt.
API Interaction:

Construct the API prompt in the following structure:
vbnet
Copy
here is what Im doing
<Request>
file 1: <content from file path 1>
file 2: <content from file path 2>
...
This is what my current problem:
<current problem to solve:>
Send the prompt to the OpenAI assistant (ID: asst_gpMZde0cPZgU0AOSgUZhVcZz).
Response Handling:

Capture the API response.
Parse the response using regex to extract sections with headers like ###Solution:, ###Prompt:, and ###Currentbug:.
Response Delivery:

Package the parsed content and send it back to the frontend for display and further processing.
Module 3: File Handling & Processing

Description:
This module takes care of reading from and writing to local files based on user input and API response.

Steps & Details:

File Reading:

For each file path provided, open and read the file’s content.
Data Parsing:

Use regex to detect and extract content under the headers:
###Solution:
###Prompt:
###Currentbug:
Ensure each section’s text is accurately captured.
File Writing:

Update the files using the extracted content:
Solution File: Write the content corresponding to ###Solution: into the file located at the user-specified solution file path.
Current Bug File: Write the content corresponding to ###Currentbug: into the file located at the user-specified current bug file path.
Popup Interaction:

The ###Prompt: content is shown in a popup on the frontend. This popup includes a copy button for quick clipboard copying and an accept button to close the popup.
Module 4: Web App Deployment & Local Execution

Description:
Ensuring that our app runs locally, yet feels robust and web-like.

Steps & Details:

Backend:
Use a lightweight Flask framework in Python to serve API endpoints.
Frontend:
Serve a React or plain HTML/CSS/JS interface, making sure it’s smooth and responsive.
Local File Operations:
Ensure file read/write operations are performed locally without relying on any cloud services.
Deployment:
Package the app so it can be run on a local machine (using something like a virtual environment or Docker if needed) to maintain independence from external dependencies.
Module 5: UI Enhancements & User Experience

Description:
Polish the app to ensure that it’s not only functional but also user-friendly and visually appealing.

Steps & Details:

Dynamic Tab Additions:
Allow users to add or remove file path tabs dynamically up to a maximum of 10.
Visual Feedback:
Loading indicators to signal API processing.
Clear error messages for form validations (e.g., mandatory fields not filled).
Design:
Use a CSS framework (like Bootstrap or Tailwind CSS) for a modern, clean look.
Responsive design so the app works well on different screen sizes.
User Guidance:
Tooltips or small inline instructions to help guide the user through the input process.
Interactive Popup:
A well-designed popup that shows the final prompt, with intuitive controls (copy and accept).