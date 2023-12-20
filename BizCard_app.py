# Import necessary libraries
import easyocr  
import os
import mysql.connector  
import pandas as pd
import streamlit as st 
import tempfile
import re
from PIL import Image 

# Set Streamlit page configuration: title and layout
st.set_page_config(page_title="BizCardX", layout="wide", initial_sidebar_state="auto")

# Define a temporary directory to store uploaded images
UPLOADS_DIR = tempfile.mkdtemp()

# Initialize easyOCR reader for English language
reader = easyocr.Reader(['en'])

# Connect to MySQL database
mysqldb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123",
    port="3306",
    database="bizcard")
mycursor = mysqldb.cursor(buffered=True)

# Create BizCardX_Data table if not exists in the database
mycursor.execute("""CREATE TABLE IF NOT EXISTS BizCardX_Data (
                    company_name TEXT,
                    cardholder_name TEXT,
                    designation TEXT,
                    mobile_number VARCHAR(35),
                    email TEXT,
                    website TEXT,
                    area TEXT,
                    city TEXT,
                    state TEXT,
                    pincode VARCHAR(10),
                    image LONGBLOB)""")

# Function to handle image upload and data extraction
def upload():
    # File uploader widget for business card images
    uploaded_card = st.file_uploader("Upload a Business Card Image", type=["png", "jpeg", "jpg"])

    if uploaded_card is not None:
        # Function to save the uploaded image to the temporary directory
        def save_uploaded_image(uploaded_image):
            filename = os.path.join(UPLOADS_DIR, uploaded_card.name)
            with open(filename, 'wb') as file:
                file.write(uploaded_image.read())
        save_uploaded_image(uploaded_card)
        
        # Get the path to the uploaded image
        image_path = os.path.join(UPLOADS_DIR, uploaded_card.name)
        
        # Use easyOCR to extract text from the business card image
        results = reader.readtext(image_path)

        # Function to convert image data to binary format
        def image_to_binary(image):
            with open(image, 'rb') as file:
                binary_data = file.read()
                return binary_data
        
        # Prepare data dictionary for insertion into MySQL
        data = {
            "Company_Name": [],
            "Cardholder_Name": [],
            "Designation": [],
            "Mobile_Number": [],
            "Email": [],
            "Website": [],
            "Area": [],
            "City": [],
            "State": [],
            "Pincode": [],
            "image": image_to_binary(image_path)}

        # Function to organize extracted data into the data dictionary
        def define_data(results):
            for index, text in enumerate(results):
                # Extract different fields from the OCR results
                if index == len(results) - 1:
                    data["Company_Name"].append(text[1])
                elif index == 0:
                    data["Cardholder_Name"].append(text[1])
                elif index == 1:
                    data["Designation"].append(text[1])
                elif "-" in text[1] or "+" in text[1]:
                    data["Mobile_Number"].append(text[1])
                    if len(data["Mobile_Number"]) == 2:
                        data["Mobile_Number"] = " / ".join(data["Mobile_Number"])
                elif "@" in text[1] and ".com" in text[1]:
                    data["Email"].append(text[1])
                elif "www " in text[1].lower() or "www." in text[1].lower():
                    data["Website"].append(text[1])
                elif "WWW" in text[1]:
                    data["Website"].append(results[4][1] + "." + results[5][1])
                if re.findall('^[0-9].+, [a-zA-Z]+', text[1]):
                    data["Area"].append(text[1].split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+', text[1]):
                    data["Area"].append(text[1])
                match1 = re.findall('.+St , ([a-zA-Z]+).+', text[1])
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', text[1])
                match3 = re.findall('^[E].*', text[1])
                if match1:
                    data["City"].append(match1[0])
                elif match2:
                    data["City"].append(match2[0])
                elif match3:
                    data["City"].append(match3[0])
                state_match = re.findall('[a-zA-Z]{9} +[0-9]', text[1])
                if state_match:
                    data["State"].append(text[1][:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);', text[1]):
                    data["State"].append(text[1].split()[-1])
                if len(data["State"]) == 2:
                    data["State"].pop(0)
                if len(text[1]) >= 6 and text[1].isdigit():
                    data["Pincode"].append(text[1])
                elif re.findall('[a-zA-Z]{9} +[0-9]', text[1]):
                    data["Pincode"].append(text[1][10:])

        define_data(results)

        # Display the uploaded image and extracted text in two columns
        col1, col2 = st.columns(2)
        with col1:
            st.write("Displaying the Uploaded Business Card")
            uploaded_image = Image.open(image_path)
            st.image(uploaded_image, width=470)
            st.write("")
            
        with col2:
            text_list = [result[1] for result in results]
            st.write("Extracted Text from Business Card")
            st.write(text_list)
        
        # Display organized data in a DataFrame
        df = pd.DataFrame(data)
        st.write("Organized data from Extracted Text")
        st.write(df)
        
        # Button to insert data into MySQL database
        if st.button("Insert text to MySQL"):
            for i, row in df.iterrows():
                # Check if the data already exists in the database
                existing_query = "SELECT * FROM BizCardX_Data WHERE cardholder_name=%s"
                mycursor.execute(existing_query, (row['Cardholder_Name'],))
                existing_data = mycursor.fetchone()
                if existing_data:
                    st.warning(f"Data for {row['Cardholder_Name']} already exists in the database.")
                else:
                    # Insert the data into the database
                    insert_query = """INSERT INTO BizCardX_Data (company_name, cardholder_name, designation, mobile_number, email, website, area, city, state, pincode, image)
                             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    mycursor.execute(insert_query, tuple(row))
                    mysqldb.commit()
                    st.success(f"Inserted data for {row['Cardholder_Name']} to MySQL database successfully!")
    else:
        st.warning("Please upload an image")

# Function to handle modification of data in the database
def modify():
    # Query to get all cardholder names from the database
    mycursor.execute("SELECT cardholder_name FROM BizCardX_Data")
    results = mycursor.fetchall()
    business_cards = {}
    for row in results:
        business_cards[row[0]] = row[0]
    if not business_cards:
        st.warning("No Cardholder_Name available in the database.")
        return
    # Dropdown to select a cardholder name for modification
    selected_card = st.selectbox("Select a Cardholder_Name", list(business_cards.keys()))
    # Query to get details of the selected cardholder from the database
    mycursor.execute("SELECT company_name, cardholder_name, designation, mobile_number, email, website, area, city, state, pincode FROM BizCardX_Data WHERE cardholder_name=%s", (selected_card,))
    results = mycursor.fetchone()
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)
    
    # Input fields for user to update
    company_name = st.text_input("Company_Name", results[0])
    designation = st.text_input("Designation", results[2])
    email = st.text_input("Email", results[4])
    area = st.text_input("Area", results[6])
    state = st.text_input("State", results[8])
    cardholder_name = st.text_input("Cardholder_Name", results[1])
    mobile_number = st.text_input("Mobile_Number", results[3])
    website = st.text_input("Website", results[5])
    city = st.text_input("City", results[7])
    pincode = st.text_input("Pincode", results[9])

    st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)
    
    # Button to commit changes
    st.write("Click the 'Commit changes' button to update the changes made in the MySQL database.")
    if st.button("Commit changes"):
        # Update the information for the selected business card in the database
        mycursor.execute("""
            UPDATE BizCardX_Data
            SET company_name=%s, cardholder_name=%s, designation=%s, mobile_number=%s, email=%s, website=%s, area=%s, city=%s, state=%s, pincode=%s
            WHERE cardholder_name=%s
        """, (company_name, cardholder_name, designation, mobile_number, email, website, area, city, state, pincode, selected_card))
        mysqldb.commit()
        st.success("Modified text updated in the database successfully.")

    # Button to delete data
    st.write("Click the 'Delete' button if you wish to delete data from the MySQL database.")
    if st.button("Delete"):
        # Delete data for the selected cardholder name
        mycursor.execute(f"DELETE FROM BizCardX_Data WHERE cardholder_name='{selected_card}'")
        mysqldb.commit()
        st.success("Business card text data deleted from the database successfully.")

    # Button to view updated text
    st.write("Click the 'View updated text' button to view the updated text in the MySQL database.")
    if st.button("View updated text"):
        # Query to get all data from the BizCardX_Data table
        mycursor.execute("SELECT company_name, cardholder_name, designation, mobile_number, email, website, area, city, state, pincode FROM BizCardX_Data")
        # Create DataFrame with the updated data
        df = pd.DataFrame(mycursor.fetchall(), columns=["Company_Name", "Cardholder_Name", "Designation", "Mobile_Number", "Email", "Website", "Area", "City", "State", "Pincode"])
        st.write(df)

    st.markdown("<hr style='margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)

# Function to create the Streamlit dashboard
def dashboard_creation():
    st.markdown("<h3 style='text-align: center;'>BizCardX: Extracting Business Card Data with OCR</h3>", unsafe_allow_html=True)
    selected_process = st.selectbox("Select an Option", ["Upload & Extract", "Modify & Delete"])
    st.write(f'You have selected the option: {selected_process}')
    # Display content based on selected tab
    if selected_process == "Upload & Extract":
        upload()
    elif selected_process == "Modify & Delete":
        modify()
    
# Function to display information about the project
def display_BizCardX_overview():
    # Display project overview title
    st.markdown("<h3 style='text-align: center;'>Project Overview</h3>", unsafe_allow_html=True)
    # Display project details
    st.markdown("<h4>Title</h4>", unsafe_allow_html=True)
    st.markdown("BizCardX: Extracting Business Card Data with OCR")
    st.markdown("<h4>Objective</h4>", unsafe_allow_html=True)
    st.markdown("Develop a Streamlit application for uploading business card images, extracting relevant information using easyOCR, and storing data in a database.")
    # Display technologies used
    st.markdown("<h4>Technologies Used</h4>", unsafe_allow_html=True)
    st.write("- Python")
    st.write("- Streamlit")
    st.write("- easyOCR")
    st.write("- Database Management System (MySQL)")
    # Display domain
    st.markdown("<h4>Domain</h4>", unsafe_allow_html=True)
    st.write("Data Extraction, OCR (easyOCR), GUI Development, Database Management")
    # Display problem statement
    st.markdown("<h4>Problem Statement</h4>", unsafe_allow_html=True)
    st.write("Develop a Streamlit application that allows users to upload a business card image, extract relevant information using easyOCR, and store the extracted data along with the image in a database. The application should provide functionalities for reading, updating, and deleting data through the Streamlit GUI.")
    # Display information about easyOCR
    st.markdown("<h4>easyOCR</h4>", unsafe_allow_html=True)
    st.write("easyOCR is a Python library used for Optical Character Recognition (OCR) tasks. It plays a crucial role in this project by facilitating the extraction of text data from business card images. With easyOCR, the application achieves accurate and efficient information retrieval from uploaded images.")
    # Display approach
    st.markdown("<h4>Approach</h4>", unsafe_allow_html=True)
    st.write("*1. Install Required Packages*")
    st.write("- Install Python, Streamlit, easyOCR, and a chosen database management system (MySQL).")
    st.write("*2. Design User Interface*")
    st.write("- Create an intuitive UI with Streamlit using widgets like file uploader, buttons, and text boxes.")
    st.write("*3. Implement Image Processing and OCR with easyOCR*")
    st.write("- Utilize easyOCR for Optical Character Recognition to extract information from the uploaded business card image.")
    st.write("- Apply image processing techniques for quality enhancement.")
    st.write("*4. Display Extracted Information*")
    st.write("- Present the extracted information in a clean and organized manner in the Streamlit GUI.")
    st.write("- Use widgets like tables, text boxes, and labels for presentation.")
    st.write("*5. Database Integration*")
    st.write("- Use MySQL to store extracted information along with business card images.")
    st.write("- Implement SQL queries for table creation, data insertion, retrieval, updating, and deletion through the Streamlit UI.")
    st.write("*6. Test the Application*")
    st.write("- Thoroughly test the application to ensure expected functionality.")
    st.write("- Run the application locally using the 'streamlit run app.py' command.")
    st.write("*7. Continuous Improvement*")
    st.write("- Enhance the application by adding new features, optimizing code, fixing bugs, and adding security measures like user authentication and authorization.")
    # Display results
    st.markdown("<h4>Results</h4>", unsafe_allow_html=True)
    st.write("The project delivers a Streamlit application allowing users to upload business card images, extract information using easyOCR, and store data in a database. Extracted information includes company name, cardholder name, designation, mobile number, email address, website URL, area, city, state, and pincode.")
    st.write("Users can easily manage data through the Streamlit GUI, including reading, updating, and deleting entries.")
    st.write("The application provides a simple and intuitive interface, making it a useful tool for efficient business card information management.")
    # Display dataset link
    st.markdown("**Dataset Link:** [Data Link](https://drive.google.com/drive/folders/1FhLOdeeQ4Bfz48JAfHrU_VXvNTRgajhp)")
    st.markdown("*Note: For access to the dataset and additional information, please follow the provided hyperlink.*")

# Get user input for page selection
page = st.sidebar.selectbox("Select Page", ["About", "Dashboard", "Exit"])

# Main section to display different pages
def main():
    if page == "About":
        display_BizCardX_overview()
    elif page == "Dashboard":
        dashboard_creation()
    elif page == "Exit":
        st.subheader("Exit Application")
        st.markdown("Thank you for using the BizCardX: Extracting Business Card Data with OCR application.")
        st.markdown("If you wish to exit, simply close the browser tab or window.")
        st.markdown("Have a great day!")

# Call the main function to display the appropriate content based on the selected page
main()