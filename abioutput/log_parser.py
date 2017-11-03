from .output_parser import OutputParser


class LogParser(OutputParser):
    """An ABINIT log file parser.
    """

    def _get_data_per_dtset(self, *args, **kwargs):
        """Overridden function. For a log file, do not parse each dtset for
        now.

        TODO: Implement this function for dtset parsing in the logfile.
        """
        return None
