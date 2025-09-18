# Macula GNT to GRASS Converter

This project provides a set of Python scripts to convert the deeply nested, hierarchical XML of the [Macula Greek New Testament](https://github.com/Clear-Bible/macula-greek) syntax trees into a flat, query-friendly CSV format. I called it "grass" because where Macula data is a bunch of _trees_, this simplification makes it more akin to grass.

The final output is a single, unified CSV file (`macula_grass.csv`) containing the entire New Testament, where each word is assigned a unique, sequential integer ID for its sentence, clause, and phrase-group, making it ideal for less complex queries (especially if you're familiar with the [BHSA data](https://etcbc.github.io/bhsa/)).

## The Problem

The Macula GNT data is an incredibly rich resource for detailed syntactic analysis. However, its XML structure, while precise, is difficult to use for answering straightforward linguistic questions, such as:

-   "Find all clauses that contain the preposition *ἐν* and the verb *λέγω*."
-   "Show me all the subjects of the verb *ποιέω*."
-   "Analyze the co-occurrence of specific words within a single clausal unit."

Performing these queries on the raw XML requires complex tree-traversal code, making simple data exploration a significant programming challenge.

## The Solution: The "Grass" Format

This project solves the problem by "flattening" the syntax tree into a simple, tabular format. It processes the XML and assigns each word three crucial identifiers:

1.  **`sentence_id`**: A unique ID for each sentence.
2.  **`clause_id`**: A unique ID for each clause.
3.  **`phrase_id`**: A unique ID for each major **functional constituent** of a clause (e.g., the entire subject phrase, the verb phrase, an adverbial phrase).

This structure clusters words into meaningful units, making the data behave much more like the BHSA dataset and enabling powerful, simple queries. It should be noted, however, that syntax is actually far more hierarchical and this represents an oversimplification for the sake of usability.

### Key Features

-   **Flattens Hierarchical XML:** Converts complex trees into a simple, row-per-word CSV.
-   **Preserves Word Order:** The output CSV maintains the exact word order of the original Greek text.
-   **Intelligent Clause Grouping:** It identifies the main functional parts of a clause and groups them under a shared `phrase_id`.
-   **Fixes Broken Clauses:** It intelligently re-assigns clause-linking conjunctions (like `καί` and `δέ`) to the clause they logically introduce, ensuring clausal units are continuous and not broken.
-   **Unified Dataset:** Processes all individual book XMLs and combines them into a single, analysis-ready CSV for the entire New Testament.

## Installation

1.  **Python:** Requires Python 3.6 or newer.

2.  **Libraries:** Install the necessary Python libraries using pip. The one I needed was `natsort`:

```bash
pip install pandas natsort
```

3.  **Macula Data:** Download or clone the Macula Greek New Testament data. This script assumes the SBLGNT XML files are located in a directory structure like `../macula-greek/SBLGNT/nodes/`.

## Usage

### 1. File Structure

Before running, ensure your directory structure looks like this:

```
project_root/
├── main.py               # The main processing script
├── process_csvs.py       # The script to unify CSVs (or included in main.py)

### 2. Execution

Run the main script from your terminal. Pass the path to all the XML files as an argument. The wildcard `*` is the easiest way to do this.

```bash
python main.py "/path/to/macula-greek/SBLGNT/nodes/*"
```

### 3. Workflow Explained

When you run the command, the following process occurs:

1.  **Intermediate Directory:** The script first creates a directory named `grass/`.
2.  **Book-by-Book Processing:** `main.py` iterates through each XML file (Matthew, Mark, etc.). For each book, it performs the flattening and clause-correction logic and saves a corresponding CSV file (e.g., `40-MAT.csv`) in the `grass/` directory.
3.  **Automatic Unification:** After all XML files have been processed, the script automatically calls the `process_csvs` function.
4.  **ID Renumbering & Final Output:** This function reads all the individual CSV files from the `grass/` directory, combines them in biblical order, replaces the original unit IDs with clean, sequential integer IDs, and writes the final, complete dataset to **`macula_grass.csv`** in the root of your project folder.

## Output Format

The final `macula_grass.csv` file will contain the following columns:

| Column        | Description                                                                                              |
|---------------|----------------------------------------------------------------------------------------------------------|
| `sentence_id` | A unique integer ID for each sentence.                                                                   |
| `clause_id`   | A unique integer ID for each clause. Words in the same clause share this ID.                             |
| `phrase_id`    | A unique integer ID for each major functional part of a clause (e.g., the subject, the object, etc.).    |
| `word_id`     | The original `xml:id` from the Macula data (e.g., `n40001001001`).                                       |
| `ref`         | The precise biblical reference for the word (e.g., `MAT 1:1!1`).                                         |
| `text`        | The Greek word as it appears in the text.                                                                |
| `lemma`       | The dictionary lemma of the Greek word.                                                                  |
| `gloss`       | The English gloss of the word's lemma.                                                                   |
| `strong`      | The Strong's number for the word's lemma.                                                                |
| `morph`       | The detailed morphological code (e.g., `N-NSM`, `V-AAI-3S`).                                             |


# License

## Code: MIT License

The code in this repository is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Data: CC BY 4.0

The data in this repository is licensed under the [Creative Commons Attribution 4.0 International (CC BY 4.0) License](http://creativecommons.org/licenses/by/4.0/). It is wholly derived from the [Macula Greek Linguistic Datasets](https://github.com/Clear-Bible/macula-greek/), which is also licensed under CC BY 4.0.

This is a human-readable summary of (and not a substitute for) the [license](http://creativecommons.org/licenses/by/4.0/).

### You are free to:

 * **Share** — copy and redistribute the material in any medium or format
 * **Adapt** — remix, transform, and build upon the material
for any purpose, even commercially.

The licensor cannot revoke these freedoms as long as you follow the license terms.

### Under the following terms:

 * **Attribution** — You must attribute the work as follows: "MACULA Greek Linguistic Datasets, available at https://github.com/Clear-Bible/macula-greek/". You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.

**No additional restrictions** — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.
