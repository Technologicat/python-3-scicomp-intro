with open("utf8_text_file.txt", "rt", encoding="utf-8") as f:
    lines = []
    for line in f:
        lines.append(line.strip())  # strip() removes leading and trailing whitespace

for i,s in enumerate(lines):
    print(i, s, sep=': ', end='\n')
