import socket
import threading
import random
import string
import logging
import xml.etree.ElementTree as ET

logging.basicConfig(filename='errors.log', level=logging.ERROR)

BUFFER_SIZE = 10
buffer = []
buffer_lock = threading.Lock()
buffer_full = threading.Semaphore(0)
buffer_empty = threading.Semaphore(BUFFER_SIZE)

class ITStudent:
    def __init__(self, student_name, student_id, programme, courses, marks):
        # Initialize the ITStudent object with the given student information
        self.student_name = student_name
        self.student_id = student_id
        self.programme = programme
        self.courses = courses
        self.marks = marks

def handle_client(client_socket, address):
    #Function that handles the client connection. It receives requests from the client,
    #performs different operations based on the request, and sends back responses.

    while True:
        # Receive the request from the client
        request = client_socket.recv(5120).decode()

        # Process the request based on its value
        if request == "generate":
            try:
                # Generate a random student and save it as an XML file
                student = generate_random_student()
                file_name = f"student{random.randint(1, 10)}.xml"
                xml_data = generate_xml_data(student)
                save_xml_file(file_name, xml_data)
                client_socket.send(f"Student file: {file_name} has been generated successfully".encode())
                
                # Acquire the buffer lock and add the file name to the buffer
                buffer_empty.acquire()
                buffer_lock.acquire()
                buffer.append(file_name)
                buffer_lock.release()
                buffer_full.release()


            except Exception as e:
                logging.error(f"Exception in producer thread: {e}")

        elif request == "process":
            try:
                # Acquire the buffer lock and process the next file in the buffer
                buffer_full.acquire()
                buffer_lock.acquire()
                file_name = buffer.pop(0)
                buffer_lock.release()
                buffer_empty.release()

                 # Read the XML file, parse the data, and perform calculations
                xml_data = read_xml_file(file_name)
                student = parse_xml_data(xml_data)
                calculate_average_mark(student)
                info = get_student_info(student)

                # Send the student information to the client
                client_socket.send(info.encode())

                # Delete the XML file
                delete_xml_file(file_name)

            except Exception as e:
                logging.error(f"Exception in consumer thread: {e}")


        elif request == "exit":
            break


    client_socket.close()

def generate_random_student():
    # Generate a random student name from a list of names
    student_name = ''.join(random.choice(['Parrish Kehlani','Kim Soo Hyun','Hero Fiennes Tiffin','Cole Sprouse','Ahn Hyo Seop','Kim Min Kyu','Micheal Behling','Corey Mylchreest','Daniel Ezra','Zade Meadows']))
    # Generate a random student ID consisting of 9 digits
    student_id = ''.join(random.choices(string.digits, k=9))
    # Generate a random programme from a list of programmes
    programme = random.choice(['Computer Science', 'Information Technology', 'Software Engineering','Computer Engineering'])
    # Generate a random list of courses from a list of course options
    courses = random.choices(['Intergrative Programming', 'Computer Security', 'Database Design', 'Web Development','Entrepreneurship and Innovation','Information Technology','Data Mining'], k=5)
    # Generate a random list of marks for the courses
    marks = random.choices(range(0, 100),k=5)
    # Create and return an ITStudent object with the generated student information
    return ITStudent(student_name, student_id, programme, courses, marks)
    

def generate_xml_data(student):
    # Create the root element of the XML tree with the tag "Student"
    root = ET.Element("Student")
    # Create sub-elements for the student's name, ID, and programme
    name_element = ET.SubElement(root, "Name")
    name_element.text = student.student_name
    id_element = ET.SubElement(root, "ID")
    id_element.text = student.student_id
    programme_element = ET.SubElement(root, "Programme")
    programme_element.text = student.programme
    # Create a sub-element for the student's courses
    courses_element = ET.SubElement(root, "Courses")
    
    for i, course in enumerate(student.courses):
        # Create a sub-element for each course
        course_element = ET.SubElement(courses_element, "Course")
        # Set the "name" attribute of the course element to the course name
        course_element.set("name", course)
         # Create a sub-element for the mark of the course
        mark_element = ET.SubElement(course_element, "Mark")
        # Set the text of the mark element to the corresponding mark from the student's marks list
        mark_element.text = str(student.marks[i])

    # Converts the XML tree to a string with the unicode encoding    
    return ET.tostring(root, encoding= 'unicode')
    

def save_xml_file(file_name, xml_data):
    try:
         # Opens the specified file in write mode
        with open(file_name, 'w') as file:
            # Writes XML data to the file
            file.write(xml_data)
    except Exception as e:
         # Handle the specific exception or log the error
            logging.error(f"Exception in saving XML file: {e}")
            

def read_xml_file(file_name):
    # Opens the  specified file in read mode
    with open(file_name, 'r') as file:
        # Read the contents of the file and return them
        return file.read()
 

def parse_xml_data(xml_data):
    try: 
        # Parse the XML data and get the root element
        root = ET.fromstring(xml_data)

        # Extract student details from the XML
        student_name = root.find("Name").text
        student_id = root.find("ID").text
        programme = root.find("Programme").text

        # Initialize empty lists for enrolled courses and enrolled course marks
        courses = []
        marks = []

        for course_element in root.find("Courses"):
            # Extract course name and mark from each course element
            course_name = course_element.get("name")
            mark = int(course_element.find("Mark").text)

            # Append course name and mark to the respective lists
            courses.append(course_name)
            marks.append(mark)

        # Create a new ITStudent object with the extracted information
        return ITStudent(student_name, student_id, programme, courses, marks)
    except Exception as e:
      #Handle the specifc exception or log the error
      logging.error(f"Exception in parsing XML data: {e}")
      return None


def calculate_average_mark(student):
    try:
         # Calculate the students average mark by summing all their course marks and dividing by the number of courses they have enrolled for
        average_mark = sum(student.marks) / len(student.marks)
        student.average_mark = average_mark
    except ZeroDivisionError:
         #Handle the exception or log the error 
         print("ZeroDivisionError: No marks found for the student")    

def delete_xml_file(file_name):
 # removes the generated xml files from the file system they are stored in using the os module
    try:
          import os #imports the os module for operating system related functions
          os.remove(file_name) # removes the specified file from the file system
    except Exception as e:
         # logs the error
            logging.error(f"Exception in deleting XML file: {e}")

def get_student_info(student):
    info = ""
    info += f"Name: {student.student_name}\n"
    info += f"Student ID: {student.student_id}\n"
    info += f"Programme: {student.programme}\n"
    info += "Courses and Marks:\n"
    for i, course in enumerate(student.courses):
        info += f"  {course}: {student.marks[i]}\n"
    info += f"Average Mark: {student.average_mark}\n"
    info += f"Pass/Fail: {'Pass' if student.average_mark >= 50 else 'Fail'}\n"
    return info


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8080))
    server_socket.listen(5)

    while True:
        client_socket, address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()

if __name__ == '__main__':
    main()