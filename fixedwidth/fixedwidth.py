#!/usr/bin/env python

from decimal import Decimal


class FixedWidth(object):
    
    """
    Class for converting between Python dictionaries and fixed-width
    strings.
    
    Requires a 'config' dictonary. See unittest below for an example.
        

    Notes: 
        A field must have a start_pos and either an end_pos or a length.
        If both an end_pos and a length are provided, they must not conflict.
        
        A field may not have a default value if it is required.
        
        Type may be string, integer, or decimal.
        
        Alignment and padding are required.
        
        'required' must have a value.
        
    }
    
    """
    
    def __init__(self, config, **kwargs):
        
        """
        Arguments: 
            config: required, dict defining fixed-width format
            kwargs: optional, dict of values for the FixedWidth object
        """
        
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
                raise ValueError("Not all required values provided for field %s" % (key,))
            
                
                
            #end position or length required
            if ('end_pos' not in value and 'length' not in value):
                raise ValueError("And end position or length is required for field %s" % (key,))
            
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
            if not value['type'] in ('string', 'integer', 'decimal', 'numeric'):
                raise ValueError("Field %s has an invalid type (%s). Allowed: 'string', \
                    'integer', 'decimal', 'numeric'" % (key, value['type']))

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
                types = {'string': str, 'decimal': Decimal, 'integer': int}
                if not isinstance(value['default'], types[value['type']]):
                    raise ValueError("Default value for %s is not a valid %s" \
                        % (key, value['type']))
        
        
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
        ensure the data in self.data is consistant with self.config
        """
        
        type_tests = {
            'string': lambda x: isinstance(x, str) or isinstance(x, unicode), 
            'decimal': lambda x: isinstance(x, Decimal), 
            'integer': lambda x: str(x).isdigit(),
            'numeric': lambda x: str(x).isdigit(),
        }
        
        for field_name, parameters in self.config.items():
            
            if field_name in self.data:
                
                #make sure passed in value is of the proper type
                if not type_tests[parameters['type']](self.data[field_name]):
                    raise ValueError("%s is defined as a %s, \
                    but the value is not of that type." \
                    % (field_name, parameters['type']))
                    
                #ensure value passed in is not too long for the field
                if len(str(self.data[field_name])) > parameters['length']:
                    raise ValueError("%s is too long (limited to %d \
                        characters)." % (field_name, parameters['length']))
                    
                    
                if 'value' in parameters \
                    and parameters['value'] != self.data[field_name]:  
                    
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
        
        return True
        
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
                datum = str(self.data[field_name])
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
            

        return line + '\r\n'
    
    
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
            }
            
            
            self.data[field_name] = conversion[self.config[field_name]\
                ['type']](fw_string[start_pos - 1:self.config[field_name]['end_pos']])
            
        return self.data
    
    
    
    
    line = property(_build_line, _string_to_dict)
    