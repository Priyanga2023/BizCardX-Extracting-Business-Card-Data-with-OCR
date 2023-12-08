# BizCardX: Extracting Business Card Data with OCR

## Overview
BizCardX is a powerful yet user-friendly tool designed to streamline the process of managing business card information. Leveraging Optical Character Recognition (OCR) and a sleek Streamlit graphical user interface (GUI), the application allows users to effortlessly upload business card images and extract key details such as company name, cardholder name, designation, contact information, and geographical details.

## Key Features
- **EasyOCR Integration:** Utilizing the EasyOCR library for efficient and accurate text extraction from business card images.
- **Interactive Streamlit GUI:** A well-designed Streamlit interface for seamless image upload, data extraction, and management.
- **MySQL Database Integration:** Storing extracted information and corresponding business card images in a MySQL database for easy retrieval and management.

## How It Works
1. **Upload Business Card Image:** Users can upload a business card image through the intuitive Streamlit interface.
2. **Extract Information:** The application employs EasyOCR to extract relevant information from the uploaded image.
3. **Database Integration:** Extracted data is stored in a MySQL database, allowing users to manage and retrieve information efficiently.
4. **User-Friendly Management:** Users can add, read, update, and delete entries through the GUI, providing a comprehensive solution for business card data management.

## Problem Statement
Develop a Streamlit application that allows users to upload a business card image and extract relevant information using EasyOCR. Extracted information includes company name, cardholder name, designation, mobile number, email address, website URL, area, city, state, and pin code. The application should display information in the GUI and allow users to save data, read data, update data, and delete data in a database along with the business card image.

## Technologies Used
- **OCR**
- **Streamlit**
- **MySQL**
- **Data Extraction**

## Skills Required
- **Image processing**
- **OCR**
- **GUI development (Streamlit)**
- **Database management (MySQL)**

## Approach
Install Required Packages:
  Install Python, Streamlit, EasyOCR, and a database management system (MySQL).

### Design User Interface:

1.Create an intuitive Streamlit GUI for uploading business card images.
2.Utilize widgets like file uploader, buttons, and text boxes for an interactive interface.

### Implement Image Processing and OCR:

1.Use EasyOCR for extracting information from uploaded images.
2.Apply image processing techniques for enhancing image quality.

### Display Extracted Information:

Present extracted information in an organized manner using Streamlit widgets (tables, text boxes, labels).

### Implement Database Integration:

1.Use MySQL to store extracted information and business card images.
2.Use SQL queries for creating tables, inserting, updating, and deleting data.

### Test the Application:

1.Thoroughly test the application to ensure functionality.
2.Run the application locally using streamlit run app.py in the terminal.

## Results:
The final application will be a Streamlit tool allowing users to upload business card images, extract relevant information using EasyOCR, and store data in a database. The GUI will be intuitive, displaying information neatly. Users can easily manage data with features like adding, reading, updating, and deleting entries.

## Conclusion:
This project aims to provide an efficient solution for managing business card information. With a user-friendly interface and robust functionalities, BizCardX can be a valuable tool for businesses and individuals.

## Contribution Guidelines

Contributions to this project are highly encouraged. If you come across any challenges or have ideas for enhancements, we invite you to submit a pull request. Your input is valuable to us, and we appreciate your contributions.

## Contact Information

- **Email:** sec19ee048@sairamtap.edu.in
- **LinkedIn:** [www.linkedin.com/in/priyanga070302](https://www.linkedin.com/in/priyanga070302)

If you have any more questions or need further information, please don't hesitate to get in touch. We're here to help and answer any inquiries you may have.
