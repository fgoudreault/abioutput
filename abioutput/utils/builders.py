from ..bases import BaseUtility
from .bases import BaseBuilder
from .calculation_dir import CalculationDir
from .routines import styled_text
from tabulate import tabulate
from colorama import Fore, Style
import numpy as np
import os
import time


TIME_BETWEEN_UPDATES = 300  # seconds


class Table(BaseUtility):
    """Class that serves as template to print a table in terminal.
    """
    _loggername = "Table"

    def __init__(self, column_names, **kwargs):
        """Table init method.

        Parameters
        ----------
        column_names : list
                       The list of column names. The length of this list
                       dictates the number of columns.
        """
        super().__init__(**kwargs)
        self.column_names = column_names
        self.rows = []

    def add_column(self, column_header, column, index=None):
        """Add a column to the table.

        Paramters
        ----------
        column_header : str
                        The title of the column.
        column : list
                 The data list of the column. Must match the
                 number of rows.
        index : int, optional
                If not None, insert column before that index.
        """
        self.column_names.append(column_header)
        if len(column) != len(self.rows) and len(self.rows) > 0:
            raise ValueError("Column length does not match number of rows.")
        if index is None:
            index = len(self.rows[0])  # append at the end
        for i, data in enumerate(column):
            self.rows[i].insert(index, data)

    def add_row(self, row):
        """Add a row to the table.

        Parameters
        ----------
        row : list
              The row of data to add. Must be the same length
              as the number of columns.
        """
        if len(row) != len(self.column_names):
            raise ValueError("Row to add is not the same length"
                             " as the others.")
        self.rows.append(row)

    def _check_column_exists(self, column_title):
        if column_title not in self.column_names:
            raise KeyError(f"{column_title} not in the column headers.")

    def is_column_sortable(self, column_title):
        """Check if a column is sortable or not.

        Parameters
        ----------
        column_title : str
                       The column header.

        Returns
        -------
        bool : True if the column is (at least partially) sortable.
        """
        self._check_column_exists(column_title)
        sortable_rows = self._sortable_rows_indices(column_title)
        if len(sortable_rows) == 0:
            return False
        return True

    def _sortable_rows_indices(self, column_title):
        # find sortable values rows by checking value in the column
        # if value is not a float nor an int, row is not sortable
        column_index = self.get_column_index(column_title)
        sortable_rows = [i for i, x in enumerate(self.rows)
                         if type(x[column_index]) in (int, float)]
        return sortable_rows

    def sortby(self, column_title):
        """Sort the table.

        Parameters
        ----------
        column_title : str
                       Sort in increasing order according to this column.
        """
        self._check_column_exists(column_title)
        if not self.is_column_sortable(column_title):
            self._logger.warning(f"{column_title} not sortable...")
        self._logger.info(f"Sorting table according to {column_title}.")
        sortable_rows = self._sortable_rows_indices(column_title)
        non_sortable_rows = [i for i in range(len(self.rows))
                             if i not in sortable_rows]
        # sort the sortable rows
        sort_indices = np.argsort(self.get_column(column_title,
                                                  indices=sortable_rows))
        newrows = [self.rows[x] for x in sort_indices]
        # add non sortable rows at the end
        for i in non_sortable_rows:
            newrows.append(self.rows[i])
        # just a little checkup that everything went well
        assert len(newrows) == len(self.rows)
        self.rows = newrows

    def get_column(self, column_title, indices=None):
        """Returns the data of a column.

        Parameters
        ----------
        column_title : str
                        The column header.
        indices : list, optional
                  The list if index to keep.
        """
        self._check_column_exists(column_title)
        column_index = self.column_names.index(column_title)
        toreturn = [row[column_index] for row in self.rows]
        # remove indices if needed
        if indices is not None:
            toret = []
            for i in indices:
                toret.append(toreturn[i])
            toreturn = toret
        return toreturn

    def get_column_index(self, column_title):
        """Returns the index of the column.

        Parameters
        ----------
        column_title : str
                       The column header.
        """
        self._check_column_exists(column_title)
        return self.column_names.index(column_title)

    def print(self):
        print(tabulate(self.rows, headers=self.column_names))


class TreeBuilder(BaseBuilder):
    """Object that starts at the top of a directory tree and scrolls down
    in all its subdirectories in order to get the status of each abinit
    calculations. The status is checked by looking at the log file for the
    'Calculation completed.' keyword.

    When looking down in the tree, we assume that a caculation directory
    does not have subdirectories containing other calculations
    (this may be a future feature to look down everywhere).
    """
    _loggername = "TreeBuilder"

    def __init__(self, top_directory,
                 ignore=None,
                 time_between_updates=TIME_BETWEEN_UPDATES, **kwargs):
        """TreeBuilder init method.

        Parameters
        ----------
        top_directory : str
                        The top directory path.
        ignore : list, optional
                 If not None, ignore these directories and its subdirectories.
        time_between_updates : float, optional
                               Gives the minimal time before updating
                               the status tree.
        """
        super().__init__(top_directory, **kwargs)
        self._logger.info(f"Computing calculation tree status from"
                          f" {self._top_directory}")
        if ignore is None:
            ignore = []
        if isinstance(ignore, str):
            ignore = [ignore, ]
        self._logger.debug(f"Ignore these directories: {ignore}.")
        self.tree = self._get_tree(self._top_directory, ignore)
        self._status = None
        self._last_update = time.time() - time_between_updates
        self.time_between_updates = time_between_updates

    def _set_main_directory(self, directory_name):
        self._top_directory = directory_name

    def _get_tree(self, top_directory, ignore):
        # check if current dir is a calculation directory
        if CalculationDir.is_calculation_dir(top_directory):
            self._logger.debug(f"Found a calculation directory:"
                               f" {top_directory}")
            return [CalculationDir(top_directory,
                                   ignore=ignore,
                                   loglevel=self._logger.level)]
        # if not, look in all subdirectories
        subentries = os.listdir(top_directory)
        subdirs = [os.path.join(top_directory, x)
                   for x in subentries if os.path.isdir(x)]
        # remove directories to ignore
        subdirs = [x for x in subdirs if os.path.basename(x) not in ignore]
        status = []
        for subdir in subdirs:
            status += self._get_tree(os.path.join(top_directory,
                                                  subdir),
                                     ignore)
        return status

    @property
    def status(self):
        if time.time() - self._last_update < self.time_between_updates:
            self._logger.debug("Don't need to reupdate tree: too soon.")
            return self._status
        status = []
        self._logger.info("Computing status of calculation tree.")
        for calc in self.tree:
            status.append(calc.status)
        self._status = status
        self._last_update = time.time()
        return self._status

    def print_attributes(self, *args, shortpath=True, delta=None, sortby=None,
                         precision=2):
        """Print a table of the arguments from each calculation in the tree.
        Can print computation status as well as output variables.

        Parameters
        ----------
        args : str
               All args are either 'status' and/or abinit variable names.
               All args are shown in the printed table at the end.
               If the arg is 'status', prints the state of the calculation.
               If the arg is 'convergence_reached', prints the convergence
               status.
               Anything else will print the value of the output variable.
        shortpath : bool, optional
                    If False, the full path to the calculation is shown.
        delta : str, optional
                A column will be added
                to show the variations of the parameter. It should be
                an abinit output variable (like 'etotal').
        sortby : str, optional
                 Sorts the calculations by the name of this variable.
                 E.g.: if you give 'ecut' in args and in sortby, calculations
                 will be sorted by increasing ecut.
        precision : int, optional
                    Number of decimals for delta columns.
        """
        if delta is not None and sortby is None:
            raise ValueError("Delta is not None but values need to be compared"
                             " to something. Use the sortby argument to tell"
                             " which value to compare to.")
        args = list(args)
        self._logger.info(f"Getting tree attributes for {args}.")
        # create first column which tells the calculation title
        table = Table(["calculations"])
        calcs = self._get_calculations()
        for calc in calcs:
            table.add_row([calc])

        # print calculation status if needed
        if "status" in args:
            args.remove("status")
            table.add_column("status",
                             self._get_calculation_status())
        # print convergence status if needed
        if "convergence_reached" in args:
            args.remove("convergence_reached")
            table.add_column("convergence", self._get_convergence())
        # print each attribute column
        for arg in args:
            values = []
            for i, calc in enumerate(self.tree):
                status = self.status[i]
                # if computation not finished; attribute is not available
                if not status["calculation_finished"]:
                    values.append(styled_text("NOT AVAILABLE",
                                              style=Style.BRIGHT))
                    continue
                # use element 0 here cause values are tuples (val, units)
                values.append(calc.get_output_var(arg)[0])
            table.add_column(arg, values)
            self._logger.debug(f"Values for {arg} found are: {values}.")

        # sort table if needed
        if sortby is not None:
            table.sortby(sortby)
        # finish the first loop to make sure the sorted value is retrieved
        # and table has been sorted already.
        if delta is not None:
            self._add_delta_columns(delta, table, precision)
        table.print()

    def _add_delta_columns(self, delta, table, precision):
        # in the table, add columns of delta values for each value in delta
        # sorted according to the sortby column. Print result with 'precision'
        # decimals
        # WE ASSUME HERE THE TABLE HAS ALREADY BEEN SORTED
        for d in delta:
            if not table.is_column_sortable(d):
                # column cannot be sorted, do not compute deltas
                continue
            deltas = []  # delta column values
            # if column is sortable => at least one value is an int or a float
            data = table.get_column(d)
            index = table.get_column_index(d)
            # indices of values which we can extract a delta
            can_work_with_indices = [i for i, x in enumerate(data)
                                     if type(x) in (int, float)]
            last_can_work = 0
            for i, x in enumerate(data):
                if i in can_work_with_indices:
                    # can compute a delta
                    if last_can_work == 0:
                        # first value => no delta to compute
                        deltas.append("--")
                        last_can_work += 1
                        continue
                    lastval = data[can_work_with_indices[last_can_work - 1]]
                    delta_val = round((x - lastval) / abs(lastval) * 100,
                                      precision)
                    deltas.append(delta_val)
                    last_can_work += 1
                else:
                    # cannot work with this value
                    deltas.append(styled_text("NOT AVAILABLE",
                                              style=Style.BRIGHT))
            self._logger.debug(f"deltas to add {d}: {deltas}.")
            table.add_column("delta_" + d + " (%)", deltas, index=index + 1)

    def print_status(self, shortpath=True):
        """Prints the status of each calculation in the calculation tree.

        Parameters
        ----------
        shortpath : bool, optional
                    If False, the full path to the calculation directories are
                    given instead of relative paths.
                    If True, the relative path to the current directory (where
                    the script is executed) is given instead.
        """
        self.print_attributes("status", "convergence_reached",
                              shortpath=shortpath)

    def _get_calculations(self, shortpath=True):
        paths = []
        for calc in self.tree:
            path = calc.path
            if shortpath:
                path = os.path.relpath(path)
            paths.append(path)
        return paths

    def _get_calculation_status(self):
        # get calculation status for each calculation.
        statuses = []
        for calculation in self.status:
            started = calculation["calculation_started"]
            finished = calculation["calculation_finished"]
            if not started:
                status = styled_text("NOT STARTED",
                                     color=Fore.RED,
                                     style=Style.BRIGHT)
            elif started and not finished:
                status = styled_text("NOT FINISHED",
                                     color=Fore.YELLOW,
                                     style=Style.BRIGHT)
            elif started and finished:
                status = styled_text("COMPLETED",
                                     color=Fore.GREEN,
                                     style=Style.BRIGHT)
            statuses.append(status)
        return statuses

    def _get_convergence(self):
        # we assume here a SCF calculation
        statuses = []
        for output, calculation in zip(self.tree, self.status):
            started = calculation["calculation_started"]
            finished = calculation["calculation_finished"]
            conv = output.is_calculation_converged
            if not started and not finished:
                status = styled_text("NOT AVAILABLE",
                                     style=Style.BRIGHT)
            if started and not finished:
                status = styled_text("NOT AVAILABLE",
                                     style=Style.BRIGHT)
            elif conv is False and finished:
                status = styled_text("NOT REACHED",
                                     color=Fore.RED,
                                     style=Style.BRIGHT)
            elif conv is True and finished:
                status = styled_text("REACHED",
                                     color=Fore.GREEN,
                                     style=Style.BRIGHT)
            statuses.append(status)
        return statuses
