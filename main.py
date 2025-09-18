import argparse
from glob import glob
import os
import xml.etree.ElementTree as ET
import pandas as pd
import sys
from process_csvs import process_csvs

# Ensure you have natsort installed: pip install natsort
from natsort import natsorted

def flatten_macula_xml(xml_data: str) -> pd.DataFrame:
    """
    Parses Macula GNT XML data to produce a flattened, duplicate-free DataFrame.
    It corrects for "broken clauses" by re-assigning clause-linking conjunctions
    to the clause they introduce. The final output is sorted by biblical text order.

    Args:
        xml_data: A string containing the Macula XML data.

    Returns:
        A pandas DataFrame with the flattened syntactic information.
    """
    all_words_data = []

    def _traverse_and_collect_words(node, sentence_id, active_clause_id, active_phrase_id):
        """
        Recursively performs a single top-down traversal of the tree, collecting
        word data and propagating the correct IDs.
        """
        current_cat = node.get('Cat', '').lower()
        
        is_word_node = (node.text and node.text.strip()) and not node.findall('Node')
        if is_word_node:
            word_info = {
                'sentence_id': sentence_id,
                'clause_id': active_clause_id,
                'phrase_id': active_phrase_id,
                'word_id': node.get('{http://www.w3.org/XML/1998/namespace}id'),
                'ref': node.get('ref'),
                'text': node.text.strip(),
                'lemma': node.get('UnicodeLemma'),
                'gloss': node.get('English'),
                'strong': node.get('StrongNumber'),
                'morph': node.get('FunctionalTag'),
            }
            all_words_data.append(word_info)
            return

        if current_cat == 'cl':
            new_clause_id = node.get('nodeId')
            for child_phrase in node.findall('./Node'):
                new_phrase_id = child_phrase.get('nodeId')
                _traverse_and_collect_words(child_phrase, sentence_id, new_clause_id, new_phrase_id)
        else:
            for child in node.findall('./Node'):
                _traverse_and_collect_words(child, sentence_id, active_clause_id, active_phrase_id)

    # --- Pass 1: Collect all word data and sort into linear text order ---
    root = ET.fromstring(xml_data)

    for sentence in root.findall('Sentence'):
        sentence_ref = sentence.get('ref')
        tree_root = sentence.find('.//Tree/Node')
        if tree_root is not None:
            _traverse_and_collect_words(tree_root, sentence_ref, active_clause_id=None, active_phrase_id=None)

    sorted_words_data = natsorted(all_words_data, key=lambda x: x['ref'])
    
    # --- Pass 2: Post-processing to fix broken clauses ---
    # Iterate through the sorted list to re-assign clause-linking conjunctions.
    for i in range(len(sorted_words_data) - 1):
        current_word = sorted_words_data[i]
        next_word = sorted_words_data[i+1]

        # A word is a clause-linking conjunction if its morph tag is CONJ
        # and its clause differs from the word immediately following it.
        is_conjunction = current_word.get('morph') == 'CONJ'
        
        if is_conjunction and current_word['clause_id'] != next_word['clause_id']:
            # Re-assign this conjunction to the next word's clause and phrase.
            current_word['clause_id'] = next_word['clause_id']
            current_word['phrase_id'] = next_word['phrase_id']
            
    return pd.DataFrame(sorted_words_data)


# --- Main execution block ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flatten Macula GNT XML files.")
    parser.add_argument("root_folder", help="Glob pattern for input XML files (e.g., '../macula-greek/SBLGNT/nodes/*')")
    args = parser.parse_args()

    root_folder = args.root_folder
    
    # I'm using `grass/` because it's no longer a tree :)
    os.makedirs("grass", exist_ok=True)
    
    for file_path in glob(root_folder):
        filename = file_path.split("/")[-1]
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            flat_df = flatten_macula_xml(xml_content)
            
            print(f"Successfully processed '{file_path}'.")
            print("--- Flattened Macula Data Writing to File ---\n")

            out_file = "grass/" + filename.replace(".xml", "_flat_corrected.csv")
            with open(out_file, "w", encoding="utf-8") as out_file:
                out_file.write(flat_df.to_csv())

        except ET.ParseError as e:
            print(f"Error: Could not parse the XML file. It may be malformed.", file=sys.stderr)
            print(f"Details: {e}", file=sys.stderr)
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)

    process_csvs("macula_grass.csv")