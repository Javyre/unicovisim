import csv
import json
import os
from math import ceil

day_map = {
    'M': 0,
    'T': 1,
    'W': 2,
    'R': 3,
    'F': 4,
    'S': 5,
    'U': 6,
}

def convCSVtoJSON(csv_path, faculty, json_path):
    passed_counter = 0
    total_counter = 0
    classData = {}
    with open(csv_path, encoding='utf-8') as csvfile:
        csvRead = csv.DictReader(csvfile)
        credits = 0
        index = 0
        hours = 0

        for row in csvRead:
            subject = row['Subject']
            ctype = row['Type']
            # Valid Class row to analyse
            if ctype in ["Lecture", "Studio", "Seminar", "Field Course (GDEU)"]:
                # New subject --> Dump to JSON file
                if index != subject:
                    monkey = str(json_path) + str(index) + ".json"
                    with open(monkey, 'w') as outfile:
                        json.dump(classData, outfile, indent=4)
                    index = subject
                    classData = {}

                # Analyse Class data
                course_index = row['CRN']

                hours = 0
                credits = float(row['Credits'])

                classDict = {}
                classDict['CRN'] = course_index
                classDict['Subject'] = subject
                classDict['CourseNum'] = row['Course']
                classDict['Capacity'] = row['Capacity']
                # classDict['ActualCapacity'] = row['Actual']
                classDict['Credits'] = credits

                days = row['Days']
                times = row['Time']

                # Pass if data no good
                total_counter+=1
                if "TBA" in days or "TBA" in times:
                    passed_counter+=1
                    continue

                days = [day_map[x] for x in days]
                times = times.replace("-",'').replace(" ",'').replace("m","m ").split()
                start_times, end_times = [], []

                try:
                    counter = 0
                    for time in times:
                        h = int(''.join(time[0:2])) + (12 if ('p' in time and int(''.join(time[0:2])) != 12) else 0)
                        minutes = int(''.join(time[3:5]))
                        time = h*60 + minutes
                        if not counter%2:
                            start_times.append(time)
                        else:
                            end_times.append(time)
                            hours += time - start_times[-1]
                        counter+=1

                    if (len(start_times) < len(days)) and (len(start_times) == 1):
                        start_times = [start_times[0]] * len(days)
                        end_times = [end_times[0]] * len(days)

                    if not (len(days) == len(start_times) and len(days) == len(end_times)): # or (credits < ceil(hours/60)):
                        raise ValueError("Error at %s%s in %s with credits or length of stuff"%(subject, row['Course'], faculty))
                except:
                    print("Error at %s%s in %s"%(subject, row['Course'], faculty))
                    print("CRN : ", course_index)
                    print("Principal line")
                    passed_counter+=1
                    continue

                classDict['Days'] = days
                classDict['StartTimes'] = start_times
                classDict['EndTimes'] = end_times

                classData[course_index] = classDict

            elif ctype == '' and len(row['CRN']) == 0 and len(classData.keys()) != 0 and course_index in classData.keys():
                if credits <= ceil(hours/60):
                    continue

                # days = classData[course_index]['Days']
                # time = classData[course_index]['Time']
                days = row['Days']
                times = row['Time']
                # print(days)
                if "TBA" in days or "TBA" in times:
                    continue

                days = [day_map[x] for x in days]
                times = times.replace("-",'').replace(" ",'').replace("m","m ").split()
                # print(times)
                start_times, end_times = [], []
                try:
                    counter = 0
                    for time in times:
                        h = int(''.join(time[0:2])) + (12 if ('p' in time and int(''.join(time[0:2])) != 12) else 0)
                        minutes = int(''.join(time[3:5]))
                        time = h*60 + minutes
                        if not counter%2:
                            start_times.append(time)
                        else:
                            end_times.append(time)
                            hours += time - start_times[-1]
                        counter+=1

                    if (len(start_times) < len(days)) and (len(start_times) == 1):
                        start_times = [start_times[0]] * len(days)
                        end_times = [end_times[0]] * len(days)

                    if not (len(days) == len(start_times) and len(days) == len(end_times)):
                        raise ValueError("Error at %s%s in %s with credits or length of stuff"%(subject, row['Course'], faculty))
                except:
                    print("Error at %s%s in %s"%(subject, row['Course'], faculty))
                    print("CRN : ", course_index)
                    print("Non principal line")
                    continue

                if (days == classData[course_index]['Days']) and (start_times == classData[course_index]['StartTimes']):
                    continue

                if ceil(hours/60) <= credits and not (days == classData[course_index]['Days']) and (start_times == classData[course_index]['StartTimes']):
                    classData[course_index]['Days']+=days
                    classData[course_index]['StartTimes']+=start_times
                    classData[course_index]['EndTimes']+=end_times

    monkey = str(json_path) + str(index) + ".json"
    with open(monkey, 'w') as outfile:
        json.dump(classData, outfile, indent=4)
    print(passed_counter, " classes passed in ", faculty)
    print(total_counter, " total classes in ", faculty)

# csvFileName = r'./Faculties/Arts.csv'
# convCSVtoJSON(csvFileName, "Arts", "./Courses/Arts/")

def convAll(csv_dir, json_dir):

    for filename in os.listdir(csv_dir):
        faculty = filename.split('.')[0]
        # create directory if not exists
        if not os.path.exists(json_dir + faculty):
            print("Directory created for ", faculty)
            os.makedirs(json_dir + faculty)

        convCSVtoJSON(csv_dir + filename, faculty, json_dir + faculty + "/")
        print("JSON done for ", faculty)

convAll("./Faculties/", "./Courses/")
