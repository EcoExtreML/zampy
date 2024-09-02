# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## Unreleased


## 0.2.0 (2024-09-02)
First release of `zampy`.

`zampy` is designed to retrieve data for LSM model input. It can help you prepare the data within the following steps:

1. **Download** the data for the specified location(s) / geographical area.
2. **Ingest** data into unified (zampy) format.
3. **Load** the variables in a standardized way (standardized names & standardized units).
4. **Convert** the data to standard formats:
    - ALMA / PLUMBER2's ALMA formatted netCDF.
    - *CMOR formatted netCDF*.
