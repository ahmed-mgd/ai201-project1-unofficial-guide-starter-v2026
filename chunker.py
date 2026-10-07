"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


# A thread is a title line followed by replies, each opened by a header like
# "--- reply 2 (9 votes) ---". Replies are 68 to 195 characters, and no reply
# makes sense without the question above it.
_REPLY_HEADER = re.compile(r"(?m)^--- reply \d+ \(\d+ votes\) ---$")

# Threads run 400 to 810 characters. 900 keeps every current thread whole and
# only forces a split on a thread longer than any of them.
MAX_THREAD_CHARS = 900


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split advice threads into chunks, one thread per chunk.

    A reply on its own ("Yes. Cuts an 18 minute walk to about 6.") means nothing
    without the question, and the replies in a thread disagree with each other,
    so the answer to a question like "is a bike worth it?" is the whole
    thread. Each thread is kept together with its title line.

    If a thread is longer than MAX_THREAD_CHARS, it is cut only between
    replies, never inside one. Every piece repeats the title, and each piece
    after the first starts with the last reply of the one before it, so the
    overlap is one whole reply rather than a number of characters.
    """
    chunks: list[Chunk] = []
    for doc in documents:
        parts = _REPLY_HEADER.split(doc.text)
        headers = _REPLY_HEADER.findall(doc.text)
        title = parts[0].strip()
        replies = [f"{h}\n{body.strip()}" for h, body in zip(headers, parts[1:])]

        if not replies:  # not a thread; keep it whole rather than guess
            pieces = [doc.text]
        else:
            pieces = _group_replies(title, replies)

        for index, piece in enumerate(pieces):
            chunks.append(
                Chunk(
                    text=piece,
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )
    return chunks


def _group_replies(title: str, replies: list[str]) -> list[str]:
    """Pack whole replies under the title, up to MAX_THREAD_CHARS per piece."""
    pieces: list[str] = []
    current: list[str] = []
    for reply in replies:
        candidate = "\n\n".join([title, *current, reply])
        if current and len(candidate) > MAX_THREAD_CHARS:
            pieces.append("\n\n".join([title, *current]))
            current = [current[-1]]  # one-reply overlap
        current.append(reply)
    pieces.append("\n\n".join([title, *current]))
    return pieces


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
