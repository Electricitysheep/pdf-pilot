---
name: Bug Report
description: Report a bug with pdf2doc
labels: [bug]
body:
  - type: textarea
    attributes:
      label: Description
      description: What went wrong?
    validations:
      required: true
  - type: textarea
    attributes:
      label: Steps to Reproduce
      description: |
        ```bash
        pdf2doc input.pdf -o output.md --engine auto
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
      label: pdf2doc Version
      placeholder: "0.1.0"
