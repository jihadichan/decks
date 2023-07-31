import csv
import re
from pathlib import Path, PurePath

"""
Rows look like this:
['我喜欢也。', 'Wǒ xǐhuan yě.', 'I like it too.', '', 'invalid', 'The "also" adverb "ye"', 'Subj. + 也 + Verb / [Verb Phrase]', 'https://resources.allsetlearning.com/chinese/grammar/ASGG25MD']
"""

newDeckName = "allset"
compiledDeckDir = PurePath('./compiled_decks').joinpath(newDeckName)
newDeckPath = compiledDeckDir.joinpath(f"{newDeckName}.csv")
originalDeckPath = PurePath('./original_decks/allset.csv')
rows = []

if not Path(compiledDeckDir).exists():
    Path(compiledDeckDir).mkdir(parents=True)

with open(originalDeckPath, 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter='\t')

    for row in csvreader:
        if 'invalid' in row[4]:
            print(f"Skipping because 'invalid': {row}")
            continue
        if row[1].strip() == "":
            print(f"Skipping because 'no pinyin': {row}")
            continue
        if row[2].strip() == "":
            print(f"Skipping because 'no translation': {row}")
            continue

        notes = [f"- {row[2]}"]
        if row[3].strip() != "":
            notes.append(f"- {row[3]}")
        if row[5].strip() != "":
            notes.append(f"- {row[5]}")
        if row[6].strip() != "":
            notes.append(f"- {row[6]}")

        rows.append({
            "sentence": re.sub("&lt;.*?&gt;", " ", f"<ruby>{row[0]}<rt>{row[1]}</rt></ruby>"),
            "display": "",
            "notes": re.sub("&lt;.*?&gt;", " ", "<br>".join(notes).replace("&lt;.*&gt;", " ")),
            "source": f"<a href='{row[7]}'>src</a>",
            "mp3": "",
            "data": "{}"
        })

with open(newDeckPath, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter='\t')

    for row in rows:
        writer.writerow([row['sentence'], row['display'], row['notes'], row['source'], row['mp3'], row['data']])

    print(f"Total written rows: {len(rows)}")
