# Open e2sSample.all Library Editor (Oe2sSLE) for Electribe Sampler

This is an editor for electribe sampler (e2s) sample library.
It allows library management and supports sample loops and slices editing.
You can also remove or replace factory samples with your own.

This code was developed for python 3.6, but shall be compatible with python 3.5 and 3.4.
Graphical user interface is using tkinter to reduce external dependencies. The only requirement is
[pyaudio](https://people.csail.mit.edu/hubert/pyaudio/) for audio sample listening (tested with pyaudio v0.2.11):

`pip install pyaudio`

run the application with

`python Oe2sSLE_GUI.py`

This application is still under development, so if you encounter a bug, do not hesitate to report it as a new Issue.

For this, if possible try to reproduce the bug, then delete (or rename) the log file, then reproduce the bug one more time and attach (or copy/paste content of) the new created (clean) log file to the
description of the Issue.

The log file should be located in `~/.Oe2sSLE/Oe2sSLE.log` (`<your drive letter>:\\Users\\<your username>\\.Oe2sSLE\\Oe2sSLE.log` on windows).


For Mac OS X Users
---

If you want to run the application directly from the source, there are know issues when you use tkinter (Tcl/Tk python wrapper) for GUI development on Mac OS X.
If you follow the next steps, it should work:
- First you will need to install a Tcl/Tk distribution that is more recent than the one provided in Mac OS. It is recommended to install ActiveTcl 8.5.18.0 from [Active State web site](http://www.activestate.com/activetcl/downloads).
- Then it is recommended to install the official python 3.5.3 distribution from [python web site](https://www.python.org/downloads/mac-osx/).

For more details on the issue, see [this page](https://www.python.org/download/mac/tcltk/).


Some screenshots:
---

![Main window screenshot](doc/images/screenshot_main.png?raw=true "Screen shot of the main interface window")

Screen shot of the main interface window

![Sample edit window screenshot 1](doc/images/screenshot_slice_edit_1.png?raw=true "Screen shot of the sample loop/sclices edition window: editing area for sample's and slices points")

Screen shot of the sample loop/sclices edition window: editing area for sample's and slices points

![Sample edit window screenshot 2](doc/images/screenshot_slice_edit_2.png?raw=true "Screen shot of the sample loop/sclices edition window: editing area for slices tempo")

Screen shot of the sample loop/sclices edition window: editing area for slices tempo


Quick documentation:
---

The Oe2sSLE (Open e2sSample.all Library Editor) is an application editing an `e2sSample.all` file (a sample library).

### 1. Basics

#### 1.1 Open

The sample library is empty when the application starts. Use the `Open` button of the application if you want to edit an existing library, previously saved by the application, or exported by the electribe sampler using `DATA UTILITY/EXPORT ALL SAMPLE` (in which case it is in the `KORG/electribe sampler/Sample/` of the SD card, with the name `e2sSample.all`).

> When you use `Open` button, unsaved work will be lost. Don't forget to save your work before using `Open`.

#### 1.2 Save As

At any time you can save your work (the edited sample library) with the `Save As` button.

You can then put the sample library file onto an SD card:
- into the `KORG/electribe sampler/Sample/` directory of the SD card, with the `e2sSample.all` filename; thus the sample library will be loaded by the electribe sampler when it boots. Note that it is also the location where the electribe sampler exports the `e2sSample.all` file. If you do `DATA UTILITY/EXPORT ALL SAMPLE` from the electribe sampler menu, you will erase your file.
- in a folder of your choice, with the name of your choice (you must use the '.all' extension); then you will be able to import it with the electribe sampler from `DATA UTILITY/IMPORT SAMPLE` menu. Note that the file names are displayed by the electribe sampler without the file extension ('foo.all' file will be displayed as 'foo'). This is the same for classical WAV files: the '.wav' extension is not displayed. So, preferably do not use the same name for a WAV file and for your sample library, as it could be confusing.

> Do not forget to save frequently, as the software may still contain some bugs. Also we recommend to make backups of your work, as the life of an SD card is limited.

#### 1.3 Remove samples from the library

##### 1.3.1 Clear all

If you want to completely clear the edited sample library (i.e. remove all the samples), use the `Clear all` button.

> When you use `Clear all` button, unsaved work will be lost. Don't forget to save your work before using `Clear all`.

##### 1.3.2 Delete individual samples

If you want to delete a specific sample, use the 'delete' ![delete sample icon](images/trash.gif?raw=true "delete") button of the corresponding sample.

> You can't undo the delete operation.

#### 1.4 Import samples

##### 1.4.1 Import wav Sample(s)

In order to import and add existing samples contained into WAV files, use the `Import wav Sample(s)` button.

> Imported samples will be attributed the first free sample number starting from `From #Num` (default is 19) as specified in the `Import Options` ([see Import Options section](#144-import-options)).

##### 1.4.2 Import samples of a sample library file

In order to import and add to your library all the samples contained in an existing sample library file, you can use the `Import e2sSample.all` button.

> When a sample library is imported (not opened) the original sample numbers will not be kept. Instead, each sample (taken in the same order as in the library file) will be attributed the first free sample number starting from `From #Num` (default is 19) as specified in the `Import Options` ([see Import Options section](#144-import-options)).

##### 1.4.3 Import a single sample to replace an existing one

If you want to import a sample to replace an existing one, use the 'import replacement sample' ![import replacement sample icon](images/replace.gif?raw=true "import replacement sample") button corresponding to the sample to be replaced.

> After a sample has been replaced by another one, it is lost. You can't undo the operation.

##### 1.4.4 Import options

If you click on `Import Options` button, you will open the `Import options` dialog window.

You can select default values for `OSC Cat.`, `1-shot` and `+12dB` columns (see [section 2](#2-usual-sample-properties)).
This default values are used when an imported sample does not contain this information in its metadata.

You can also force to use these values for any imported sample by checking the associated check-boxes `Force to reset`.

The `Import options` dialog window also allow to choose with `From #Num` from which number a free sample number will be looked for when importing a sample.

When the `Force mono` checkbox is activated, any imported stereo sample will be automatically converted to mono, using the pan mixing configuration specified by the scroll bar on the right of that checkbox.

##### 1.4.5 Check that your sample library is not exceeding the electribe sampler memory limit.

At the bottom right of the main window, you can see `Total data size : `, the memory used by your samples as well as the memory limit of electribe sampler. If the limit is reached the used memory will turn red in order to warn you.

#### 1.5 Export samples to WAV files

##### 1.5.1 Export all the samples

If you want to export all the samples of the edited sample library file in individual WAV files, use the `Export all as wav` button. You will be asked to select a directory in which all the samples will be extracted.

##### 1.5.2 Export individual samples

If you want to export a specific sample, use the 'export sample' ![export sample icon](images/export.gif?raw=true "export sample") button of the corresponding sample.

##### 1.5.3 Export options

If you click on `Export Options` button, you will open the `Export options` dialog window.

This dialog allows you to choose if you want to include a `smpl` chunk in the WAV file to indicate the `start/stop/loop` points to a DAW (understanding that chunk), for instance.

The dialog also allows to choose if you want to include `cue ` chunks in the WAV file to indicate the slices positions to a DAW (understanding that chunk), for instance.
If `Export slices info in 'cue ' chunk` is checked, a `cue ` chunk will be generated if at least one slice is non empty (has a length greater than zero), and a cue point in that cue chunk will be used for each non empty slice to indicate its start.

#### 1.6 Listen a sample

To listen the WAV content of a specific sample, use the 'play' ![play sample icon](images/play.gif?raw=true "play full WAV content (start/loop/end are ignored)") button of the corresponding sample.

> When you play a sample like this the `start`/`stop`/`loop` points are ignored. The content is played from the start to the end of the WAV data.
> You can stop the playback of the samples by using the 'stop' ![stop-small sample icon](images/stop-small.gif?raw=true "stop playback") button on the top of the 'play' buttons.

> It is possible to listen the sample in a way closer to how it will be rendered by the electribe sampler ([section 3. Advanced sample properties (loop/slices...)](#3-advanced-sample-properties-loopslices)).

#### 1.7 Move a sample

On the left side of the sample list there are 'radio' buttons that allow you to select a specific sample. The selected sample can be moved using the buttons on the left of the radio buttons.

##### 1.7.1 Exchange with another

You can exchange the selected sample with another one, using the 'exchange with another' ![exchange sample icon](images/exchange.gif?raw=true "exchange with another") button.
You will be asked to select the sample with which you want to exchange the selected one.

##### 1.7.2 Swap up/down

You can swap the selected sample up or down. Swapping up (or down) by one position is similar to exchanging the selected sample with the previous (or next one).
It can be achieved by using the 'swap up' ![swap prev icon](images/swap-prev.gif?raw=true "swap up") button (or the 'swap down' ![swap next icon](images/swap-next.gif?raw=true "swap down")).

If you want to swap 10 times the selected sample you can use 'swap up by 10' ![swap prev 10 icon](images/swap-prev-10.gif?raw=true "swap up by 10") button (or the 'swap down by 10' ![swap next 10 icon](images/swap-next-10.gif?raw=true "swap down by 10")).

If you want to swap 100 times the selected sample you can use 'swap up by 100' ![swap prev 100 icon](images/swap-prev-100.gif?raw=true "swap up by 100") button (or the 'swap down by 100' ![swap next 100 icon](images/swap-next-100.gif?raw=true "swap down by 100")).

> If there are less than 10/100 samples before (or after) the selected sample, it will be swapped up to the beginning (or down to the end) of the sample list.

##### 1.7.3 Move up/down to a free sample number

You can move up (or down) a sample to the previous (or next) free sample number using the 'move up to next free' ![prev free icon](images/prev-free.gif?raw=true "move up to next free") button (or the 'move down to next free' ![next free icon](images/next-free.gif?raw=true "move down to next free") button).

> If there is no previous (or next) free sample number, the sample will not be moved

### 2 Usual sample properties

The main window of the editor shows the sample library as a vertical list of samples, and allows to edit or displays, aligned by columns, some properties of the samples.

#### 2.1 Sample number

You can edit the number of a sample in the column `#Num` of the sample list. If you increase (or decrease) a sample number up (or down) to a sample number that is greater (or lower) or equal to the next (or previous) sample number, the next (or previous) sample number will also be increased (or decreased) so that it stays with a sample number greater (or lower) than the edited sample. This is recursively applied to the following (or previous) samples.

> A sample number will not be increased (or decreased) if there is no free sample number after (or before).

#### 2.2 Sample name

You can edit the name of a sample that is in the column `Name` of the sample list. This name will be displayed by the electribe sampler as the OSC Name.

> There is a limited set of characters that are allowed by the electribe sampler. The software may allow characters that will not be properly displayed by the electribe, but it will refuse extended sets of characters that are not understood by the electribe sampler.

#### 2.3 Sample category

You can select the category of a sample that is in the column `Cat.`.

> In order to navigate quickly in your samples with the electribe sample (using `shift` key and `Oscillator` knob), it is recommended to put successively several samples belonging to the same category.

#### 2.4 One-shot sample or looped sample

In the column `1-shot` you can see and specify if your sample is
- one-shot (check box is checked): sample will be played once from start point to end point (even if note is off);
- looped (check box is unchecked): each time end point of the sample is reached playback will continue from loop point (while the note is on).

See [section 3. Advanced sample properties (loop/slices...)](#3-advanced-sample-properties-loopslices) for how to set sample points.

> Note that the electribe sampler requires that if a sample is single shot its loop point must be equal to end point. So if you uncheck the check box of a looped sample, you will loose the loop point position (it cannot be saved/stored in the file).

> From the electribe sampler, to set a sample as looped you need to set the loop point to a different value than the end point. If your sample is set as looped in the editor with a end point equal to the loop point and if you open the edit menu from the electribe sampler, it may become one-shot, unless you modify the value of the loop point to be less than the end point (-1 for instance).

#### 2.5 Play level

In the column `+12dB` you can see and edit the `PLAY LEVEL` of the sample with a check box:
- unchecked means that the sample will be played as `Normal` from the electribe (volume is lower to hide potential acquisition noise);
- checked means that it will be played at +12dB (volume is not reduced).

> The software playback does not take into account this parameter.

#### 2.6 Sample tune

In the column `Tune` you can edit the `SAMPLE TUNE` parameters which allows to tune the playback speed (pitch).

> The software playback does not take into account this parameter.

#### 2.7 Sample frequency (Hz)

The column `Freq (Hz)` shows the sampling frequency of the sample. You can also edit it to tune the playback speed of the sample (pitch).

> The software playback takes into account this parameter.

#### 2.8 Time (in seconds)

The column `Time (s)` displays the length of the sample in seconds.

##### 2.9 Mono/Stereo

In the column `stereo`, a check bock is indicating if your sample is mono or stereo. If the sample is stereo, you can uncheck the box. It will open a dialog window to allow you to tune the stereo (left and right channels) to mono mix settings.

> You cannot revert a conversion from stereo to mono, nor convert a mono sample to a stereo one.

##### 2.10 Sample data size

The column `Data Size` displays the audio data size of the sample in bytes.

#### 3 Advanced sample properties (loop/slices...)

To edit sample `start`, `end` and `loop` points or to edit slice data of a sample, use the 'edit' ![edit sample icon](images/edit.gif?raw=true "edit loop/slices points") button of the corresponding sample.
It opens another window with two different parts. The first part is a visual preview of the wave form of the sample, and can be used to edit points position (see below). The second part is used to display/edit directly the numerical values of the points, and to also edit the steps of the sliced samples.

> The wave form preview can be used to help to adjust a point to a zero crossing for instance. You can zoom in and out if you want to see closer to sample data or farther to see the sample shape.

#### 3.1 Normal sample options

The `Normal sample options` section allows to edit points of a non sliced sample.
The points you can edit are
- `Start`: the point from where the playback will start,
- `End`: the point from where the playback will end,
- `Loop start`: the point where the playback will loop after reaching the end point, if the sample is not used as a single shot sample,
- `Play volume`: the volume level to which the sample will be played by the electribe sampler.

These points can be edited by dragging the highlighted lines appearing in the wave form preview when one of these values is active for keyboard edition.

You can also find a 'play' ![play sample icon](images/play.gif?raw=true) and 'stop' ![stop sample icon](images/stop.gif?raw=true) buttons that can be used for the audio preview of the sample. The playback takes into account the points values.

> The software playback does not takes into account `Play volume` parameter.

> Note that even if the sample is sliced these informations are stored in the sample library and you will be able to use them if you decide to stop to use your sample as sliced.

In the `Normal sample options` section you can also find a 'trim' ![trim icon](images/trim.gif?raw=true) button. When pressing that button, unused sample parts before `Start` point and after `End` point will be deleted.

> Trim is not reversible, be careful (you will need to re-import your original sample to restore deleted sections).

> Trim only takes into account `Start` and `End` points. If your sample is sliced, and you have slices before `Start` or after `End` point, they will be lost.

#### 3.2 Sliced sample options

The `Sliced sample options` area can be used to edit slices' points.
There can be up to 64 slices.
For each slice you can set/tune the start point `First` and the end point `Last`. The two other values are set by the electribe sampler when you create a sliced sample with it, but they don't seems to affect the slice playback if you change them. From the values given by the electribe, `?Attack?` seems to indicate the end of the attach of a slice, and `?Amplitude?` seems to indicate a sound level of the slice.

Like sample normal sample options, you can edit the point of a given slice by dragging the highlighted lines appearing in the wave form preview when one of the values of that given slice is active for keyboard edition.

> Keeping default values for `?Attack?` and `?Amplitude?` seems to be ok. Don't hesitate to post an Issue if you find cases where these values seems to be usefull...

#### 3.3 Sliced sample steps

The bottom part of the window allows to see/edit which one of the slices is selected to be started for each step of the bar. By default they are all set to zero (to mimic the eletribe sampler), which means that if you set your sample as sliced, the slice number 0 will be started at each step.

The first thing to do when you start slicing your sample is to reset all the steps to `Off` value, which means that no slice will be started at that step. For that you can use the `Off them all` button that will reset all the steps at once.

For a sample to be considered by the electribe as sliced, it is needed that:
- the sample is mono,
- the 'number of steps' (to be edited bellow `Steps`) is greater than 0,
- at least one of the step between the first and the 'number of steps' is active (not `Off`).

For each step you can indicate which one of the slices shall be started to be played, by indicating it number instead of `Off`.

> This is not really easy to edit and need some improvements...

#### 3.4 Warning

Remember that the software allow you to edit slice settings of a stereo sample and to store them in the sample library, but the electribe will not used this information, as it is not able to use sliced stereo samples.
> If you want to use the slice of a stereo sample, you will need to convert it to mono.

### 4 Software informations

Using `About` button you will see copyright notice as well as software version and home page address.

### 5 To offer me a beer

If you find the software useful, consider making a donation (any amount will be appreciated).
This can be done by using the 'donate' buttons [![donate € with paypal](images/donate-eur.gif?raw=true)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=L6BSNDEHYQ2HE) or [![donate $ with paypal](images/donate-usd.gif?raw=true)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=PG6YDQS4EZAE2) in the application.

You can also directly click on the above image ;)

