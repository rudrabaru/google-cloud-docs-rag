# AI Engineering Development Instructions

You are assisting in the development of a Retrieval-Augmented Generation (RAG) system for Google Cloud documentation.

The objective is to learn AI systems engineering deeply while building the system incrementally.

Core Development Philosophy:

* Prioritize understanding over abstraction.
* Prefer minimal working implementations first.
* Build incrementally and observably.
* Avoid unnecessary frameworks and premature optimization.
* Keep architectures transparent and inspectable.

Engineering Requirements:

* Always expose intermediate outputs for debugging.
* Print and inspect:

  * crawled markdown
  * cleaned text
  * chunk boundaries
  * retrieved chunks
  * similarity scores
  * generated prompts
  * LLM responses
* Explain WHY implementation decisions are made.
* Clearly separate:

  * crawling
  * processing
  * embeddings
  * retrieval
  * generation
  * evaluation

Coding Style:

* Prefer simple Python implementations.
* Keep modules small and understandable.
* Avoid excessive abstractions.
* Avoid unnecessary class hierarchies.
* Prefer readability over cleverness.
* Prefer explicit data flow.

Retrieval Engineering Priorities:

* Focus heavily on retrieval quality.
* Treat chunking quality as critical.
* Optimize for semantic coherence.
* Avoid noisy context construction.
* Encourage retrieval debugging before blaming the LLM.

Debugging Philosophy:
When failures occur, analyze:

* document quality
* chunking issues
* embedding quality
* retrieval relevance
* context contamination
* prompt construction
* token limitations

Avoid assuming the LLM is the primary issue.

Learning-Focused Behavior:

* Explain tradeoffs clearly.
* Highlight likely failure modes.
* Encourage manual inspection and experimentation.
* Prefer educational implementation over production complexity.

Avoid:

* premature enterprise architecture
* unnecessary orchestration frameworks
* complex agent systems
* hidden abstractions
* magic pipelines

The system should remain understandable end-to-end.
