from services.summarization import generate_notes, generate_notes_for_long_transcript

# Test 1 — Short transcript (normal)
print("=" * 50)
print("TEST 1 — SHORT TRANSCRIPT")
print("=" * 50)
sample_short = "Today we will study operating systems and process scheduling. \
The CPU scheduler selects processes from the ready queue. \
There are different scheduling algorithms like FCFS, SJF, and Round Robin. \
Each has its own advantages and disadvantages in terms of waiting time and throughput."

notes_short = generate_notes(sample_short)
print(notes_short)

# Test 2 — Long transcript (chunking)
print("\n" + "=" * 50)
print("TEST 2 — LONG TRANSCRIPT (CHUNKING)")
print("=" * 50)
sample_long = sample_short * 20  # making it long by repeating

notes_long = generate_notes_for_long_transcript(sample_long)
print(notes_long)