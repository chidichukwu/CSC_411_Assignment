import threading
import random
import string
import logging
import xml.etree.ElementTree as ET


#logger configuration
logging.basicConfig(filename='errors.log', level=logging.ERROR)


BUFFER_SIZE = 10
buffer = []
buffer_lock = threading.Lock()
buffer_full = threading.Semaphore(0)
buffer_empty = threading.Semaphore(BUFFER_SIZE)


class ITStudent:
    def __init__(self, student_name, student_id, programme, courses, marks):
        # Initializes the ITStudent object with the given student information
        self.student_name = student_name
        self.student_id = student_id
        self.programme = programme
        self.courses = courses
        self.marks = marks

def generate_random_student():
    # Generates a random student name from a list of names
    student_name = ''.join(random.choice(['Parrish Kehlani','Kim Soo Hyun','Hero Fiennes Tiffin','Cole Sprouse','Ahn Hyo Seop','Kim Min Kyu','Micheal Behling','Corey Mylchreest','Daniel Ezra','Zade Meadows']))
    # Generates a random student ID consisting of 9 digits
    student_id = ''.join(random.choices(string.digits, k=9))
    # Generates a random programme from a list of programmes
    programme = random.choice(['Computer Science', 'Information Technology', 'Software Engineering','Computer Engineering'])
    # Generates a random list of courses from a list of course options
    courses = random.choices(['Intergrative Programming', 'Computer Security', 'Database Design', 'Web Development','Entrepreneurship and Innovation','Information Technology','Data Mining'], k=5)
    # Generates a random list of marks for the courses
    marks = random.choices(range(0, 100),k=5)
    # Creates and returns an ITStudent object with the generated student information
    return ITStudent(student_name, student_id, programme, courses, marks)

def producer():
    #initializes the counter for student objects
    number_of_students=0
    while number_of_students < 10:
        try:
            # Generates a random student object
            student = generate_random_student()
            # Generates a random file name for the XML file
            file_name = f"student{random.randint(1, 10)}.xml"
            # Generates XML data from the student object
            xml_data = generate_xml_data(student)
            # Saves the XML file with the generated file name and XML data
            save_xml_file(file_name, xml_data)
            # Prints a success message indicating the file has been generated
            print(f"Student file: {file_name} has been generated successfully")
            # Acquires the buffer_empty semaphore to wait for space in the buffer
            buffer_empty.acquire()
            # Acquires the buffer_lock semaphore to access the buffer
            buffer_lock.acquire()
            # Appends the file name to the buffer
            buffer.append(file_name)
            # Releases the buffer_lock semaphore to allow other threads to access the buffer
            buffer_lock.release()
            # Releases the buffer_full semaphore to indicate that the buffer is no longer empty
            buffer_full.release()

            # Increments the count of generated students
            number_of_students += 1
             
        except Exception as e:
            # Logs the error
            logging.error(f"Exception in producer thread: {e}")  

        

def consumer():
    # Initializes a counter to keep track of the number of students processed
    number_of_students = 0
    # Continues processing students until 10 students have been processed
    while number_of_students < 10:
        try:
             # Acquires the buffer_full semaphore to check if the buffer is full
             buffer_full.acquire()
              # Acquires the buffer_lock to ensure exclusive access to the buffer
             buffer_lock.acquire()
             # Removes the file name from the beginning of the buffer
             file_name = buffer.pop(0)
             # Releases the buffer_lock to allow other threads to access the buffer
             buffer_lock.release()
             # Releases the buffer_empty semaphore to indicate that the buffer is no longer empty
             buffer_empty.release()
             # Reads the XML data from the file
             xml_data = read_xml_file(file_name)
             # Parses the XML data to create a student object
             student = parse_xml_data(xml_data)
             # Calculates the average mark of the student
             calculate_average_mark(student)
             # Prints the student information
             print_student_info(student)
             # Deletes the XML file
             delete_xml_file(file_name)
             # Increments the counter for the number of students processed
             number_of_students +=1
        except Exception as e:
            # logs the error
            logging.error(f"Exception in consumer thread: {e}")


def generate_xml_data(student):
    # Creates the root element of the XML tree with the tag "Student"
    root = ET.Element("Student")
    # Creates sub-elements for the student's name, ID, and programme
    name_element = ET.SubElement(root, "Name")
    name_element.text = student.student_name
    id_element = ET.SubElement(root, "ID")
    id_element.text = student.student_id
    programme_element = ET.SubElement(root, "Programme")
    programme_element.text = student.programme
    # Creates a sub-element for the student's courses
    courses_element = ET.SubElement(root, "Courses")
    
    for i, course in enumerate(student.courses):
        # Creates a sub-element for each course
        course_element = ET.SubElement(courses_element, "Course")
        # Sets the "name" attribute of the course element to the course name
        course_element.set("name", course)
         # Creates a sub-element for the mark of the course
        mark_element = ET.SubElement(course_element, "Mark")
        # Sets the text of the mark element to the corresponding mark from the student's marks list
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
         # logs the error
            logging.error(f"Exception in saving XML file: {e}")


def read_xml_file(file_name):
    # Opens the  specified file in read mode
    with open(file_name, 'r') as file:
        # Reads the contents of the file and return them
        return file.read()

def parse_xml_data(xml_data):
    try: 
        # Parses the XML data and get the root element
        root = ET.fromstring(xml_data)

        # Extracts student details from the XML
        student_name = root.find("Name").text
        student_id = root.find("ID").text
        programme = root.find("Programme").text

        # Initializes empty lists for enrolled courses and enrolled course marks
        courses = []
        marks = []

        for course_element in root.find("Courses"):
            # Extracts course name and mark from each course element
            course_name = course_element.get("name")
            mark = int(course_element.find("Mark").text)

            # Appends course name and mark to the respective lists
            courses.append(course_name)
            marks.append(mark)

        # Creates a new ITStudent object with the extracted information
        return ITStudent(student_name, student_id, programme, courses, marks)
    except Exception as e:
      #logs the error
      logging.error(f"Exception in parsing XML data: {e}")
      return None

def calculate_average_mark(student):
    try:
         # Calculates the student's average mark by summing all their course marks and dividing by the number of courses they have enrolled for
        average_mark = sum(student.marks) / len(student.marks)
        student.average_mark = average_mark
    except ZeroDivisionError:
         #logs the error 
         print("ZeroDivisionError: No marks found for the student")    


def print_student_info(student):
    #displays the student's information on the screen , this information includes the student's name, id, programme, courses they have enrolled for , the marks obtained for each enrolled course, average and finally their overall result
    print(f"Name: {student.student_name}")
    print(f"Student ID: {student.student_id}")
    print(f"Programme: {student.programme}")
    print("Courses and Marks:")
    for i, course in enumerate(student.courses):
                print(f"  {course}: {student.marks[i]}")
    print(f"Average Mark: {student.average_mark}")
    print(f"Pass/Fail: {'Pass' if student.average_mark >= 50 else 'Fail'}")
    print()

def delete_xml_file(file_name):
 # removes the generated xml files from the file system they are stored in using the os module
    try:
          import os #imports the os module for operating system related functions
          os.remove(file_name) # removes the specified file from the file system
    except Exception as e:
         # logs the error
            logging.error(f"Exception in deleting XML file: {e}")



 # Creates a new thread object named 'producer_thread' that will execute the 'producer' function       
producer_thread = threading.Thread(target=producer)

# Creates a new thread object named 'consumer_thread' that will execute the 'consumer' function
consumer_thread = threading.Thread(target=consumer)

# Starts the execution of the 'producer_thread' in parallel with the main thread        
producer_thread.start()

# Starts the execution of the 'consumer_thread' in parallel with the main thread
consumer_thread.start()
