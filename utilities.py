#/usr/bin/python

def flattenList1(x):
    """
    Flatten a list of lists into a single list
    (c) Alex Martelli, 6/4/09 http://goo.gl/7JUxE
    """
    y = [item for sublist in x for item in sublist]
    return(y)

def flattenList2(x):
    """
    Flatten a list of lists into a single list
    (c) "Triptych" 6/4/09 http://goo.gl/7JUxE
    """
    y = sum(x,[])
    return(y)

