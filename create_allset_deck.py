import csv
import json
import re
from pathlib import Path, PurePath

from src import Utils
from src.Mp3Creator import Mp3Creator

"""
Rows look like this:
['我喜欢也。', 'Wǒ xǐhuan yě.', 'I like it too.', '', 'invalid', 'The "also" adverb "ye"', 'Subj. + 也 + Verb / [Verb Phrase]', 'https://resources.allsetlearning.com/chinese/grammar/ASGG25MD']
"""


def normalizeText(sentence: str):
    return re.sub("&lt;.*?&gt;", " ", sentence)


newDeckName = "allset"
compiledDeckDir = Path('./compiled_decks').joinpath(newDeckName)
compiledDeckMp3Dir = compiledDeckDir.joinpath("mp3")
newDeckCsvPath = compiledDeckDir.joinpath(f"{newDeckName}.csv")
originalDeckPath = Path('./original_decks/allset.csv')
rows = []
repeaterCards = []  # for that player thingy
sentenceCells = []  # for the sentences HTML
index = 0
synth = Mp3Creator()

if not Path(compiledDeckDir).exists():
    Path(compiledDeckDir).mkdir(parents=True)
if not Path(compiledDeckMp3Dir).exists():
    Path(compiledDeckMp3Dir).mkdir(parents=True)

with open(originalDeckPath, 'r') as csvfile:
    csvreader = csv.reader(csvfile, delimiter='\t')

    for row in csvreader:
        if 'invalid' in row[4]:
            print(f"Skipping because 'invalid': {row}")
            continue
        if row[0].strip() == "":
            print(f"Skipping because 'no sentence': {row}")
            continue
        if row[1].strip() == "":
            print(f"Skipping because 'no pinyin': {row}")
            continue
        if row[2].strip() == "":
            print(f"Skipping because 'no translation': {row}")
            continue

        synth.create(normalizeText(row[0].strip()), compiledDeckMp3Dir)

        notes = [f"- {row[2]}"]
        if row[3].strip() != "":
            notes.append(f"- {row[3]}")
        if row[5].strip() != "":
            notes.append(f"- {row[5]}")
        if row[6].strip() != "":
            notes.append(f"- {row[6]}")

        rows.append({
            "sentence": normalizeText(f"<ruby>{row[0]}<rt>{row[1]}</rt></ruby>"),
            "display": "",
            "notes": normalizeText("<br>".join(notes).replace("&lt;.*&gt;", " ")),
            "source": f"<a href='{row[7]}'>src</a>",
            "mp3": f"[sound:{Path(f'{newDeckName}/mp3').joinpath(synth.createFileName(normalizeText(row[0])))}]",
            "data": "{}"
        })

        repeaterCards.append({
            "index": index,
            "japanese": normalizeText(row[0]),
            "english": row[2],
            "fileName": synth.createFileName(normalizeText(row[0]))
        })
        index += 1

        sentenceCell = normalizeText(f"<ruby>{row[0]}<rt>{row[1]}</rt></ruby>")
        sentenceCells.append(f"""
          <tr>
            <td class="big">{sentenceCell}</td>
            <td class="small">{row[2]}</td>
            <td class="small"><a href='{row[7]}'>src</a></td>
          </tr>
        """)

# Anki CSV
with open(newDeckCsvPath, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter='\t')

    for row in rows:
        writer.writerow([row['sentence'], row['display'], row['notes'], row['source'], row['mp3'], row['data']])

    print(f"Total written rows: {len(rows)}")

# Repeater JSON
outputJson = f"var sentences = {json.dumps(repeaterCards, ensure_ascii=False)}"
outputFile = compiledDeckDir.joinpath('meknow-data.js')
Utils.writeToFile(outputFile, outputJson, f"Failed to write {outputFile}")

# Sentences HTML
html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AllSet</title>
</head>
<style>
  body {
    font-family: "DejaVu Sans";
  }
  table {
    min-width: 800px;
    border-spacing: 0;
  }
  td {
    border: 1px #ccc solid;
    padding: 5px;
  }
  .big {
      font-size: 1.4em;
  }
  .small {
      font-size: 1em;
  }
</style>
<body>

<table>
  ###CELLS###
</table>

</body>
</html>
"""
html = html.replace('###CELLS###', "".join(sentenceCells))
outputFile = compiledDeckDir.joinpath('sentences.html')
Utils.writeToFile(outputFile, html, f"Failed to write {outputFile}")

