# Xtract Universal Plugin for Dataiku

The Xtract Universal Plugin for Dataiku enables you to load SAP data directly into your Dataiku workflow.

# About Xtract Universal

Xtract universal is a standalone software that extracts and loads your SAP data into any target environment.
It supports a wide range of SAP systems, SAP objects and target environments.
The following data extraction types are available for Dataiku:

- **BAPI** - Execute BAPIs and Function Modules.
- **BW Cube** - Extract data from SAP BW InfoCubes and BEx Queries.
- **BW Hierarchy** - Extract Hierarchies from an SAP BW / BI system.
- **DeltaQ** - Extract data from DataSources (OLTP) and extractors from ERP and ECC systems.
- **OData** - Extract data via SAP OData services.
- **ODP** - Extract data via the SAP Operational Data Provisioning (ODP) framework.
- **OHS** - Extract data from InfoSpokes and OHS destinations.
- **Query** - Extract data from ERP queries.
- **Report** - Extract data from SAP ABAP reports.
- **Table** - Extract data from SAP tables and views.
- **Table CDC** - Extract delta data from SAP tables and views.

For more information on Xtract Universal, refer to the [Theobald Software website](https://theobald-software.com/en/xtract-universal/).

# Prerequisites

The following prerequisites are required to use the Xtract Universal plugin in Dataiku:

- Access to an Xtract Universal server instance
- An existing data extraction that uses the [Dataiku destination](https://helpcenter.theobald-software.com/xtract-universal/documentation/destinations/dataiku/)

# How it works

Follow the workflow below to get started with your SAP data extractions:

1. Install the Xtract Universal plugin.
2. Use the plugin settings to [connect to an Xtract Universal server instance](https://helpcenter.theobald-software.com/xtract-universal/documentation/destinations/dataiku/#use-xtract-universal-in-dataiku).
3. Add an **Xtract Universal** dataset to your workflow.
4. Select your data extraction. Note that you can only select extractions that use the [Dataiku destination](https://helpcenter.theobald-software.com/xtract-universal/documentation/destinations/dataiku/).
5. Start processing your SAP data in Dataiku.

For more detailed information, refer to the [Xtract Universal HelpCenter](https://helpcenter.theobald-software.com/xtract-universal/documentation/destinations/dataiku/).

