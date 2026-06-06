# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

**ASU CS/Software Engineering Course & Professor Guide (Fulton Schools)**

Official ASU course catalogs provide the syllabus, but they don't capture the student experience—such as how harsh a grader a professor is, which electives are most useful for software engineering interviews, or which prerequisite courses are the most notoriously difficult. This knowledge is incredibly valuable for students planning their schedules but is typically scattered across Reddit threads, Discord servers, and word-of-mouth, making it hard to find and aggregate efficiently.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Reddit r/ASU CSE 310 Thread Summary | Text File | `documents/cse310_reddit_summary.txt` |
| 2 | Reddit r/ASU CSE 340 Thread Summary | Text File | `documents/cse340_reddit_summary.txt` |
| 3 | Reddit r/ASU CSE 240 Thread Summary | Text File | `documents/cse240_reddit_summary.txt` |
| 4 | Reddit r/ASU CSE 110 Thread Summary | Text File | `documents/cse110_reddit_summary.txt` |
| 5 | Reddit r/ASU Prof. Ryan Meuth Reviews | Text File | `documents/ryan_meuth_reviews.txt` |
| 6 | Reddit r/ASU CSE 412 Thread Summary | Text File | `documents/cse412_reddit_summary.txt` |
| 7 | Reddit r/ASU CSE 355 Thread Summary | Text File | `documents/cse355_reddit_summary.txt` |
| 8 | Reddit r/ASU Prof. Mutsumi Nakamura Reviews | Text File | `documents/mutsumi_nakamura_reviews.txt` |
| 9 | Reddit r/ASU CSE 445 Thread Summary | Text File | `documents/cse445_reddit_summary.txt` |
| 10 | Reddit r/ASU Prof. Yinong Chen Reviews | Text File | `documents/yinong_chen_reviews.txt` |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 characters (respecting word boundaries)

**Overlap:** 100 characters

**Why these choices fit your documents:** The documents are mostly short, bulleted summaries. A 500-character chunk easily captures 2-3 bullet points or a full paragraph, ensuring the context (like a professor's name) isn't lost. The 100-character overlap prevents cutting a single thought in half across chunks. We also strip whitespace and avoid cutting mid-word during chunking.

**Final chunk count:** 39 chunks

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` (via `sentence-transformers` and `chromadb`'s built-in wrapper).

**Production tradeoff reflection:** If cost was not a constraint, I might switch to OpenAI's `text-embedding-3-small` or `text-embedding-3-large`. These API-hosted models provide significantly larger context length limits (up to 8k tokens) and exceptional multilingual and domain-specific accuracy. However, they introduce latency because of network calls and require managing API keys and rate limits. The local `all-MiniLM-L6-v2` is incredibly fast and entirely free, which is perfect for this project, but it is limited to a smaller sequence length and english-only text.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
I used the following exact system prompt to enforce strict grounding:
"You are an ASU Computer Science course and professor guide assistant. You must answer the user's question using ONLY the provided context. If the provided context does not contain the answer, you must say exactly: "I don't have enough information on that." Do not use outside knowledge. Do not guess."
In addition, we structure the prompt to pass `Context:\n{context_str}` explicitly before the question.

**How source attribution is surfaced in the response:**
Source attribution is enforced programmatically. In `app.py`, as we iterate through retrieved documents, we create a set of `unique_sources`. These are then explicitly listed in the Gradio UI in a dedicated "Retrieved from" text box. We also instruct the LLM to briefly cite the source inline (e.g., `(source: filename.txt)`).

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about the workload and projects for CSE 340, and what is the best way to manage it? | Difficult, 30-40 hours each project. Start early, seek help from TAs early. | Accurately reported 30-40 hours per project and advised starting early and seeking TA help. | Relevant | Accurate |
| 2 | What programming language is used in CSE 310, and what specific concepts should I be comfortable with before taking it? | C++, concepts like pointers, memory management, debugging. | Accurately stated C++, pointers, memory management, and debugging. | Relevant | Accurate |
| 3 | What is the general student consensus on Professor Ryan Meuth, and what external resource of his is highly recommended? | Best professor, enthusiastic. Highly recommended his YouTube channel. | Captured "best professor" and enthusiasm. Failed to mention the YouTube channel. | Partially relevant | Partially accurate |
| 4 | How does CSE 355 differ from practical programming courses, and what YouTube channel do students recommend for it? | Theory-heavy, proof-based. "Easy Theory" YouTube channel recommended. | Correctly identified it as theory-based, but incorrectly recommended Adam Doupe's YouTube channel. | Partially relevant | Inaccurate |
| 5 | What is Professor Yinong Chen's exam format in CSE 445, and what is the key strategy for success on these exams? | Open-note, key strategy is organization/indexing notes for Ctrl+F. | Accurately reported open-note format and strategy to effectively organize notes. | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** How does CSE 355 differ from practical programming courses, and what YouTube channel do students recommend for it?

**What the system returned:** CSE 355 differs from practical programming courses as it is a theory-heavy, proof-based course. For supplemental materials, students recommend YouTube tutorials, specifically Adam Doupe's lectures, to aid in their studies.

**Root cause (tied to a specific pipeline stage):** This is a generation hallucination caused by cross-contamination during the retrieval stage. Because the query asked about "YouTube channel", the retriever pulled chunks from both `cse355_reddit_summary.txt` (which has the correct "Easy Theory" channel) and `cse340_reddit_summary.txt` (which mentions "Adam Doupe's lectures"). The LLM got confused by the mixed context and incorrectly attributed the CSE 340 YouTube channel to the CSE 355 question.

**What you would change to fix it:** Add metadata filtering to the retrieval stage. If a user asks about "CSE 355", we could extract the course name and pre-filter the ChromaDB query to only return chunks from files that match `*cse355*`. This would completely eliminate context cross-contamination.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
Writing the exact chunking strategy (500 chars, 100 overlap) and the retrieval approach (top-k=3) in the spec gave me a concrete blueprint to implement in `ingest.py` and `retrieve.py`. It prevented me from guessing parameters or relying on defaults, making the coding phase much faster because I just had to translate my decisions into python.

**One way your implementation diverged from the spec, and why:**
In the spec, I planned to use a simple fixed-character chunker. However, when I inspected the actual chunks in Milestone 3, I noticed it was cutting words right in half (e.g., splitting "prerequisite" into "pre" and "requisite"). I updated the implementation to explicitly respect word boundaries (spaces) when calculating the 500-character split, which kept the semantic meaning intact.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* I provided the `planning.md` architecture diagram and instructions to build the ingestion pipeline with `glob` and a chunker.
- *What it produced:* It produced a `chunk_text()` script that strictly split exactly at the 500th character, even if it was mid-word.
- *What I changed or overrode:* I rewrote the chunking loop to include an `rfind(' ')` to ensure it only broke at the last space before the 500th character, keeping whole words intact.

**Instance 2**

- *What I gave the AI:* I asked for the code to connect ChromaDB retrieval to Groq's `llama-3.3-70b-versatile` API and build a minimal Gradio UI.
- *What it produced:* It produced a functional Gradio skeleton but didn't cleanly expose the source citations in a separate UI component.
- *What I changed or overrode:* I added a programmatic collection of `unique_sources` and added a dedicated `gr.Textbox(label="Retrieved from")` to explicitly surface the sources for the user, rather than solely relying on the LLM citing it in the text.
