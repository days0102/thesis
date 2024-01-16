'''
Author       : Outsider
Date         : 2023-11-29 19:58:08
LastEditors  : Outsider
LastEditTime : 2023-11-29 21:00:15
Description  : In User Settings Edit
FilePath     : /thesis/backend/drishti/args.py
'''


class Argument:
    export_html = None
    darshan = None
    export_size = None
    only_issues = None
    export_svg = None
    export_theme_light = None
    verbose = None
    code = None
    full_path = None
    export_csv = None
    json = None
    delete_convert = False

    def __init__(self, file) -> None:
        self.darshan = file
        self.export_html = False
        self.delete_convert = True
