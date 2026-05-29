3. Recommended Phase 0 architecture
flowchart TD
    A[Paper PDF / arXiv / Repo URL] --> B[Research Contract]
    B --> C[Paper Parser]
    C --> D[Evidence Ledger]
    D --> E[Empirical Claim Extractor]
    E --> F[Challenge / Contribution Extractor]

    F --> G[Artifact Discovery]
    G --> G1[Code Repo]
    G --> G2[Dataset]
    G --> G3[Benchmark Script]
    G --> G4[Model Checkpoints]

    G1 --> H[Repo Inspector]
    H --> I[Environment Builder]
    G2 --> J[Dataset Resolver]
    G3 --> K[Benchmark Contract Builder]

    I --> L[Install Runner]
    J --> L
    K --> M[Benchmark Runner]
    L --> M

    M --> N[Metric Extractor]
    N --> O[Result Comparator]
    O --> P[Reproduction Verdict]

    P -->|fail but repairable| Q[Repair DAG]
    Q --> I

    P --> R[Validation Report]
    P --> S[Trace Dataset]

The key is that Benchmark Contract Builder sits between paper claims and code execution.