class AbinitVarStrToNum:
    def __init__(self, var_dict):
        # class that converts a dict of variables got from abipy
        # as string pairs into pairs of string; numeric value
        self.data = self._extract_data(var_dict)

    def _extract_data(self, var_dict):
        data = {}
        for name, value in var_dict.items():
            if "Printing" in value:
                # only exceptions is variables that only prints warnings
                continue
            val, units = self._convert_value(value)
            data[name] = {"value": val, "units": units}
        return data

    def _convert_value(self, value):
        # here, value is a the value of an abinit variable as a string
        # we want to convert it into a float, int or array
        a = StrConverter(value)
        return a.value, a.units


class StrConverter:
    def __init__(self, string):
        # converts a string to an usable value
        self.value, self.units = self._get_value(string)

    def _get_value(self, string):
        # converts the string
        # check it has units
        numpart, units = self._extract_units(string)
        # here, numpart should only be a string containing digits
        # check if its a vector
        s = numpart.split()
        if len(s) > 1:
            return self._convert_to_vector(s), units
        # not a vector => single value
        return self._convert_to_numeric(numpart), units

    def _convert_to_vector(self, list_of_str):
        vector = []
        for x in list_of_str:
            vector.append(self._convert_to_numeric(x))
        return vector

    def _convert_to_numeric(self, numericstring):
        # here we assume that numeric string is a string of a digit
        # check if integer
        try:
            i = int(numericstring)
        except ValueError:
            # not an integer
            pass
        else:
            return i

        # check should be a float
        try:
            f = float(numericstring)
        except ValueError:
            # not a float
            pass
        else:
            return f
        # if we are here, there is a problem
        raise ValueError("'%s' is not a numeric string!" % numericstring)

    def _extract_units(self, string):
        splitted = string.split()
        if len(splitted) == 1:
            # don't bother
            return string, None
        if splitted[-1].isalpha():
            # this string is a unit string
            return " ".join(splitted[:-1]), splitted[-1]
        else:
            # no units
            return string, None
