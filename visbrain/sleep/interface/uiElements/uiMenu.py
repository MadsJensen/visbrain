"""Main class for sleep menus managment."""


import numpy as np
import os
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer

from ....io import (dialogSave, dialogLoad, write_fig_hyp, write_csv,
                    write_txt, write_hypno_txt, write_hypno_hyp, read_hypno)

__all__ = ['uiMenu']


class uiMenu(object):
    """Main class for sleep menus managment."""

    def __init__(self):
        """Init."""
        # _____________________________________________________________________
        #                                 SAVE
        # _____________________________________________________________________
        # Hypnogram :
        self.menuSaveHypnogramData.triggered.connect(self.saveHypData)
        self.menuSaveHypnogramFigure.triggered.connect(self.saveHypFig)
        # Stats info table :
        self.menuSaveInfoTable.triggered.connect(self.saveInfoTable)
        # Scoring table :
        self.menuSaveScoringTable.triggered.connect(self.saveScoringTable)
        # Detections :
        self.menuSaveDetectAll.triggered.connect(self.saveAllDetect)
        self.menuSaveDetectSelected.triggered.connect(self.saveSelectDetect)
        # Sleep GUI config :
        self.menuSaveConfig.triggered.connect(self.saveConfig)
        # Screenshot :
        self.menuSaveScreenshotEntire.triggered.connect(self.saveScreenEntire)

        # _____________________________________________________________________
        #                                 LOAD
        # _____________________________________________________________________
        # Load hypnogram :
        self.menuLoadHypno.triggered.connect(self.loadHypno)
        # Sleep GUI config :
        self.menuLoadConfig.triggered.connect(self.loadConfig)
        # Detections :
        self.menuLoadDetectAll.triggered.connect(self.loadDetectAll)
        self.menuLoadDetectSelect.triggered.connect(self.loadDetectSelect)

        # _____________________________________________________________________
        #                                 EXIT
        # _____________________________________________________________________
        self.menuExit.triggered.connect(QtWidgets.qApp.quit)

        # _____________________________________________________________________
        #                              DISPLAY
        # _____________________________________________________________________
        # Quick settings panel :
        self.menuDispSettings.triggered.connect(self._disptog_settings)
        self.q_widget.setVisible(True)
        # Spectrogram :
        self.menuDispSpec.triggered.connect(self._disptog_spec)
        # Hypnogram :
        self.menuDispHypno.triggered.connect(self._disptog_hyp)
        # Time axis :
        self.menuDispTimeax.triggered.connect(self._disptog_timeax)
        # Navigation bar :
        self.menuDispNavbar.triggered.connect(self._disptog_navbar)
        # Time indicators :
        self.menuDispIndic.triggered.connect(self._disptog_indic)
        # Topoplot :
        self.menuDispTopo.triggered.connect(self._disptog_topo)
        # Zoom :
        self.menuDispZoom.triggered.connect(self._disptog_zoom)

        # _____________________________________________________________________
        #                               SETTINGS
        # _____________________________________________________________________
        self.menuSettingCleanHyp.triggered.connect(self.settCleanHyp)

        # _____________________________________________________________________
        #                     SHORTCUTS & DOC
        # _____________________________________________________________________
        self.menuShortcut.triggered.connect(self._fcn_showShortPopup)
        self.menuDocumentation.triggered.connect(self._fcn_openDoc)
        self.menuDownload_pdf_doc.triggered.connect(self._fcn_downloadDoc)

    ###########################################################################
    ###########################################################################
    #                           SAVE
    ###########################################################################
    ###########################################################################

    # ______________________ HYPNOGRAM ______________________
    def saveHypData(self):
        """Save the hypnogram data either in a hyp or txt file."""
        filename = dialogSave(self, 'Save File', 'hypno', "Text file (*.txt);;"
                              "Elan file (*.hyp);;All files (*.*)")
        if filename:
            file, ext = os.path.splitext(filename)

            # Switch between differents types :
            if ext == '.hyp':
                write_hypno_hyp(filename, self._hypno, self._sf, self._sfori,
                                self._N)
            elif ext == '.txt':
                write_hypno_txt(filename, self._hypno, self._sf, self._sfori,
                                self._N, 1)
            else:
                raise ValueError("Not a valid extension")

    def saveHypFig(self):
        """Save a 600 dpi .png figure of the hypnogram."""
        filename = dialogSave(self, 'Save Hypnogram figure', 'hypno',
                              "PNG (*.png);;All files (*.*)")
        if filename:
            write_fig_hyp(filename, self._hypno, self._sf, self._toffset)

    # ______________________ STATS INFO TABLE ______________________
    def saveInfoTable(self):
        """Export stat info."""
        # Get file name :
        path = dialogSave(self, 'Save file', 'statsinfo',
                          "CSV file (*.csv);;Text file (*.txt);;"
                          "All files (*.*)")
        if path:
            file, ext = os.path.splitext(path)
            if ext.find('csv') + 1:
                write_csv(file + '.csv', zip(self._keysInfo, self._valInfo))
            elif ext.find('txt') + 1:
                write_txt(file + '.txt', zip(self._keysInfo, self._valInfo))

    # ______________________ SCORING TABLE ______________________
    def saveScoringTable(self):
        """Export score info."""
        # Read Table
        rowCount = self._scoreTable.rowCount()
        staInd, endInd, stage = [], [], []
        for row in np.arange(rowCount):
            staInd.append(str(self._scoreTable.item(row, 0).text()))
            endInd.append(str(self._scoreTable.item(row, 1).text()))
            stage.append(str(self._scoreTable.item(row, 2).text()))
        # Get file name :
        path = dialogSave(self, 'Save file', 'scoring_info',
                          "CSV file (*.csv);;Text file (*.txt);;"
                          "All files (*.*)")
        if path:
            file, ext = os.path.splitext(path)
            if ext.find('csv') + 1:
                write_csv(file + '.csv', zip(staInd, endInd, stage))
            elif ext.find('txt') + 1:
                write_txt(file + '.txt', zip(staInd, endInd, stage))

    # ______________________ DETECTIONS ______________________
    def _CheckDetectMenu(self):
        """Activate/Deactivate the saving detection menu."""
        self.menuSaveDetections.setEnabled(bool(self._detect))

    def saveAllDetect(self):
        """Export all detections."""
        # Get file name :
        path = dialogSave(self, 'Save all detections', 'detections',
                          "NumPy (*.npy);;All files (*.*)")
        if path:
            file = os.path.splitext(str(path))[0]
            np.save(file + '.npy', self._detect.dict)

    def saveSelectDetect(self):
        """Export selected detection."""
        channel = self._currentLoc[0]
        method = self._currentLoc[1]
        # Read Table
        rowCount = self._DetectLocations.rowCount()
        staInd = [channel, '', 'Time index (s)']
        duration = [method, '', 'Duration (s)']
        stage = ['', '', 'Sleep stage']
        for row in np.arange(rowCount):
            staInd.append(str(self._DetectLocations.item(row, 0).text()))
            duration.append(str(self._DetectLocations.item(row, 1).text()))
            stage.append(str(self._DetectLocations.item(row, 2).text()))
        # Get file name :
        saveas = "locinfo" + '_' + channel + '-' + method
        path = dialogSave(self, 'Save ' + method + ' detection', saveas,
                          "CSV file (*.csv);;Text file (*.txt);;"
                          "All files (*.*)")
        if path:
            file, ext = os.path.splitext(path)
            file += '_' + channel + '-' + method
            if ext.find('csv') + 1:
                write_csv(file + '.csv', zip(staInd, duration, stage))
            elif ext.find('txt') + 1:
                write_txt(file + '.txt', zip(staInd, duration, stage))

    # ______________________ SLEEP GUI CONFIG ______________________
    def saveConfig(self):
        """Save a config file (*.txt) containing several display parameters."""
        import json
        filename = dialogSave(self, 'Save config File', 'config',
                              "Text file (*.txt);;All files (*.*)")
        if filename:
            with open(filename, 'w') as f:
                config = {}
                # Get channels visibility / amplitude :
                viz, amp = [], []
                for i, k in enumerate(self._chanChecks):
                    viz.append(k.isChecked())
                    amp.append(self._ymaxSpin[i].value())
                config['Channel_Names'] = self._channels
                config['Channel_Visible'] = viz
                config['Channel_Amplitude'] = amp
                config['AllAmpMin'] = self._PanAllAmpMin.value()
                config['AllAmpMax'] = self._PanAllAmpMax.value()
                config['SymAmp'] = self._PanAmpSym.isChecked()
                config['AutoAmp'] = self._PanAmpAuto.isChecked()
                # Spectrogram :
                config['Spec_Visible'] = self.menuDispSpec.isChecked()
                config['Spec_Length'] = self._PanSpecNfft.value()
                config['Spec_Overlap'] = self._PanSpecStep.value()
                config['Spec_Cmap'] = self._PanSpecCmap.currentIndex()
                config['Spec_Chan'] = self._PanSpecChan.currentIndex()
                config['Spec_Fstart'] = self._PanSpecFstart.value()
                config['Spec_Fend'] = self._PanSpecFend.value()
                config['Spec_Con'] = self._PanSpecCon.value()
                # Hypnogram/time axis/navigation/topo/indic/zoom :
                config['Hyp_Visible'] = self.menuDispHypno.isChecked()
                config['Time_Visible'] = self.menuDispTimeax.isChecked()
                config['Topo_Visible'] = self.menuDispTopo.isChecked()
                config['Nav_Visible'] = self.menuDispNavbar.isChecked()
                config['Indic_Visible'] = self.menuDispIndic.isChecked()
                config['Zoom_Visible'] = self.menuDispZoom.isChecked()
                # Navigation bar properties :
                config['Slider'] = self._SlVal.value()
                config['Step'] = self._SigSlStep.value()
                config['Window'] = self._SigWin.value()
                config['Goto'] = self._SlGoto.value()
                config['Magnify'] = self._slMagnify.isChecked()
                config['AbsTime'] = self._slAbsTime.isChecked()
                config['Grid'] = self._slGrid.isChecked()
                config['Unit'] = self._slRules.currentIndex()
                json.dump(config, f)

    # ______________________ SCREENSHOT ______________________
    def saveScreenEntire(self):
        """Screenshot using the GUI."""
        # self.setFixedSize(100, 100)
        # Get filename :
        filename = dialogSave(self, 'Screenshot', 'screenshot', "PNG (*.PNG);;"
                              "TIFF (*.tiff);;JPG (*.jpg);;""All files (*.*)")
        # Screnshot function :
        def _takeScreenShot():
            """Take the screenshot."""
            screen = QtWidgets.QApplication.primaryScreen()
            p = screen.grabWindow(0)
            p.save(filename)
        # Take screenshot if filename :
        if filename:
            # Timer (avoid shooting the saving window)
            self.timerScreen = QTimer()
            # self.timerScreen.setInterval(100)
            self.timerScreen.setSingleShot(True)
            self.timerScreen.timeout.connect(_takeScreenShot)
            self.timerScreen.start(500)

    ###########################################################################
    ###########################################################################
    #                                    LOAD
    ###########################################################################
    ###########################################################################

    def loadHypno(self):
        """Load a hypnogram."""
        # Get filename :
        filename = dialogLoad(self, 'Load hypnogram File', 'hypno',
                              "Text file (*.txt);;Elan file (*.hyp);;"
                              "All files (*.*)")
        if filename:
            # Load the hypnogram :
            self._hypno = read_hypno(filename, self._N).astype(np.float32)
            self._hyp.set_data(self._sf, self._hypno, self._time)
            # Update info table :
            self._fcn_infoUpdate()
            # Update scoring table :
            self._fcn_Hypno2Score()
            self._fcn_Score2Hypno()

    def loadConfig(self):
        """Load a config file (*.txt) containing several display parameters."""
        import json
        if self._config_file is not None:
            filename = self._config_file
        else:
            filename = dialogLoad(self, 'Load config File', 'config',
                                  "Text file (*.txt);;All files (*.*)")
        if filename:
            with open(filename) as f:
                # Load the configuration file :
                config = json.load(f)

                def _try(string, self=self, config=config):
                    """Execute the string.

                    This function insure backward compatibility for loading the
                    configuration file.
                    """
                    try:
                        exec(string)
                    except:
                        pass

                # Channels
                for i, k in enumerate(self._chanChecks):
                    self._chanChecks[i].setChecked(config['Channel_Visible'][i])
                    self._ymaxSpin[i].setValue(config['Channel_Amplitude'][i])
                # Amplitudes :
                _try("self._PanAllAmpMin.setValue(config['AllAmpMin'])")
                _try("self._PanAllAmpMax.setValue(config['AllAmpMax'])")
                _try("self._PanAmpSym.setChecked(config['SymAmp'])")
                _try("self._PanAmpAuto.setChecked(config['AutoAmp'])")
                # Spectrogram
                _try("self.menuDispSpec.setChecked(config['Spec_Visible'])")
                _try("self._PanSpecNfft.setValue(config['Spec_Length'])")
                _try("self._PanSpecStep.setValue(config['Spec_Overlap'])")
                _try("self._PanSpecCmap.setCurrentIndex(config['Spec_Cmap'])")
                _try("self._PanSpecChan.setCurrentIndex(config['Spec_Chan'])")
                _try("self._PanSpecFstart.setValue(config['Spec_Fstart'])")
                _try("self._PanSpecFend.setValue(config['Spec_Fend'])")
                _try("self._PanSpecCon.setValue(config['Spec_Con'])")
                # Hypnogram/time axis/navigation/topo/indic/zoom :
                _try("self.menuDispHypno.setChecked(config['Hyp_Visible'])")
                _try("self.menuDispTimeax.setChecked(config['Time_Visible'])")
                _try("self.menuDispTopo.setChecked(config['Topo_Visible'])")
                _try("self.menuDispNavbar.setChecked(config['Nav_Visible'])")
                _try("self.menuDispIndic.setChecked(config['Indic_Visible'])")
                # Navigation bar properties :
                _try("self._SlVal.setValue(config['Slider'])")
                _try("self._SigSlStep.setValue(config['Step'])")
                _try("self._SigWin.setValue(config['Window'])")
                _try("self._SlGoto.setValue(config['Goto'])")
                _try("self._slMagnify.setChecked(config['Magnify'])")
                _try("self._slAbsTime.setChecked(config['AbsTime'])")
                _try("self._slGrid.setChecked(config['Grid'])")
                _try("self._slRules.setCurrentIndex(config['Unit'])")
                # Update display
                self._fcn_chanViz()
                self._fcn_chanAmplitude()
                self._fcn_specSetData()
                self._disptog_spec()
                self._disptog_hyp()
                self._disptog_timeax()
                self._disptog_topo()
                self._disptog_indic()
                self._disptog_zoom()
                self._fcn_gridToggle()
                self._fcn_updateAmpInfo()
                self._fcn_chanAutoAmp()
                self._fcn_chanSymAmp()

    def loadDetectAll(self):
        """Load all detections."""
        # Dialog window for detection file :
        file = dialogLoad(self, "Import detections", '',
                          "NumPy (*.npy);;All files (*.*)")
        self._detect.dict = np.ndarray.tolist(np.load(file))
        # Made canvas visbles :
        for k in self._detect:
            if self._detect[k]['index'].size:
                # Get channel number :
                idx = self._channels.index(k[0])
                self.canvas_setVisible(idx, True)
                self._chan.visible[idx] = True
        # Plot update :
        self._fcn_sliderMove()
        self._locLineReport()
        self._CheckDetectMenu()

    def loadDetectSelect(self):
        """Load a specific detection."""
        # Get file name :
        file = dialogLoad(self, "Import table", '',
                          "CSV file (*.csv);;Text file (*.txt);;"
                          "All files (*.*)")
        # Get channel / method from file name :
        (chan, meth) = file.split('_')[-1].split('.')[0].split('-')
        # Load the file :
        (st, dur) = np.genfromtxt(file, delimiter=',')[3::, 0:2].T
        # Sort by starting index :
        idxsort = np.argsort(st)
        st, dur = st[idxsort], dur[idxsort]
        # Convert into index :
        stInd = np.round(st * self._sf).astype(int)
        durInd = np.round(dur * self._sf / 1000.).astype(int)
        # Build the index array :
        index = np.array([])
        for k, i in zip(stInd, durInd):
            index = np.append(index, np.arange(k, k+i))
        index = index.astype(np.int, copy=False)
        # Set index :
        self._detect[(chan, meth)]['index'] = index
        # Plot update :
        self._fcn_sliderMove()
        self._locLineReport()
        self._CheckDetectMenu()

    ###########################################################################
    ###########################################################################
    #                            DISPLAY
    ###########################################################################
    ###########################################################################

    def _disptog_settings(self):
        """Toggle method for display / hide the settings panel.

        Shortcut : CTRL + D
        """
        self.q_widget.setVisible(not self.q_widget.isVisible())

    def _disptog_spec(self):
        """Toggle method for display / hide the spectrogram.

        Shortcut : S
        """
        viz = self.menuDispSpec.isChecked()
        self._SpecW.setVisible(viz)
        self._specLabel.setVisible(viz)
        self._PanSpecW.setEnabled(viz)

    def _disptog_hyp(self):
        """Toggle method for display / hide the hypnogram.

        Shortcut : H
        """
        viz = self.menuDispHypno.isChecked()
        self._HypW.setVisible(viz)
        self._hypLabel.setVisible(viz)

    def _disptog_navbar(self):
        """Toggle method for display / hide the navigation bar.

        Shortcut : P
        """
        self._slFrame.hide() if self._slFrame.isVisible(
                                                    ) else self._slFrame.show()

    def _disptog_timeax(self):
        """Toggle method for display / hide the time axis.

        Shortcut : X
        """
        viz = self.menuDispTimeax.isChecked()
        self._TimeAxisW.setVisible(viz)
        self._timeLabel.setVisible(viz)

    def _disptog_topo(self):
        """Toggle method for display / hide the topoplot.

        Shortcut : T
        """
        viz = self.menuDispTopo.isChecked()
        self._topoW.setVisible(viz)
        self._PanTopoVizW.setEnabled(viz)
        if viz:
            self._fcn_topoSettings()
            self._fcn_sliderMove()

    def _disptog_indic(self):
        """Toggle method for display / hide the time indicators."""
        self._specInd.mesh.visible = self.menuDispIndic.isChecked()
        self._hypInd.mesh.visible = self.menuDispIndic.isChecked()
        self._TimeAxis.mesh.visible = self.menuDispIndic.isChecked()
        self._fcn_sliderMove()

    def _disptog_zoom(self):
        """Toggle zoom mode."""
        activeIndic = self.menuDispZoom.isChecked()
        if not activeIndic:
            # Spectrogram camera :
            self._speccam.rect = (self._time.min(), self._spec.freq[0],
                                  self._time.max() - self._time.min(),
                                  self._spec.freq[-1] - self._spec.freq[0])
            self._specInd.mesh.visible = self.menuDispIndic.isChecked()
            # Hypnogram camera :
            self._hypcam.rect = (self._time.min(), -5.,
                                 self._time.max() - self._time.min(), 7.)
            # Time camera :
            self._timecam.rect = (self._time.min(), 0.,
                                  self._time.max() - self._time.min(), 1.)

        # Activate / Deactivate indicators :
        self.menuDispIndic.setChecked(not activeIndic)
        self.menuDispIndic.setEnabled(not activeIndic)
        self._hypInd.mesh.visible = not activeIndic
        self._specInd.mesh.visible = not activeIndic
        self._TimeAxis.mesh.visible = not activeIndic

        self._fcn_sliderSettings()

    ###########################################################################
    ###########################################################################
    #                            SETTINGS
    ###########################################################################
    ###########################################################################
    def settCleanHyp(self):
        """Clean the hypnogram."""
        self._hypno = np.zeros((len(self._hyp),), dtype=np.float32)
        self._hyp.clean(self._sf, self._time)
        # Update info table :
        self._fcn_infoUpdate()
        # Update scoring table :
        self._fcn_Hypno2Score()
        self._fcn_Score2Hypno()

    ###########################################################################
    ###########################################################################
    #                            SHORTCUT & DOC
    ###########################################################################
    ###########################################################################

    def _fcn_showShortPopup(self):
        """Open shortcut window."""
        self._shpopup.show()

    def _fcn_openDoc(self):
        """Open documentation."""
        import webbrowser
        webbrowser.open('http://etiennecmb.github.io/visbrain/sleep.html')

    def _fcn_downloadDoc(self):
        """Open documentation."""
        import webbrowser
        webbrowser.open("https://drive.google.com/file/d/"
                        "0B6vtJiCQZUBvNFJMTER3SERGUW8/view?usp=sharing")