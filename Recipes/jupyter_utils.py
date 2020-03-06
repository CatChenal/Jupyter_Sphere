# jupyter_utils.py

import IPython
from IPython import get_ipython
from IPython.display import Markdown


def test_ipkernel(verbose=False):
    found = 'ipykernel_launcher.py' in sys.argv[0]
    if verbose:
        verb = 'IS' if found else 'IS NOT'
        msg = f'Code *{verb}* running in Jupyter platform (notebook, lab, etc.)'       
        print(msg)
    return found


def is_lab_notebook():
    import re
    import psutil

    return any(re.search('jupyter-lab-script', x)
               for x in psutil.Process().parent().cmdline())

def ipy_set_next_input(cell_contents, replace_cell):
    if replace_cell:
        shell = get_ipython()

        payload = dict(
            source='set_next_input',
            text=cell_contents,
            replace=True,
        )
        shell.payload_manager.write_payload(payload, single=False)
    else:
        return Markdown(cell_contents)
    

def insert_md_div(div_text_format, div_data=None, replace_cell=False):
    """
    Output Markdown of string with inserted data.
    div_text_format, e.g.: 
               "this is my data: {}" if div_data=x or [x]
               "that too: {}, {}" if div_data=[x,y] or (x,y)
     => assume # place holders == # data items.
    """
    if div_data is None or '{' not in div_text_format:
        # todo: flag error? (bc function not needed)
        return Markdown(div_text_format)

    mismatch_err = 'Format placeholders != data items'
    if isinstance(div_data, (tuple, list)):
        if div_text_format.count('{}') != len(div_data):
            raise IndexError(mismatch_err)
        div = div_text_format.format(*div_data)
        
    elif isinstance(div_data, dict):
        if '{}' not in div_text_format:
            # eg, assume keys given as indices: 'a is {a}, b is {b}'
            div = div_text_format.format_map(div_data)
        else:
            if div_text_format.count('{}') != len(div_data.values()):
                raise IndexError(mismatch_err)
            div = div_text_format.format(*div_data.values())

    else:
        if div_text_format.count('{}') != 1:
            raise IndexError(mismatch_err)
        div = div_text_format.format(div_data)

    return ipy_set_next_input(div, replace_cell)


def insert_alert_div(div_class, div_header=None, div_text=None, 
                     use_class_as_header=True,
                     replace_cell=False):
    """
    use_class_as_header: if div_header=None, div_class is used if 
                         use_class_as_header=True
    Behaviour with `replace_cell=True`:
    The cell is overwritten with the output string:
    ```
    [x]
    alert_div('warning', 'Tip: ', 'some tip here', replace_cell=True)
    The [x] cell becomes:
    [x]
    <div class="alert alert-warning"><b>Tip: </b>some tip here</div>
    ```
    However, the cell mode is still in 'code' not 'markdown', so the desired output
    is obtained only after *manually* changing the cell mode to Markdown.
    
    If `replace_cell=False (default)`, the Markdown string is displayed as any code output cell,
    i.e. below the code cell.
    """
    accepted = ['info', 'warning', 'danger']
    if div_class.lower() not in accepted:
        s = f'<div class="alert"><b>Wrong class:</b> `div_class` not in {accepted}</div>'
        return Markdown(s)
    
    div_class = div_class.lower()
    div_class = 'alert-' + div_class
    div = f'<div class="alert {div_class}"><p style="font-size:1.2em">'
    
    headr = div_header is not None
    if use_class_as_header and not headr:
        div_header = div_class.capitalize()
        headr = True
        
    if headr:
        div_header = div_header.capitalize()
        div += f'<b>{div_header}</b>'
        
    if div_text is not None:
        div_text =  div_text[0].upper() + div_text[1:]
        if headr:
            div += f'<br>&emsp;&emsp;{div_text}'
        else:
            div += f'&ensp;{div_text}'
    
    div += '</p></div>'

    return ipy_set_next_input(div, replace_cell)


def format_with_bold(s_format, data=None):
    """
    Returns the string with all placeholders preceeded by '_b' replaced 
    with a bold indicator value;
    
    :param: s_format: a string format; 
            if contains '_b{}b_' this term gets bolded.
    :param: s: a string or value
    
    Note 1: '... _b{}; something {}b_ ...' is a valid format.
    Note 2: IndexError is raised using the output format only when
            the input tuple length < number of placeholders ({});
            it is silent when the later are greater (see Example).
    
    Example:
    # No error:
    fmt = 'What! _b{}b_; yes: _b{}b_; no: {}.'
    print(format_with_bold(fmt).format('Cat', 'dog', 3, '@no000'))
    # IndexError:
    print(format_with_bold(fmt).format('Cat', 'dog'))
    """
    if data is None:
        raise TypeError('Missing data (is None).')
    if '{' not in s_format:
        raise TypeError('Missing format placeholders.')
                    
    # Check for paired markers:
    if s_format.count('_b') != s_format.count('b_'):
        err_msg1 = "Bold indicators not paired. Expected '_b with b_'."
        raise LookupError(err_msg1)
    
    # Check for start bold marker:
    b1 = '_b'
    i = s_format.find(b1 + '{')
    
    # Check marker order: '_b' before 'b_':
    if i > s_format.find('}' + 'b_'):
        err_msg2 = "Starting bold indicator not found. Expected '_b before b_'."
        raise LookupError(err_msg2)
        
    while i != -1:
        # Check for trailing bold marker:
        b2 = 'b_'
        j = s_format.find('}' + b2)
        
        if j != -1:
            s_format = s_format.replace(b1, '\033[1m')
            s_format = s_format.replace(b2, '\033[0m')
        else:
            err_msg3 = "Trailing bold indicator not found. Expected '_b with b_'."
            raise LookupError(err_msg3)
            
        i = s_format.find(b1 + '{')
    
    # Now combine string with data:
    mismatch_err = 'Format placeholders != data items'
    
    if isinstance(data, (tuple, list)):
        if s_format.count('{}') != len(data):
            raise IndexError(mismatch_err)
        return s_format.format(*data)
    
    elif isinstance(data, dict):
        if '{}' not in s_format:
            # eg, assume keys given as indices: 'a is {a}, b is {b}'
            return s_format.format_map(data)
        else:
            if s_format.count('{}') != len(data.values()):
                raise IndexError(mismatch_err)
            return s_format.format(*data.values())
    else:
        if s_format.count('{}') != 1:
            raise IndexError(mismatch_err)
        return s_format.format(data)


def poly_to_latex_str(p):
    import numpy as np


    terms = ['{:.2g}'.format(p.coef[0])]
    if len(p) > 1:
        term = 'x'
        c = p.coef[1]
        if c != 1:
            term = ('{:.2g}'.format(c)) + term
        terms.append(term)
    if len(p) > 2:
        for i in range(2, len(p)):
            term = 'x^{:d}'.format(i)
            c = p.coef[i]
            if c != 1:
                term = ('{:.2g}'.format(c)) + term
            terms.append(term)
    px = '$P(x) = {:s}$'.format(' + '.join(terms))
    px += ', $x \in [{:.2g},\ {:.2g}]$'.format(*p.domain)
    return px


def CSI_examples():
    s = "Some simple string"
    ESC_ = '\033['

    print(f"{ESC_}0;0;0m{s}{ESC_}0;0;m")
    print(f"{ESC_}0;0;1m{s}{ESC_}0;0;m")
    print(f"{ESC_}0;0;4m{s}{ESC_}0;0;m") #4m: underline
    #print(f"{ESC_}1;38;41m{s}{ESC_}1;38;0m")
    print(f"{ESC_}45;37;4m{s}{ESC_}0;0;m\n")
    
    print(f"{ESC_}0;0;41m{s}{ESC_}0;0;m")
    print(f"{ESC_}0;0;42m{s}{ESC_}0;0;m")
    print(f"{ESC_}0;0;43m{s}{ESC_}0;0;m")
    print(f"{ESC_}0;0;44m{s}{ESC_}0;0;m\n")
    
    print(f"{ESC_}0;0;45m{s}{ESC_}0;0;m")
    print(f"{ESC_}41;4;11m{s}{ESC_}m")
    print(f"{ESC_}0;0;46m{s}{ESC_}0;0;m")
    print(f"{ESC_}10;0;41m{s}{ESC_}m\n")
    
    
    print("These may not render properly:\n")

    print("\033[5;37;0m{}\033[5;37;m".format('Normal text'))
    print("\033[5;51;0m{}\033[5;37;m".format('Normal text2'))

    print("\033[5;38;1m{}\033[5;38;0m".format('Bold text'))
    print("\033[5;38;2m{}\033[5;37;0m".format('Faint text'))

    #print("\033[1;31;50m{}\033[0m 1;31;50m \n".format('Some text')) 
    #print("\033[1;37;40m{}\033[0m 1;37;40m \n".format('Some text')) 

    print("\033[5;37;5m{}\033[5;37;m".format('Bright Colour'))
    print("\033[5;37;4m{}\033[5;37;m".format('Underlined text'))

    print("\033[3;37;m{}\033[0;37;m".format('Negative Colour'))
    print("\033[4;37;m{}\033[0;37;m".format('which? Colour'))
    print("\033[5;37;m{}\033[0;37;m".format('Negative Colour'))

