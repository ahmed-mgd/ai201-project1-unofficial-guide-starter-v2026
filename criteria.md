# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions in `questions.py`, at least one of the
top 5 retrieved chunks contains that question's `expects` phrase, and reading
that chunk shows it actually answers the question.

**Why this target:**
Four of five leaves room for one miss. Each question points at a different thread, and the parking question is spread across three replies (west permit, east lot, free street parking), so it's the likeliest one to come back with only part of the answer. Five of five would make one unlucky chunk boundary a failure of the whole system. Three of five would let the system be wrong on two questions that each have a single plain answer in the documents.

---

## 2. Every answer names a source

For each of my 5 test questions that gets past the relevance gate, the answer
text includes the file name of at least one document (for example
`thread_parking.txt`). A refusal from the gate has no answer and isn't counted.

**Why this target:**
All of them, because every answer comes out of retrieved chunks that each carry a file name, so there's no reason for one to arrive without a source. The generator is also told to name the file. A refusal from the gate doesn't count here, since it never reaches the model and has nothing to cite. If an answer ever shows up with no source, either the prompt or the code that assembles it is broken, and I'd want to know about that rather than shrug off a 4 of 5.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries. The gate is the distance check that runs before the
model is called, and a refusal means the exact sentence above comes back with
zero model calls. The five questions are the ones in `OUT_OF_SCOPE` in
`questions.py`.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
Before any tuning, I have two data points: an in-corpus question about bikes landed at distance 0.296, and an off-topic housing lottery question landed at 0.725 against the starter's 0.6 cutoff. That's a decent gap, but the corpus is about student life in general, so a question that sounds a bit like a student problem (the ibuprofen one mentions a headache, and there's a sleep thread) could slip under the cutoff. I allow one such miss. Five of five would be too strict, since a single borderline question would push me to raise the cutoff and start refusing things I do have answers for.

---

## 4. Chunks are whole thoughts

Across every chunk the index produces for my corpus, the shortest is at least 60
characters (counting spaces), and no chunk mixes text from two different files.
Each file is one thread, and each reply starts at a `--- reply N` line. Every
chunk must also begin at the start of a reply and end at the end of one, never
partway through a reply's text.

**Why this target:**
The shortest of the 75 replies in my corpus is 68 characters, so anything under 60 has to be a leftover fragment rather than a real reply. The starter chunker produces a 2-character chunk, which is the failure this is meant to catch. I check all of the chunks, not a sample of five, because there are only a few dozen and one bad chunk is easy to miss in a sample. I left out a target on the average size, since the replies vary from about 70 to 195 characters and an average wouldn't tell me anything.

---

## 5. Numbers in answers match the documents

Every number in an answer (dollars, pages, days, GB of RAM) also appears in the
chunks retrieved for that question, where "ten" and "10" count as the same
number. I check this on all 5 test questions. The three whose `expects` phrase
is a number (meal plan days, printing pages, RAM) must all pass, and the other
two pass as long as their answers don't add a number the chunks don't contain.

**Why this target:**
The documents are full of small facts that cost money if they're wrong: $30 and about 600 pages, ten days to change a meal plan, 16GB of RAM. A model that rounds or makes up a figure sounds just as sure as one that doesn't, and a reader wouldn't catch it. Three of my five questions have a figure as the answer, and I require all three to match rather than two of three, because a wrong number is the one error a reader acts on without checking. 

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         