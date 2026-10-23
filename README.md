AGNAYA

Simulating Heatwave-Driven Infrastructure Cascades in Raipur

An exploratory scenario model for heatwave impacts on power, water, indoor temperatures, and healthcare systems.

«Project status: AGNAYA is an exploratory simulation/prototype. Unless the team has separately validated the model and inputs, its outputs should be treated as scenario results—not operational forecasts, live utility data, or guaranteed predictions of outages or health impacts.»

1. Overview

Extreme heat can put pressure on several connected urban systems at the same time. Electricity demand may rise as cooling needs increase; electricity interruptions can affect water pumping and indoor cooling; and unsafe indoor temperatures can increase demand for healthcare services.

AGNAYA is being developed to help people explore these possible knock-on effects in a single scenario workflow. It is intended to make assumptions and potential system interactions easier to inspect, compare, and discuss.

The project focuses on Raipur, India, as the illustrative study setting. The use of local place names does not, by itself, mean that the model is connected to live infrastructure telemetry or has been calibrated to measured local operating data.

2. Key Features and Objectives

The project aims to explore the following areas, depending on what is implemented in the current application:

- Heatwave scenarios: Change scenario conditions to explore how heat stress may evolve over time.
- Cross-sector dependencies: Examine possible links between electricity, water, indoor thermal conditions, and healthcare demand.
- Time-based simulation: Inspect how scenario indicators may change over a simulated period, intended to cover up to 48 hours where implemented.
- Infrastructure network visualization: Inspect relationships between infrastructure components if the network visualization is available.
- Intervention comparison: Compare a baseline case with selected interventions where supported by the interface.
- Risk indicators and alerts: View model-generated indicators or simulated alerts. These are exploratory outputs, not official emergency alerts.

Only describe features that are available in the current application as implemented functionality.

3. Technology Stack

- Programming language: Python
- Application framework: Streamlit
- Distribution: The project is reported to be packaged as a Windows executable (EXE) with a bundled Python runtime and dependencies.

The exact Python packages, application entry point, packaging tool, and supported operating systems should match the current source code and build configuration.

4. Getting Started

Option A — Run the packaged executable

1. Download or copy the release/build supplied by the project team.
2. Extract the release folder if it is distributed as a ZIP file.
3. Run the supplied AGNAYA launcher or EXE.
4. If a browser window does not open automatically, follow the launcher's instructions and use the local address displayed in its console or log.
5. Keep any companion files and folders shipped with the EXE in their original relative locations.

The launch behavior depends on how the executable was packaged. If the executable starts a local Streamlit server, the application may appear in a browser while the server runs in the background. Keep the relevant console or process running unless the launcher is designed to manage it automatically.

Option B — Run from Python source

Use this method if the source code and dependency list are included in the repository.

Prerequisites

- A compatible Python version matching the version tested by the project team.
- The project source code.
- A "requirements.txt" file containing the required dependencies.

Installation steps

1. Clone the repository:
   
   git clone https://github.com/sathiyatskrj/AGNAYA.git

2. Navigate to the project directory:
   
   cd AGNAYA

3. Create a virtual environment:
   
   python -m venv .venv

4. Activate the virtual environment.
   
   Windows:
   
   .venv\Scripts\activate
   
   Linux/macOS:
   
   source .venv/bin/activate

5. Install the dependencies:
   
   python -m pip install -r requirements.txt

6. Start the Streamlit application. Replace "app.py" with the actual entry-point filename if it differs:
   
   python -m streamlit run app.py

7. Open the local URL printed in the terminal.

Note: The source-based instructions require the repository to contain a working entry-point file and a tested "requirements.txt". Update the commands if the project uses a different setup.

5. Repository Structure

A suggested organization for the repository is:

AGNAYA/
├── README.md
├── MODEL_AND_METHODOLOGY.md
├── requirements.txt
├── .gitignore
├── app.py
├── supporting_modules/
├── assets/
└── release/

This is an illustrative structure. Keep it synchronized with the files actually committed to the repository and replace "app.py" or other names where necessary.

The repository may also include a separate release download for the packaged EXE. Where possible, source code should be provided so reviewers and contributors can inspect how the simulation works.

6. Project Workflow

The intended workflow is:

1. Select the available heatwave or scenario inputs.
2. Run the simulation using the model implemented in the application.
3. Inspect the resulting time series, infrastructure relationships, indicators, or alerts provided by the interface.
4. Change supported scenario settings or interventions.
5. Compare the outputs against a baseline and interpret differences as modeled scenario differences, rather than proof of real-world effects.

The exact workflow depends on the current application interface and its implemented features.

7. Data and Assumptions

Transparency about data sources and assumptions is important for interpreting simulation results.

Each input should be identified as one of the following:

- Measured or published: Obtained from a published or measured source.
- Estimated: Derived from a documented source or estimation method.
- Developer-configured: Defined by the development team.
- Synthetic or illustrative: Created for testing, demonstration, or scenario exploration.

For every external dataset, document its title, provider, URL or citation, retrieval date, time resolution, geographic coverage, units, and any transformations applied.

Synthetic topology and illustrative values must not be described as official Raipur utility data. If the project uses real place names with synthetic connections or values, clearly disclose this distinction.

8. Limitations and Appropriate Use

- AGNAYA is intended for exploration, demonstration, and research discussion. It is not an operational dispatch or emergency-management system.
- Unless independently verified, its outputs are not calibrated predictions of electricity outages, water shortages, indoor temperatures, hospital load, illness, or mortality.
- Results depend on input values, model rules, assumptions, and the level of detail represented in the simulation.
- Place names and diagrams do not establish that real infrastructure assets or dependency paths have been verified.
- Simulated alerts are not substitutes for official weather warnings, utility communications, public-health guidance, or emergency services.
- Before use in real-world decision-making, the model would need documented data provenance, verification, calibration, sensitivity testing, and validation with appropriate domain experts and data owners.

9. Validation and Testing

Before presenting the repository as a finished project, verify the following:

- [ ] The documented launch command works from a clean environment.
- [ ] "requirements.txt" contains the dependencies needed to run the application and has been tested.
- [ ] The EXE and source builds produce consistent outputs for the same scenario, where both are supported.
- [ ] Inputs, units, defaults, and permitted ranges are documented.
- [ ] The methodology document matches the current code.
- [ ] Formulas and risk weights are traceable to their implementation and appropriately characterized as heuristic, calibrated, or otherwise.
- [ ] Sources of real-world data are listed, and synthetic data are clearly labeled.
- [ ] Known limitations and failure cases are documented.
- [ ] Screenshots show the current application rather than an outdated version or mock-up.

10. Team Contributions

Document the actual contributions of each team member before submission.

Suggested format:

- Application and simulation: Implementation of the Python/Streamlit workflow and simulation logic.
- Documentation: Preparation of setup instructions and the methodology and assumptions documentation.
- Testing and review: Verification of reproducibility, interface behavior, and consistency between the documentation and source code.

Replace these descriptions with the team's actual names and contributions.

11. License

See ""LICENSE"" (LICENSE) for the project's license.

If the repository does not contain a "LICENSE" file, choose and add an appropriate license before describing the project as open source.

12. Citation

If you use or discuss AGNAYA, cite the repository and the version or commit you reviewed:

«AGNAYA team. AGNAYA: Simulating Heatwave-Driven Infrastructure Cascades in Raipur. GitHub repository: https://github.com/sathiyatskrj/AGNAYA. Accessed October 23, 2026.»

For reproducibility, cite the specific release or commit hash whenever possible.