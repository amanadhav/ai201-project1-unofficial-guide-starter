from app import ask

queries = [
    "What do students say about the workload and projects for CSE 340, and what is the best way to manage it?",
    "What programming language is used in CSE 310, and what specific concepts should I be comfortable with before taking it?",
    "What is the general student consensus on Professor Ryan Meuth, and what external resource of his is highly recommended?",
    "How does CSE 355 differ from practical programming courses, and what YouTube channel do students recommend for it?",
    "What is Professor Yinong Chen's exam format in CSE 445, and what is the key strategy for success on these exams?"
]

for i, q in enumerate(queries):
    res = ask(q)
    print(f"\n--- Q{i+1} ---")
    print(f"Q: {q}")
    print(f"A: {res['answer']}")
    print(f"Sources: {res['sources']}")
