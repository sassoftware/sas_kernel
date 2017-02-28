
Getting Started
===============

The SAS Kernel for Juypter is designed to allow users to use Jupyter Notebooks
to interact with SAS (SAS 9.4 or SAS Viya). It makes SAS the
analytical engine or "calculator" for data analysis. In its most simple
form, SASPY is a code translator taking python commands and converting
them into SAS procedure and data step calls and then displaying the
results.

Load Data Into SAS
------------------

.. code:: sas

    filename x "./HR_comma_sep.csv";
    proc import datafile=x out=_csv dbms=csv replace; run;

Explore the data
----------------

.. code:: sas

    proc contents data=work._csv;
        ods select Variables;
    run;

.. code:: sas

    proc print data=work._csv(obs=5);
    run;

.. code:: sas

    proc means data=work._csv n nmiss median mean std min p25 p50 p75 max;
    run;

.. code:: sas

    proc sgplot data=work._csv;
        vbar salary;
    run;

.. code:: sas

    proc sgplot data=work._csv;
        vbar sales;
    run;

.. code:: sas

    proc sgplot data=work._csv;
        histogram last_evaluation / scale=count;
        density last_evaluation;
    run;

.. code:: sas

    proc sgplot data=work._csv;
        histogram time_spend_company / scale=count;
        density time_spend_company;
    run;
    proc sgplot data=work._csv;
        histogram last_evaluation / scale=count;
        density last_evaluation;
    run;
    proc sgplot data=work._csv;
        histogram satisfaction_level / scale=count;
        density satisfaction_level;
    run;

.. code:: sas

    proc sgplot data=work._csv;
        heatmap x=last_evaluation y=satisfaction_level;
    run;

.. code:: sas

    proc sgplot data=work._csv(where=(satisfaction_level <.2 and last_evaluation>.7));
        heatmap x=last_evaluation y=satisfaction_level;
    run;

.. code:: sas

    proc sgpanel data=work._csv;
        *where satisfaction_level <.2 and last_evaluation>.7;
        PANELBY left;
        hbar sales / response=last_evaluation stat=median;
        hbar sales / response=satisfaction_level stat=median ;
    run;


Split the data into training and test
-------------------------------------

.. code:: sas

    proc hpsample data=work._csv out=work._csv samppct=70 seed=9878 partition;
        class left _character_;
        target left;
        var work_accident average_montly_hours last_evaluation number_project promotion_last_5years satisfaction_level
        time_spend_company;
    run;

`Decision Tree <http://support.sas.com/documentation/cdl/en/stathpug/68163/HTML/default/viewer.htm#stathpug_hpsplit_toc.htm>`__
-------------------------------------------------------------------------------------------------------------------------------

.. code:: sas

    proc hpsplit data=work._csv(where=(_partInd_=1)) plot=all;
        class work_accident promotion_last_5years sales salary;
        model left = work_accident promotion_last_5years sales salary
                    satisfaction_level time_spend_company number_project average_montly_hours;
    run;

GLM
---

.. code:: sas

    proc glm data=work._csv(where=(_partInd_=1)) plot=all;
        class work_accident promotion_last_5years sales salary;
        model left = work_accident promotion_last_5years sales salary
                    satisfaction_level time_spend_company number_project average_montly_hours;
    run;

Logistic
--------

.. code:: sas

    proc hplogistic data=work._csv(where=(_partInd_=1));
        class work_accident promotion_last_5years sales salary;
        model left = work_accident promotion_last_5years sales salary
                    satisfaction_level time_spend_company number_project average_montly_hours;
    run;

Neural Network
--------------

.. code:: sas

    proc hpneural data=work._csv;
        hidden 19;
        input work_accident promotion_last_5years sales salary / level=nominal;
        input satisfaction_level time_spend_company number_project average_montly_hours / level=interval;
        target left /level=nominal;
        train numtries=15 maxiter=300;
    run;

Decision Forest
---------------

.. code:: sas

    proc hpforest data=work._csv;
        input work_accident promotion_last_5years sales salary / level=nominal;
        input satisfaction_level time_spend_company number_project average_montly_hours / level=interval;
        target left /level=nominal;
    run;

