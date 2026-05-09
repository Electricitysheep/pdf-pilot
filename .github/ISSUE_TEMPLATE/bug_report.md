---
name: Bug Report
description: Report a bug with pdf_pilot
labels: [bug]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for reporting a bug! Please fill out the sections below.
  - type: textarea
    attributes:
      label: Description
      description: What went wrong? What did you expect to happen?
    validations:
      required: true
  - type: textarea
    attributes:
      label: Steps to Reproduce
      description: |
        Include the command you ran and any relevant context:
        ```bash
        pdf_pilot input.pdf -o output.md --engine auto
        ```
    validations:
      required: true
  - type: input
    attributes:
      label: Python Version
      placeholder: "3.12.0"
  - type: input
    attributes:
      label: OS
      placeholder: "Windows 11 / Ubuntu 22.04"
  - type: input
    attributes:
      label: pdf_pilot Version
      placeholder: "0.2.0"
  - type: textarea
    attributes:
      label: PDF File (if applicable)
      description: |
        If the issue is with a specific PDF, please attach it or describe its characteristics (scanned, multi-column, tables, etc.)
