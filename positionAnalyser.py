import xml.etree.ElementTree as ET
import os

countTopPositions = 5
calculatedDepth = 10
xmlFile = f"analysis\\calcEval\\starting_pos_analysis_depth_{calculatedDepth}.xml"
outputFile = f"analysis\\topPositions\\top_{countTopPositions}_positions_depth_{calculatedDepth}.txt"
allPositionFile = ".\\legacy\\startingPositions.txt"

print(f"Finding the top {countTopPositions} positions")

def parse_eval(eval_str):
    """
    Convert an evaluation string to a numeric value for sorting.
    If the evaluation starts with 'M' (mate), we convert it to a very high value,
    so that a mate (e.g., M5) is considered much better.
    Otherwise, we convert the centipawn evaluation string to a float.
    """
    eval_str = eval_str.strip()
    if eval_str.startswith("M"):
        try:
            mate_val = int(eval_str[1:])
        except ValueError:
            return None
        # In mate evaluations, a mate in fewer moves is better.
        # We subtract mate moves from 100000 (an arbitrarily high number)
        return 100000 - mate_val
    else:
        try:
            return float(eval_str)
        except ValueError:
            return None

def load_fens(fen_file):
    """
    Read the FEN file and return a list of FEN strings.
    (One FEN per non-empty line; first line corresponds to position 1.)
    """
    with open(fen_file, "r") as f:
        fens = [line.strip() for line in f if line.strip()]
    return fens

# Parse the XML file.
if os.path.isfile(xmlFile):
    tree = ET.parse(xmlFile)
    root = tree.getroot()
else:
    print(f"The file does not exist {xmlFile}")
    exit(0)

positions = []  # This will hold tuples of the form (position_number, evaluation)

# Loop over each startingPosition element in the XML.
for sp in root.findall("startingPosition"):
    # Get the child elements. (Note: we used the same tag "startingPosition" for the index.)
    pos_num_elem = sp.find("positionNumber")
    eval_elem = sp.find("evalScore")
    if pos_num_elem is None or eval_elem is None:
        continue
    
    try:
        pos_num = int(pos_num_elem.text.strip())
    except (ValueError, AttributeError):
        continue

    eval_text = eval_elem.text.strip() if eval_elem.text else ""
    numeric_eval = parse_eval(eval_text)
    if numeric_eval is None:
        continue
    positions.append((pos_num, numeric_eval))

# Sort positions in descending order (assuming a higher numeric value is "better")
positions.sort(key=lambda x: x[1], reverse=True)

# Load the FEN file.
fens = load_fens(allPositionFile)

# Combine the XML evaluations with the corresponding FEN string.
# Here we assume that the position number in the XML corresponds to the line number in the FEN file.
results = []
for pos_num, evaluation in positions:
    # Since fens is zero-based (first FEN is index 0), use pos_num - 1.
    if 1 <= pos_num <= len(fens):
        fen = fens[pos_num - 1]
    else:
        fen = "N/A"
    results.append((pos_num, evaluation, fen))

# Display the top N positions.
print(f"\n{countTopPositions} Top Positions with depth {calculatedDepth} (format: (position, evaluation, FEN)):")
for r in results[:countTopPositions]:
    # Print evaluation in its raw numeric form.
    print(f"({r[0]}, {r[1]}, {r[2]})")


# write the output file
# Create the root element
root_elem = ET.Element("positions")

# Loop through the top positions from your 'results' list
for pos_num, evaluation, fen in results[:countTopPositions]:
    position_elem = ET.SubElement(root_elem, "position")
    
    posnum_elem = ET.SubElement(position_elem, "positionNumber")
    posnum_elem.text = str(pos_num)
    
    fen_elem = ET.SubElement(position_elem, "fen")
    fen_elem.text = fen

# Write the XML to a file
tree = ET.ElementTree(root_elem)
tree.write(outputFile, encoding="utf-8", xml_declaration=True)

print(f"Top positions have been written to {outputFile}")