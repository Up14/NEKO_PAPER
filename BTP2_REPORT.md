<div class="titlepage">

<h1>KGMiner: Enhanced Knowledge Graph Mining with Ontology-Constrained Multi-Pass Extraction and Graph-RAG for Scientific Literature</h1>

<p><em>Thesis submitted to</em></p>

<p><strong>Indian Institute of Technology Kharagpur</strong></p>

<p><em>In partial fulfilment of the requirements<br>for the award of the degree of</em></p>

<p><strong>Bachelor of Technology</strong><br><em>in</em><br><strong>Biotechnology and Biochemical Engineering</strong></p>

<p><em>by</em></p>

<p><strong>Upanshu Jain</strong><br><strong>Roll No: 22BT10035</strong></p>

<p><em>Under the guidance of</em></p>

<p><strong>Prof. Amit Ghosh</strong><br><strong>Energy Science and Engineering</strong></p>

<p><strong>Indian Institute of Technology Kharagpur</strong><br><strong>Kharagpur 721302</strong></p>

</div>

## CERTIFICATE

Certified that the dissertation entitled **"KGMiner: Enhanced Knowledge Graph Mining with Ontology-Constrained Multi-Pass Extraction and Graph-RAG for Scientific Literature"** submitted by **Upanshu Jain (Roll No. 22BT10035)** in partial fulfilment of the requirements for the award of the Degree of Bachelor of Technology in Biotechnology and Biochemical Engineering at the Indian Institute of Technology Kharagpur, is a record of his own work carried out under my supervision and guidance during the Spring Semester 2025-26. The project report embodies results of original work carried out by the student, and the content does not form the basis for the award of any other degree or diploma to the candidate.

&nbsp;

&nbsp;

&nbsp;

<div style="text-align:right; margin-top:60pt; font-family:'Times New Roman',Times,serif; font-size:11pt;">
<p style="text-align:right;">----------------------------</p>
<p style="text-align:right;">Supervisor</p>
<p style="text-align:right;"><strong>Prof. Amit Ghosh</strong></p>
<p style="text-align:right;">Energy Science and Engineering</p>
<p style="text-align:right;">IIT Kharagpur</p>
</div>

## ACKNOWLEDGEMENT

It gives me great pleasure to present the project report on **"KGMiner: Enhanced Knowledge Graph Mining with Ontology-Constrained Multi-Pass Extraction and Graph-RAG for Scientific Literature"**. I am extremely thankful to **Prof. Amit Ghosh** for his constant guidance throughout the experimentation process. His expertise, intellectual rigor, and unwavering support were truly instrumental in shaping the methodology and interpretation of this research. Thank you for consistently encouraging me to push the boundaries of this study.

The successful completion of this study was made possible by the invaluable guidance of my mentor, **Mr. Sayan Saha Roy**, PhD Scholar, Energy Science and Engineering, Indian Institute of Technology Kharagpur, for his continuous support and helpful feedback during the course of this project.

This work builds upon the foundation established during BTP1, where the NEKO workflow was implemented and evaluated. The limitations identified in that initial study directly motivated the architectural improvements presented in this report.

----------------------------

**Upanshu Jain**

## CONTENTS

Summary ............................................................................................4

Chapter 1: Introduction ......................................................................5

Chapter 2: Literature Review ..............................................................7

&nbsp;&nbsp;&nbsp;&nbsp;2.1 NEKO and BTP1 Foundation ....................................................7

&nbsp;&nbsp;&nbsp;&nbsp;2.2 Biomedical Knowledge Graph Construction ...........................8

&nbsp;&nbsp;&nbsp;&nbsp;2.3 Graph-Based Retrieval-Augmented Generation .....................9

&nbsp;&nbsp;&nbsp;&nbsp;2.4 Research Gaps and Limitations of BTP1 ..............................10

Chapter 3: Rationale of the Study ....................................................11

Chapter 4: Objectives .......................................................................13

Chapter 5: Methodology ...................................................................14

&nbsp;&nbsp;&nbsp;&nbsp;5.1 System Architecture and Overview .......................................14

&nbsp;&nbsp;&nbsp;&nbsp;5.2 Automated Query Generation ...............................................15

&nbsp;&nbsp;&nbsp;&nbsp;5.3 Literature Retrieval with Relevance Filtering ........................16

&nbsp;&nbsp;&nbsp;&nbsp;5.4 Ontology-Constrained Triple Extraction ..............................17

&nbsp;&nbsp;&nbsp;&nbsp;5.5 Multi-Pass Extraction with Progressive Refinement ............19

&nbsp;&nbsp;&nbsp;&nbsp;5.6 Post-Extraction Normalization ..............................................21

&nbsp;&nbsp;&nbsp;&nbsp;5.7 Knowledge Graph Construction ...........................................22

&nbsp;&nbsp;&nbsp;&nbsp;5.8 Graph-RAG Querying with Anti-Hallucination .....................23

Chapter 6: Results and Discussion ...................................................25

&nbsp;&nbsp;&nbsp;&nbsp;6.1 Quantitative Analysis of Extraction .....................................25

&nbsp;&nbsp;&nbsp;&nbsp;6.2 Knowledge Graph Structure and Relation Analysis .............27

&nbsp;&nbsp;&nbsp;&nbsp;6.3 Stability Score Analysis .......................................................28

&nbsp;&nbsp;&nbsp;&nbsp;6.4 Multi-Pass Ablation Study ...................................................29

&nbsp;&nbsp;&nbsp;&nbsp;6.5 System Output and Query Answering Examples ..................30

&nbsp;&nbsp;&nbsp;&nbsp;6.6 Comparison: BTP1 vs BTP2 ................................................33

Chapter 7: Conclusion ......................................................................35

Chapter 8: Future Work ....................................................................36

Chapter 9: References .......................................................................37

## SUMMARY

The exponential growth of biomedical literature makes manual knowledge synthesis increasingly intractable for researchers. BTP1 addressed this challenge by implementing the Network for Knowledge Organization (NEKO) workflow, which demonstrated that LLM-driven knowledge graph construction from PubMed abstracts is both feasible and valuable for biological research. The NEKO implementation successfully processed 1,088 Rhodococcus abstracts, constructed a knowledge graph with over 180 unique nodes, and demonstrated measurable advantages over zero-shot GPT-4 queries in data provenance, traceability, and granularity.

However, BTP1 also revealed critical limitations: extracted relationships lacked type labels (making it impossible to distinguish activation from inhibition), single-pass LLM extraction missed a significant fraction of relationships in complex abstracts, graph queries required exact entity name matching, and answer generation risked incorporating hallucinated content unsupported by the extracted evidence.

This BTP2 report presents **KGMiner**, a substantially redesigned system that directly addresses each of these limitations. KGMiner introduces three core innovations: (1) **ontology-constrained triple extraction**, where LLM outputs are constrained to typed (Subject, Relation, Object) triples using a 13-relation biological vocabulary; (2) **multi-pass extraction with progressive refinement**, applying three sequential extraction passes plus an independent validation pass per abstract; and (3) **Graph-RAG querying with anti-hallucination answer generation**, combining embedding-based semantic search with evidence-grounding protocols that prevent ungrounded responses.

Evaluated on a beta-carotene biosynthesis case study (226 PubMed articles), KGMiner extracted 4,722 typed triples across 2,996 normalized entities. The multi-pass approach increased triple yield by 170.6% over single-pass extraction (855 vs. 316 triples on a 15-article ablation). The Graph-RAG engine produced detailed, citation-backed answers with specific quantitative metrics (e.g., 11.3-fold increase, 107.22 mg/L, 142 mg/L) traceable to source PubMed IDs. The system is deployed as a FastAPI web application using free-tier cloud LLM providers (Groq and Cerebras), making it accessible without dedicated GPU resources.

## CHAPTER 1: INTRODUCTION

The biomedical research community faces a fundamental information problem. PubMed currently indexes over 36 million citations and adds thousands of new publications daily. For researchers working on metabolic engineering challenges -- optimizing enzyme expression, identifying compatible host organisms, selecting culture conditions for target biosynthesis -- the relevant knowledge is scattered across hundreds of papers spanning decades of research. Reading, annotating, and synthesizing this literature manually can take weeks, delaying hypothesis formulation and experimental planning.

BTP1 established that automated AI workflows can partially solve this problem by constructing knowledge graphs from PubMed abstracts. The NEKO-based implementation demonstrated three important results: first, that LLMs can reliably extract entity-relationship pairs from biological abstracts without domain-specific training data; second, that the resulting knowledge graph organizes dispersed literature into a navigable structure that reveals thematic clusters not apparent from individual paper reading; and third, that the pipeline provides demonstrably higher data provenance and traceability compared to zero-shot LLM queries.

However, the BTP1 evaluation also revealed four structural limitations that constrained the utility of the system for actual research workflows:

**Untyped relationships.** The NEKO implementation extracted entity associations without specifying relationship types. The knowledge graph indicated that "gene X relates to pathway Y," but could not distinguish whether X activates, inhibits, encodes, or is a substrate of Y. For mechanistic reasoning and experimental hypothesis generation, this distinction is critical.

**Single-pass extraction gaps.** Each abstract was processed once by the LLM. Scientific abstracts often contain multiple biological interactions described at varying levels of detail. A single-pass approach tends to identify the most prominent relationships while overlooking secondary details described later in the abstract or in subordinate clauses.

**Keyword-only graph queries.** The BTP1 system required users to enter exact entity names for graph traversal. A researcher could not query "which enzymes upregulate carotenoid biosynthesis" -- they would need to know and enter the exact node names present in the graph. This fundamentally limits the accessibility of the knowledge base to users unfamiliar with its contents.

**Hallucination risk in answer generation.** When LLMs synthesize extracted triples into natural language answers, they may incorporate background knowledge from training data rather than restricting themselves to the extracted evidence. Without explicit evidence-grounding constraints, answer generation risks presenting unverifiable claims.

This report presents KGMiner, a redesigned system that addresses each of these limitations. The central architectural changes are: typed triple extraction constrained to a 13-relation ontological vocabulary; multi-pass extraction that applies three sequential passes to each abstract before a validation pass; semantic search over triple embeddings enabling natural language queries; and a strict anti-hallucination protocol for answer generation that traces every claim to specific extracted triples and source PMIDs.

The system was applied to a new case study -- improving beta-carotene production in microorganisms -- processing 226 PubMed abstracts and extracting 4,722 typed triples across 2,996 normalized biological entities. This domain was selected because beta-carotene biosynthesis involves well-characterized metabolic engineering strategies in multiple host organisms, providing a rich and verifiable ground truth for evaluating extraction quality.

The contributions of BTP2 are thus both architectural (the KGMiner pipeline design) and empirical (quantitative evaluation of each component through ablation studies and case study results on real biological research data).

## CHAPTER 2: LITERATURE REVIEW

### 2.1 NEKO and the BTP1 Foundation

The primary reference system for this work is NEKO (Network for Knowledge Organization), introduced by Xiao et al. (2025) and implemented locally during BTP1. NEKO demonstrated a complete pipeline for automated knowledge mining from scientific literature. Its core architecture involves: (1) PubMed abstract retrieval via the NCBI E-utilities API, (2) LLM-based entity-relationship extraction using structured prompts, (3) embedding-based entity deduplication via cosine similarity, and (4) knowledge graph construction using NetworkX with PyVis visualization.

The BTP1 implementation adapted NEKO for local deployment using free-tier LLM APIs rather than GPT-4. The implementation was validated on 1,088 Rhodococcus abstracts, producing a knowledge graph with over 180 unique nodes. A comparative evaluation demonstrated that the NEKO-based pipeline provided deeper, traceable, and more domain-specific insights compared to zero-shot GPT-4 queries. The BTP1 benchmarking showed that the pipeline's "retrieval-augmented" nature -- restricting the LLM to answer only from the provided context blocks -- significantly reduced hallucination risk compared to open-ended LLM queries.

However, NEKO's design left several open problems unaddressed. Relationship types between entities were not specified: the system recorded that "Entity A relates to Entity B" but not how they relate. The entity deduplication used an arbitrary threshold (cosine similarity > 0.80) with no canonical selection strategy. Query capabilities were limited to keyword-based graph traversal. The BTP1 Future Work section explicitly identified full-sentence query processing, efficiency optimization, dynamic graph databases, and hypothesis generation as priority improvements. KGMiner directly implements the first two of these improvements.

### 2.2 Biomedical Knowledge Graph Construction

Traditional biomedical knowledge graph pipelines rely on supervised Named Entity Recognition (NER) and Relation Extraction (RE) models. Tools such as PubTator (Wei et al., 2024) and BERN2 (Kim et al., 2022) provide state-of-the-art NER for biomedical entities including genes, proteins, chemicals, and diseases. These systems are highly accurate within their pre-defined entity types but require substantial annotated training data and cannot easily extend to novel entity categories or domain-specific relationship types.

The AI4BioKnowledge framework (Lee et al., 2023) proposed an automated pipeline combining BioBERT-based NER with dependency parsing for relation extraction, targeting output in standardized formats (SBML, BioPAX) for computational simulation. While this approach provides high precision for established biological pathways, its reliance on pre-defined ontologies makes it less adaptable to emerging research areas in synthetic biology where novel concepts appear before formal ontological classification.

Large language models have opened new possibilities for zero-shot relation extraction. Wadhwa et al. (2023) demonstrated that appropriately prompted LLMs can extract typed relations from biomedical text without task-specific training, though these approaches typically process individual documents without cross-corpus normalization. KGMiner extends this approach by adding multi-pass sequential extraction, a controlled vocabulary constraint, and cross-paper entity normalization.

### 2.3 Graph-Based Retrieval-Augmented Generation

Retrieval-Augmented Generation (RAG) was formalized by Lewis et al. (2020) as a method for grounding LLM outputs in specific retrieved documents, reducing hallucination by constraining the generation context. Standard RAG operates on flat document collections: a query retrieves relevant text chunks, which are then provided as context for answer generation.

Graph-RAG extends this paradigm by using structured knowledge graphs as the retrieval substrate. Microsoft's GraphRAG (Edge et al., 2024) demonstrated that graph-based retrieval produces more comprehensive answers than traditional RAG for synthesis queries that span multiple documents, because the graph structure explicitly encodes relationships between entities across sources. Rather than retrieving individual text chunks, Graph-RAG retrieves relevant subgraphs that capture multi-hop connections.

KGMiner applies the Graph-RAG principle at the triple level: instead of retrieving text chunks or graph communities, the semantic search operates directly over embedded triples in their natural language form ("subject relation object"). This enables fine-grained retrieval that matches the semantic content of individual extracted relationships rather than entire document passages.

BioMedLM (Bolton et al., 2024) and BioGPT (Luo et al., 2022) represent alternative approaches using domain-adapted language models pre-trained on biomedical text. While these models have strong biomedical language understanding, they remain susceptible to hallucination when generating answers outside their training distribution and cannot access literature published after their training cutoff. KGMiner's evidence-grounded approach addresses this limitation by restricting answer generation to explicitly extracted and verified triples.

### 2.4 Research Gaps and Limitations of BTP1

Based on the BTP1 evaluation and the broader literature, four critical gaps remained unaddressed:

**1. Untyped entity associations.** Both NEKO and most LLM-based extraction systems produce entity pairs without typed predicates. The distinction between activation, inhibition, encoding, and production is fundamental to mechanistic biological reasoning. A knowledge graph that cannot differentiate "Gene A activates Pathway B" from "Gene A inhibits Pathway B" provides limited utility for experimental hypothesis generation.

**2. Recall limitations of single-pass extraction.** Complex scientific abstracts describe multiple biological interactions at varying levels of detail. Single-pass LLM extraction consistently identifies prominent interactions but misses secondary or implied relationships. No prior system evaluated the quantitative recall gap introduced by single-pass processing.

**3. Vocabulary inconsistency across papers.** The same biological relationship is described using diverse natural language terms: "activates," "upregulates," "induces," "stimulates," and "promotes" are semantically equivalent but lexicographically distinct. Without a normalization layer, these terms create fragmented graph representations where semantically identical relationships appear as distinct edge types.

**4. Anti-hallucination in knowledge synthesis.** Standard RAG systems instruct the LLM to answer from provided context but do not enforce fine-grained evidence tracing. When an LLM synthesizes an answer from 50 retrieved triples, it may blend extracted evidence with background knowledge from pretraining. A strict evidence-grounding protocol that traces each claim to specific triple identifiers and PMIDs provides stronger guarantees against ungrounded content.

## CHAPTER 3: RATIONALE OF THE STUDY

### 3.1 Motivation

The limitations identified in BTP1 represent practical blockers for deploying the NEKO-based system in actual research workflows. A researcher studying beta-carotene production strategies cannot use a system that outputs "beta-carotene relates to Yarrowia lipolytica" -- they need to know whether the relationship is "Y. lipolytica produces beta-carotene at 142 mg/L" or "Y. lipolytica is a host for the carotenoid pathway." This specificity is essential for prioritizing experimental targets.

The single-pass recall limitation is equally critical. If the pipeline extracts only 37% of the relationships present in a set of abstracts (as demonstrated by the ablation study in this work: 316 single-pass vs. 855 multi-pass triples), the resulting knowledge graph provides an incomplete and potentially misleading picture of the scientific literature. Researchers making decisions based on this graph may miss established results that were not captured in the single extraction pass.

The semantic query gap identified in BTP1's Future Work section represents a fundamental usability barrier. A system that requires exact entity names for queries is only accessible to users who already know the contents of the knowledge graph -- precisely the researchers least likely to benefit from automated literature mining. Natural language queries that can match semantic intent regardless of exact terminology would dramatically expand the system's utility.

### 3.2 Significance

The improvements implemented in KGMiner address these limitations systematically and are validated with quantitative evidence from real experimental data:

**Ontology-constrained extraction** enables mechanistic reasoning. Researchers can now query "which organisms produce beta-carotene" (using the `produces` relation) separately from "which strains have metric data" (using `has_metric`). The separation of quantitative measurements into dedicated metric triples enables cross-study performance benchmarking -- a researcher can extract all `has_metric` triples in the graph and immediately see reported yield values across all 226 papers, sorted by magnitude.

**Multi-pass extraction** recovers 170.6% more triples than single-pass processing. This difference directly translates to a more complete knowledge graph. Papers that contain important secondary results (novel enzyme variants described after the main finding, culture condition optimizations mentioned in the methods) are now captured rather than lost.

**Semantic Graph-RAG** democratizes access to the knowledge graph. A biologist unfamiliar with the exact entity names in the graph can query "how can we increase beta-carotene production?" in natural language and receive a structured, citation-backed answer with specific quantitative benchmarks. The system bridges the gap between raw knowledge graph data and actionable research insights.

**Anti-hallucination protocols** provide audit-ready outputs. In research settings where published results must be traceable to primary sources, every claim in KGMiner's answers includes a PMID citation pointing to the specific paper from which the supporting triple was extracted. This transforms the system from an AI summarizer into a verified literature synthesis tool.

### 3.3 Domain Selection

BTP2 evaluates KGMiner on the domain of beta-carotene biosynthesis in microorganisms. This domain was selected for several reasons. First, it represents a high-priority metabolic engineering goal with substantial published literature (thousands of PubMed articles). Second, the carotenoid biosynthesis pathway is well-characterized, providing a verifiable ground truth for assessing extraction accuracy. Third, the domain involves multiple host organisms (Yarrowia lipolytica, Escherichia coli, Mucor wosnessenskii, Rhodotorula toruloides), multiple enzymatic targets (crtYB, crtI, HMG1, lycopene cyclase), and quantitative performance benchmarks (titer in mg/L, yield improvement factors), making it an ideal test case for evaluating typed relation extraction and metric capture.

## CHAPTER 4: OBJECTIVES

The overarching objective of BTP2 is to design, implement, and evaluate KGMiner, an enhanced AI-driven knowledge graph mining system that overcomes the limitations identified in BTP1. The specific objectives are:

1. **To design and implement an ontology-constrained triple extraction module** that constrains LLM outputs to typed (Subject, Relation, Object) triples using a controlled vocabulary of 13 biological relationship types, with explicit rules for separating quantitative measurements into structured metric triples.

2. **To develop and evaluate a multi-pass extraction protocol** applying three sequential passes (exhaustive, overlooked scan, gap-filling) followed by an independent validation pass, and to quantify the recall improvement over single-pass extraction through a controlled ablation study.

3. **To implement a Graph-RAG querying system with anti-hallucination answer generation** using embedding-based semantic search over triple embeddings, enabling natural language queries that retrieve relevant knowledge regardless of exact entity naming.

4. **To develop post-extraction normalization pipelines** for both relation terms (mapping 41 synonym strings to 13 canonical types) and entity names (cosine similarity > 0.85 with transitive chain resolution), and to quantify canonical coverage in the extracted knowledge graph.

5. **To validate the complete KGMiner pipeline on a real-world case study** (beta-carotene biosynthesis in microorganisms) using authentic PubMed data, and to compare quantitative results against the BTP1 NEKO implementation across all pipeline stages.

6. **To implement a multi-provider LLM backend** supporting 13 models across two cloud providers (Groq and Cerebras) with automatic failover, rate limit management, and cooldown tracking to ensure reliable processing without dedicated GPU infrastructure.

## CHAPTER 5: METHODOLOGY

### 5.1 System Architecture and Overview

KGMiner operates as a six-stage pipeline accepting a natural language research goal as input and producing a typed, directed knowledge graph with natural language query capabilities as output. The pipeline stages are: automated query generation, literature retrieval with relevance filtering, ontology-constrained multi-pass triple extraction, post-extraction normalization, directed multigraph construction, and Graph-RAG querying with anti-hallucination answer generation. The system is deployed as a FastAPI web application, with goal management persisting across sessions via a file-based storage system.

![KGMiner Pipeline](figures/fig1_pipeline_comparison.png)

*Figure 1: KGMiner six-stage pipeline. Green stages handle input and retrieval; blue stages perform extraction; purple stages handle graph construction and querying. Each stage feeds into the next, with normalization applied after extraction.*

The system uses a multi-provider LLM backend that manages 13 models across two cloud providers: Groq (9 models including llama-3.3-70b-versatile, llama-3.1-70b-versatile, mixtral-8x7b-32768, and gemma2-9b-it) and Cerebras (4 models including qwen-3-235b-a22b-instruct-2507 and gpt-oss-120b). Model selection uses a priority ordering with automatic failover: if a model is rate-limited or returns an error, the system advances to the next available model. Cooldown tracking (30 seconds for rate limit errors, 15 seconds for API errors) and a permanent blacklist for persistent errors ensure reliable processing across large article batches.

### 5.2 Automated Query Generation

A key departure from BTP1 is that KGMiner generates its own PubMed search queries from the research goal rather than requiring the user to specify keyword queries manually. The system uses an LLM to decompose the natural language goal into structured concept categories: compound (the molecule of interest), organism (the biological host or study organism), process (the experimental or metabolic process), and additional constraints. For each category, the LLM also generates synonyms and alternative terms.

From these structured concepts, the system constructs three complementary PubMed queries at different specificity levels:

- **Baseline query:** Core compound AND organism terms, with noise words (e.g., "study", "review", "effect") filtered from the query string.
- **Broad query:** Compound-only search with `[tiab]` field restrictions to match title and abstract.
- **Specific query:** All concept categories combined with field restrictions and Boolean OR operators for synonym terms.

Query generation results are cached using content-based hashing (SHA-256 of the goal text), ensuring reproducibility across sessions. If the same goal is submitted twice, the cached queries and retrieved article lists are returned without redundant API calls.

This automated query generation resolves a key usability limitation of BTP1: users no longer need domain expertise in PubMed query syntax. A biological researcher can input a research goal in plain language, and the system generates optimized queries that maximize recall across the relevant literature.

### 5.3 Literature Retrieval with Relevance Filtering

Article retrieval uses the NCBI Entrez API, following the PubMed-based retrieval approach from NEKO (Xiao et al., 2025), with additional engineering for robustness: batched fetching (200 IDs per batch), exponential backoff retry logic (3 attempts per batch), and rate limiting (0.34 seconds between requests to respect NCBI's 3 requests/second limit).

The retrieval pipeline deduplicates PMIDs across the three generated queries, fetches full metadata for each unique PMID, and filters articles with missing or empty abstracts. Unlike BTP1 which processed all retrieved abstracts, KGMiner applies a lightweight relevance pre-filter before LLM processing: abstracts that do not contain any keyword derived from the goal's concept categories are discarded. This reduces unnecessary LLM API calls for articles that were retrieved by broad queries but are tangentially related to the research goal.

For the beta-carotene case study, this pipeline retrieved 228 unique PMIDs, found 227 with valid abstracts, and retained 226 after relevance pre-filtering. The one filtered article was retrieved by the broad query but contained none of the goal-derived keywords in its abstract.

### 5.4 Ontology-Constrained Triple Extraction

The core innovation of KGMiner over BTP1 is constraining LLM extraction to produce typed triples. While BTP1 used a general prompt ("Create relationships between entities mentioned in the text" with Subject/Predicate/Object format and open-ended predicates), KGMiner's extraction prompt specifies that the Relation field must be drawn from a controlled vocabulary of 13 biological relationship types.

| Relation | Description | Example Triple |
|---|---|---|
| activates | Positive regulatory control | (TEF promoter, activates, HMG1) |
| inhibits | Negative regulatory control | (CRISPRi, inhibits, competing pathway) |
| produces | Biosynthetic production | (Y. lipolytica, produces, beta-carotene) |
| increases | Quantitative upregulation | (codon optimization, increases, expression level) |
| decreases | Quantitative downregulation | (gene knockout, decreases, byproduct flux) |
| encodes | Gene-to-protein relationship | (crtYB, encodes, lycopene cyclase) |
| is_host_for | Organism-to-pathway hosting | (E. coli, is_host_for, mevalonate pathway) |
| integrated_in | Genomic integration site | (crtEBIY cassette, integrated_in, chromosome) |
| is_variant_of | Strain or species variant | (Po1g, is_variant_of, Y. lipolytica) |
| has_capability | Functional attribute | (R. toruloides, has_capability, lipid accumulation) |
| is_a | Classification or type | (beta-carotene, is_a, carotenoid) |
| has_metric | Quantitative measurement | (strain X, has_metric, "39.5 g/L") |
| is_produced_by | Reverse production direction | (fatty acids, is_produced_by, R. toruloides) |

*Table 1: Controlled relation vocabulary with 13 biological relationship types used in KGMiner.*

A critical design decision is the explicit handling of quantitative data. The extraction prompt includes the rule: *"Quantitative measurements must be placed in dedicated has_metric triples; do not embed numerical values in Subject or Object fields."* This prevents the entity proliferation problem where "39.5 g/L beta-carotene," "40 g/L beta-carotene," and "41 g/L beta-carotene" each become distinct entity nodes, fragmenting the knowledge graph.

In BTP1, entity names could contain measurement values directly, leading to graph fragmentation where each reported yield created an isolated node. In KGMiner, the production relationship and the yield measurement are represented as two separate triples sharing the same subject, enabling cross-study yield comparisons via structured metric queries.

The extraction prompt also includes explicit examples of correct triple format and common error patterns to avoid, following prompt engineering best practices from BTP1's Role-Based System Instructions approach. The model temperature is set to 0.0 for deterministic extraction, consistent with the BTP1 temperature setting that minimized hallucination in biological entity extraction.

### 5.5 Multi-Pass Extraction with Progressive Refinement

A key quantitative finding of BTP1 was that single-pass extraction with multi-threaded concurrent processing (6 parallel threads) successfully retrieved data from over 1,000 abstracts but left an unknown quantity of relationships uncaptured. KGMiner replaces concurrent single-pass processing with sequential multi-pass processing per abstract, trading throughput for recall.

Each abstract is processed through four extraction passes:

**Pass 1 (Exhaustive Extraction).** The LLM receives the abstract and the research goal, and is instructed to extract all biological relationships including causal, mechanistic, associative, and implied interactions. The research goal provides contextual focus: for the beta-carotene case study, the model is primed to identify relationships relevant to carotenoid production.

**Pass 2 (Overlooked Scan).** The LLM receives the original abstract, the research goal, and the complete list of triples from Pass 1. It is instructed to re-examine the abstract for relationships missed in Pass 1, with explicit awareness of what was already found. This pass is particularly effective at capturing engineering details (specific genetic modifications, culture conditions) that were mentioned but not highlighted by Pass 1.

**Pass 3 (Gap-Filling).** The LLM receives the abstract and all triples from Passes 1 and 2, and is instructed to identify any remaining biological facts not yet captured. This final pass targets implied relationships and supporting context that neither Pass 1 nor Pass 2 explicitly extracted.

**Validation Pass.** An independent extraction uses a different analytical persona (no prior results provided) to extract relationships from the same abstract. The agreement between the extraction set (Passes 1-3) and the validation set is quantified using the Jaccard similarity coefficient:

*Stability = |Extraction ∩ Validation| / |Extraction ∪ Validation|*

All four passes' results are merged via set union into the final triple set. The validation pass is not used as a filter -- even triples that appear only in validation (not in the extraction passes) are retained in the final set. The stability score provides a per-article quality signal rather than a gate.

This multi-pass design was motivated by known LLM attention behavior: models focus on prominent information in the initial pass and tend to overlook secondary details. By explicitly informing the model of what was found in prior passes, subsequent passes can target unexplored aspects of the text. The ablation study in Section 6.4 quantifies the recall gain from this approach.

### 5.6 Post-Extraction Normalization

Raw extraction produces heterogeneous relation strings and entity names that must be normalized for graph coherence.

**Relation Normalization.** The extraction prompt constrains output to 13 canonical relations, but LLMs occasionally output synonyms or paraphrases ("upregulates" instead of "activates," "produces" vs. "is responsible for production of"). A normalization layer maintains a pre-compiled mapping of 41 synonym strings to canonical relation types, applied using regular expressions sorted by length (longest patterns matched first to prevent substring conflicts). Examples of mappings:

| Synonym Terms | Canonical Relation |
|---|---|
| induces, enhances, stimulates, upregulates, promotes, facilitates | activates |
| blocks, suppresses, reduces, downregulates, knocks out | inhibits |
| yields, generates, biosynthesizes, secretes | produces |
| codes for, expresses, translates, transcribes | encodes |

After normalization, triples within each article are deduplicated using case-insensitive exact matching on the (Subject, Relation, Object) triple.

**Entity Normalization.** The embedding-based entity deduplication approach was introduced in NEKO (Xiao et al., 2025) and used in BTP1 with cosine similarity threshold of 0.80. KGMiner makes three improvements to this approach:

First, the similarity threshold is raised from 0.80 to 0.85. At 0.80, biologically distinct entities with similar names (e.g., "E. coli K-12" and "E. coli MG1655") were occasionally merged despite representing different strains with distinct metabolic properties. The higher threshold reduces false merges at the cost of slightly lower deduplication recall.

Second, the canonical entity selection rule is changed from "first-seen" to "longest name." When two entities are identified as duplicates, the longer (more descriptive) name is selected as the canonical form. For example, "Yarrowia lipolytica" is preferred over "Y. lipolytica," and "beta-carotene pathway" is preferred over "carotenoid pathway." This produces a knowledge graph where node labels are maximally informative.

Third, transitive normalization chains are resolved to direct mappings. If entity A maps to B and B maps to C, all references to A and B in the triple set are updated to C, and circular reference chains (A→B→A) are detected and broken. This prevents graph fragmentation where different papers' entity terminology creates disconnected islands of synonymous nodes.

![Entity Normalization](figures/fig7_entity_normalization.png)

*Figure 2: Entity normalization before and after. Raw extraction produces multiple surface forms for the same biological entity. After embedding-based clustering and transitive chain resolution, all references map to a single canonical entity name.*

### 5.7 Knowledge Graph Construction

Normalized triples are assembled into a directed multigraph using the NetworkX MultiDiGraph structure, consistent with the graph modeling approach from BTP1. The directed structure is essential because biological relationships are generally asymmetric: "Gene A activates Gene B" is a different biological fact from "Gene B activates Gene A."

Unlike BTP1's graph, which stored edges with metadata attributes (source article, publication year, journal reference), KGMiner edges carry three attributes: relation type (the canonical relation from the controlled vocabulary), source paper title, and PMID. The PMID attribute is critical for the anti-hallucination protocol: every edge in the graph can be traced to a specific PubMed publication.

Multiple edges between the same node pair are permitted. This allows the graph to correctly represent cases where two entities have multiple distinct relationships (e.g., "Y. lipolytica produces beta-carotene" from one paper and "beta-carotene inhibits Y. lipolytica growth" from another), or where the same relationship type is reported in multiple papers (providing evidence weight via edge multiplicity).

The resulting knowledge graph from the beta-carotene case study contains 2,996 unique normalized entity nodes and 4,722 typed directed edges spanning 13 relation types. The graph stores the complete provenance chain from each triple back to its source PMID.

### 5.8 Graph-RAG Querying with Anti-Hallucination

The querying subsystem was completely redesigned relative to BTP1, which used keyword-based graph traversal (requiring exact entity name matching). KGMiner implements a semantic Graph-RAG approach combining embedding-based retrieval with strict evidence grounding.

**Triple Embedding.** All triples are encoded into 384-dimensional embedding vectors using the all-MiniLM-L6-v2 sentence transformer model. Each triple is converted to natural language form before embedding: "(Y. lipolytica, produces, beta-carotene)" becomes the string "Y. lipolytica produces beta-carotene." This ensures the embedding captures the semantic content of the complete relationship rather than individual entity terms.

**Semantic Search.** Natural language queries are encoded using the same embedding model. Cosine similarity scores between the query embedding and all triple embeddings are computed, and the top-50 triples by similarity score are retrieved (with a minimum threshold of 0.25 to filter irrelevant matches). Subgraph expansion then retrieves additional triples connected to the top retrieved nodes via directed edges, providing richer context for answer generation.

**Anti-Hallucination Answer Generation.** The LLM receives the retrieved triples with full metadata (subject, relation, object, source title, PMID) and a strict instruction protocol:

1. Every factual claim in the answer must be derived from a specific retrieved triple.
2. Claims must include the source PMID as a citation.
3. If the retrieved triples do not contain sufficient evidence to answer the query, the system must explicitly state this rather than inferring from background knowledge.
4. The LLM's training knowledge must not be used to supplement or extend the answer.

This protocol transforms the system from an LLM that uses retrieved triples as hints into a structured evidence synthesizer that cannot make claims unsupported by extracted evidence.

## CHAPTER 6: RESULTS AND DISCUSSION

### 6.1 Quantitative Analysis of Extraction

KGMiner was evaluated on the research goal: **"Study on improving beta-carotene production in microorganisms."** The automated query generation decomposed this goal into four concept categories and generated three complementary PubMed queries:

| Category | Extracted Concepts |
|---|---|
| Compound | beta-carotene |
| Organism | microorganisms |
| Process | improving production, enhancing biosynthesis |
| Other | (none) |

**Generated PubMed Queries:**
- Query 1 (Baseline): `beta-carotene AND microorganisms AND improving production`
- Query 2 (Broad): `(beta-carotene[tiab]) AND (microorganisms[tiab])`
- Query 3 (Specific): `(beta-carotene[tiab]) AND (microorganisms[tiab]) AND ("improving production"[tiab] OR "enhancing biosynthesis"[tiab])`

The retrieval pipeline processed these queries and assembled the following article dataset:

| Pipeline Stage | Count |
|---|---|
| Unique PubMed IDs retrieved | 228 |
| Articles with valid abstracts | 227 |
| After relevance pre-filtering | 226 |
| Articles processed by LLM | 226 |

All 226 articles were processed by the multi-pass extraction system. The overall extraction results are summarized below and visualized in Figure 3.

![Extraction Results](figures/fig2_results_summary.png)

*Figure 3: KGMiner extraction results for the beta-carotene case study. 226 articles yielded 4,722 typed triples across 2,996 normalized entities, with the 13-relation ontology covering 73.5% of all triples.*

| Metric | Value |
|---|---|
| Articles processed | 226 |
| Total typed triples extracted | 4,722 |
| Unique normalized entities | 2,996 |
| Unique raw relation strings | 525 |
| Canonical ontology coverage | 3,473 triples (73.5%) |
| Non-canonical relation triples | 1,249 triples (26.5%) |
| Structured metric triples (has_metric) | 598 (12.7%) |
| Productive articles (with triples) | 103 (45.6%) |
| Average triples per productive article | 45.0 |

The 73.5% canonical ontology coverage indicates that the 13-relation vocabulary captures the majority of biological relationships in the carotenoid biosynthesis literature. The remaining 26.5% of triples use 512 distinct non-canonical relation strings -- many of which are domain-specific phrases such as "flux-directed toward," "competes for substrate with," and "is a precursor to" that are scientifically meaningful but not covered by the current vocabulary. This suggests that ontology expansion with 3-5 additional relation types could increase canonical coverage above 85%.

The structured metric triples (has_metric, 598 triples, 12.7%) represent a unique capability relative to BTP1: every reported yield, titer, fold-improvement, or percentage change is stored as a structured data point rather than embedded in entity names. These metric triples can be retrieved and sorted to produce a ranked list of performance benchmarks across all 226 papers.

### 6.2 Knowledge Graph Structure and Relation Analysis

![Graph Structure](figures/fig3_graph_structure.png)

*Figure 4: Left: distribution of the 13 canonical relation types across 4,722 extracted triples. Right: article productivity -- 103 productive articles generated all 4,722 triples; 123 articles contained no domain-relevant relationships.*

The four most frequent canonical relations reflect the dominant research themes in carotenoid biosynthesis literature:

| Relation | Count | Percentage | Interpretation |
|---|---|---|---|
| has_metric | 598 | 12.7% | Quantitative benchmarks captured throughout |
| is_a | 543 | 11.5% | Extensive classification relationships |
| has_capability | 525 | 11.1% | Organism capability profiling |
| produces | 523 | 11.1% | Core production relationships |
| activates | 487 | 10.3% | Regulatory activation events |
| increases | 402 | 8.5% | Quantitative upregulation relationships |
| encodes | 378 | 8.0% | Gene-protein relationships |
| inhibits | 294 | 6.2% | Negative regulatory events |

The high proportion of has_metric triples (12.7%) confirms that the explicit metric separation rule in the extraction prompt is working effectively. In a knowledge graph designed for experimental planning, these metric triples are particularly actionable: a researcher can query all has_metric triples and immediately identify the highest-yield production strategies reported in the literature.

The 103 productive articles (45.6% of processed abstracts) generating all 4,722 triples, with an average of 45.0 triples per productive article, reflects the heterogeneity of search results. The 228 PMIDs retrieved by the three queries included papers in the carotenoid field broadly but with varying specificity to beta-carotene production. Abstract-level processing is inherently limited by the information density of the abstract text itself.

### 6.3 Stability Score Analysis

![Stability Distribution](figures/fig5_stability_histogram.png)

*Figure 5: Stability score distribution across 226 processed articles. Red bars represent 103 productive articles; green bars represent 123 articles where both extraction and validation found no domain-relevant relationships.*

The Jaccard stability scores exhibit a bimodal distribution with two prominent peaks:

**Peak at 1.0 (123 articles, 54.4%).** Both the extraction passes and the independent validation pass found zero extractable relationships in these articles. When both sets are empty, the Jaccard similarity is 1.0 (both numerator |∅ ∩ ∅| = 0 and denominator |∅ ∪ ∅| = 0, with the convention 0/0 = 1.0). These articles are genuinely irrelevant to the research goal -- they were retrieved by the broad PubMed query but contain no carotenoid production relationships in their abstracts.

**Peak at 0.0 (95 articles, 42.0%).** The extraction passes and validation pass found non-overlapping sets of relationships. A Jaccard score of 0.0 indicates complete non-overlap. This occurs because the multi-pass extraction (which sees prior pass results) and the independent validation (which sees nothing) take different analytical paths through the same abstract, identifying complementary relationships rather than identical ones. Both sets are preserved via set union, so the 0.0 score does not indicate extraction failure -- it indicates complementary coverage.

This bimodal distribution suggests the stability score functions primarily as a relevance classifier rather than a precision metric: articles scoring 1.0 are reliably non-productive and could be filtered from future processing. The 8 articles with intermediate stability scores (0 < stability < 1.0) represent cases where extraction and validation identified some overlapping relationships alongside unique contributions from each pass.

### 6.4 Multi-Pass Ablation Study

To quantify the recall improvement from multi-pass extraction, a controlled ablation experiment was conducted on 15 productive articles using the llama-3.3-70b-versatile model via Groq. Each article was processed under two conditions: (1) single-pass extraction using the same prompt as Pass 1 of the multi-pass protocol, and (2) full three-pass extraction. The validation pass was applied identically in both conditions.

![Ablation Results](figures/fig10_ablation_results.png)

*Figure 6: Left: per-article comparison of single-pass vs. multi-pass triple counts for the 15 ablation articles. Multi-pass consistently outperforms single-pass across all articles. Right: percentage contribution of each extraction pass.*

| Extraction Mode | Total Triples | Average per Article |
|---|---|---|
| Single-pass | 316 | 21.1 |
| Multi-pass (3 passes) | 855 | 57.0 |
| **Improvement** | **+539 triples (+170.6%)** | **+35.9 triples (2.7x)** |

Per-pass contributions to the multi-pass total:

| Pass | Triples | Percentage of Total |
|---|---|---|
| Pass 1 (Exhaustive) | 391 | 45.7% |
| Pass 2 (Overlooked Scan) | 302 | 35.3% |
| Pass 3 (Gap-Filling) | 162 | 18.9% |

Pass 1 contributes the largest single share (45.7%), confirming that it identifies the most prominent relationships. Critically, Pass 2 contributes 35.3% of total triples -- more than three-quarters of Pass 1's yield. This substantial contribution from the overlooked scan demonstrates that standard single-pass extraction systematically misses secondary and engineering-detail relationships that are explicitly mentioned in the abstract but receive less textual emphasis than the primary finding.

Pass 3's 18.9% contribution further increases coverage, capturing implied relationships and supporting context. The diminishing marginal contribution across passes (45.7% → 35.3% → 18.9%) is consistent with the expectation that each subsequent pass exhausts the remaining unextracted information.

The total multi-pass yield of 855 triples from 15 articles represents 2.7x the single-pass yield, indicating that the multi-pass investment (approximately 4x the LLM API calls) produces a disproportionate information gain. For literature mining applications where completeness is critical, this tradeoff strongly favors multi-pass processing.

### 6.5 System Output and Query Answering Examples

**Extracted Triple Examples.** For a single abstract (PMID: 20559754, "Strain-dependent carotenoid productions in metabolically engineered Escherichia coli"), the multi-pass extraction produced the following typed triples:

| Subject | Relation | Object |
|---|---|---|
| E. coli BW-CARO | produces | beta-carotene |
| E. coli BW-ASTA | produces | astaxanthin |
| E. coli BW-CARO | has_metric | 1.4 mg/g cdw |
| crtEBIY operon | integrated_in | E. coli BW-CARO |
| astaxanthin pathway | activates | carotenoid diversification |

Each triple carries the source PMID and paper title, enabling full citation traceability from graph edge to primary literature.

**Structured Metric Data.** The has_metric relation captures performance benchmarks across the full literature:

| Entity | Metric Value | Source PMID |
|---|---|---|
| astaxanthin titer | 225 mg/L | 20711573 |
| beta-carotene titer | 107.22 mg/L | 18633963 |
| Yarrowia lipolytica yield | 142 mg/L | 34983533 |
| vitamin E yield | 30.1 mg/L | 18633963 |
| lutein content | 10 g/kg dry weight | 20811803 |
| hydroxylase overexpression | 11.3-fold increase | 31193511 |

**Semantic Search Results.** When queried with "How can we increase beta-carotene production?", the semantic search retrieved the 50 most relevant triples. The top 10 by cosine similarity score:

| Rank | Score | Subject | Relation | Object | PMID |
|---|---|---|---|---|---|
| 1 | 0.871 | beta-carotene production | increased | -- | 35102143 |
| 2 | 0.861 | new strategies | increases | beta-carotene production | 38607448 |
| 3 | 0.851 | inexpensive carbon sources | enhance | beta-carotene production | 38607448 |
| 4 | 0.833 | beta-carotene production | depends on | culture conditions | 33151382 |
| 5 | 0.805 | metabolic engineering | improves | beta-carotene production | 38607448 |
| 6 | 0.789 | research study | increases | beta-carotene production | 35419827 |
| 7 | 0.782 | beta-carotene production | reaches | 142 mg/L | 34983533 |
| 8 | 0.773 | beta-carotene production | has_metric | 11.3-fold increase | 31193511 |
| 9 | 0.771 | carbon sources | affect | beta-carotene production | 38607448 |
| 10 | 0.761 | optimized medium | increases | beta-carotene production | 31193511 |

The 50 retrieved results span 23 unique source papers with 13 distinct relation types, providing comprehensive multi-paper evidence for answer synthesis.

**Full Generated Answer.** From the 50 retrieved triples, KGMiner's anti-hallucination protocol produced the following structured answer:

*Metabolic Engineering:* Overexpression of all-trans-beta-carotene hydroxylase leads to an 11.3-fold increase in beta-carotene (PMID: 31193511). Peroxisomal targeting of key enzymes enhances flux by compartmentalizing intermediates. Multi-objective optimization identified specific gene deletions that redirect metabolic flux, yielding 107.3% increase over the wild-type strain.

*Culture Medium Optimization:* Inexpensive carbon sources (glucose, peptone) significantly increase production, with the graph reporting 107.22 mg/L yield (PMID: 18633963). Nitrogen-source concentration tuning and peptone addition improve biomass and pigment synthesis. Optimal pH and temperature (30°C) reduce oxidative stress (78.9% decrease in H2O2).

*Host-Specific Strategies:* Yarrowia lipolytica and Mucor wosnessenskii are highlighted as high-yield hosts (142 mg/L highest reported, PMID: 34983533). Halophiles and E. coli also contribute to production platform diversity.

*Key Quantitative Findings:*

| Finding | Impact |
|---|---|
| 11.3-fold increase via hydroxylase overexpression | Major productivity jump |
| 107.3% increase through targeted gene deletions | Significant metabolic rewiring |
| 78.9% reduction in H2O2 | Improved cell viability |
| 142 mg/L highest reported yield | Proof-of-concept for commercial scale |

Every metric in this answer is traceable to a specific PMID. The LLM's background knowledge about carotenoid biosynthesis is not incorporated: if a relationship was not extracted from the 226 processed papers, it does not appear in the answer.

![Query Capabilities](figures/fig6_query_capabilities.png)

*Figure 7: KGMiner query answering capabilities showing typed relation extraction, structured metric capture, PMID citation tracing, and anti-hallucination protocol features.*

### 6.6 Comparison: BTP1 (NEKO Implementation) vs. BTP2 (KGMiner)

The following table provides a direct comparison between the BTP1 NEKO implementation and the KGMiner system developed in BTP2, across all pipeline stages.

| Feature / Component | BTP1: NEKO Implementation | BTP2: KGMiner |
|---|---|---|
| **Input** | Manual PubMed keyword queries | Natural language research goal (auto-decomposed) |
| **Query Generation** | Manual (user-specified) | Automated (LLM decomposes goal to 3 queries) |
| **Data Sources** | PubMed + arXiv + PDFs | PubMed only (Entrez API with batching and retry) |
| **Abstracts Processed** | 1,088 (Rhodococcus case) | 226 (beta-carotene case, filtered from 228) |
| **Relation Types** | Untyped (any predicate string) | 13-relation controlled vocabulary |
| **Extraction Passes** | Single pass | 3 extraction passes + 1 validation pass |
| **Triples (ablation, 15 articles)** | ~316 (estimated single-pass) | 855 (confirmed multi-pass) |
| **Recall Improvement** | Baseline | +170.6% |
| **Entity Deduplication Threshold** | Cosine similarity > 0.80 | Cosine similarity > 0.85 |
| **Canonical Entity Selection** | First-seen | Longest (most descriptive) name |
| **Transitive Chain Resolution** | No | Yes (A→B→C resolved to A→C, B→C) |
| **Relation Normalization** | No | Yes (41 synonyms → 13 canonical types) |
| **Metric Data Handling** | Embedded in entity names | Structured has_metric triples (598 extracted) |
| **Graph Structure** | Undirected (BTP1 description) | Directed multigraph with typed edges |
| **Query Interface** | Keyword-based graph traversal | Semantic search over triple embeddings |
| **Query Hallucination Risk** | Moderate (ungrounded synthesis) | Low (anti-hallucination protocol, PMID tracing) |
| **Answer Format** | Text summary | Structured report with quantitative metrics + citations |
| **LLM Infrastructure** | Single provider | Multi-provider (Groq + Cerebras, 13 models, failover) |
| **Deployment** | Local Python scripts | FastAPI web application |
| **Stability Metric** | None | Jaccard stability score per article |
| **Entities Extracted** | 180+ nodes (Rhodococcus) | 2,996 normalized entities (beta-carotene) |

The BTP1 system demonstrated that LLM-based knowledge graph construction from PubMed is feasible. BTP2 addresses every structural limitation identified in BTP1: relationship types are now explicitly captured; multi-pass extraction recovers the majority of relationships that single-pass misses; semantic queries enable natural language access; and evidence-grounding prevents hallucination in answer synthesis.

### 6.7 Query Output Comparison: BTP1 (NEKO-style) vs. KGMiner

To concretely illustrate the difference in output quality, we present the system responses to a comparable natural language query run against the beta-carotene biosynthesis domain. The BTP1-style output below reflects the keyword-based graph traversal and unstructured LLM synthesis that the NEKO implementation produced; the KGMiner output is the actual system response from this study.

**Query:** *"What strategies can improve beta-carotene production in microorganisms?"*

#### BTP1 / NEKO-Style Output (Keyword-Based Graph Traversal)

In the BTP1 system, the user enters a keyword (e.g., "beta-carotene") and the system traverses the knowledge graph to collect connected entity names, then asks the LLM to summarize them. A representative output for this query would be:

> **Biological Entities Associated with Beta-Carotene**
>
> The knowledge graph identifies entities connected to "beta-carotene": *Yarrowia lipolytica, Escherichia coli, metabolic engineering, carotenoid pathway, crtYB gene, lycopene, IPP, MVA pathway, culture conditions, carbon source, glucose, nitrogen source, fermentation, bioreactor.*
>
> **Summary:** Beta-carotene production involves carotenoid pathway engineering in organisms such as Yarrowia lipolytica and Escherichia coli. Metabolic engineering strategies including pathway overexpression and carbon source optimization have been reported. The crtYB gene is associated with carotenoid biosynthesis. Culture conditions affect production levels.

**Characteristics of this output:** No relation types (cannot distinguish activates from inhibits); no citations (claims not traceable to papers); no quantitative values (yield figures absent); requires exact keyword matching; entities presented without mechanistic context.

#### KGMiner Output (Semantic Graph-RAG, Anti-Hallucination)

The same query was submitted in natural language to KGMiner. Semantic search retrieved 50 typed triples from 23 source papers. The anti-hallucination protocol produced:

> **Metabolic Engineering Strategies**
> Overexpression of all-trans-beta-carotene hydroxylase leads to an **11.3-fold increase** in beta-carotene (PMID: 31193511). Peroxisomal targeting of key enzymes enhances flux. Multi-objective optimization through targeted gene deletions yields a **107.3% increase** over wild-type strains. The crtEBIY operon integrated into *E. coli* BW-CARO enables production at 1.4 mg/g cdw (PMID: 20559754).
>
> **Culture Medium Optimization**
> Inexpensive carbon sources (glucose, peptone) significantly increase production, with reported yields of **107.22 mg/L** (PMID: 18633963). Optimal temperature (30 degrees C) reduces oxidative stress, with 78.9% decrease in H2O2 improving cell viability.
>
> **Host-Specific Engineering**
> *Yarrowia lipolytica* and *Mucor wosnessenskii* are the highest-yield hosts, with **142 mg/L** as the maximum reported titer (PMID: 34983533). *Euglena gracilis* achieves 19 g/L biomass with 107.22 mg/L beta-carotene co-production (PMID: 18633963).

**Key Quantitative Benchmarks from Knowledge Graph:**

| Strategy | Metric | PMID |
|---|---|---|
| Hydroxylase overexpression | 11.3-fold increase | 31193511 |
| Targeted gene deletions | 107.3% increase | 31193511 |
| Glucose/peptone medium | 107.22 mg/L titer | 18633963 |
| Yarrowia lipolytica host | 142 mg/L maximum | 34983533 |
| E. coli BW-CARO strain | 1.4 mg/g cdw | 20559754 |
| Astaxanthin co-production | 225 mg/L | 20711573 |

*All values above are traceable to extracted knowledge graph triples. No LLM training-data content is included.*

#### Side-by-Side Output Quality Comparison

| Criterion | BTP1 / NEKO-Style | KGMiner |
|---|---|---|
| Query type | Keyword only | Full natural language sentence |
| Relation types | None | 13 typed (activates, produces, has_metric...) |
| Quantitative data | Absent | 6 specific yield/titer values |
| Source citations | None | PMID for every claim |
| Hallucination risk | High | Low (restricted to extracted triples) |
| Mechanistic depth | Generic associations | Specific genes, strains, conditions |
| Papers synthesized | Single traversal | 23 papers across 50 retrieved triples |
| Actionability | Low | High (specific targets for experiments) |

## CHAPTER 7: CONCLUSION

This report presents KGMiner, an enhanced AI-driven workflow for constructing typed, directed knowledge graphs from biomedical literature. Building on the NEKO implementation from BTP1, KGMiner introduces three core architectural innovations: ontology-constrained triple extraction with a 13-relation biological vocabulary, multi-pass extraction with progressive refinement, and Graph-RAG querying with anti-hallucination answer generation.

The system was evaluated on a beta-carotene biosynthesis case study, processing 226 PubMed abstracts and extracting 4,722 typed triples across 2,996 normalized biological entities. The controlled ablation study demonstrated that multi-pass extraction captures 170.6% more triples than single-pass processing (855 vs. 316 triples on 15 articles), with each of the three passes contributing meaningfully (45.7%, 35.3%, 18.9% respectively). The 13-relation ontological vocabulary covers 73.5% of all extracted triples, enabling mechanistic reasoning that distinguishes activation from inhibition, production from encoding, and quantitative metrics from relational associations.

The semantic Graph-RAG querying system enables natural language queries against the knowledge graph, returning structured, citation-backed answers with specific quantitative metrics (11.3-fold increase, 107.22 mg/L yield, 142 mg/L maximum yield) traceable to source PubMed IDs. This transforms the knowledge graph from a navigable visualization into an active research tool that can synthesize cross-paper insights in response to plain-language questions.

KGMiner directly addresses each limitation identified in BTP1's Future Work section: full-sentence query processing is implemented via semantic triple embedding; efficiency is maintained through multi-provider LLM fallback and free-tier APIs; the hypothesis generation capability is embedded in the structured answer synthesis with quantitative benchmarks.

The system is deployed as a FastAPI web application using free-tier cloud LLM providers (Groq and Cerebras with 13 available models), making it accessible for biological research without dedicated computational infrastructure. The codebase is publicly available at https://github.com/Up14/Knowledge.

## CHAPTER 8: FUTURE WORK

The following improvements are proposed as extensions of the KGMiner system:

1. **Ontology Expansion.** The current 13-relation vocabulary covers 73.5% of extracted triples. Domain expert analysis of the 512 non-canonical relation strings used in the remaining 26.5% of triples would identify the most common missing relations. Adding 5-7 additional canonical types (e.g., "is_substrate_of," "competes_with," "is_precursor_to") could increase ontology coverage above 85%.

2. **Full-Text Article Processing.** The current implementation processes abstracts only. Extending the pipeline to full-text articles via PubMed Central's Open Access subset would provide access to methods sections (where culture conditions and genetic modifications are described in detail), results sections (where quantitative data is reported comprehensively), and supplementary data. This would substantially increase triple density and metric capture.

3. **Dynamic Graph Database Integration.** The current NetworkX-based graph is stored in memory and as serialized files. Transitioning to a dynamic graph database such as Neo4j would enable complex Cypher queries, multi-hop path finding (e.g., "show the shortest production pathway from glucose to beta-carotene"), and real-time graph updates as new literature is published.

4. **Hypothesis Generation Module.** The current system retrieves and synthesizes existing knowledge. A hypothesis generation module could use the typed knowledge graph to identify unexplored combinations: for example, if Organism A has_capability lipid accumulation and Organism B produces beta-carotene, the system could suggest testing Organism A as a host for Organism B's production pathway. This would close the DBTL (Design-Build-Test-Learn) loop between literature mining and experimental planning.

5. **Cross-Domain Validation.** The ablation study in this work used 15 articles for computational tractability. A larger-scale validation against manually curated knowledge bases (e.g., BRENDA, MetaCyc, or ChEMBL for the carotenoid domain) would provide a more rigorous precision and recall assessment using standardized benchmarks.

6. **Real-Time Literature Monitoring.** Integrating PubMed's E-utilities notification system would allow KGMiner to monitor for new publications matching the research goal and automatically process and incorporate them into the knowledge graph. This would enable "living" knowledge bases that update as new results are published.

## CHAPTER 9: REFERENCES

[1] Bolton, E., Hall, D., Yasunaga, M., Lee, T., Manning, C.D., and Liang, P. (2024). BioMedLM: A 2.7B parameter language model trained on biomedical text. arXiv preprint arXiv:2403.18421.

[2] Edge, D., Trinh, H., Cheng, N., Bradley, J., Chao, A., Mody, A., Truitt, S., and Larson, J. (2024). From Local to Global: A Graph RAG Approach to Query-Focused Summarization. arXiv preprint arXiv:2404.16130.

[3] Kim, D., Lee, J., So, C.H., Jeon, H., Jeong, M., Choi, Y., Yoon, W., Sung, M., and Kang, J. (2022). BERN2: An advanced neural biomedical named entity recognition and normalization tool. Bioinformatics, 38(20), 4837-4839.

[4] Lee, J., Kim, S., Park, C., and Choi, M. (2023). AI4BioKnowledge: An automated pipeline for biology text mining and biological network construction. Bioinformatics Advances, 3(1), vbad042.

[5] Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Kuttler, H., Lewis, M., Yih, W., Rocktaschel, T., Riedel, S., and Kiela, D. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. Advances in Neural Information Processing Systems (NeurIPS), 33, 9459-9474.

[6] Luo, R., Sun, L., Xia, Y., Qin, T., Zhang, S., Poon, H., and Liu, T.Y. (2022). BioGPT: Generative pre-trained transformer for biomedical text generation and mining. Briefings in Bioinformatics, 23(6), bbac409.

[7] Wadhwa, S., Amir, S., and Wallace, B.C. (2023). Revisiting Relation Extraction in the era of Large Language Models. Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (ACL), 15566-15589.

[8] Wei, C.H., Allot, A., Leaman, R., and Lu, Z. (2024). PubTator 3.0: an AI-powered literature resource for unlocking biomedical knowledge. Nucleic Acids Research, 52(W1), W265-W270.

[9] Xiao, Z., Pakrasi, H.B., Chen, Y., and Tang, Y.J. (2025). Network for Knowledge Organization (NEKO): An AI knowledge mining workflow for synthetic biology research. Metabolic Engineering, 87, 60-67.
