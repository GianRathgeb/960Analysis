import xml.etree.ElementTree as ET

countTopPositions = 50
xmlFile = "analysis\\starting_pos_analysis_depth_25.xml"


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

def main():
    # Parse the XML file.
    tree = ET.parse(xmlFile)
    root = tree.getroot()

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

    # Display the top N positions.
    print(f"{countTopPositions} Top Positions (format: (position, evaluation)):")
    for pos in positions[:countTopPositions]:
        print(f"({pos[0]}, {pos[1]})")

if __name__ == "__main__":
    main()
