class ExceptionObj():
    def __init__(self, 
        _ID     : int = -1,
        _name   : str = "",
        _url    : str = "",
        _file   : str = "",
        _line   : str = "",       
        _func   : str = ""        
    ):
        self.ID     = _ID
        self.name   = _name
        self.url    = _url
        self.file   = _file
        self.line   = _line
        self.func   = _func

    def __print__():
        print("Exception!")
        print("")