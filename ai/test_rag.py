from services.rag import ask_question

# Fake transcript to test with
transcript = """
Scheduling is the process of deciding which process runs next on the CPU.
There are different scheduling algorithms like Round Robin, FCFS, and Priority Scheduling.
Round Robin gives each process a fixed time slot called a quantum.
FCFS stands for First Come First Serve, where processes are executed in order of arrival.
Priority Scheduling assigns a priority number to each process and runs the highest priority first.
The main goal of scheduling is to maximize CPU utilization and minimize waiting time.
"""

# Test questions
questions = [
    "What is scheduling?",
    "Explain Round Robin",
    "What is FCFS?",
    "Give a summary",
]

for q in questions:
    print(f"\nQ: {q}")
    print(f"A: {ask_question(q, transcript)}")
    print("-" * 50)