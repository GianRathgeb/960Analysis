import chess
import chess.engine
import time
import sys
import os


startingPositionsFile = ".\\startingPositions.txt"
startingPositions = []
stockfishPath = ".\\stockfish\\stockfish-windows-x86-64-avx2.exe"
depth = 1

results = []

startTime = time.time()

with open(startingPositionsFile) as file:
    startingPositions = [line.rstrip() for line in file]

totalPositions = sum(1 for _ in open(startingPositionsFile))

print(f"Starting analysing {totalPositions} starting positions with a depth of {depth}")

for index, startingPosition in enumerate(startingPositions):
    positionIndex = index + 1
    sys.stdout.write(f"\rProgress: {positionIndex}/960")
    sys.stdout.flush()
    board = chess.Board(startingPosition)
    with chess.engine.SimpleEngine.popen_uci(stockfishPath) as engine:
        # Set Threads to the number of logical cores.
        max_threads = os.cpu_count()  # e.g., 8 or 16
        # Set Hash to a high value (in MB) that your system can spare.
        # For instance, use 2048 if you have a system with plenty of RAM.
        engine.configure({"Threads": max_threads, "Hash": 8192})

        searchLimit = chess.engine.Limit(depth=depth)
        analysis = engine.analyse(board, limit=searchLimit)
        score = analysis.get("score")
        # Interpret the score. For example, if it's a mate score:
        if score.is_mate():
            mate_in = score.mate()
            score = f"M{mate_in}"
        else:
            # For centipawn scores, you might convert it to pawns if desired:
            centipawn = score.pov(chess.WHITE).score()
            finalScore = centipawn / 100
        pv_moves = analysis.get("pv")
        if pv_moves:
            moves = " ".join(move.uci() for move in pv_moves)
            results.append((positionIndex, finalScore, moves))
        else:
            results.append((positionIndex, finalScore, "No moves"))

print()
endTime = time.time()
duration = (endTime - startTime)/60

print(f"The calculation of all {totalPositions} with depth: {depth} took {duration} minutes.")