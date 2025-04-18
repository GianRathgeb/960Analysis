import time
import sys
import os
from stockfish import Stockfish
import xml.etree.ElementTree as ET

startingPositionsFile = ".\\analysis\\topPositions\\top_25_positions_depth_30.xml"
stockfishPath = ".\\stockfish\\stockfish-windows-x86-64-avx2.exe"
depth = 10
showMoves = 20
resultsToFile = True
outputFile = f".\\analysis\\calcEval\\starting_pos_analysis_depth_{depth}.xml"

createTempFile = True
tempFile = f".\\analysis\\calcEval\\temp\\starting_pos_analysis_depth_{depth}.xml"

results = []
startingPositions = []


# Check if the max moves is more than depth, if yes, only show the depth
if showMoves > depth:
    maxMoves = depth
else:
    maxMoves = showMoves

# Create the output file
def write_results_to_xml(results, output_file):
    root = ET.Element("results")

    for positionIndex, finalScore, moves in results:
        starting_position_elem = ET.SubElement(root, "startingPosition")
        
        index_elem = ET.SubElement(starting_position_elem, "positionNumber")
        index_elem.text = str(positionIndex)
        
        eval_elem = ET.SubElement(starting_position_elem, "evalScore")
        eval_elem.text = str(finalScore)
        
        moves_elem = ET.SubElement(starting_position_elem, "bestMoves")
        moves_elem.text = moves

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)


def load_fens_from_xml(fen_xml_file):
    """
    Read the FEN XML file and return a list of FEN strings.
    Expects an XML structure like:
    
    Returns a list of FEN strings sorted by positionNumber.
    """
    try:
        tree = ET.parse(fen_xml_file)
    except Exception as e:
        print(f"Error parsing FEN XML file: {e}")
        exit(0)
    root = tree.getroot()
    
    fen_dict = {}
    for sp in root.findall("startingPosition"):
        pos_elem = sp.find("positionNumber")
        fen_elem = sp.find("fen")
        if pos_elem is None or fen_elem is None:
            continue
        try:
            pos = int(pos_elem.text.strip())
            fen_str = fen_elem.text.strip()
            fen_dict[pos] = fen_str
        except Exception:
            continue
    # Sorted by position number (assuming positions start at 1)
    return fen_dict

# Load starting positions from the XML file.
startingPositions = load_fens_from_xml(startingPositionsFile)
totalPositions = len(startingPositions)

stockfish = Stockfish(
    path=stockfishPath,
    depth=depth,
    parameters={
        "Threads": (os.cpu_count() / 2),  # use half of all the available logical cores
        "Hash": 8192                # in MB; adjust according to your available RAM
    }
)

startTime = time.time()
formattedStartTime = time.strftime("%H:%M:%S", time.localtime(startTime))
print(f"{formattedStartTime} - Starting analysing {totalPositions} starting positions with a depth of {depth}")

positionsDone = 0
for positionIndex, startingPosition in startingPositions.items():
    # during the first run, don't show anything
    if positionsDone != 0:
        # calculate the undergoing time
        tempTime = time.time()
        tempDuration = time.gmtime((tempTime - startTime))
        formattedTempTime = time.strftime("%H:%M:%S", tempDuration)

        # calculate est. full time
        restPositions = totalPositions - positionsDone
        timePerCalc = (tempTime - startTime) / positionsDone
        estSeconds = restPositions * timePerCalc

        totalHours = int(estSeconds // 3600)
        remainingSeconds = estSeconds % 3600
        minutes = int(remainingSeconds // 60)
        seconds = int(remainingSeconds % 60)

        formattedEstTime = f"{totalHours:02d}:{minutes:02d}:{seconds:02d}"

        # update progress
        sys.stdout.write(f"\r{formattedTempTime} - Progress: {positionsDone}/{totalPositions}    est. time {formattedEstTime}")
        sys.stdout.flush()

    # Evaluate the position.
    # The get_evaluation() method returns a dict like: 
    # # {"type": "cp", "value": 123} or {"type": "mate", "value": 5}
    try:
        stockfish.set_fen_position(startingPosition)
        eval_obj = stockfish.get_evaluation() 
        # Interpret the score. For example, if it's a mate score:
        # Format the evaluation in the style of chess.com
        if eval_obj["type"] == "mate":
            # e.g., {"type": "mate", "value": 5} becomes "M5"
            finalScore = f"M{eval_obj['value']}"
        else:
            # Convert centipawn (cp) evaluation into pawn units (divide by 100)
            finalScore = eval_obj["value"] / 100.0
    except Exception as e:
        print(f"\nError in the evaluation of position {positionIndex}: {e}")
        finalScore = None
    
    try:
        topMoves = stockfish.get_top_moves(maxMoves)

        if topMoves:
            moves = " ".join(item["Move"] for item in topMoves)
            
        else:
            moves = "No moves"
    except Exception as e:
        print(f"\nError retrieving top moves for position {positionIndex}: {e}")
        topMoves = None

    results.append((positionIndex, finalScore, moves))
    positionsDone += 1

    # try to write to the temp file
    try:
        if createTempFile & resultsToFile:
            write_results_to_xml(results, tempFile)
    except:
        # nothing to do, but this should not happen
        pass


print()
endTime = time.time()
duration = (endTime - startTime)/60
durationHours =duration / 60

print(f"The calculation of all {totalPositions} with depth: {depth} took {duration} minutes ({durationHours})")

try:
    if resultsToFile:
        print(f"Writing results to output file {outputFile}")
        write_results_to_xml(results, outputFile)
        if createTempFile:
            print(f"Removing the temporary file {tempFile}")
            os.remove(tempFile)
    else:
        print(results)

except Exception as e:
    print(f"Error while writing all positions with depth {depth} to output file with the following error: {e}")
    print(results)