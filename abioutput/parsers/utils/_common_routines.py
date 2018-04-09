from math import sqrt  # noqa


def decompose_line(line):
    # from here we have the lines from either format
    # varname         value
    # value
    # _logger.debug("Decomposing line %s" % line)
    l = line.split(" ")
    strings = []
    ints = []
    floats = []
    for element in l:
        try:
            if element == "":
                # drop the empty strings
                continue
            # check if element is an integer
            try:
                i = int(element)
            except ValueError:
                # not an integer
                pass
            else:
                ints.append(i)
                continue
            # check if element is a float
            try:
                f = float(element)
            except ValueError:
                # not a float
                pass
            else:
                floats.append(f)
                continue
            # check if it is a fraction or radical exposed as a string
            try:
                f = eval(element)
            except (NameError, SyntaxError):
                # not a fraction-like string
                pass
            else:
                # append only if it is a float
                if callable(f):
                    # return it to a string. This means the word was eval
                    # as a valid python function like "max" or "min" or etc.
                    strings.append(f.__name__)
                else:
                    floats.append(f)
                continue
            if "E-" in element and "." in element:
                # maybe there is a bug with abinit and two floats are
                # glued together. try to separate them
                f1, f2 = try_debug_2floats(element)
                if f1 is not None:
                    # it worked !
                    floats.append(f1)
                    floats.append(f2)
                    continue
            # from here, element is neither a float nor an int => string
            strings.append(element)
        except SyntaxError as e:
            # if we're here, something unexpected happened in the file.
            # return None and alert user
            print("Can't parse line for some reason: %s" % line)
            raise e
    return strings, ints, floats


def try_debug_2floats(string):
    # try to separate two floats glued in a string e.g. 1.52E-0210.000
    E = string.index("E")
    # there is always two numbers in the exponent
    split = E + 4
    f1 = string[:split]
    f2 = string[split:]
    try:
        f1 = float(f1)
        f2 = float(f2)
    except:
        print("%s could not be decomposed into 2 floats." % string)
        return None, None
    else:
        # it worked
        return f1, f2
