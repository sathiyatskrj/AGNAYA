# AGNAYA — Model and Methodology

**Document purpose:** explain the model implemented in the current Python/Streamlit application, its inputs and assumptions, how scenario results are produced, and what the results can and cannot support.

> **Important verification note:** This is a structured methodology draft based on the project description available to the documentation authors. It has not been checked against the current Python source code in this workspace. Before using it as evidence of implementation, replace each instruction or conditional statement with details confirmed in the actual code. Do not claim a formula, algorithm, dataset, dependency, or feature is implemented until it has been verified in source.

## 1. Objective and scope

AGNAYA explores potential cascading effects of extreme heat across connected urban infrastructure and services in Raipur, India. The intended domains include electricity, water, indoor thermal conditions, and healthcare demand or capacity.

The core question is exploratory:

> Under a specified set of heatwave and infrastructure assumptions, how might changes in one domain affect indicators in other domains over the simulated period, and how do the modelled outcomes differ when selected interventions are applied?

The tool should be described as a **scenario simulation**, not as a live digital twin, a real-time grid model, or a validated forecasting service unless those properties are independently demonstrated.

## 2. Conceptual model

A conceptual cascade can be represented as follows:

```text
Heatwave conditions
        |
        +--> Higher cooling needs / electricity demand
        |              |
        |              +--> Possible electricity stress or interruption
        |                               |
        |                               +--> Potential water-service impacts
        |                               +--> Reduced indoor cooling
        |                                                |
        +----------------------------------------------> Heat exposure
                                                         |
                                                         +--> Potential healthcare demand
```

This diagram is a conceptual dependency story, not proof that every arrow is implemented or that the effects are quantified from observed data. In the final documentation, annotate each arrow as one of:

- **Implemented:** represented by a calculation or state update in source code.
- **Assumed:** represented through a configured rule or developer-defined dependency.
- **Conceptual only:** included to explain the domain but not calculated by the current program.

Remove or relabel any connection that is not represented in the actual implementation.

## 3. Simulation time and state

The project description indicates a time-based scenario, intended to explore up to 48 hours. Confirm the actual simulation horizon, time-step size, and update method in the code.

Document these items after verification:

| Item | What to record from the implementation |
|---|---|
| Simulation horizon | Actual start, end, and total duration |
| Time step | Minutes/hours per update and whether it is fixed or variable |
| State variables | Every variable updated during simulation, with units |
| Initial conditions | Defaults and how they are chosen |
| Boundary conditions | Clipping, minimum/maximum limits, or stopping conditions |
| Randomness | Whether any random draws are used; seed handling if applicable |
| Reproducibility | Whether identical inputs produce identical results |

Do not claim a numerical integration algorithm such as Euler or Runge–Kutta unless the relevant code calls or implements it.

## 4. Inputs and provenance

Create a complete inventory of parameters used by the current code. The categories below are prompts to help the team audit the implementation; they are not a claim that every category is presently configurable.

| Input category | Questions to answer |
|---|---|
| Heat conditions | Is heat represented by temperature, heat index, a scenario label, or another input? What are the units and source? |
| Electricity | Is demand, capacity, stress, availability, or interruption explicitly modelled? How is it calculated? |
| Water | Is pumping, supply, demand, storage, or service availability modelled? What dependency connects it to power, if any? |
| Indoor temperature | Is it a state variable, a direct formula, a lookup, or only an indicator? What assumptions govern heat gain and cooling? |
| Healthcare | Does the model represent demand, capacity, risk scores, or illustrative indicators? Avoid treating a score as a clinical forecast. |
| Infrastructure network | Are nodes and edges from verified records, manually authored, or synthetic? What does each edge mean? |
| Interventions | Which user-selectable actions exist, and which parameters do they change? |

For every input, record:

1. variable name in code;
2. display label and unit;
3. default value and allowable range;
4. data source and retrieval date, or mark as synthetic/configured;
5. any cleaning, conversion, normalization, or aggregation;
6. rationale and known uncertainty.

If the current build uses illustrative values or synthetic infrastructure relationships, state that clearly and prominently. Do not infer actual utility dependencies from geographic proximity alone.

## 5. Computation and update sequence

Describe the real source-code execution order here. A suitable outline—only if supported by the code—is:

1. Read scenario inputs and configuration parameters.
2. Initialize time-series state and infrastructure nodes.
3. At each simulation step, update heat-related conditions.
4. Calculate the implemented electricity, water, indoor-temperature, and healthcare variables.
5. Propagate any implemented effects across infrastructure dependencies.
6. Calculate summary indicators or risk scores, if present.
7. Store step results for the interface to display.
8. Apply scenario interventions and compare against a baseline when requested.

Replace this outline with a source-faithful description. Include the function/module names that implement each step and note whether the simulation runs once, on user interaction, or whenever Streamlit reruns the script.

## 6. Equations, scores, and rules

**This section must be populated from the current Python source.** Do not copy equations from old slides, an earlier HTML prototype, or a presentation unless the same equations appear in the active Python implementation.

For each implemented equation or rule, use the following record:

| Field | Description |
|---|---|
| Equation / rule | Exact expression or concise pseudocode from source |
| Code location | File and function name; add line numbers or a commit reference where practical |
| Variables | Meaning and units of every symbol |
| Coefficients | Values, units, and origin/rationale |
| Output | Meaning, unit, range, and interpretation |
| Status | Heuristic, literature-derived, calibrated, or validated—with supporting evidence |

If a weighted risk score is used, describe its weights as **developer-configured heuristic weights** unless calibration evidence exists. Explain normalization and what a score of low/high means. A weighted score should not be presented as a probability unless its mathematical definition and calibration justify a probabilistic interpretation.

If a variable name is ambiguous—for example, `H` could mean heat or healthcare—rename it in the documentation with an unambiguous symbol or code variable name. Do not provide equations in this document until the source-code audit is complete.

## 7. Baseline and intervention comparison

If the application supports intervention comparison, document:

- the baseline scenario and which inputs remain fixed;
- each intervention available in the UI;
- the exact model parameters or rules changed by each intervention;
- whether interventions are applied individually or in combinations;
- whether scenarios use identical initial conditions and randomness;
- the outputs used for comparison;
- whether a reported difference is absolute, relative, or normalized.

Use neutral language such as **“the modelled indicator changes by … under this scenario”** rather than “the intervention prevents outages” or “saves lives.” The latter claims require external evidence and validated outcome modelling.

## 8. Outputs and interpretation

List only outputs currently shown by the interface. For each chart, number, network view, or alert, define:

- its name and unit;
- whether it is an input, a simulated state, a derived indicator, or a user-authored label;
- the calculation behind it;
- the time and geographic scope;
- its limitations and how a user should interpret it.

Clearly distinguish:

- **observations** from real datasets;
- **modelled state variables** calculated by the simulation;
- **risk/summary scores** derived from rules or weights;
- **simulated alerts** generated by threshold or scenario logic; and
- **illustrative UI elements** that do not originate from data or a model calculation.

An alert in a prototype is not an official warning and should never be styled or worded in a way that implies it came from a government agency, utility operator, or hospital.

## 9. Verification, sensitivity, and validation plan

At minimum, create tests that match the implemented model. Examples to adapt include:

### Software/logic checks

- Valid inputs are accepted; invalid or out-of-range inputs are handled safely.
- Units and conversions are consistent.
- All state variables remain within documented physical or configured bounds.
- Repeated runs with identical inputs are reproducible when the model is deterministic.
- The baseline and intervention scenarios differ only in the intended intervention settings.
- Time-series lengths align with the configured time step and horizon.
- Missing or unavailable data are handled explicitly.
- The packaged EXE and source execution behave consistently for the same test scenario, if both are distributed.

### Behavior checks

For each key relationship, describe an expected direction or invariant that follows from the code and domain assumptions. Do not assume every relationship must be monotonic; identify interactions and exceptions. Record the input configuration, expected behavior, actual result, and pass/fail status.

### Sensitivity checks

Vary the key uncertain inputs across a documented range and report how output indicators change. Explain why those ranges were chosen. Sensitivity analysis can show that conclusions depend on assumptions; it does not, by itself, validate the model.

### External validation

Before using the model for real-world predictions, compare its outputs against appropriately sourced historical or measured data. Define a validation protocol, time period, geographic coverage, metrics, baseline, and acceptance criteria. Obtain permission and expert review where utility or health data are sensitive. If this work has not been completed, state **“External validation has not yet been completed.”**

## 10. Limitations and risks

Unless further work demonstrates otherwise, the team should consider and document these limitations:

- uncertainty in heatwave conditions and local exposure;
- incomplete or synthetic infrastructure topology;
- simplified physical or operational relationships;
- limited representation of human behavior, building differences, utility operations, and healthcare capacity;
- unknown calibration of configured parameters and weights;
- omitted dependencies and possible feedback loops;
- uncertainty in the geographic and temporal representativeness of inputs;
- uncertainty in the interpretation of composite risk indicators;
- lack of independent validation, if applicable.

These limitations mean scenario outputs should be interpreted as conditional on assumptions and are not evidence that a real asset will fail or that a particular outcome will occur.

## 11. Reproducibility record

Record this information for each public demo, evaluation, or result shown in a presentation:

- repository URL and commit/release version;
- operating system, Python version, and package versions;
- scenario inputs and intervention settings;
- random seed, where applicable;
- date/time the run was performed;
- any input data file versions and source citations;
- the outputs or screenshots generated;
- known warnings or differences between source and EXE execution.

Avoid committing API keys, passwords, user data, or sensitive datasets. Provide small, openly licensed test inputs where possible.

## 12. Implementation audit checklist

Complete this checklist before treating the document as final:

- [ ] Read the current Python/Streamlit entry point and supporting modules.
- [ ] Confirm the exact UI features described in the README.
- [ ] List every state variable and input actually used in calculations.
- [ ] Copy equations only from the active source and identify the corresponding functions.
- [ ] Verify all units, coefficient meanings, thresholds, and default values.
- [ ] Mark each dataset/topology item as sourced, estimated, configured, or synthetic.
- [ ] Distinguish scenario indicators from probabilities and validated predictions.
- [ ] Test baseline/intervention comparisons for consistency.
- [ ] Record actual software tests and any validation results.
- [ ] Remove all instructions and conditional claims that do not apply to the code.

## 13. References and contextual sources

Add the sources actually used to set model assumptions. A contextual reference is not proof that its method has been implemented in AGNAYA.

For every reference, include title, organization/authors, publication date, DOI or stable URL, access date, and the exact concept used. Prefer official meteorological, public-health, electricity, water, and disaster-management sources for local context. Cite a source beside the specific parameter or assumption it supports.

**Do not claim implementation of a specific grid solver, probabilistic method, numerical integrator, machine-learning model, or named framework unless the current source code uses it and the project can explain and reproduce that use.**
