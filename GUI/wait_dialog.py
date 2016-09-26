import tkinter as tk
import tkinter.ttk

import threading


class WaitDialog(tk.Toplevel):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.transient(parent)
        self.title('Please wait...')

        body = tk.Frame(self)
        self.waitBar = tk.ttk.Progressbar(body, orient='horizontal', mode='indeterminate', length=320)
        self.waitBar.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
        self.waitBar.start()
        body.pack(padx=5, pady=5)


        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self.close)

        self.waitBar.focus_set()
        
    def run(self, task, *args, **kwargs):
        thr=threading.Thread(target=self._run_thread,args=(task,)+args,kwargs=kwargs)
        thr.start()
        self.wait_window(self)
        
    def _run_thread(self, task, *args, **kwargs):
        task(*args,**kwargs)
        self.destroy()

    def close(self):
        pass