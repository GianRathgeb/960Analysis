import time
import sys
import os
from stockfish import Stockfish
import xml.etree.ElementTree as ET

startingPositionsFile = ".\\startingPositions.txt"
stockfishPath = ".\\stockfish\\stockfish-windows-x86-64-avx2.exe"
depth = 25
showMoves = 10
resultsToFile = True

results = []
startingPositions = []


# Check if the max moves is more than depth, if yes, only show the depth
if showMoves > depth:
    maxMoves = depth
else:
    maxMoves = showMoves

with open(startingPositionsFile) as file:
    startingPositions = [line.rstrip() for line in file]

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


for index, startingPosition in enumerate(startingPositions):
    positionIndex = index + 1

    # update only every 10 positions
    if positionIndex % 10 == 0:
        # calculate the undergoing time
        tempTime = time.time()
        tempDuration = time.gmtime((tempTime - startTime))
        formattedTempTime = time.strftime("%H:%M:%S", tempDuration)

        # calculate est. full time
        restPositions = totalPositions - positionIndex
        timePerCalc = (tempTime - startTime) / positionIndex
        estTime = time.gmtime(restPositions * timePerCalc)
        formattedEstTime = time.strftime("%H:%M:%S", estTime)

        # update progress
        sys.stdout.write(f"\r{formattedTempTime} - Progress: {positionIndex}/960    est. time {formattedEstTime}")
        sys.stdout.flush()

    stockfish.set_fen_position(startingPosition)
    # Evaluate the position.
    # The get_evaluation() method returns a dict like: 
    # # {"type": "cp", "value": 123} or {"type": "mate", "value": 5}
    eval_obj = stockfish.get_evaluation() 

    # Interpret the score. For example, if it's a mate score:
    # Format the evaluation in the style of chess.com
    if eval_obj["type"] == "mate":
        # e.g., {"type": "mate", "value": 5} becomes "M5"
        finalScore = f"M{eval_obj['value']}"
    else:
        # Convert centipawn (cp) evaluation into pawn units (divide by 100)
        finalScore = eval_obj["value"] / 100.0
    
    topMoves = stockfish.get_top_moves(maxMoves)

    if topMoves:
        moves = " ".join(item["Move"] for item in topMoves)
        
    else:
        moves = "No moves"

    results.append((positionIndex, finalScore, moves))

print()
endTime = time.time()
duration = (endTime - startTime)/60

print(f"The calculation of all {totalPositions} with depth: {depth} took {duration} minutes.")



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

if resultsToFile:
    print("Writing results to output file")
    output_file = f"analysis\\starting_pos_analysis_depth_{depth}.xml"
    write_results_to_xml(results, output_file)
else:
    print(results)