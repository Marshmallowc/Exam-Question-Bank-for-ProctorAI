# Face Recognition and Question Bank Upload System

This system enables the upload of face images for recognition and the import of a question bank into a database. It integrates with a MySQL database and uses the `face_recognition` library for face encoding and recognition.

## Features
1. **Face Recognition:**
   - Upload face images, extract face encodings, and store them in the database.
   - The system uses `face_recognition` to process the images and create a unique encoding for each face.
   - The images are stored with the student’s name and number, which are extracted from the image file name.

2. **Question Bank Upload:**
   - Import a question bank (Excel file) containing various types of questions (multiple choice, fill-in-the-blank, short answer, etc.).
   - The questions are parsed and stored in the database with associated metadata like difficulty, score, and knowledge points.
   - The question content is stored in JSON format in the database.

## Installation

To get started with this system, follow these steps:

### Requirements
- Python 3.10
- MySQL database
- Required Python libraries:
  - `mysql-connector-python`
  - `pandas`
  - `face_recognition`
  - `Pillow`
  - `numpy`
  - `opencv-python`
  - `tkinter` (for the GUI)

### Install Dependencies

You can install the required Python libraries using `pip`:

```bash
pip install mysql-connector-python pandas face_recognition Pillow numpy opencv-python
