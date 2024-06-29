import re

# Function to process lines and filter relevant strings

def get_important_lines(lines):
    indexstart = 0
    for i in range(len(lines)):
        if lines[i].startswith("Detailed Syllabus: (unit wise)"):
            indexstart = i
            break
    indexstart += 5
    indexend = indexstart
    freq = 0
    for i in range(indexstart, len(lines)):
        if lines[i].startswith("Syllabus for Third Year B.Tech Program in Computer Engineering- Semester VI (Autonomous)") or lines[i].startswith("Books Recommended:") or lines[i].startswith(" Books Recommended:"):
            indexend = i
            freq += 1
            if freq == 2:
                break
    if indexend == indexstart:
        indexend = len(lines) - 1

    s_string = []
    for i in range(indexend - 1, indexstart - 1, -1):
        if lines[i].startswith("Syllabus for Third Year") or lines[i].startswith("(Academic Year"):
            continue
        s_string.append(lines[i])
    return s_string
def process_strings(input_list):
    output_list = []
    for line in input_list:
        parts = line.split(',')
        for part in parts:
            part = re.sub(r'[●,.]', '', part.strip())
            if part.isdigit() or re.match(r'^\d', part):
                continue
            if len(part) == 1 or "Uni" in part or "Description" in part:
                continue
            if "Duration" in part or "PIG-" in part or "Use of" in part:
                continue
            if re.search(r'[a-zA-Z0-9]', part):
                output_list.append(part)
    return output_list
