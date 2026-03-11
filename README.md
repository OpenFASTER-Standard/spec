# OpenFASTER

**Vendor-independent, interoperable protocol standard for EU withholding tax and dividend reporting data exchange under MiKaDiv and FASTER.**

---

## What is OpenFASTER?

OpenFASTER defines an **interoperable protocol and data exchange format** that Central Financial Intermediaries (CFIs) — including Clearstream, Euroclear, and others — can use to exchange the data and events required for **indirect reporting**. The standard is currently in active development and enables data exchange between banks in both **pull and push** modes. Interoperability, even between competitors, is a top priority.

The scope is **purely operational**: building the technical infrastructure that makes indirect reporting and the collection of supplementary data (e.g., eTRCs) efficient and standardized across the EU. OpenFASTER does not address legislative or business-logic questions such as anonymous reporting.

---

## Technical Foundation

- **BIRD** — Based on the [Bank Integrated Reporting Dictionary](https://bird.ecb.europa.eu/) by the ECB
- **Encryption** — End-to-end encryption for all data transmitted between CFIs
- **Reference implementation** — Divizend Compliance provides one implementation

---

## Regulatory Context

OpenFASTER aligns with the **EU FASTER initiative**:

| Milestone                                 | Date                |
| ----------------------------------------- | ------------------- |
| Standardized dividend reporting (MiKaDiv) | **January 1, 2027** |
| Full regulatory reporting under FASTER    | **January 1, 2030** |

Goals include harmonized dividend reporting, reduced withholding tax fraud, increased transparency, and efficient cross-border tax reclaim processing.

---

## Key Principles

- **Vendor independence** — Not tied to any single vendor
- **Interoperability** — Designed for seamless data exchange between all participants
- **Security-first** — Encrypted transmission, segregated environments per legal entity
- **Open standard** — Specification and protocol definitions are openly defined

---

## Universal Reporting Workflow

The end-to-end workflow supported by implementations of OpenFASTER:

1. **Data import** — Transaction logs, system exports, historical data from multiple financial systems
2. **Normalization and validation** — Standardize structure, validate completeness and accuracy, check regulatory rules
3. **Entity chain reconstruction** — Beneficial owner, intermediaries, jurisdictions (tax authority transparency)
4. **Report generation** — Compliant reports for tax authorities, regulators, and financial institutions
5. **Secure transmission and audit** — Secure channels, full audit trail, versioning, traceability

---

## Architecture

- Implementations can operate **inside a bank’s infrastructure**
- Each **legal entity** can have a **segregated environment** for data isolation and regulatory compliance
- Integration via APIs, batch imports, and standardized financial data formats

---

## Repository Contents

- `index.html` — OpenFASTER specification (ReSpec)
- Core specification documents
- Data schemas and protocol definitions
- This README

## Viewing the Spec

The spec is written in [ReSpec](https://respec.org/) and renders in the browser. Open `index.html` locally or view the deployed version.

### Deploying to Vercel

1. Connect this repository to [Vercel](https://vercel.com)
2. Set **Root Directory** to `spec` (if the repo root is the parent folder)
3. Deploy — no build step required; ReSpec loads from CDN at runtime

---

## Contributing

Open an issue for questions or proposed changes. Pull requests are welcome with clear rationale and references to issues.

---

## Related Standards

- [BIRD — Bank Integrated Reporting Dictionary](https://bird.ecb.europa.eu/) (ECB)
- EU FASTER initiative
