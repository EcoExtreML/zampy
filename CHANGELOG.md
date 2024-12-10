# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## Unreleased

## 0.3.0 (...)

Zampy works with [new CDS and ADS
API](https://confluence.ecmwf.int/display/CKB/Please+read%3A+CDS+and+ADS+migrating+to+new+infrastructure%3A+Common+Data+Store+%28CDS%29+Engine).

### Added

The zampy test dataset is generated using data from the new API, [PR
  #62](https://github.com/EcoExtreML/zampy/pull/62).

### Fixed

- Add supports for the new CDS API [PR
  #62](https://github.com/EcoExtreML/zampy/pull/62)
- Fixed segmentation fault error [PR
  #66](https://github.com/EcoExtreML/zampy/pull/66)

## 0.2.0 (2024-09-02)

First release of `zampy`.

`zampy` is designed to retrieve data for LSM model input. It can help you prepare the data within the following steps:

1. **Download** the data for the specified location(s) / geographical area.
2. **Ingest** data into unified (zampy) format.
3. **Load** the variables in a standardized way (standardized names & standardized units).
4. **Convert** the data to standard formats:
    - ALMA / PLUMBER2's ALMA formatted netCDF.
    - *CMOR formatted netCDF*.
