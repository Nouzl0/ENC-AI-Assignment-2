# AI Student worksheet

Complete this worksheet before full data collection. Submit the initial version with the proposal and the completed version with the final report.

## A. Project identity

**Project title:**

**Team members:**

**Roles:**

**Primary track:**

- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  

**Project scope:**

- [ ]  
- [ ]  
- [ ]  

**Worksheet version and date:**

---

## B. Research question

**Primary research question:**

---

---

**Capability being measured:**

---

**Primary hypothesis:**

---

**Alternative explanation:**

---

**What result would challenge our hypothesis?**

---

---

## C. Measurement target

**Operational definition:**

---

---

**Unit of analysis:**

- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  

**Primary metric:**

---

**Why is it valid?**

---

**What important quality dimension does it fail to capture?**

---

---

## D. Systems and conditions

| System | Interface/API | Visible model/version | Tools enabled | Prompt adaptations | Date tested |
| --- | --- | --- | --- | --- | --- |
| ChatGPT |  |  |  |  |  |
| Gemini |  |  |  |  |  |
| Claude |  |  |  |  |  |
| Claude Code |  |  |  |  |  |
| Grok |  |  |  |  |  |
| Perplexity |  |  |  |  |  |

**Comparison design:**

- [ ]  
- [ ]  
- [ ]  

**What cannot be made equal?**

---

**How will this limitation affect interpretation?**

---

---

## E. Data and test-set plan

**Total cases:**

**Development cases:**

**Validation cases:**

**Held-out test cases:**

**Repeated-run cases:**

| Stratum | Planned number | Actual number | How selected |
| --- | --- | --- | --- |
| Ordinary |  |  |  |
| Difficult |  |  |  |
| Edge or adversarial |  |  |  |
| Ambiguous or incomplete |  |  |  |
| Czech |  |  |  |
| English |  |  |  |
| Mixed language |  |  |  |
| Other relevant stratum |  |  |  |

**Data provenance:**

---

**Why is this dataset representative of the intended use?**

---

**What leakage or contamination risks exist?**

---

---

## F. Prompt protocol

#### Common baseline prompt

```

```

#### Structured prompt

```

```

#### Optimized prompt

```

```

**What remains constant?**

---

**What is intentionally different?**

---

**When will prompts be frozen?**

---

**How will held-out cases remain protected?**

---

---

## G. Prompt-change log

| Version | Date | Change | Evidence | Expected effect | Actual validation effect | Retained? |
| --- | --- | --- | --- | --- | --- | --- |
| v0 |  |  |  |  |  |  |
| v1 |  |  |  |  |  |  |
| v2 |  |  |  |  |  |  |
| v3 |  |  |  |  |  |  |

---

## H. Evaluation plan

| Metric | Primary/secondary | Automatic/
human/judge | Calculation | Calibration or validation | Limitation |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

**Human raters:**

**Blinding procedure:**

**Response-order randomization:**

**Inter-rater agreement measure:**

**LLM-as-judge used?** Yes / No

If yes, state judge model, rubric, calibration sample, and known risks:

---

---

## I. Failure and retry policy

**What counts as a failed run?**

---

**Are retries allowed?**

---

**Maximum retries:**

---

**How will first-attempt and eventual success be reported?**

---

**Which product or infrastructure failures will be excluded, and why?**

---

---

### J. Logging checklist

- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  
- [ ]  

**Storage location:**

---

**Anonymization and data-protection procedure:**

---

---

## K. Pilot review

**Pilot size:**

**What failed in the pilot?**

---

**Which cases were rewritten or removed?**

---

**Which metric or rubric changes were made?**

---

**What evidence supports freezing the benchmark?**

---

**What remains uncertain?**

---

---

## L. Results table

| System | Condition | *N* | Primary score | Interval or variation | Secondary score | Median latency | Cost | First-attempt success |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ChatGPT | Baseline |  |  |  |  |  |  |  |
| ChatGPT | Structured |  |  |  |  |  |  |  |
| ChatGPT | Optimized |  |  |  |  |  |  |  |
| Gemini | Baseline |  |  |  |  |  |  |  |
| Gemini | Structured |  |  |  |  |  |  |  |
| Gemini | Optimized |  |  |  |  |  |  |  |
| Claude | Baseline |  |  |  |  |  |  |  |
| Claude | Structured |  |  |  |  |  |  |  |
| Claude | Optimized |  |  |  |  |  |  |  |
| Claude Code | Baseline |  |  |  |  |  |  |  |
| Claude Code | Structured |  |  |  |  |  |  |  |
| Claude Code | Optimized |  |  |  |  |  |  |  |
| Grok | Baseline |  |  |  |  |  |  |  |
| Grok | Structured |  |  |  |  |  |  |  |
| Grok | Optimized |  |  |  |  |  |  |  |
| Perplexity | Baseline |  |  |  |  |  |  |  |
| Perplexity | Structured |  |  |  |  |  |  |  |
| Perplexity | Optimized |  |  |  |  |  |  |  |

---

### M. Error analysis

| Error ID | System | Condition | Task ID | Category | Severity | First attempt? | Description | Likely cause | Preventable by prompt? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |

**Most frequent error:**

---

**Most consequential error:**

---

**Did optimization change the error distribution?**

---

---

## N. Practical recommendation

**Best system for the defined capability:**

---

**Best prompt condition:**

---

**Conditions under which this recommendation holds:**

---

**Important cost, latency, or human-effort trade-off:**

---

**What should a practitioner not infer from this study?**

---

---

## O. Validity and limitations

**Construct validity: are we measuring the intended capability?**

---

**Internal validity: could another factor explain the result?**

---

**External validity: where might the result fail to generalize?**

---

**Statistical uncertainty or sample-size limitation:**

---

**Product or model-version drift:**

---

**Evaluation bias or judge bias:**

---

**Most important follow-up experiment:**