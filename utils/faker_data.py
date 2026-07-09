from faker import Faker
import csv
import os
import random

# Create Faker object
fake = Faker()

# Create generated_data folder if it doesn't exist
os.makedirs("generated_data", exist_ok=True)

# CSV File Path
CSV_FILE = "generated_data/candidates.csv"

# Subjects List
subjects = [
    "Python",
    "Java",
    "C++",
    "Data Structures",
    "Operating System",
    "Database Management",
    "Computer Networks",
    "Artificial Intelligence",
    "Machine Learning",
    "Web Development"
]

# Open CSV File
with open(CSV_FILE, mode="w", newline="") as file:

    writer = csv.writer(file)

    # Header Row
    writer.writerow([
        "Candidate ID",
        "Name",
        "Email",
        "Age",
        "Exam Subject"
    ])

    # Generate 20 Candidates
    for i in range(1, 21):

        candidate_id = f"C{i:03}"

        name = fake.name()

        email = fake.unique.email()

        age = random.randint(18, 30)

        subject = random.choice(subjects)

        writer.writerow([
            candidate_id,
            name,
            email,
            age,
            subject
        ])

print("20 Candidate Records Generated Successfully!")
print("File Saved At:", CSV_FILE)