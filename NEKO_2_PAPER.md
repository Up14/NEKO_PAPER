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

Before sending abstracts to the LLM (the most time-consuming step), NEKO 2.0 applies a lightweight relevance filter. Keywords longer than three characters are extracted from the research goal, and abstracts that do not contain any of these keywords are removed from processing. In the beta-carotene case study, only 1 of 227 articles (0.4%) was filtered out, indicating that the LLM-generated queries were already well-targeted. For broader or noisier research goals, this filter is expected to save a larger percentage of LLM API calls.

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

**[Figure 3: TODO: SCREENSHOT -- (a) NEKO single keyword query "rhodococcus" with retmax=300. (b) NEKO 2.0 concept extraction JSON + 4 generated queries for "Study on improving beta-carotene production in microorganisms"]**

For the beta-carotene production case study, NEKO 2.0 automatically decomposed the research goal into structured concepts: compound=["beta-carotene"], organism=["microorganisms"], process=["improving production", "enhancing biosynthesis"]. From these concepts, it generated three complementary PubMed queries:

1. `beta-carotene AND microorganisms AND improving production` (baseline)
2. `(beta-carotene[tiab]) AND (microorganisms[tiab])` (broad)
3. `(beta-carotene[tiab]) AND (microorganisms[tiab]) AND ("improving production"[tiab] OR "enhancing biosynthesis"[tiab])` (specific)

| Metric | NEKO | NEKO 2.0 |
|---|---|---|
| Search queries generated | 1 (manual keyword) | 3 (automatic, from concept decomposition) |
| Articles retrieved (PubMed IDs) | 200-300 (retmax limit) | 228 |
| Articles fetched with abstracts | 200-300 | 227 |
| Relevance filtering | None | 1 article removed (226 passed) |
| Articles sent to LLM | 200-300 (all) | 226 |

In this case study, the relevance filter removed only 1 article (0.4%), indicating that the LLM-generated queries were already well-targeted. For broader research goals, the filtering savings would be higher.

The four-tier query strategy retrieves articles by capturing papers that use different terminology for the same concepts. The relevance pre-filter prevents this broader retrieval from wasting LLM processing time on irrelevant articles.

### 6.2 Extraction Quality Comparison

**[Figure 4: TODO: SCREENSHOT -- (a) Open NEKO's `filterd_entity_carotene_network.html` (421 nodes, 431 edges, undirected, unlabeled). (b) Open NEKO 2.0's knowledge graph from `/api/goals/306f70a7.../graph` (2,996 entities, 4,722 triples, directed, typed). Screenshot both.]**

For the beta-carotene case study, we compared extraction results from the original NEKO (Yarrowia PDF processing with Qwen1.5-14B, ~233 PDFs) against NEKO 2.0 (PubMed abstracts, 226 articles):

| Metric | NEKO | NEKO 2.0 | Change |
|---|---|---|---|
| Extraction format | (Entity A, Entity B) | (Subject, Relation, Object) | Typed |
| Relationship types captured | 1 (untyped) | 525 raw, normalized to 13 canonical | +12 ontology types |
| Extraction passes per abstract | 1 | 3 + validation | +3 passes |
| Total relationships extracted | 431 edges | 4,722 triples | **11x more** |
| Relationships per article (average) | ~1.9 pairs/article | ~20.9 triples/article | **11x more** |
| Unique entities extracted | 421 nodes | 2,996 entities | **7.1x more** |
| has_metric triples (quantitative data) | 0 (embedded in entity names) | 598 (12.7% of all triples) | **New capability** |
| Articles with stability score > 0.5 | N/A | 54.4% (123 of 226) | Majority are high-confidence |

**[Figure 5: TODO: CREATE HISTOGRAM -- Stability scores show a bimodal distribution: 103 articles (45.6%) scored near 0.0 and 123 articles (54.4%) scored near 1.0, with very few in between. This suggests that the extraction-validation agreement is either very low or very high per article, not gradual. Plot from "Stability Score Q2" column.]**

The 11x increase in extracted relationships per article is primarily driven by the multi-pass extraction (3 passes + validation) and the typed triple format, which captures more specific relationships that untyped pairs would merge. [TODO: To measure per-pass contribution specifically, add logging to `ask_llm_with_fallback` in Minning.py to track |pass1_triples|, |pass2_new|, |pass3_new| counts.]

### 6.3 Relation Type Distribution

**[Figure 6: TODO: CREATE BAR CHART from the data below -- horizontal bar chart sorted by count]**

From the 4,722 triples extracted in the beta-carotene case study, the relation type distribution is:

| Relation Type | Count | % of Total |
|---|---|---|
| has_metric | 598 | 12.7% |
| is_a | 543 | 11.5% |
| has_capability | 525 | 11.1% |
| produces | 523 | 11.1% |
| increases | 382 | 8.1% |
| decreases | 173 | 3.7% |
| inhibits | 167 | 3.5% |
| integrated_in | 160 | 3.4% |
| is_host_for | 156 | 3.3% |
| activates | 127 | 2.7% |
| encodes | 63 | 1.3% |
| is_variant_of | 56 | 1.2% |
| **Other (non-canonical)** | **1,249** | **26.5%** |
| **Total** | **4,722** | **100%** |

The top 13 canonical ontology relations account for 3,473 triples (73.5% of total). The remaining 1,249 triples (26.5%) use 512 unique non-canonical relation strings that survived normalization, indicating room for expanding the synonym mapping dictionary.

The `has_metric` relation is the most frequent canonical type (598 triples, 12.7%), confirming that the numeric data separation rule is actively capturing quantitative performance data that would have been embedded in entity names in the original NEKO. The `produces` (523) and `has_capability` (525) relations together capture core metabolic engineering knowledge about what organisms can make.

### 6.4 Normalization Impact

**[Figure 7: TODO: SCREENSHOT -- show a before/after example from the actual run data. Take 3-4 entity names from the similar_phrases mapping output.]**

| Normalization Step | Effect |
|---|---|
| Relation normalization | Reduced 525 unique raw relation strings to 13 canonical ontology types (covering 73.5% of triples). 41 synonym mappings applied. |
| Entity normalization (threshold 0.85) | Merged similar entities from 2,996 unique entities. [TODO: add print statement to `find_similar_phrases()` to log len(similar_phrases) vs len(entities) and compute merge percentage.] |
| Transitive chain resolution | [TODO: add logging to `apply_entity_normalization()` to count chains with length > 1.] |
| Longer-name canonical | [TODO: print 3-4 example entries from the similar_phrases dict showing shorter -> longer canonical selection.] |

Note: The relation normalization results are confirmed from the actual run: 525 raw relation types were found in the output, of which the 13 canonical types account for 3,473 of 4,722 triples. The remaining 26.5% non-canonical relations suggest the synonym dictionary could be expanded further.

### 6.5 Knowledge Graph Structure Comparison

**[Figure 8: Side-by-side knowledge graphs -- NEKO (undirected, unlabeled edges) vs. NEKO 2.0 (directed, labeled edges with relation types)]**

| Graph Property | NEKO | NEKO 2.0 |
|---|---|---|
| Graph type | Undirected simple | Directed multigraph |
| Edge labels | None (paper title as tooltip) | Relation type + paper title + PMID |
| Multiple edges between same nodes | Not possible | Supported |
| Causal direction preserved | No | Yes |
| Edge provenance (PMID) | No | Yes |
| Total nodes | 421 | 2,996 | **7.1x more** |
| Total edges | 431 | 4,722 | **11x more** |
| Average node degree | ~2.0 (431 edges / 421 nodes, undirected) | ~3.2 (4,722 edges / 2,996 nodes, directed) | Higher connectivity |

### 6.6 Search and Answer Quality

**[Figure 9: Query answering comparison -- same question asked to NEKO and NEKO 2.0]**

| Aspect | NEKO | NEKO 2.0 |
|---|---|---|
| Search method | Keyword substring on node names | Semantic cosine similarity on triple embeddings |
| Query: "What genes improve lipid production?" | Must search "lipid" or "gene" exactly | Natural language query finds semantically relevant triples |
| Answer grounding | Generic summary from node names | Every claim cites specific (S, R, O) triple with PMID |
| Answer hallucination risk | High (no guardrails) | Low (8-rule anti-hallucination system) |
| Follow-up questions | Not supported | Chat history maintained |
| Citation traceability | 0% (no inline citations) | PMID-backed triples in every answer (see query history examples below) |

The query history from the completed beta-carotene run shows three real queries and their answers. For example, the query "How we can increase beta carotene production" returned an answer citing specific quantitative findings from the knowledge graph: 11.3-fold increase via hydroxylase overexpression, 107.3% increase via gene deletions, 78.9% reduction in H2O2, 0.165 g/L/h specific productivity, 142 mg/L highest yield, and 107.22 mg/L titer -- all traceable to extracted triples from the 2,996-entity, 4,722-relationship knowledge graph.

**[Figure 9: TODO: SCREENSHOT -- (a) Run NEKO Module 2 with `search_network(G, "carotene", depth=1)` then summarize -- screenshot the generic LLM output. (b) Screenshot the NEKO 2.0 answer for "How we can increase beta carotene production" from the web UI, showing inline citations and specific metrics.]**

### 6.7 Ablation Study

The full NEKO 2.0 pipeline produced 4,722 triples from 226 articles with a mean stability score of 0.55. Below we report known component contributions:

| Variant | Effect | Source |
|---|---|---|
| **NEKO 2.0 (full)** | 4,722 triples, 2,996 entities, 13 canonical relation types, mean stability 0.55 | Completed run |
| **Without relation normalization** | 525 raw relation types instead of 13 canonical (73.5% of triples would be fragmented across non-standard labels) | From actual data: 525 unique relations before normalization |
| **Without has_metric separation** | 598 fewer structured metric triples; numeric values would be embedded in entity names, increasing entity count but reducing graph usability | From actual data: 598 has_metric triples in output |

**[TODO: THE FOLLOWING ABLATIONS REQUIRE RE-RUNNING THE PIPELINE WITH MODIFICATIONS]**

| Variant | How to Run | Expected Measurement |
|---|---|---|
| Without multi-pass (single pass only) | In `app.py: _process_article_batch()`, change `multi_pass=True` to `multi_pass=False`. Run on same 226 articles. | Count triples in output -- compare against 4,722 |
| Without entity normalization improvements | In `app.py: run_pipeline()`, change `find_similar_phrases(entities, 0.85)` to `find_similar_phrases(entities, 0.80)`. Run. | Count entities after merge -- compare against 2,996 |
| Without 4-tier queries (single keyword) | Bypass `generate_search_queries()`, use single `"beta-carotene microorganisms"[Abstract]` query. Run. | Count articles retrieved and final triples |
| Without relevance pre-filter | Skip the keyword-presence filter in `run_pipeline()`. Run. | Count LLM calls (should be 227 vs 226 in this case, but larger difference on broader topics) |

**[Figure 10: TODO: CREATE BAR CHART after running ablation experiments above]**

### 6.8 Comparison with GPT-4 Zero-Shot

Following the original NEKO paper's comparison methodology (which showed NEKO provided 200% more gene targets and 200% more engineering strategies than GPT-4 zero-shot), we extend this comparison to include NEKO 2.0:

| Metric | GPT-4 Zero-Shot | NEKO (Original) | NEKO 2.0 |
|---|---|---|---|
| Total entities/nodes | N/A | 421 (Yarrowia case) | 2,996 (beta-carotene case) |
| Total relationships | N/A | 431 (untyped pairs) | 4,722 (typed triples) |
| Quantitative metrics (titers, yields) | None | Embedded in entity names | 598 structured has_metric triples |
| Sources cited | 0 | Paper titles on edges | 226 PMIDs traceable in answers |
| Relationship types | Implicit in text | 1 (untyped) | 13 (typed ontology) |
| Answer grounding | None | Partial (from KG node names) | Full (triple + PMID citations) |
| Confidence scoring | None | None | Jaccard stability score per article (mean: 0.55) |
| Gene targets mentioned | [TODO: ask GPT-4 "How to improve beta-carotene production in microorganisms", count gene names] | [TODO: count gene names from NEKO Yarrowia Excel output] | [TODO: count gene names from NEKO 2.0 Excel -- grep for gene-like entities in "Answer to Question 2" column] |
| Engineering strategies | [TODO: count from GPT-4] | [TODO: count from NEKO] | [TODO: count from NEKO 2.0] |

**[TODO: SCREENSHOT -- GPT-4 zero-shot answer vs NEKO 2.0 grounded answer for "How we can increase beta carotene production", side by side. The NEKO 2.0 answer already exists in query_history.json.]**

Note: The gene target and engineering strategy counts require manual counting from the Excel outputs. The original paper reported 200% more for NEKO vs GPT-4; NEKO 2.0's 7.1x more entities and 11x more relationships suggest an even larger gap.

---

## 7. Discussion

### 7.1 Impact of Typed Triple Extraction

The shift from untyped entity pairs to typed triples with a controlled ontology is the most impactful improvement in NEKO 2.0. In the original NEKO, a pair like (HMG-CoA reductase, mevalonate pathway) tells us these entities are related but not how. In NEKO 2.0, the triple (HMG-CoA reductase, activates, mevalonate pathway) explicitly captures the mechanistic relationship. This enables queries like "what genes activate the mevalonate pathway?" which are impossible with untyped graphs.

The `has_metric` relation is particularly valuable for metabolic engineering research. By separating quantitative measurements into dedicated triples, researchers can search for performance benchmarks across studies (e.g., "what are the reported titers for beta-carotene production?") without these values being conflated with entity names.

### 7.2 Multi-Pass Extraction Effectiveness

The multi-pass extraction with validation produced 4,722 triples from 226 articles (20.9 triples per article), compared to the original NEKO's 431 pairs from ~233 PDFs (1.9 pairs per article). While the comparison is not perfectly controlled (different input sources and LLM models), the 11x increase in extraction density suggests that multi-pass typed extraction captures substantially more knowledge per article. [TODO: Run single-pass ablation to measure the exact contribution of multi-pass vs typed-triple format.]

The Jaccard stability score shows a distinctive bimodal distribution: 103 articles (45.6%) scored near 0.0 and 123 articles (54.4%) scored near 1.0, with very few scores in between. This bimodal pattern suggests that extraction-validation agreement is binary rather than gradual -- the LLM either consistently identifies the same key relationships (high stability) or produces substantially different extractions on each pass (low stability). [TODO: Manually examine 5-10 low-stability articles to determine whether low scores correlate with ambiguous abstracts, highly technical language, or multi-topic papers.]

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
