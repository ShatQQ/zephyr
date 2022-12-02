.. _zephyr_reqtrace_notes:

Req trace
#############

.. item:: SWRQ-1
    :value: 40
    :status: Approved
    :nocaptions:

    SW 1

.. item:: SWRQ-2
    :value: 45
    :status: Approved
    :nocaptions:

    SW 2

.. item:: SWTE-1
    :value: 45
    :status: Approved
    :nocaptions:

    Test 1

.. item:: SWTE-2
    :value: 45
    :status: Approved
    :nocaptions:

    Test 2


.. item-link::
    :source: SWRQ-\d
    :target: SWTE-[12]
    :type: validates
    :nooverwrite:


.. item-matrix:: Trace software Requirements to test
    :source: SWRQ
    :target: SWTE
    :sourcetitle: Software req
    :targettitle: Test req
    :nocaptions:
    :stats:

.. toctree::
   :maxdepth: 1
   :glob:
   :reversed:

