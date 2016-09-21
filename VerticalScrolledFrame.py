import tkinter as tk

# adapted from http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
class VerticalScrolledFrame(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)
        self.config(borderwidth=2, relief='sunken')

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=tk.NW)

        self.prev_size = (interior.winfo_reqwidth(), max(interior.winfo_reqheight(), canvas.winfo_reqheight()))

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), max(interior.winfo_reqheight(), canvas.winfo_height()))
            if self.prev_size != size:
                canvas.config(scrollregion="0 0 %s %s" % size)
                self.prev_size = size
            # update the canvas's width to fit the inner frame
            if canvas.winfo_reqwidth() != interior.winfo_reqwidth():
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            # update the inner frame's width to fill the canvas
            if canvas.winfo_reqwidth() != interior.winfo_reqwidth():
                canvas.itemconfigure(interior_id, width=canvas.winfo_reqwidth())
        canvas.bind('<Configure>', _configure_canvas)
        self.canvas=canvas
