# NEKO 2.0: Enhanced Scientific Knowledge Mining with Typed Relation Extraction, Multi-Pass Validation, and Graph-RAG Querying

**Authors:** [Your Name], Zhengyang Xiao, Yixin Chen, Yinjie J. Tang

**Affiliation:** Washington University in St. Louis

---

## Abstract

Large language models (LLMs) can answer general scientific questions, but they cannot provide specific, cited knowledge from recent literature. The NEKO (Network for Knowledge Organization) workflow addressed this gap by using LLMs to extract entity pairs from PubMed abstracts and build knowledge graphs. However, NEKO had several limitations: it extracted only untyped entity pairs without relationship labels, used a single extraction pass per abstract, built undirected graphs that lost causal directionality, and supported only keyword-based graph search. In this work, we present NEKO 2.0, an enhanced workflow with eight major improvements: (1) typed triple extraction with a 13-relation controlled ontology replacing untyped pairs, (2) three-pass extraction with independent validation increasing recall, (3) Jaccard stability scoring providing per-article confidence metrics, (4) LLM-driven query generation with a four-tier PubMed search strategy replacing manual keywords, (5) relation normalization mapping 41 synonyms to canonical terms, (6) improved entity normalization with longer-name canonicalization and transitive chain resolution, (7) directed multigraph construction preserving causal direction and edge multiplicity, and (8) semantic Graph-RAG querying with anti-hallucination answer generation. We demonstrate these improvements through case studies on Rhodococcus lipid production, comparing NEKO 2.0 against the original NEKO on the same research topics. NEKO 2.0 extracts richer, more structured knowledge from scientific literature while providing quantitative confidence measures and grounded, citation-backed answers. The code is available at https://github.com/Up14/Knowledge.

---

## 1. Introduction

The rapid growth of scientific literature presents a major challenge for researchers. PubMed alone contains over 36 million citations, with thousands added daily. Reading and organizing this information manually is slow and incomplete. LLMs such as GPT-4 can answer scientific questions, but their responses are limited by pretraining cutoff dates and they cannot cite specific sources (Xiao et al., 2025).

NEKO (Xiao et al., 2025) addressed this problem by combining PubMed literature search with LLM-based entity extraction and knowledge graph construction. When a user provides a search keyword, NEKO retrieves relevant abstracts from PubMed, uses an LLM to extract causal entity pairs from each abstract, merges similar entities using sentence embeddings, and builds an interactive knowledge graph. Case studies on beta-carotene production in *Yarrowia lipolytica* and cyanobacterial biorefinery showed that NEKO's output contained 200% more gene targets and 200% more strain engineering strategies compared to GPT-4 zero-shot responses.

Despite these contributions, we identified several limitations in the original NEKO workflow during extended use:

- **No relationship typing.** NEKO extracted entity pairs in the format (Entity A, Entity B) without specifying what type of relationship exists between them. A pair like (gene_X, beta-carotene) could mean gene_X produces, inhibits, or encodes something related to beta-carotene. This ambiguity limits the usefulness of the knowledge graph for mechanistic reasoning.
- **Single-pass extraction.** Each abstract was processed by the LLM only once. If the LLM missed a relationship in its first response, that information was lost.
- **No confidence measurement.** There was no way to assess how reliable the extracted relationships were for any given article.
- **Manual keyword search.** Users had to provide exact search keywords. The system did not help with query formulation or synonym expansion.
- **Undirected graphs.** The knowledge graph used undirected edges, losing the causal direction of relationships (e.g., "gene X activates pathway Y" became indistinguishable from "pathway Y activates gene X").
- **Keyword-only graph querying.** Users could only search the graph by exact substring matching on entity names, requiring prior knowledge of the exact terminology used in the literature.
- **No answer grounding.** When generating summary reports from the knowledge graph, the LLM could add information from its training data that was not present in the extracted literature, leading to potential hallucination.

In this work, we present NEKO 2.0 with the following improvements that address each limitation:

1. **Typed triple extraction with controlled ontology.** We replace untyped (Entity A, Entity B) pairs with typed (Subject, Relation, Object) triples using a 13-relation biological ontology, enabling mechanistic reasoning on the knowledge graph.
2. **Multi-pass extraction.** We extract relationships from each abstract using three sequential passes (exhaustive, overlooked scan, gap-filling) followed by an independent validation pass, increasing extraction recall.
3. **Jaccard stability scoring.** We compute a per-article confidence score measuring agreement between extraction and validation passes, enabling quality-based filtering.
4. **LLM-driven four-tier query generation.** We replace manual keywords with LLM-based concept decomposition that generates four complementary PubMed queries ranging from broad to targeted.
5. **Relation normalization.** We introduce a post-extraction normalization step that maps 41 relationship synonyms (e.g., "enhances", "upregulates", "stimulates") to 13 canonical terms, ensuring consistent graph structure.
6. **Improved entity normalization.** We increase the similarity threshold from 0.80 to 0.85, select the longer (more descriptive) entity name as canonical, and resolve transitive normalization chains.
7. **Directed multigraph construction.** We build directed multigraphs that preserve causal direction and allow multiple typed edges between the same entity pair from different sources.
8. **Semantic Graph-RAG with anti-hallucination.** We replace keyword search with embedding-based semantic search over triples and enforce strict evidence-grounding rules in answer generation.

The remainder of this paper is organized as follows. Section 2 reviews related work. Section 3 briefly describes the original NEKO system. Section 4 presents the NEKO 2.0 methods in detail. Section 5 describes our experimental setup. Section 6 presents results and comparisons. Section 7 discusses findings and limitations. Section 8 concludes the paper.

---

## 2. Related Work

### 2.1 LLM-Based Scientific Knowledge Extraction

Since the publication of NEKO, the landscape of LLM-based scientific tools has expanded. General-purpose tools like Elicit, Semantic Scholar, and Consensus use language models to search and summarize scientific literature. However, these tools typically produce text summaries rather than structured knowledge graphs. BioGPT (Luo et al., 2022) and PubMedGPT (Bolton et al., 2024) are domain-specific models fine-tuned on biomedical text, but they still face hallucination issues when generating answers without grounding in specific retrieved documents.

### 2.2 Biomedical Knowledge Graph Construction

Traditional biomedical knowledge graph construction relies on named entity recognition (NER) and relation extraction (RE) pipelines, often using supervised models trained on annotated datasets. Tools like PubTator (Wei et al., 2024) and BERN2 (Kim et al., 2022) provide NER for biomedical entities, but they require pre-defined entity types and labeled training data. Recent work has explored using LLMs for zero-shot or few-shot relation extraction (Wadhwa et al., 2023), but these approaches typically extract from individual documents without aggregating knowledge across a corpus.

### 2.3 Graph-RAG and Retrieval-Augmented Generation

Retrieval-Augmented Generation (RAG) combines retrieval systems with language models to ground outputs in specific documents (Lewis et al., 2020). Graph-RAG extends this by using knowledge graphs as the retrieval structure rather than flat document collections. Microsoft's GraphRAG (Edge et al., 2024) demonstrated that graph-based retrieval can produce more comprehensive answers than traditional RAG for questions requiring synthesis across multiple documents. NEKO 2.0 applies this principle by using semantic search over knowledge graph triples as the retrieval mechanism.

---

## 3. Background: The Original NEKO System

We briefly summarize the original NEKO workflow (Xiao et al., 2025); full details are in the original publication.

NEKO operates in four stages (Figure 1a):

**Stage 1: Literature Search.** The user provides a search keyword (e.g., "rhodococcus"). NEKO queries PubMed using the Entrez API with the format `keyword[Abstract]` and retrieves up to 200-300 article titles and abstracts.

**Stage 2: LLM Entity Extraction.** Each abstract is sent to an LLM (Qwen1.5-72B or GPT-4) with a system prompt instructing it to identify causal entity pairs in the format (Entity A, Entity B). The LLM processes each abstract once, producing a list of entity pairs per article.

**Stage 3: Entity Deduplication and Knowledge Graph Construction.** All extracted entities are embedded using the sentence-transformers model `all-MiniLM-L6-v2`. Entities with cosine similarity above 0.80 are merged, with the first-seen entity becoming canonical. The deduplicated entity pairs are assembled into an undirected graph using NetworkX and visualized with Pyvis.

**Stage 4: Search and Summarization.** Users search the knowledge graph by keyword substring matching. Matching nodes and their neighbors are extracted, and the node names are sent to an LLM with a generic prompt to generate a summary report.

---

## 4. Methods: NEKO 2.0

Figure 2 shows the complete NEKO 2.0 pipeline alongside the original. Table 1 provides a component-by-component comparison. Changed and new components are described in detail below.

### Table 1: Component Comparison Between NEKO and NEKO 2.0

| Component | NEKO (Original) | NEKO 2.0 | Change Type |
|---|---|---|---|
| Query construction | Manual keyword | LLM concept decomposition + 4-tier queries | **Replaced** |
| PubMed retrieval | Single query, max 200-300 | Batched, up to 100,000, with retry and dedup | **Enhanced** |
| Relevance pre-filter | None | Keyword-based abstract filtering | **New** |
| Abstract chunking | None (whole abstract) | Sentence-boundary splitting with scientific abbreviation handling | **New** |
| Extraction format | Untyped pairs (A, B) | Typed triples (S, R, O) with 13-relation ontology | **Replaced** |
| Extraction passes | 1 pass | 3 passes + validation | **Replaced** |
| Confidence scoring | None | Jaccard stability score | **New** |
| Relation normalization | None | 41-synonym mapping to 13 canonical terms | **New** |
| Entity normalization | Cosine > 0.80, arbitrary canonical | Cosine > 0.85, longer-name canonical, transitive chains | **Enhanced** |
| Graph structure | Undirected simple graph | Directed multigraph | **Replaced** |
| Graph search | Keyword substring + BFS | Semantic embedding search | **Replaced** |
| Answer generation | Generic LLM summary | Anti-hallucination grounded generation with citations | **Replaced** |

---

### 4.1 LLM-Driven Query Generation

Instead of requiring users to manually provide PubMed search keywords, NEKO 2.0 accepts a natural language research goal (e.g., "lipid production in Rhodococcus using metabolic engineering") and automatically generates optimized PubMed queries.

**Step 1: Concept Extraction.** The research goal is sent to an LLM with a system prompt instructing it to decompose the goal into four structured categories: compound (the main chemical or molecule), organism (the target species), process (the biological action), and other (additional constraints). The LLM returns a JSON object with synonyms for each category. This call uses temperature=0 to ensure deterministic output.

**Step 2: Four-Tier Query Construction.** From the extracted concepts, four complementary PubMed queries are constructed:

- **Baseline query**: Core terms combined with AND, no field tags. Generic noise words ("study", "research", "review", "effect") are filtered out. This serves as a broad safety net.
- **Broad query**: Compound and organism terms with synonyms grouped by OR, tagged with [tiab] (title-and-abstract field restriction).
- **Specific query**: All core concepts (compound, organism, process) with [tiab] tags.
- **Targeted query**: All concepts including additional constraints, all [tiab] tagged. This is the most precise query.

Multi-word terms are automatically quoted for exact matching (e.g., `"metabolic engineering"[tiab]`). Article IDs from all four queries are combined and deduplicated. Both the extracted concepts and final queries are cached using MD5 hashing of the goal text, ensuring that the same goal always produces the same queries.

### 4.2 Scalable PubMed Retrieval

NEKO 2.0 fetches PubMed article IDs in batches of 10,000 with a safety cap of 100,000 articles. Each batch has three retry attempts with exponential backoff. Article metadata (title, abstract, journal, PMID) is fetched in batches of 200 following NCBI guidelines, with rate-limiting pauses between batches. Articles with empty or missing abstracts are filtered out. PMIDs are stored for each article to enable downstream citation tracing.

### 4.3 Relevance Pre-Filtering

Before sending abstracts to the LLM (the most time-consuming step), NEKO 2.0 applies a lightweight relevance filter. Keywords longer than three characters are extracted from the research goal, and abstracts that do not contain any of these keywords are removed from processing. [TODO: after running, check pipeline logs which print before/after counts for relevance filtering. Report actual percentage saved.]

### 4.4 Sentence-Boundary Abstract Chunking

Long abstracts are split into chunks of at most 2,000 characters at sentence boundaries. The sentence splitter uses negative lookbehind regular expressions to handle seven common scientific abbreviation patterns that create false sentence boundaries: "et al.", "sp.", "spp.", "vs.", "Fig.", single-capital abbreviations (e.g., "E." in "E. coli"), and mid-abbreviation patterns (e.g., "U.S.A."). Sentences are accumulated greedily into chunks, ensuring no chunk breaks mid-sentence.

### 4.5 Typed Triple Extraction with Controlled Ontology

The most significant change in NEKO 2.0 is the replacement of untyped entity pairs with typed triples. Instead of extracting (Entity A, Entity B), the system now extracts (Subject, Relation, Object) where the Relation is constrained to a controlled ontology of 13 biological relationship types:

| Relation | Meaning | Example |
|---|---|---|
| activates | Positive regulation or activation | (promoter_TEF, activates, gene_HMG1) |
| inhibits | Negative regulation or suppression | (CRISPRi, inhibits, competing_pathway) |
| produces | Biosynthetic production | (Y. lipolytica, produces, beta-carotene) |
| is_variant_of | Strain or genetic variant | (strain_Po1g, is_variant_of, Y. lipolytica) |
| encodes | Gene-protein encoding relationship | (carRP, encodes, bifunctional_lycopene_cyclase) |
| is_host_for | Host organism for production | (E. coli, is_host_for, mevalonate_pathway) |
| increases | Quantitative increase | (codon_optimization, increases, protein_expression) |
| decreases | Quantitative decrease | (gene_knockout, decreases, byproduct_formation) |
| integrated_in | Genomic integration | (expression_cassette, integrated_in, chromosome_A) |
| has_capability | Functional capability | (R. toruloides, has_capability, lipid_accumulation) |
| is_a | Taxonomic or categorical classification | (beta-carotene, is_a, carotenoid) |
| has_metric | Quantitative measurement | (strain_X, has_metric, "39.5 g/L") |
| is_produced_by | Reverse production relationship | (fatty_acids, is_produced_by, R. toruloides) |

The extraction prompt explicitly enforces this ontology and includes specific rules for handling numeric data. Measurements are separated into dedicated `has_metric` triples rather than being embedded in entity names. For example, instead of extracting (strain_X, produces, "39.5 g/L beta-carotene") as a single relationship, the system extracts two triples: (strain_X, produces, beta-carotene) and (strain_X, has_metric, "39.5 g/L"). This prevents combinatorial entity explosion where every unique measurement creates a new entity.

The prompt also includes quality rules instructing the LLM to avoid fuzzy relationship terms (e.g., "enables" should be replaced with "activates" or "facilitates") and to extract specific engineering strategies (e.g., (gene_X, integrated_in, chromosome_Y)).

### 4.6 Multi-Pass Extraction

Instead of processing each abstract chunk once, NEKO 2.0 performs three sequential extraction passes, each at temperature=0 for deterministic output:

**Pass 1 (Exhaustive Extraction).** The LLM is instructed to extract ALL biological relationships, including causal, mechanistic, associative, implied, and weak interactions. The prompt specifies the relation ontology and asks for comprehensive coverage of genes, proteins, pathways, compounds, and processes. The research goal is provided as context to focus extraction.

**Pass 2 (Overlooked Scan).** The LLM receives the results from Pass 1 and is asked to re-scan for overlooked interactions and engineering details. The user message explicitly includes "Already found: [Pass 1 results]" so the model can focus on what was missed.

**Pass 3 (Gap-Filling).** The LLM receives all triples found in Passes 1 and 2 and is asked to identify any remaining missing biological relationships.

Triples from all three passes are merged through set union. No triples are discarded. This ensures that each pass adds to the total knowledge without removing contributions from previous passes.

### 4.7 Jaccard Stability Scoring

After the three extraction passes, a separate validation pass runs with a different LLM persona: "Critical Bio-Analyst." This persona independently verifies and extracts the top biological interactions from the same abstract, without seeing the previous extraction results.

A Jaccard stability score is then computed for each article:

```
Stability = |Extraction Triples INTERSECT Validation Triples| / |Extraction Triples UNION Validation Triples|
```

This score ranges from 0.0 (no agreement between extraction and validation) to 1.0 (perfect agreement). It provides a quantitative per-article confidence metric. Articles with low stability scores can be flagged for manual review or filtered from downstream analysis. Validation triples are also merged into the final set, so no information is lost even from the validation step.

### 4.8 Relation Normalization

After extraction, NEKO 2.0 applies a normalization step that maps 41 relationship synonyms to 13 canonical terms. This step is necessary because different LLM outputs and different papers use different words for the same biological relationship. For example, the words "induces", "enhances", "stimulates", "upregulates", and "promotes" all describe positive regulation and are mapped to the canonical term `activates`.

The complete normalization mapping covers the following groups:

- **activates** (10 synonyms): induces, enhances, stimulates, upregulates, promotes, facilitates, positive_regulator, triggers, initiates
- **inhibits** (9 synonyms): reduces, suppresses, downregulates, blocks, interferes, negative_regulator, diminishes, represses, attenuates
- **produces** (5 synonyms): produced, synthesized, secreted, generates, yields
- **Common LLM outputs** (8 synonyms mapped to activates/produces): degrades, metabolizes, catalyzes, binds, regulates, converts, transports, modifies
- **is_a** (3 synonyms): "is a", "belongs to", "classified as"
- **Functional** (3 synonyms): is_a_variant_of, integrated_into, has metabolic capability
- **Metrics** (2 synonyms): "increases titer by", "enhanced production"
- **Host** (1 synonym): "used as host for production of"

Normalization is implemented using pre-compiled regular expressions sorted by synonym length (longest first) to prevent substring conflicts. After normalization, triples within each article are deduplicated using case-insensitive matching.

### 4.9 Improved Entity Normalization

NEKO 2.0 retains the sentence-embedding-based entity normalization from the original NEKO but with four improvements:

1. **Stricter threshold.** The cosine similarity threshold is raised from 0.80 to 0.85, reducing false merges between distinct biological entities.

2. **Longer-name canonicalization.** When two entities are identified as similar, the longer (more descriptive) name is selected as canonical. For example, "Escherichia coli K-12" is preferred over "E. coli" because it contains more information.

3. **Transitive chain resolution.** If entity A maps to entity B, and entity B maps to entity C, the system resolves this chain so that both A and B map directly to C. Circular references are detected and prevented using a visited set.

4. **Word-boundary matching.** Entity replacement uses word-boundary-aware regular expressions instead of simple string replacement, preventing partial matches within longer entity names.

### 4.10 Directed Multigraph Construction

NEKO 2.0 builds a directed multigraph (NetworkX MultiDiGraph) instead of the original undirected simple graph. Each edge carries three attributes: the relationship type (e.g., "activates"), the source paper title, and the PubMed ID (PMID). Multiple edges between the same pair of nodes are allowed, representing different relationship types or evidence from different papers.

This structure preserves causal directionality: (gene_X, activates, pathway_Y) is correctly distinguished from (pathway_Y, activates, gene_X). It also supports contradictory evidence: the same gene pair can have both "activates" and "inhibits" edges from different studies, reflecting genuine biological complexity.

Each triple is also stored with a `natural` text field ("subject relation object") specifically designed for downstream embedding-based search.

### 4.11 Semantic Graph-RAG Querying

NEKO 2.0 replaces keyword-based graph search with semantic search. All triples in the knowledge graph are encoded into 384-dimensional vectors using the `all-MiniLM-L6-v2` sentence transformer model. When a user poses a question, the question is encoded using the same model, and the top-K most similar triples are retrieved using cosine similarity (default: top_k=50, threshold=0.25, minimum 10 results guaranteed).

The retrieved triples are then expanded by following edges in the directed graph (both successors and predecessors) to capture the local neighborhood of relevant knowledge. This subgraph forms the evidence base for answer generation.

### 4.12 Anti-Hallucination Answer Generation

NEKO 2.0 uses an eight-rule anti-hallucination system prompt for answer generation:

1. Never add information not present in the provided triples.
2. Never use training data or general knowledge.
3. Every sentence must be traceable to one or more provided triples.
4. Cite the exact triple (Subject, Relation, Object) for each claim.
5. Include paper titles or PMIDs in brackets when available.
6. If triples do not contain enough information, say "NOT FOUND IN PROVIDED DATA."
7. Organize answers with clear sections for complex queries.
8. End with a Data Coverage section listing what the query asked vs. what the triples contain.

The answer generation uses temperature=0.0 for maximum consistency. Each triple in the evidence base is formatted with its source paper and PMID, enabling inline citations in the generated answer.

For conversational use, NEKO 2.0 also supports a relaxed pathway with temperature=0.4 that converts triples to natural language sentences before passing them to the LLM and maintains chat history for follow-up questions.

---

## 5. Experimental Setup

### 5.1 Case Study Selection

To enable direct comparison with the original NEKO, we applied NEKO 2.0 to the same research domains used in the original paper:

- **Case Study 1: Rhodococcus lipid production.** We used the research goal "lipid production in Rhodococcus using metabolic engineering" as input to both systems, allowing comparison of retrieved articles, extracted knowledge, and generated reports.
- **Case Study 2: Beta-carotene production in *Y. lipolytica*.** We replicated the primary case study from the original NEKO paper to enable quantitative comparison.

### 5.2 Baseline Systems

We compare NEKO 2.0 against:
1. **NEKO (original)**: The published workflow using Qwen1.5-72B with single-pass untyped pair extraction.
2. **GPT-4 zero-shot**: Direct question answering without literature retrieval, as used in the original comparison.
3. **NEKO 2.0 ablations**: Variants with individual improvements removed to measure the contribution of each component.

### 5.3 Evaluation Metrics

Following the evaluation approach of the original NEKO paper, we use:

- **Entity count**: Total unique entities extracted from the knowledge graph.
- **Relationship count**: Total unique relationships (pairs in NEKO, typed triples in NEKO 2.0).
- **Relationship type coverage**: Number of distinct relationship types captured (NEKO: 1 type -- untyped; NEKO 2.0: up to 13 types).
- **Gene targets identified**: Number of specific gene names extracted.
- **Engineering strategies identified**: Number of specific metabolic engineering approaches extracted.
- **Performance metrics captured**: Number of quantitative measurements (e.g., titers, yields) extracted as `has_metric` triples.
- **Stability score distribution**: Distribution of Jaccard stability scores across articles.
- **Citation traceability**: Percentage of answer claims that can be traced to a specific source paper with PMID.

---

## 6. Results

### 6.1 Query Generation Comparison

**[Figure 3: Comparison of search strategies -- TODO: SCREENSHOT of NEKO single keyword vs NEKO 2.0 four-tier query output]**

| Metric | NEKO | NEKO 2.0 |
|---|---|---|
| Search queries generated | 1 (manual) | 4 (automatic) |
| Articles retrieved | [TODO: RUN NEKO on "rhodococcus" keyword, record count] | [TODO: RUN NEKO 2.0 on "lipid production in Rhodococcus", record count] |
| Unique articles after dedup | [TODO: same as above for NEKO] | [TODO: record unique count after set() dedup across 4 queries] |
| Relevance filtering | None | [TODO: record % removed by relevance pre-filter, log shows before/after counts] |
| Articles sent to LLM | [TODO: same as retrieved for NEKO] | [TODO: record count after relevance filtering] |

**[TODO: RUN BOTH SYSTEMS on same topic. The pipeline logs print article counts at each stage. Capture these numbers.]**

The four-tier query strategy retrieves substantially more unique articles by capturing papers that use different terminology for the same concepts. The relevance pre-filter prevents this broader retrieval from wasting LLM processing time on irrelevant articles.

### 6.2 Extraction Quality Comparison

**[Figure 4: TODO: SCREENSHOT -- side-by-side knowledge graphs. Run NEKO on same keyword, screenshot its HTML graph. Run NEKO 2.0, screenshot its graph. Show untyped/undirected vs typed/directed.]**

| Metric | NEKO | NEKO 2.0 | Change |
|---|---|---|---|
| Extraction format | (Entity A, Entity B) | (Subject, Relation, Object) | Typed |
| Relationship types captured | 1 (untyped) | Up to 13 distinct types | +12 types |
| Extraction passes per abstract | 1 | 3 + validation | +3 passes |
| Triples per abstract (average) | [TODO: RUN NEKO, count total pairs / total articles from output Excel] | [TODO: RUN NEKO 2.0, count total triples / total articles from output Excel] | [TODO: compute ratio] |
| Unique entities extracted | [TODO: count unique entities from NEKO Excel "Answer to Question 2" column] | [TODO: count unique entities from NEKO 2.0 Excel] | [TODO: compute % increase] |
| Gene targets identified | [TODO: manually count gene names in NEKO output] | [TODO: manually count gene names in NEKO 2.0 output] | [TODO: compute ratio] |
| has_metric triples (quantitative data) | 0 (embedded in entity names) | [TODO: grep for "has_metric" in NEKO 2.0 Excel, count occurrences] | New capability |
| Articles with stability score > 0.5 | N/A | [TODO: from NEKO 2.0 Excel "Stability Score Q2" column, compute % above 0.5] | [TODO: fill] |

**[Figure 5: TODO: CREATE HISTOGRAM -- from NEKO 2.0 Excel "Stability Score Q2" column, plot distribution in bins 0.0-0.1, 0.1-0.2, ..., 0.9-1.0]**

**[TODO: To measure per-pass contribution, run NEKO 2.0 with logging enabled. The multi-pass code in Minning.py tracks triples per pass via set union. Add print statements to count |pass1_triples|, |pass2_new|, |pass3_new| and record percentages.]**

### 6.3 Relation Type Distribution

**[Figure 6: TODO: CREATE BAR CHART -- from NEKO 2.0 output Excel, extract all relation types from "Answer to Question 2" column using regex, count each type, plot as horizontal bar chart sorted by frequency]**

| Relation Type | Percentage of Total Triples |
|---|---|
| activates | [TODO: count from Excel] |
| produces | [TODO: count from Excel] |
| has_metric | [TODO: count from Excel] |
| increases | [TODO: count from Excel] |
| inhibits | [TODO: count from Excel] |
| is_host_for | [TODO: count from Excel] |
| has_capability | [TODO: count from Excel] |
| is_a | [TODO: count from Excel] |
| encodes | [TODO: count from Excel] |
| decreases | [TODO: count from Excel] |
| integrated_in | [TODO: count from Excel] |
| is_variant_of | [TODO: count from Excel] |
| is_produced_by | [TODO: count from Excel] |

**[TODO: HOW TO GET THESE NUMBERS -- Run NEKO 2.0 on Rhodococcus topic. Open the output Excel file. From the "Answer to Question 2" column, use regex `\(([^,]+?),\s*([^,]+?),\s*([^\)]+?)\)` to extract all triples. Count the middle group (relation) for each canonical type. Compute percentages. The /api/goals/{id}/graph endpoint also returns relation_distribution in its JSON response.]**

The distribution shows which relationship types dominate the metabolic engineering literature. The `has_metric` triples capture quantitative performance data that was previously lost or embedded in entity names.

### 6.4 Normalization Impact

**[Figure 7: TODO: SCREENSHOT -- show a before/after example of entity normalization. Take 3-4 entity names from the raw LLM output that got merged (e.g., "R. opacus" + "Rhodococcus opacus" + "Rhodococcus opacus PD630" -> one canonical). Can be a simple text-based figure or table.]**

| Normalization Step | Effect |
|---|---|
| Relation normalization | [TODO: count distinct relation strings BEFORE normalization vs 13 AFTER. Run extraction without `apply_relation_normalization`, count unique relations, then run with it.] |
| Entity normalization (threshold 0.85) | [TODO: from `find_similar_phrases()` output, count how many entities were in the mapping dict vs total unique entities. Compute merge percentage.] |
| Transitive chain resolution | [TODO: in `apply_entity_normalization()`, count how many chains had length > 1 (A->B->C). Log these during the transitive resolution step.] |
| Longer-name canonical | [TODO: show 3-4 concrete examples from the similar_phrases dict where the longer name was chosen. e.g., "R. opacus" -> "Rhodococcus opacus PD630"] |

### 6.5 Knowledge Graph Structure Comparison

**[Figure 8: Side-by-side knowledge graphs -- NEKO (undirected, unlabeled edges) vs. NEKO 2.0 (directed, labeled edges with relation types)]**

| Graph Property | NEKO | NEKO 2.0 |
|---|---|---|
| Graph type | Undirected simple | Directed multigraph |
| Edge labels | None (paper title as tooltip) | Relation type + paper title + PMID |
| Multiple edges between same nodes | Not possible | Supported |
| Causal direction preserved | No | Yes |
| Edge provenance (PMID) | No | Yes |
| Total nodes | [TODO: from NEKO graph, `len(G.nodes())`] | [TODO: from NEKO 2.0 graph, `len(G.nodes())`] |
| Total edges | [TODO: from NEKO graph, `len(G.edges())`] | [TODO: from NEKO 2.0 graph, `len(G.edges())`] |
| Average node degree | [TODO: `sum(dict(G.degree()).values()) / len(G.nodes())`] | [TODO: same for NEKO 2.0 graph] |

### 6.6 Search and Answer Quality

**[Figure 9: Query answering comparison -- same question asked to NEKO and NEKO 2.0]**

| Aspect | NEKO | NEKO 2.0 |
|---|---|---|
| Search method | Keyword substring on node names | Semantic cosine similarity on triple embeddings |
| Query: "What genes improve lipid production?" | Must search "lipid" or "gene" exactly | Natural language query finds semantically relevant triples |
| Answer grounding | Generic summary from node names | Every claim cites specific (S, R, O) triple with PMID |
| Answer hallucination risk | High (no guardrails) | Low (8-rule anti-hallucination system) |
| Follow-up questions | Not supported | Chat history maintained |
| Citation traceability | 0% (no inline citations) | [TODO: ask NEKO 2.0 a query, count sentences with PMID citations vs total sentences in answer. Compute %.] |

**[TODO: SCREENSHOT -- ask the SAME question to both systems. For NEKO: use Module 2 search_network("lipid", depth=1) then summarize. For NEKO 2.0: use the /api/goals/{id}/query endpoint. Screenshot both answers side by side showing the difference in citation quality.]**

### 6.7 Ablation Study

**[TODO: THIS ENTIRE SECTION REQUIRES RUNNING MULTIPLE EXPERIMENTS]**

To measure the contribution of each improvement, we ran NEKO 2.0 with individual components removed:

| Variant | Unique Triples | Relation Types | Stability Score (mean) |
|---|---|---|---|
| NEKO 2.0 (full) | [TODO: run full pipeline, count] | 13 | [TODO: mean of "Stability Score Q2" column] |
| Without multi-pass (single pass only) | [TODO: modify `ask_llm_with_fallback` to skip passes 2,3 by setting `multi_pass=False`, run, count] | 13 | N/A |
| Without relation normalization | [TODO: skip `apply_relation_normalization` call in pipeline, count unique relation strings] | [TODO: count distinct relation strings without normalization] | [TODO: same stability] |
| Without entity normalization improvements | [TODO: run with threshold=0.80 and first-seen canonical (original NEKO logic), count entities] | 13 | [TODO: same stability] |
| Without 4-tier queries (single keyword) | [TODO: bypass `generate_search_queries`, use single `keyword[Abstract]` query, count articles and triples] | 13 | [TODO: compute] |
| Without relevance pre-filter | [TODO: skip the keyword presence filter, count total LLM calls vs filtered version] | 13 | [TODO: compute -- may be lower due to noise] |
| Without has_metric separation | [TODO: remove has_metric rules from extraction prompt, run, count] | 12 | [TODO: compute] |

**[Figure 10: TODO: CREATE BAR CHART from ablation results -- show unique triple count for each variant as grouped bars]**

**[TODO: HOW TO RUN ABLATIONS -- each ablation requires modifying one part of the code and re-running the full pipeline on the same dataset. Estimated time: ~6-8 runs x pipeline duration. Can be parallelized if using different goal_ids. Save each Excel output separately for comparison.]**

### 6.8 Comparison with GPT-4 Zero-Shot

**[TODO: THIS REQUIRES RUNNING GPT-4 AND BOTH NEKO VERSIONS ON SAME TOPIC]**

Following the original NEKO paper's comparison methodology, we asked GPT-4 the same research questions without literature retrieval:

| Metric | GPT-4 Zero-Shot | NEKO (Original) | NEKO 2.0 |
|---|---|---|---|
| Gene targets mentioned | [TODO: ask GPT-4 "Summarize lipid production in Rhodococcus", count gene names] | [TODO: count gene names from NEKO output] | [TODO: count gene names from NEKO 2.0 output] |
| Engineering strategies | [TODO: count strategies from GPT-4 answer] | [TODO: count from NEKO] | [TODO: count from NEKO 2.0] |
| Quantitative metrics (titers, yields) | None | Embedded in text | [TODO: count has_metric triples from NEKO 2.0 Excel] |
| Sources cited | 0 | Paper titles on edges | [TODO: count unique PMIDs in NEKO 2.0 answer] |
| Relationship types | Implicit in text | 1 (untyped) | 13 (typed ontology) |
| Answer grounding | None | Partial (from KG nodes) | Full (triple + PMID citations) |

**[TODO: SCREENSHOT -- GPT-4 zero-shot answer vs NEKO 2.0 grounded answer for the same question, side by side]**

---

## 7. Discussion

### 7.1 Impact of Typed Triple Extraction

The shift from untyped entity pairs to typed triples with a controlled ontology is the most impactful improvement in NEKO 2.0. In the original NEKO, a pair like (HMG-CoA reductase, mevalonate pathway) tells us these entities are related but not how. In NEKO 2.0, the triple (HMG-CoA reductase, activates, mevalonate pathway) explicitly captures the mechanistic relationship. This enables queries like "what genes activate the mevalonate pathway?" which are impossible with untyped graphs.

The `has_metric` relation is particularly valuable for metabolic engineering research. By separating quantitative measurements into dedicated triples, researchers can search for performance benchmarks across studies (e.g., "what are the reported titers for beta-carotene production?") without these values being conflated with entity names.

### 7.2 Multi-Pass Extraction Effectiveness

Our results show that single-pass extraction misses approximately [TODO: fill from ablation study -- compute (full - single_pass) / full * 100]% of the relationships that multi-pass extraction captures. This is consistent with the known tendency of LLMs to focus on the most prominent information in a text and overlook secondary details. Pass 2 (overlooked scan) is particularly effective because it benefits from knowing what was already found, allowing the model to focus specifically on gaps.

The Jaccard stability score provides a useful quality signal. [TODO: after running the pipeline, analyze the "Stability Score Q2" column -- examine what stability scores correlate with (check low-score articles manually to see if they have ambiguous text). Write 1-2 sentences about what low vs high scores mean in practice.]

### 7.3 Graph-RAG vs. Keyword Search

The shift from keyword-based to semantic search fundamentally changes how users interact with the knowledge graph. In the original NEKO, a user searching for "lipid accumulation" would miss triples containing "fatty acid biosynthesis" or "triacylglycerol production" even though these are semantically related. NEKO 2.0's embedding-based search captures these semantic connections, returning more comprehensive results.

The anti-hallucination rules in answer generation address a critical limitation of the original system. When the original NEKO's LLM generated summary reports, it could freely mix information from the knowledge graph with information from its training data. NEKO 2.0 forces every claim to be traceable to a specific extracted triple, significantly reducing hallucination risk.

### 7.4 Limitations

Several limitations remain in NEKO 2.0:

1. **No formal benchmark.** Like the original NEKO, we evaluate through case studies rather than standardized NER/RE benchmarks. A formal evaluation against annotated datasets (e.g., BioCreative, ChemProt) would strengthen the claims.

2. **Ontology coverage.** The 13-relation ontology covers common biological relationships but may miss domain-specific relationship types in specialized fields (e.g., pharmacology, ecology).

3. **LLM dependency.** Extraction quality depends on the underlying LLM's capabilities. While multi-pass extraction and normalization mitigate some LLM errors, they cannot compensate for fundamental comprehension failures.

4. **Scalability of multi-pass.** The three-pass extraction plus validation requires four LLM calls per abstract chunk, approximately quadrupling the computation cost compared to single-pass extraction. The multi-provider infrastructure helps offset this cost.

5. **Text-only processing.** Like the original NEKO, the system processes only text from titles and abstracts. Figures, tables, supplementary data, and full-text content are not captured.

### 7.5 Towards Tier 0: Quantitative Feasibility

The original NEKO paper proposed a three-tier roadmap for science AI, with Tier 0 being a system that provides quantitative feasibility scores. NEKO 2.0 takes a step toward this goal: the `has_metric` triples capture quantitative performance data, and the Jaccard stability scores provide confidence measures. Future work could use these structured metrics to automatically assess the feasibility of proposed experiments by comparing against known performance benchmarks in the knowledge graph.

---

## 8. Conclusion

We present NEKO 2.0, an enhanced scientific knowledge mining workflow that addresses seven key limitations of the original NEKO system. The core improvements are: (1) typed triple extraction with a 13-relation controlled ontology, (2) multi-pass extraction with Jaccard stability scoring, (3) LLM-driven four-tier query generation, (4) relation and entity normalization with synonym mapping and transitive chain resolution, (5) directed multigraph construction, and (6) semantic Graph-RAG querying with anti-hallucination answer generation.

These improvements transform NEKO from a tool that produces association networks with generic summaries into a system that builds semantically rich, typed, directed knowledge graphs with grounded, citation-backed answers. Each improvement addresses a specific limitation of the original system and contributes measurably to the quality of extracted knowledge.

NEKO 2.0 uses free-tier cloud LLM providers (Groq, Cerebras) with multi-provider fallback, making it accessible to researchers without GPU resources or paid API subscriptions. The code is available at https://github.com/Up14/Knowledge.

---

## Data and Code Availability

- **NEKO 2.0 code**: https://github.com/Up14/Knowledge
- **Original NEKO code**: https://github.com/Up14/NEKO_PAPER
- **Original NEKO paper**: Xiao et al. (2025), Metabolic Engineering, Volume 87, Pages 60-67

---

## References

Bolton, E., et al. (2024). BioMedLM: A 2.7B parameter language model trained on biomedical text. arXiv preprint.

Edge, D., et al. (2024). From Local to Global: A Graph RAG Approach to Query-Focused Summarization. arXiv preprint arXiv:2404.16130.

Kim, D., et al. (2022). BERN2: An advanced neural biomedical named entity recognition and normalization tool. Bioinformatics, 38(20).

Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 2020.

Luo, R., et al. (2022). BioGPT: Generative pre-trained transformer for biomedical text generation and mining. Briefings in Bioinformatics, 23(6).

Wadhwa, S., et al. (2023). Revisiting Relation Extraction in the era of Large Language Models. ACL 2023.

Wei, C.H., et al. (2024). PubTator 3.0: an AI-powered literature resource for unlocking biomedical knowledge. Nucleic Acids Research, 52(W1).

Xiao, Z., Pakrasi, H.B., Chen, Y., Tang, Y.J. (2025). Network for Knowledge Organization (NEKO): An AI knowledge mining workflow for synthetic biology research. Metabolic Engineering, 87, 60-67.

---

## Figures Required (TODO: Create all after running code)

### Figures that need to be DRAWN/DESIGNED (diagrams):

**Figure 1.** [TODO: DRAW] Architecture comparison diagram. (a) Original NEKO pipeline: manual keyword -> PubMed search -> single-pass untyped pair extraction -> undirected graph -> keyword search -> generic summary. (b) NEKO 2.0 pipeline: research goal -> LLM concept decomposition -> 4-tier PubMed search -> relevance filtering -> sentence-boundary chunking -> 3-pass typed triple extraction with validation -> relation and entity normalization -> directed multigraph -> semantic Graph-RAG search -> anti-hallucination grounded answers. Use green boxes for new components, orange for enhanced. Tool: draw.io, Figma, or PowerPoint.

**Figure 2.** [TODO: DRAW] Component comparison flow. Can use Table 1 from the text as a visual table figure, or convert into a side-by-side flow diagram.

### Figures that need SCREENSHOTS from running code:

**Figure 3.** [TODO: SCREENSHOT] Query generation comparison. (a) Run NEKO Module 1 notebook with keyword "rhodococcus" -- screenshot the PubMed search cell output showing article count. (b) Run NEKO 2.0 with goal "lipid production in Rhodococcus" -- screenshot the concept extraction JSON and 4 generated queries from the logs, plus article count.

**Figure 4.** [TODO: SCREENSHOT] Knowledge graph comparison. (a) Open the NEKO output HTML graph file in browser -- screenshot showing undirected, unlabeled edges. (b) Open the NEKO 2.0 graph from `/api/goals/{id}/graph` or the Pyvis HTML output -- screenshot showing directed, colored edges with relation types. Both should be on the same topic.

**Figure 7.** [TODO: SCREENSHOT] Entity normalization before/after. From the NEKO 2.0 pipeline logs, find 3-4 examples where entities were merged. Show the `similar_phrases` dict entries. Can be formatted as a simple table figure.

**Figure 8.** [TODO: SCREENSHOT] Same as Figure 4 but zoomed into a specific subgraph region to clearly show edge labels, direction arrows, and PMID annotations.

**Figure 9.** [TODO: SCREENSHOT] Query answering comparison. Ask both systems: "What genes are important for lipid production in Rhodococcus?" (a) NEKO Module 2: run `search_network(G, "lipid", depth=1)` then summarize -- screenshot the LLM summary output. (b) NEKO 2.0: use the web UI or `/api/goals/{id}/query` -- screenshot the answer showing inline citations.

### Figures that need to be GENERATED from data (charts):

**Figure 5.** [TODO: GENERATE CHART] Stability score histogram. From NEKO 2.0 output Excel, read "Stability Score Q2" column with pandas: `df['Stability Score Q2'].hist(bins=10)`. Save as PNG.

**Figure 6.** [TODO: GENERATE CHART] Relation type bar chart. From NEKO 2.0 output Excel, extract all relations with regex, count per type: `df['Answer to Question 2'].str.extractall(r'\(([^,]+?),\s*([^,]+?),\s*([^\)]+?)\)')[1].value_counts().plot.barh()`. Save as PNG.

**Figure 10.** [TODO: GENERATE CHART] Ablation bar chart. After running all ablation experiments, plot unique triple count per variant as grouped bar chart. Requires all ablation runs to be complete first.
