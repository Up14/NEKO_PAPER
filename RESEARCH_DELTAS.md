# Step-by-Step Research Delta Analysis: NEKO Paper to Knowledge System

## STEP 1: Literature Search & Query Construction

### 1A. Query Generation

| | Original NEKO | Updated Knowledge |
|---|---|---|
| **Method** | Manual keyword string passed directly | LLM-driven concept decomposition into structured JSON |
| **Query format** | `"{keyword}[Abstract]"` (single query) | 4-tier strategy: Baseline, Broad, Specific, Targeted |
| **Concept extraction** | None | LLM extracts `{compound, organism, process, other}` with synonyms at `temperature=0` |
| **Synonym expansion** | None - user must manually think of synonyms | LLM auto-generates synonyms for each concept category |
| **Field tagging** | Only `[Abstract]` tag | Tiers use `[tiab]` (title-and-abstract) for precision; baseline has no tags for recall |
| **Noise filtering** | None | Removes generic terms: "study", "research", "investigation", "analysis", "review", "effect", "role", "impact" |
| **Multi-word handling** | None | Multi-word terms auto-quoted for exact PubMed matching |
| **Caching** | None | MD5 hash of goal text -> `concept_cache_{hash}.json` + `query_cache_{hash}.json` for deterministic reproducibility |

**Delta significance**: Transforms query construction from a manual, single-shot keyword search into a systematic, reproducible, multi-strategy retrieval approach. The 4-tier strategy ensures both high recall (broad query catches papers a narrow query misses) and high precision (targeted query filters noise). This is a fundamental methodological improvement in literature coverage.

---

### 1B. PubMed API Interaction

| | Original NEKO | Updated Knowledge |
|---|---|---|
| **Max results** | `retmax=200-1000` (single call) | Batched in chunks of 10,000 IDs with safety cap at 100,000 |
| **Retry logic** | None | 3 retries per batch with exponential backoff: `sleep(2 * (retry + 1))` |
| **Rate limiting** | None | `time.sleep(0.5)` between batches (NCBI courtesy) |
| **Fetch batching** | Single `Entrez.efetch` with all IDs | Batched at 200 IDs per call (NCBI recommended max) with `time.sleep(0.4)` |
| **Empty abstract handling** | Included in dataset | Explicitly filtered: skips empty, whitespace-only, or "N/A" abstracts |
| **ID deduplication** | None (single query) | `set()` dedup across all 4 tier queries |
| **PMID tracking** | Not stored | PMID stored per article for downstream citation tracing |

**Delta significance**: Scalable retrieval (200 to 100,000 articles), robust to API failures, and deduplicates across multiple search strategies.

---

### 1C. Relevance Pre-Filtering

| | Original NEKO | Updated Knowledge |
|---|---|---|
| **Pre-filter** | None - all retrieved articles go to LLM | Keyword presence check before any LLM call |
| **Method** | -- | Extracts goal keywords (words > 3 characters), filters abstracts requiring at least one match |
| **Savings** | -- | Estimated 15-30% reduction in LLM API calls |

**Delta significance**: New stage that did not exist before. Reduces cost and processing time by filtering obviously irrelevant articles before expensive LLM extraction.

---

## STEP 2: Abstract Processing

### 2A. Chunking

| | Original NEKO | Updated Knowledge |
|---|---|---|
| **PubMed abstracts** | Sent whole, no chunking | Split at sentence boundaries into <=2000 character chunks |
| **PDF chunking** | 1000-word chunks split on whitespace | N/A (no PDF processing in updated version) |
| **Sentence boundary detection** | None | Compound negative lookbehind regex handling 7 scientific abbreviation patterns: `et al.`, `sp.`, `spp.`, `vs.`, `Fig.`, single-capital abbreviations (e.g., `E.` in `E. coli`), mid-abbreviation patterns (e.g., `U.S.A.`) |
| **Chunk preservation** | Splits mid-sentence/mid-word | Greedy sentence accumulation -- never breaks mid-sentence |

**Delta significance**: Scientific text has unique abbreviation patterns that create false sentence boundaries. The original had no chunking for abstracts (acceptable for short ones) and dumb whitespace splitting for PDFs. The new system ensures each chunk contains complete semantic units, critical for relationship extraction accuracy.

---

## STEP 3: LLM Extraction

### 3A. Relationship Model

| | Original NEKO | Updated Knowledge |
|---|---|---|
| **Output format** | Untyped pairs: `(Entity A, Entity B)` | Typed triples: `(Subject, Relation, Object)` |
| **Relationship labels** | None -- relationship semantics embedded in entity names | 13-term controlled ontology: `activates, inhibits, produces, is_variant_of, encodes, is_host_for, increases, decreases, integrated_in, has_capability, is_a, has_metric, is_produced_by` |
| **Directionality** | Lost (undirected pairs) | Preserved (subject -> relation -> object) |
| **Regex for parsing** | `r'\(([^,]+), ([^\)]+)\)'` (2 groups) | `r'\(([^,]+?),\s*([^,]+?),\s*([^\)]+?)\)'` (3 groups, non-greedy) |

**Delta significance**: This is arguably the single most important research delta. Moving from untyped pairs to typed triples with a controlled ontology transforms the output from an association network into a semantically rich knowledge graph that supports mechanistic reasoning. The relationship type tells you *how* entities interact, not just *that* they interact.

---

### 3B. Extraction Prompts

**Original NEKO system prompt (GPT-4 version):**

```
This GPT is specialized for analyzing scientific paper abstracts, focusing on 
identifying specific entities related to biological studies, such as performance, 
species, genes, methods of genetic engineering, enzymes, proteins, and bioprocess 
conditions (e.g., growth conditions), and determining causal relationships between 
them. It outputs all possible combinations of causal relationships among identified 
entities in structured pairs. The output strictly follows the format: 
(Entity A ,Entity B), with no additional text.
```

**Updated Knowledge system prompt:**

```
You are a specialized Knowledge Graph Engineer. Your task is to extract precise 
relationships between entities.

### RELATION ONTOLOGY:
Use ONLY these relations where possible:
- activates, inhibits, produces, is_variant_of, encodes, is_host_for, increases, 
  decreases, integrated_in, has_capability, is_a, has_metric

### NUMERIC DATA RULES:
Separate measurements into distinct triples using 'has_metric'.
BAD: (strain_X, produces, 39.5 g/L beta-carotene)
GOOD: (strain_X, produces, beta-carotene); (strain_X, has_metric, "39.5 g/L")

### QUALITY RULES:
- Avoid fuzzy statements like "enables". Use "activates" or "facilitates".
- Ensure every triple has (Subject, Relation, Object). No empty fields.
- Extract exact engineering strategies (e.g., (gene_X, integrated_in, chromosome_Y)).

### OUTPUT FORMAT:
Output ONLY raw triples: (subject, relation, object).
```

**Key prompt engineering deltas:**

1. **Controlled vocabulary enforcement** -- ontology specified in the prompt itself
2. **Numeric data separation rules** -- explicit BAD/GOOD examples forcing metric isolation
3. **Quality rules** -- anti-fuzziness instructions ("avoid 'enables', use 'activates'")
4. **Engineering strategy extraction** -- explicit instruction to capture genomic integration details
5. **Goal context injection** -- `"Goal context: {user_goal}"` passed to focus extraction on research relevance

**Delta significance**: The prompt evolved from a generic "find causal pairs" instruction into a structured knowledge engineering specification with ontology constraints, data quality rules, and concrete examples. This directly controls extraction quality and consistency.

---

### 3C. Multi-Pass Extraction

| | Original NEKO | Updated Knowledge |
|---|---|---|
| **Passes per abstract** | 1 pass | 3 passes + 1 validation pass |
| **Pass 1** | Single extraction | "Exhaustive extraction" -- extract ALL relationships including causal, mechanistic, associative, implied, or weak interactions |
| **Pass 2** | -- | "Overlooked scan" -- re-scans for missed interactions given Pass 1 results: `"Already found: {pass1}\n\nScan again: {question}"` |
| **Pass 3** | -- | "Validation/gap-filling" -- given all triples found so far, identifies specifically missing relationships |
| **Validation** | -- | Separate "Critical Bio-Analyst" persona independently verifies and extracts top interactions |
| **Merging** | -- | Set union of all passes -- no information discarded |
| **Temperature** | Not specified (API default) | All passes at `temperature=0` for determinism |

**Delta significance**: Multi-pass extraction with progressive refinement is a novel methodological contribution. Each pass approaches the same text from a different analytical angle:

- Pass 1: breadth (exhaustive)
- Pass 2: depth (what was missed, with awareness of what was found)
- Pass 3: completeness (gap analysis)
- Validation: independent verification

This directly increases recall while the union merge ensures no information is lost.

---

### 3D. Stability/Confidence Scoring

| | Original NEKO | Updated Knowledge |
|---|---|---|
| **Confidence metric** | None | Jaccard stability score per article |
| **Computation** | -- | `|extraction_triples INTERSECT validation_triples| / |extraction_triples UNION validation_triples|` |
| **Range** | -- | 0.0 to 1.0 (default 1.0 if no triples) |
| **Storage** | -- | `Stability Score Q2` column in output Excel |
| **Use** | -- | Enables downstream filtering of low-confidence extractions |

**Delta significance**: Introduces a quantitative reliability metric per article. This is a novel contribution -- measuring agreement between extraction and validation as a proxy for extraction confidence. Papers with low stability scores can be flagged for manual review or filtered out.

---

## STEP 4: Post-Extraction Normalization

### 4A. Relation Normalization

| | Original NEKO | Updated Knowledge |
|---|---|---|
| **Relation types** | None (no typed relations) | 13 canonical terms |
| **Synonym mappings** | N/A | 41 synonym to canonical mappings |
| **Implementation** | N/A | Regex patterns sorted by synonym length descending (longest first to prevent substring conflicts), pre-compiled once |
| **Post-normalization dedup** | N/A | Case-insensitive deduplication of triples within each cell after normalization |

**Groupings of the 41 synonym mappings:**

- 10 terms -> `activates` (induces, enhances, stimulates, upregulates, promotes, facilitates, positive_regulator, triggers, initiates)
- 9 terms -> `inhibits` (reduces, suppresses, downregulates, blocks, interferes, negative_regulator, diminishes, represses, attenuates)
- 5 terms -> `produces` (produced, synthesized, secreted, generates, yields)
- 8 common LLM outputs -> `activates`/`produces` (degrades, metabolizes, catalyzes, binds, regulates, converts, transports, modifies)
- 3 terms -> `is_a` (is a, belongs to, classified as)
- 3 genetic/functional mappings (is_a_variant_of -> is_variant_of, integrated_into -> integrated_in, has metabolic capability -> has_capability)
- 2 metric-related mappings (increases titer by -> increases, enhanced production -> activates)
- 1 host mapping (used as host for production of -> is_host_for)

**Delta significance**: Entirely new pipeline stage. Without relation normalization, the same biological relationship expressed differently across papers ("enhances", "upregulates", "stimulates") would create separate, disconnected edge types in the graph. This normalization is essential for graph-level analysis and querying.

---

### 4B. Entity Normalization

| | Original NEKO | Updated Knowledge |
|---|---|---|
| **Similarity threshold** | 0.80 | 0.85 (stricter -- fewer false merges) |
| **Canonical selection** | First-seen entity (arbitrary) | **Longer entity name** (more descriptive) |
| **Example** | If "E. coli" seen before "Escherichia coli K-12", "E. coli" becomes canonical | "Escherichia coli K-12" chosen over "E. coli" (more informative) |
| **Transitive chains** | Not handled -- A->B exists but if B->C also found, no resolution | Full transitive resolution: A->B, B->C resolved to A->C, B->C |
| **Circular protection** | None | Visited set detects circular references |
| **Batching** | O(n^2) pairwise, unbatched | Batched 2000x2000 blocks with PyTorch matrix operations |
| **Word boundaries** | Simple `.replace()` string substitution | Regex with `(?<![a-zA-Z0-9_])...(?![a-zA-Z0-9_])` word boundary matching |
| **Pattern compilation** | Per-row | Pre-compiled once before DataFrame loop |
| **Exclusion** | Hardcoded "Yarrowia" skip | Configurable `exclusion_keyword` parameter |
| **Validation** | None | Post-normalization validation warns about non-ontology relations that survived |

**Delta significance**: Multiple improvements here -- longer-name canonicalization preserves maximum information (critical for biological nomenclature where abbreviations lose context). Transitive chain resolution prevents inconsistency where A maps to B but B maps to C, leaving A and C unmerged. The stricter threshold (0.85 vs 0.80) reduces false merges that would conflate distinct biological entities.

---

## STEP 5: Knowledge Graph Construction

| | Original NEKO | Updated Knowledge |
|---|---|---|
| **Graph type** | `nx.Graph()` (undirected, simple) | `nx.MultiDiGraph()` (directed, multigraph) |
| **Edges** | Unlabeled, edge `title`=paper title | Labeled with `relation`, `source`=paper title, `pmid` |
| **Multiple edges** | Not supported (same node pair -> single edge) | Supported (same nodes can have multiple typed relationships from different papers) |
| **Direction** | Lost | Preserved (Subject -> Object) |
| **Triple storage** | Not stored separately | Full triple list with `{subject, relation, object, source, pmid, triple_text, natural}` |
| **`natural` field** | N/A | `"subject relation object"` as plain text -- specifically for embedding/search |
| **Deduplication** | None (relies on NetworkX internal) | Explicit case-insensitive dedup by `(subject.lower(), relation.lower(), object.lower())` |
| **Column detection** | Fixed column name | Tries `'Answer to Question 2'`, then `'Response to New Question'`, then `'Relationships'`, then scans all columns for triple patterns |

**Delta significance**: The graph structure change from undirected simple graph to directed multigraph is fundamental. It means:

- `(gene_X, activates, pathway_Y)` is now distinguishable from `(pathway_Y, activates, gene_X)`
- The same gene pair can have both `activates` AND `inhibits` edges from different studies
- Provenance (which paper, which PMID) is traceable per edge

---

## STEP 6: Graph Search & Querying

| | Original NEKO | Updated Knowledge |
|---|---|---|
| **Search method** | Keyword substring match on node labels | Semantic cosine similarity on triple embeddings |
| **Embedding model** | N/A | `all-MiniLM-L6-v2` (384-dimensional) |
| **What is embedded** | N/A | Each triple as natural language: `"subject relation object"` |
| **Query handling** | Must match exact substring in node label | Natural language query encoded and compared against all triple embeddings |
| **Expansion** | BFS neighbor expansion (depth 1-2) | Top-K results + multi-hop expansion (successors + predecessors in directed graph) |
| **Parameters** | Fixed depth=1 or depth=2 | `top_k=50`, `threshold=0.25`, minimum 10 results guaranteed |
| **Caching** | None | `KnowledgeGraphSearcher` instances cached per `goal_id` with thread-safe locking |

**Delta significance**: This is a paradigm shift in how the knowledge graph is queried. Original: you must know the exact entity name and search for it as a string. Updated: you can ask "What genes improve ethanol production in yeast?" and the system finds semantically relevant triples regardless of exact wording. This is the "Graph RAG" contribution -- combining structured knowledge graphs with embedding-based retrieval.

---

## STEP 7: Answer Generation

| | Original NEKO | Updated Knowledge |
|---|---|---|
| **Input to LLM** | Comma-joined node names from subgraph (up to 30,000 chars) | Two pathways: (A) raw triples with citations, (B) triples converted to natural language sentences |
| **Context** | Just entity names, no relationships | Full triples with relation types, paper titles, PMIDs |
| **System prompt** | `"You are a helpful assistant."` | 8-rule strict anti-hallucination system OR simple scientific assistant |
| **Anti-hallucination** | None | Rules including: "NEVER use training data", "every sentence traceable to triples", "cite exact triple", "say NOT FOUND IN PROVIDED DATA for gaps" |
| **Temperature** | Not specified | 0.0 (strict pathway) or 0.4 (robust pathway) |
| **Conversation context** | None -- single-shot | Chat history with previous Q&A pairs for follow-up questions |
| **Post-processing** | None | `_clean_llm_report()`: strips raw triple notation, removes "Data Coverage" sections, cleans boilerplate (5 regex passes) |
| **Triple-to-sentence conversion** | N/A | 28-entry relation-to-natural-language mapping (e.g., `has_capability` -> "has the capability for", `is_host_for` -> "serves as a host for") |
| **Citation** | Paper title on edge tooltip only | Inline `[Source: title] [PMID: pmid]` in answer text |

**Delta significance**: The answer generation went from "here are some entity names, write a report" to a grounded, evidence-based system where every claim must be traceable to specific extracted triples with paper citations. The anti-hallucination framework is a significant methodological contribution for trustworthy scientific AI systems.

---

## STEP 8: LLM Infrastructure

| | Original NEKO | Updated Knowledge |
|---|---|---|
| **Models** | GPT-4-turbo-preview (API) OR Qwen1.5-72B-Chat (local, 4-7 GPUs) | 13 models across 2 providers (Groq: 9 models, Cerebras: 4 models) |
| **Deployment** | Single model, single provider | Multi-provider with cross-provider fallback |
| **Rate limiting** | None | Sliding window per client (20 req/min Groq, 60 req/min per Cerebras key) |
| **API keys** | 1 key | Up to 6 keys (1 Groq + 5 Cerebras) |
| **Theoretical throughput** | Sequential, one article at a time | 320 req/min combined (20 + 5x60), parallelized across threads |
| **Error handling** | None (fails silently) | Classified: RateLimitError (30s cooldown), BadRequestError (permanent blacklist), APIStatusError (15s cooldown) |
| **Model fallback** | None | Priority-ordered fallback across all models within provider, then cross-provider |
| **Thread distribution** | Single-threaded | Articles distributed proportionally to rate limits across daemon threads |
| **Reasoning model handling** | N/A | `<think>...</think>` blocks stripped from reasoning model outputs |
| **Cost** | GPT-4 API costs OR expensive local GPU | Free-tier API providers (Groq, Cerebras) |

**Delta significance**: From single-model, single-threaded, expensive processing to a resilient multi-model, multi-provider, parallelized system. This is not just infrastructure -- it enables processing orders of magnitude more articles, which directly impacts the comprehensiveness of the knowledge graph.

---

## Summary: 8 Pipeline Stages, Each with Research Deltas

| Stage | Original | Updated | Core Delta |
|---|---|---|---|
| **1. Query** | Manual keyword | LLM concept decomposition -> 4-tier queries | Systematic retrieval coverage |
| **2. Chunking** | None / dumb split | Sentence-boundary with scientific abbreviation handling | Preserves semantic units |
| **3. Extraction** | 1 pass, untyped pairs | 3 passes + validation, typed triples with 13-relation ontology | Semantic knowledge representation + higher recall |
| **4. Confidence** | None | Jaccard stability score | Quantitative per-article reliability |
| **5. Normalization** | Similarity>0.8, arbitrary canonical | Relation ontology (41 synonyms), entity resolution (longer-name canonical, transitive chains, threshold 0.85) | Information-preserving standardization |
| **6. Graph** | Undirected simple graph | Directed multigraph with typed, attributed edges | Preserves causality + multiplicity + provenance |
| **7. Search** | Keyword substring + BFS | Semantic embedding search (Graph RAG) | Natural language graph querying |
| **8. Answers** | Generic summarization | Anti-hallucination grounded generation with triple citations | Evidence-based trustworthy outputs |
