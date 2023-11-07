import copy, time, datetime, sys, os, string, shutil, platform

try:
    import pylink  
    from eyetrackingCode import EyeLinkCoreGraphicsPsychoPyAlex #imports from subfolder
except Exception as e:
    print("An exception occurred: {str(e)}")
    print('Could not import EyeLinkCoreGraphicsPsychoPyAlex.py (you need that file to be in the eyetrackingCode subdirectory, which needs an __init__.py file in it too)')


trackEyes = True
if trackEyes:
    eyetracker_dummy_mode = False # Set this variable to True to run eyetracking in "Dummy Mode"
    eyetrackFileGetFromEyelinkMachine = True
    timeAndDateStr = time.strftime("%H:%M on %d %b %Y", time.localtime())
    subject = 'subjectNameUnknownSetLater'
    #edf_fname= 'results' #EyeTrack_'+subject+'_'+timeAndDateStr+'.EDF'  #Too long, on eyetracker PC, filename is limited to 8 chars!!
    edf_fname_short = timeAndDateStr[0:6] #tesschange from timeAndDateStr[0:8] #+ '.EDF' #on eyetracker PC, filename is limited to 8 chars!!
    print('Eyetracking file will be called',edf_fname_short)
    # Step 1: Connect to the EyeLink Host PC
    # The Host IP address, by default, is "100.1.1.1".
    # the "el_tracker" objected created here can be accessed through the Pylink
    # Set the Host PC address to "None" (without quotes) to run the script
    # in "Dummy Mode"
    if eyetracker_dummy_mode:
        el_tracker = pylink.EyeLink(None)
    else:
        try:
            el_tracker = pylink.EyeLink("100.1.1.1")
        except RuntimeError as error:
            print('ERROR:', error)
            core.quit()
            sys.exit()
    
    # Step 2: Open an EDF data file on the EyeLink PC
    try:
        el_tracker.openDataFile(edf_fname_short)
    except RuntimeError as err:
        print('ERROR:', err)
        # close the link if we have one open
        if el_tracker.isConnected():
            el_tracker.close()
        core.quit()
        sys.exit()
        
    # We download EDF data file from the EyeLink Host PC to the local hard
    # drive at the end of each testing session

    # Add a header text to the EDF file to identify the current experiment name
    # This is optional. If your text starts with "RECORDED BY " it will be
    # available in DataViewer's Inspector window by clicking
    # the EDF session node in the top panel and looking for the "Recorded By:"
    # field in the bottom panel of the Inspector.
    preamble_text = 'RECORDED BY %s' % os.path.basename(__file__)
    el_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)
    
    # Step 3: Configure the tracker
    #
    # Put the tracker in offline mode before we change tracking parameters
    el_tracker.setOfflineMode()

    # Get the software version:  1-EyeLink I, 2-EyeLink II, 3/4-EyeLink 1000,
    # 5-EyeLink 1000 Plus, 6-Portable DUO
    eyelink_ver = 0  # set version to 0, in case running in Dummy mode
    if not eyetracker_dummy_mode:
        vstr = el_tracker.getTrackerVersionString()
        eyelink_ver = int(vstr.split()[-1].split('.')[0])
        # print out some version info in the shell
        print('Running experiment on %s, version %d' % (vstr, eyelink_ver))
    
    # File and Link data control
    # what eye events to save in the EDF file, include everything by default
    file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
    # what eye events to make available over the link, include everything by default
    link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
    # what sample data to save in the EDF data file and to make available
    # over the link, include the 'HTARGET' flag to save head target sticker
    # data for supported eye trackers
    if eyelink_ver > 3:
        file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
        link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
    else:
        file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
        link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'
    el_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
    el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
    el_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
    el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)
    
    # Optional tracking parameters
    # Sample rate, 250, 500, 1000, or 2000, check your tracker specification
    # if eyelink_ver > 2:
    #     el_tracker.sendCommand("sample_rate 1000")
    # Choose a calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical),
    el_tracker.sendCommand("calibration_type = HV9")
    # Set a gamepad button to accept calibration/drift check target
    # You need a supported gamepad/button box that is connected to the Host PC
    # But if you don't have a gamepad/button box, it should work by pressing a key on the stimulus PC - at least, it works in picture.py
    el_tracker.sendCommand("button_function 5 'accept_target_fixation'")