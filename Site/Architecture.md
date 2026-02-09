
flowchart TD
    subgraph Repos
        A[richard-credit-authority]
        B[richard-loaner-ledger]
        C[richard-loaner-agreements]
        D[gitdigital-products]
        E[gitdigital-solana]
        F[opengrantstack]
    end

    subgraph Pages
        P1[(GitHub Pages\nvia Actions)]
    end

    A --> P1
    B --> P1
    C --> P1
    D --> P1
    E --> P1
    F --> P1

    P1 --> U[Public Website URLs]

/site
  index.md
  _config.yml
  assets/
