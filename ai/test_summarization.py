from services.summarization import generate_notes

sample = "Today we will study operating systems and process scheduling. \
The CPU scheduler selects processes from the ready queue. \
There are different scheduling algorithms like FCFS, SJF, and Round Robin. \
Each has its own advantages and disadvantages in terms of waiting time and throughput."

if __name__ == "__main__":
    notes = generate_notes(sample)
    print(notes)