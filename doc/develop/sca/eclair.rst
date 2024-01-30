.. _eclair:

ECLAIR support
##############

Bugseng `ECLAIR <https://www.bugseng.com/eclair/>`__ is a certified
static analysis tool and platform for software verification.
Applications range from coding rule validation, with a
particular emphasis on the MISRA and BARR-C coding standards, to the
computation of software metrics, to the checking of independence and
freedom from interference among software components, to the automatic
detection of important classes of software errors.

.. important::

   ECLAIR is a commercial tool, and it is not free software.
   You need to have a valid license to use it.

Running ECLAIR
**************

To run ECLAIR, :ref:`west build <west-building>` should be
called with a ``-DZEPHYR_SCA_VARIANT=eclair`` parameter.

.. code-block:: shell

    west build -b mimxrt1064_evk samples/basic/blinky -- -DZEPHYR_SCA_VARIANT=eclair

Configurations
**************

There are different configuration sets that can be used to run ECLAIR without adapting
the rule set.

The default configuration is ``first_analysis``, which is a tiny selection of rules
to verify that everything is correctly working.

Zephyr is a large and complex project, so the configuration sets are split the
Zephyr's guidelines selection
(taken from https://docs.zephyrproject.org/latest/contribute/coding_guidelines/index.html)
in four sets to make it more digestible to use on a private machine:

* first_analysis (default): a tiny selection of rules to verify that everything
  is correctly working.

* STU: selection of MISRA guidelines that can be verified by analysing the single
  translation units independently.

* STU_heavy: selection of complex STU guidelines that require a significant amount
  of time.

* WP: all whole program guidelines of your selection ("system" in MISRA's parlance).

* std_lib: guidelines about the C Standard Library.

To change the configuration, you can define the ``ECLAIR_RULES_SET`` variable,
for example:

.. code-block:: shell

    west build -b mimxrt1064_evk samples/basic/blinky -- -DZEPHYR_SCA_VARIANT=eclair -DECLAIR_RULES_SET=STU

Generate additional report formats
**********************************

ECLAIR can generate additional report formats (e.g. DOC, ODT, XLSX) in addition to the
default ecd file. To enable them, you can set the following variables to true:

* ECLAIR_metrics_tab: Metrics in spreadsheet format.

* ECLAIR_reports_tab: Findings in spreadsheet format.

* ECLAIR_summary_txt: Summary report in plain textual format.

* ECLAIR_summary_doc: Summary report in DOC format.

* ECLAIR_summary_odt: Summary report in ODT format.

* ECLAIR_full_txt_areas: Enable/disable detailed reports in txt format.

* ECLAIR_full_txt: Rich/detailed report in plain textual format.

* ECLAIR_full_doc_areas: Enable/disable detailed reports in ODT/DOC format.

* ECLAIR_full_doc: Rich/detailed report in DOC format.

* ECLAIR_full_odt: Rich/detailed report in ODT format.

For example, to generate a summary report in plain textual format:

.. code-block:: shell

    west build -b mimxrt1064_evk samples/basic/blinky -- -DZEPHYR_SCA_VARIANT=eclair -DECLAIR_summary_txt=true
