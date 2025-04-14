"""
The FixedWidth class definition.
"""
from decimal import Decimal, ROUND_HALF_EVEN

from datetime import datetime
from six import string_types, integer_types


class FixedWidth(object):
    """
    Class for converting between Python dictionaries and fixed-width
    strings.

    Requires a 'config' dictonary.
    Each key of 'config' is the field name.
    Each item of 'config' is itself a dictionary with the following keys:
        required    a boolean; required
        type        a string; required
        value       (will be coerced into 'type'); hard-coded value
        default     (will be coerced into 'type')
        start_pos   an integer; required
        length      an integer
        end_pos     an integer
        format      a string, to format dates, required for date fields
    The following keys are only used when emitting fixed-width strings:
        alignment   a string; required
        padding     a string; required
        precision   an integer, to format decimals numbers
        rounding    a constant ROUND_xxx used when precision is set

    Notes:
        A field must have a start_pos and either an end_pos or a length.
        If both an end_pos and a length are provided, they must not conflict.

        A field may not have a default value if it is required.

        Type may be string, integer, decimal, numeric, or date.

        Alignment and padding are required.

    """

    def __init__(self, config, **kwargs):

        """
        Arguments:
            config: required, dict defining fixed-width format
            kwargs: optional, dict of values for the FixedWidth object
        """

        self.format_functions = {
            'integer': lambda x: str(self.data[x]),
            'string': lambda x: str(self.data[x]),
            'decimal': self._get_decimal_data,
            'numeric': lambda x: str(self.data[x]),
            'date': self._get_date_data,
        }

        self.line_end = kwargs.pop('line_end', '\r\n')
        self.fixed_point = kwargs.pop('fixed_point', False)
        self.config = config

        self.data = {}
        if kwargs:
            self.data = kwargs

        self.ordered_fields = sorted(
            [(self.config[x]['start_pos'], x) for x in self.config]
        )

        #Raise exception for bad config
        for key, value in self.config.items():

            #required values
            if any([x not in value for x in (
                    'type', 'required', 'padding', 'alignment', 'start_pos')]):
                raise ValueError(
                    "Not all required values provided for field %s" % (key,))

            if value['type'] == 'date':
                if 'format' in value:
                    try:
                        datetime.now().strftime(value['format'])
                    except Exception:
                        raise ValueError("Incorrect format string provided for field %s" % (key,))
                else:
                    raise ValueError("No format string provided for field %s" % (key,))

            elif value['type'] == 'decimal':
                if 'precision' in value and type(value['precision']) != int:
                    raise ValueError("Precision parameter for field %s must be an int" % (key,))

            #end position or length required
            if 'end_pos' not in value and 'length' not in value:
                raise ValueError("An end position or length is required for field %s" % (key,))

            #end position and length must match if both are specified
            if all([x in value for x in ('end_pos', 'length')]):
                if value['length'] != value['end_pos'] - value['start_pos'] + 1:
                    raise ValueError("Field %s length (%d) does not coincide with \
                        its start and end positions." % (key, value['length']))

            #fill in length and end_pos
            if 'end_pos' not in value:
                value['end_pos'] = value['start_pos'] + value['length'] - 1
            if 'length' not in value:
                value['length'] = value['end_pos'] - value['start_pos'] + 1

            #end_pos must be greater than start_pos
            if value['end_pos'] < value['start_pos']:
                raise ValueError("%s end_pos must be *after* start_pos." % (key,))

            #make sure authorized type was provided
            if not value['type'] in ('string', 'integer', 'decimal', 'numeric', 'date'):
                raise ValueError("Field %s has an invalid type (%s). Allowed: 'string', \
                    'integer', 'decimal', 'numeric', 'date" % (key, value['type']))

            #make sure alignment is 'left' or 'right'
            if not value['alignment'] in ('left', 'right'):
                raise ValueError("Field %s has an invalid alignment (%s). \
                    Allowed: 'left' or 'right'" % (key, value['alignment']))

            #if a default value was provided, make sure
            #it doesn't violate rules
            if 'default' in value:

                #can't be required AND have a default value
                if value['required']:
                    raise ValueError("Field %s is required; \
                        can not have a default value" % (key,))

                #ensure default value provided matches type
                if value['type'] == 'decimal' and value['default'] is not None:
                    value['default'] = Decimal(value['default'])
                elif value['type'] == 'date' and isinstance(value['default'], string_types):
                    value['default'] = datetime.strptime(value['default'], value['format'])

                types = {'string': string_types, 'integer': int, 'decimal': Decimal,
                         'numeric': str, 'date': datetime}
                if value['default'] is not None and not isinstance(value['default'], types[value['type']]):
                    raise ValueError("Default value for %s is not a valid %s" \
                        % (key, value['type']))

            #if a precision was provided, make sure
            #it doesn't violate rules
            if value['type'] == 'decimal' and 'precision' in value:

                #make sure authorized type was provided
                if not isinstance(value['precision'], int):
                    raise ValueError("Precision parameter for field %s "
                        "must be an int" % (key,))

                value.setdefault('rounding', ROUND_HALF_EVEN)

        #ensure start_pos and end_pos or length is correct in config
        current_pos = 1
        for start_pos, field_name in self.ordered_fields:

            if start_pos != current_pos:
                raise ValueError("Field %s starts at position %d; \
                should be %d (or previous field definition is incorrect)." \
                % (field_name, start_pos, current_pos))

            current_pos = current_pos + config[field_name]['length']

    def update(self, **kwargs):

        """
        Update self.data using the kwargs sent.
        """

        self.data.update(kwargs)

    def validate(self):

        """
        Ensure the data in self.data is consistent with self.config
        """

        type_tests = {
            'string': lambda x: isinstance(x, string_types),
            'decimal': lambda x: isinstance(x, Decimal),
            'integer': lambda x: isinstance(x, integer_types),
            'numeric': lambda x: str(x).isdigit(),
            'date': lambda x: isinstance(x, datetime),
        }

        for field_name, parameters in self.config.items():

            if field_name in self.data:

                if self.data[field_name] is None and 'default' in parameters:
                    self.data[field_name] = parameters['default']

                data = self.data[field_name]
                # make sure passed in value is of the proper type
                # but only if a value is set
                if data and not type_tests[parameters['type']](data):
                    raise ValueError("%s is defined as a %s, \
                    but the value is not of that type." \
                    % (field_name, parameters['type']))

                #ensure value passed in is not too long for the field
                field_data = self._format_field(field_name)
                if len(str(field_data)) > parameters['length']:
                    raise ValueError("%s is too long (limited to %d \
                        characters)." % (field_name, parameters['length']))

                if 'value' in parameters \
                    and parameters['value'] != field_data:

                    raise ValueError("%s has a value in the config, \
                        and a different value was passed in." % (field_name,))

            else: #no value passed in

                #if required but not provided
                if parameters['required'] and ('value' not in parameters):
                    raise ValueError("Field %s is required, but was \
                        not provided." % (field_name,))

                #if there's a default value
                if 'default' in parameters:
                    self.data[field_name] = parameters['default']

                #if there's a hard-coded value in the config
                if 'value' in parameters:
                    self.data[field_name] = parameters['value']

            if parameters['required'] and self.data[field_name] is None:
                # None gets checked last because it may be set with a default value
                raise ValueError("None value not allowed for %s" % (field_name))

        return True

    def _get_decimal_data(self, field_name):
        """
        quantizes field if it is decimal type and precision is set
        """
        value = str(self.data[field_name])
        if 'precision' in self.config[field_name]:
            value = str(Decimal(value).
                        quantize(Decimal('0.%s' % ('0' *
                        self.config[field_name]['precision'])),
                        self.config[field_name]['rounding']))
        if self.fixed_point:
            value = value.replace('.', '')
        return value

    def _get_date_data(self, field_name):
        return str(self.data[field_name].strftime(self.config[field_name]['format']))

    def _format_field(self, field_name):
        """
        Converts field data and returns it as a string.
        """
        data = self.data[field_name]
        config = self.config[field_name]
        if data is None:
            # Empty fields can not be formatted
            return ''
        type = config['type']
        return str(self.format_functions[type](field_name) if not None else '')

    def _build_line(self):

        """
        Returns a fixed-width line made up of self.data, using
        self.config.
        """

        self.validate()

        line = ''
        #for start_pos, field_name in self.ordered_fields:
        for field_name in [x[1] for x in self.ordered_fields]:

            if field_name in self.data:
                datum = self._format_field(field_name)
            else:
                datum = ''

            justify = None
            if self.config[field_name]['alignment'] == 'left':
                justify = datum.ljust
            else:
                justify = datum.rjust

            datum = justify(self.config[field_name]['length'], \
                self.config[field_name]['padding'])

            line += datum

        return line + self.line_end

    is_valid = property(validate)

    def _string_to_dict(self, fw_string):

        """
        Take a fixed-width string and use it to
        populate self.data, based on self.config.
        """

        self.data = {}

        for start_pos, field_name in self.ordered_fields:

            conversion = {
                'integer': int,
                'string': lambda x: str(x).strip(),
                'decimal': Decimal,
                'numeric': lambda x: str(x).strip(),
                'date': lambda x: datetime.strptime(x, self.config[field_name]['format']),
            }

            row = fw_string[start_pos - 1:self.config[field_name]['end_pos']]
            if row.strip() == '' and 'default' in self.config[field_name]:
                # Use default value if row is empty
                self.data[field_name] = self.config[field_name]['default']
            else:
                self.data[field_name] = conversion[self.config[field_name]['type']](row)

        return self.data

    line = property(_build_line, _string_to_dict)
