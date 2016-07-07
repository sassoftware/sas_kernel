# SAS Kernel Magics
Jupyter magics are special functions that perform tasks before code is sent to the kernel
To see the list of magic you can use the `%lsmagic`

Magics must be at the the first line of the cell or else they will be submitted to the kernel for execution
This presents a problem for SAS since SAS Macro (R) uses `%` to denote a macro variable. Currently if you have a SAS Macro in the first line it will try and interpret it as a magic. Entering a blank line will resolve the issue

## prompt4var
prompt4var includes both a line and cell magics. The general function of hte magic is to prompt the user for values to create macro variables in the SAS session associated with that notebook.
### Line Magic

#### Examples
1. Create macro variables without code. The code below will prompt each time the cell is executed for `libpath` and `file1`. There is no associated code and the those macro variables will exist for remainder of session (or until kernel is restarted)
```
%prompt4var libpath file1
```

1. Line prompt with code included

```
%prompt4var libpath file1
filename myfile "~&file1.";
libname data "&libpath";
```
### Cell Magic
The cell magic prompts users for variables that are intended to be private -- passwords and such. The macro variables will be deleted from the when the cell finishes processing. Libnames assigned will still be active but the password will not be stored anywhere.

#### Examples
1. Password protecting a data set

```
%%prompt4var alter read 
data work.cars(alter="&alter" read="&read");
    set sashelp.cars;
    id = _n_;
run;
proc print data=cars(read="badpw" obs=10);
run;
proc print data=cars(read="&read" obs=10);
run;
```

1. Assign libraries to RDBMS

```
%%prompt4var pw1 pw2
libname foo teradata user=scott password=&pw1;
libname bar oracle user=tiger password=&pw2;
```