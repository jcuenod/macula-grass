import os
import csv

GRASS_DIR = "grass"

def process_csvs(output_file):
	files = sorted([f for f in os.listdir(GRASS_DIR) if f.endswith(".csv")])
	sentence_id_map = {}
	clause_id_map = {}
	phrase_id_map = {}
	next_sentence_id = 1
	next_clause_id = 1
	next_phrase_id = 1
	all_rows = []
	header = None

	for filename in files:
		path = os.path.join(GRASS_DIR, filename)
		print(f"Processing {path}...")
		with open(path, newline='', encoding='utf-8') as csvfile:
			reader = csv.DictReader(csvfile)
			if header is None:
				header = reader.fieldnames
			for row in reader:
				# Sentence ID
				orig_sentence = row['sentence_id']
				if orig_sentence not in sentence_id_map:
					sentence_id_map[orig_sentence] = str(next_sentence_id)
					next_sentence_id += 1
				row['sentence_id'] = sentence_id_map[orig_sentence]
				# Clause ID
				orig_clause = row['clause_id']
				if orig_clause not in clause_id_map:
					clause_id_map[orig_clause] = str(next_clause_id)
					next_clause_id += 1
				row['clause_id'] = clause_id_map[orig_clause]
				# Phrase ID
				orig_phrase = row['phrase_id']
				if orig_phrase not in phrase_id_map:
					phrase_id_map[orig_phrase] = str(next_phrase_id)
					next_phrase_id += 1
				row['phrase_id'] = phrase_id_map[orig_phrase]
				all_rows.append(row)

	# Write output
	if header is None:
		# Fallback header if no files found
		header = ["sentence_id", "clause_id", "phrase_id", "word_id", "ref", "text", "lemma", "strong", "morph"]
	with open(output_file, 'w', newline='', encoding='utf-8') as outcsv:
		writer = csv.DictWriter(outcsv, fieldnames=header)
		writer.writeheader()
		for row in all_rows:
			writer.writerow(row)

if __name__ == "__main__":
	process_csvs("macula_grass.csv")
