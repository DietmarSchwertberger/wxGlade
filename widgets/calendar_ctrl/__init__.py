"""
calendar_ctrl widget module initialization

@copyright: 2007 Alberto Griggio
@license: MIT (see license.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

def initialize():
    import config
    import codegen
    codegen.initialize()
    if config.use_gui:
        import calendar_ctrl
        return calendar_ctrl.initialize()
