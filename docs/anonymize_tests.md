# Anonymize Tests

Goal: To be able to reproduce and fix bugs without getting any personal data from bug reporters.

The PDFs that are processed by bankstate contain sensitive banking and identity information. PDFs are not transparent to bug reporters, they can contain unseen, compressed or encoded metadata that might divulge personal information. This is why it is hard to be 100% confident in any process that claims to anonymize PDFs.

On the other hand, bankstate generates a text representation of the PDF before parsing which is easy to anonymize and is transparent, so is easy to verify to the bug reporter that no personal information is being passed into the bug report.

## Steps

[X] Capture the text output and store it on disk
[X] Make capture optional, based upon need to debug
[X] Process the text output directly, instead of using a PDF for input
[] Anonymize the existing test data and publish it
[] Build the anonymization process into the text capture
[] Document the steps to provide bug reports
