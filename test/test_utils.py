"""Test utility functions."""
import numpy as np
from itertools import product
from PyQt5 import QtWidgets, QtCore
import math
import pytest

from visbrain.utils.cameras import FixedCam
from visbrain.utils.color import (color2vb, array2colormap, dynamic_color,
                                  color2faces, type_coloring, mpl_cmap,
                                  color2tuple, mpl_cmap_index, colorclip)
from visbrain.utils.filtering import (filt, morlet, ndmorlet, morlet_power,
                                      welch_power, PrepareData)
from visbrain.utils.gui.popup import (ShortcutPopup, ScreenshotPopup, HelpMenu)
from visbrain.utils.guitools import (slider2opacity, textline2color,
                                     color2json, ndsubplot,
                                     combo, is_color, MouseEventControl,
                                     disconnect_all, extend_combo_list,
                                     get_combo_list_index, safely_set_cbox,
                                     safely_set_spin, safely_set_slider,
                                     toggle_enable_tab, get_screen_size,
                                     set_widget_size)
from visbrain.utils.memory import arrays_share_data, id, code_timer
from visbrain.utils.mesh import (add_brain_template, remove_brain_template,
                                 convert_meshdata, vispy_array, volume_to_mesh,
                                 mesh_edges, smoothing_matrix)
from visbrain.utils.others import (set_log_level, get_dsf, set_if_not_none,
                                   get_data_path)
from visbrain.utils.physio import (find_non_eeg, rereferencing, bipolarization,
                                   commonaverage, tal2mni, mni2tal,
                                   generate_eeg)
from visbrain.utils.picture import (piccrop, picresize)
from visbrain.utils.sigproc import (normalize, derivative, tkeo, zerocrossing,
                                    power_of_ten, averaging, normalization,
                                    smoothing, smooth_3d)
from visbrain.utils.sleep.detection import (kcdetect, spindlesdetect,
                                            remdetect, slowwavedetect,
                                            mtdetect, peakdetect)
from visbrain.utils.sleep.event import (_events_duration, _events_removal,
                                        _events_distance_fill,
                                        _events_mean_freq, _events_amplitude,
                                        _events_to_index, _index_to_events)
from visbrain.utils.sleep.hypnoprocessing import (transient, sleepstats)
from visbrain.utils.transform import (vprescale, vprecenter, vpnormalize,
                                      array_to_stt)

###############################################################################
###############################################################################
#                                cameras.py
###############################################################################
###############################################################################


class TestCamera(object):
    """Test functions in camera.py."""

    def test_fixed_camera(self):
        """Test fixed_camera function."""
        FixedCam()

###############################################################################
###############################################################################
#                                color.py
###############################################################################
###############################################################################


class TestColor(object):
    """Test functions in color.py."""

    def test_color2vb(self):
        """Test color2vb function."""
        assert np.array_equal(color2vb(), np.array([[1., 1., 1., 1.]]))
        color2vb('green')
        color2vb('#ab4642')
        color2vb([0.5789, 1., 0.4235], alpha=.4)
        color2vb((0.5789, 1., 0.4235, .3), alpha=.4)
        assert color2vb((0., 1., 0.), length=10).shape == (10, 4)
        assert color2vb(np.array([0., 1., 0., .5])).ravel()[-1] == .5

    def test_color2tuple(self):
        """Test color2tuple function."""
        g1 = np.array([[0., 1., 0., 1.]])
        g2 = np.array([[0.5789, 1., 0.4235, .4]])
        assert len(color2tuple(g1)) == 3
        assert len(color2tuple(g2, rmalpha=False)) == 4
        assert np.asarray(color2tuple(g1,
                                      astype=np.float64)).dtype == 'float64'
        assert len(str(color2tuple(g2, astype=float, roundto=4)[0])) == 6

    def test_array2colormap(self):
        """Test array2colormap function."""
        vec = np.random.randn(10)
        mat = np.random.randn(10, 30)
        array2colormap(vec, cmap='Reds')
        array2colormap(mat, clim=(-1., 1.), cmap='viridis')
        array2colormap(mat, clim=(-1., 1.), vmin=.1, under='gray', vmax=.7,
                       over='red', cmap='Spectral_r')
        array2colormap(vec, faces_render=True)

    def test_dynamic_color(self):
        """Test dynamic_color function."""
        color = np.array([[1., 0., 0., 1.],
                         [1., 0., 0., 1.],
                         [1., 0., 0., 1.],
                         [1., 0., 0., 1.],
                         [1., 0., 0., 1.]])
        x = np.random.rand(color.shape[0])
        dynamic_color(color, x, dynamic=(0., 1.))
        dynamic_color(color, x, dynamic=(1., 0.))

    def test_color2faces(self):
        """Test color2faces function."""
        color = (1., 0., 0., 1.)
        assert color2faces(color, 10).shape == (10, 3, 4)

    def test_colorclip(self):
        """Test colorclip function."""
        x = np.arange(0, 10, 1.).reshape(5, 2)
        assert colorclip(x, 2, 'under').min() == 2
        assert colorclip(x, 5, 'over').max() == 5

    def test_type_coloring(self):
        """Test type_coloring function."""
        reps = 20
        assert type_coloring(color='rnd', n=reps).shape == (reps, 3)
        assert type_coloring(color='dynamic', n=reps, cmap='Spectral_r',
                             vmin=1., under='gray', vmax=8.,
                             over='#ab4642').shape == (reps, 3)
        uni = type_coloring(color='uniform', unicolor='red', n=reps)
        assert np.array_equal(uni, np.tile((1., 0., 0.), (reps, 1)))

    def test_mpl_cmap(self):
        """Test mpl_cmap function."""
        mpl_cmap(False)
        mpl_cmap(True)

    def test_mpl_cmap_index(self):
        """Test mpl_cmap_index function."""
        mpl = mpl_cmap()
        r = mpl_cmap_index('viridis')
        r2 = mpl_cmap_index('viridis_r')
        r3 = mpl_cmap_index('viridis', mpl)
        assert isinstance(r[0], np.int64) and not r[1]
        assert isinstance(r2[0], np.int64) and r2[1]
        assert r == r3

###############################################################################
###############################################################################
#                                detection.py
###############################################################################
###############################################################################


class TestDetections(object):
    """Test functions in detection.py."""

    @staticmethod
    def _get_eeg_dataset(n=10014, sf=100., sine=False, f=4., amp=1.,
                         offset=0.):
        """Generate a random eeg dataset."""
        if sine:
            time = np.arange(n) / sf
            data = np.sin(3 * np.pi * f * time)
            # data += .05 * np.random.rand(*data.shape)
        else:
            data = np.random.randn(n)
        data *= amp
        data += offset
        return data, sf

    @staticmethod
    def _get_eeg_hypno(n=10014):
        """Generate a random hypnogram."""
        if n % 6:
            n_per_seg = n / 6
            wake = np.zeros((n_per_seg,))
            n1 = np.ones((n_per_seg,))
            n2 = np.full((n_per_seg,), 2)
            n3 = np.full((n_per_seg,), 3)
            rem = np.full((n_per_seg,), 4)
            art = np.full((n_per_seg,), -1)
            return np.hstack((wake, n1, n2, n3, rem, art))
        else:
            return np.random.randint(-1, 4, n)

    def test_kcdetect(self):
        """Test function kcdetect."""
        # Get a dataset example :
        data, sf = self._get_eeg_dataset()
        hypno = self._get_eeg_hypno()
        kcdetect(data, sf, .8, 1., hypno, True, 100, 200, .2, .6)

    def test_spindlesdetect(self):
        """Test function spindlesdetect."""
        # Get a dataset example :
        data, sf = self._get_eeg_dataset()
        hypno = self._get_eeg_hypno()
        spindlesdetect(data, sf, .1, hypno, True)

    def test_remdetect(self):
        """Test function remdetect."""
        # Get a dataset example :
        data, sf = self._get_eeg_dataset()
        hypno = self._get_eeg_hypno()
        remdetect(data, sf, hypno, True, .1)

    def test_slowwavedetect(self):
        """Test function slowwavedetect."""
        # Get a dataset example :
        data, sf = self._get_eeg_dataset(n=10000, sine=True, offset=300., f=.7)
        slowwavedetect(data, sf, .8, min_duration_ms=5.)

    def test_mtdetect(self):
        """Test function mtdetect."""
        # Get a dataset example :
        data, sf = self._get_eeg_dataset()
        hypno = self._get_eeg_hypno()
        mtdetect(data, sf, .1, hypno, True)

    def test_peakdetect(self):
        """Test function peakdetect."""
        # Get a dataset example :
        data, sf = self._get_eeg_dataset(n=1000, sine=True, f=4., sf=128.)
        peakdetect(sf, data, get='min')
        peakdetect(sf, data, get='max')
        peakdetect(sf, data, get='minmax', threshold=.6)

###############################################################################
###############################################################################
#                                event.py
###############################################################################
###############################################################################


class TestEvent(object):
    """Test functions in event.py."""

    @staticmethod
    def _get_index():
        return np.array([0, 1, 2, 3, 4, 7, 8, 9, 10, 14, 15, 16, 17, 18, 19])

    @staticmethod
    def _get_data():
        data = np.random.rand(1000)
        idx_sup_thr = np.arange(1000)
        idx_start = np.array([10, 40, 100])
        idx_stop = np.array([50, 75, 200])
        return data, idx_sup_thr, idx_start, idx_stop

    def test_events_duration(self):
        """Test function events_duration."""
        _events_duration(self._get_index(), 100.)

    def test_events_removal(self):
        """Test function events_removal."""
        idx_start = np.array([100, 1200, 1300])
        idx_stop = np.array([110, 2200, 1800])
        _events_removal(idx_start, idx_stop, [0, 1])

    def test_events_distance_fill(self):
        """Test function events_distance_fill."""
        _events_distance_fill(self._get_index(), 200., 100.)

    def test_events_mean_freq(self):
        """Test function events_mean_freq."""
        data, idx_sup_thr, idx_start, idx_stop = self._get_data()
        _events_mean_freq(data, idx_sup_thr, idx_start, idx_stop, 100.)

    def test_event_amplitude(self):
        """Test function event_amplitude."""
        data, idx_sup_thr, idx_start, idx_stop = self._get_data()
        _events_amplitude(data, idx_sup_thr, idx_start, idx_stop, 100.)

    def test_event_to_index(self):
        """Test function event_to_index."""
        _events_to_index(self._get_index())

    def test_index_to_event(self):
        """Test function index_to_event."""
        idx = _events_to_index(self._get_index())
        _index_to_events(idx)

###############################################################################
###############################################################################
#                                filtering.py
###############################################################################
###############################################################################


class TestFiltering(object):
    """Test functions in filtering.py."""

    @staticmethod
    def _get_data(mean=False):
        if mean:
            return np.random.rand(2000), 3., 512.
        else:
            return np.random.rand(2000), [2., 4.], 512.

    def __iter__(self):
        """Iterate over filtering options."""
        btype = ['bandpass', 'bandstop', 'highpass', 'lowpass']
        order = [2, 3, 5]
        method = ['butterworth', 'bessel']
        way = ['filtfilt', 'lfilter']
        for k in product(btype, order, method, way):
            yield k

    def test_filt(self):
        """Test filt function."""
        x, f, sf = self._get_data()
        for k in self:
            filt(sf, f, x, *k)

    def test_morlet(self):
        """Test morlet function."""
        x, f, sf = self._get_data(True)
        morlet(x, sf, f)

    def test_ndmorlet(self):
        """Test ndmorlet function."""
        x, f, sf = self._get_data(True)
        for k in [None, 'amplitude', 'phase', 'power']:
            ndmorlet(x, sf, f, get=k)

    def test_morlet_power(self):
        """Test morlet_power function."""
        x, _, sf = self._get_data(True)
        f = [1., 2., 3., 4.]
        assert morlet_power(x, f, sf, norm=False).sum(0).max() > 1.
        assert math.isclose(morlet_power(x, f, sf, norm=True).sum(0).max(), 1.)

    def test_welch_power(self):
        """Test welch_power function."""
        x, _, sf = self._get_data(True)
        f = [5, 10., 15]
        assert math.isclose(welch_power(x, f, sf, norm=True).sum(0).max(), 1.)

    def test_prepare_data(self):
        """Test class PrepareData."""
        p = PrepareData(demean=True, detrend=True)
        x, f, sf = self._get_data()
        time = np.arange(len(x)) / sf
        for k in self:
            for i in ['filter', None, 'amplitude', 'phase', 'power']:
                p.btype = k[0]
                p.forder = k[1]
                p.filt_meth = k[2]
                p.way = k[3]
                p.dispas = i
                p._prepare_data(sf, x, time)


###############################################################################
###############################################################################
#                                popup.py
###############################################################################
###############################################################################


class TestPopup(object):
    """Test functions in popup.py."""

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_shortcut_popup(self):
        """Test function ShortcutPopup."""
        sh = [('key1', 'Action1'), ('key2', 'Action2')]
        app = QtWidgets.QApplication([])
        pop = ShortcutPopup()
        pop.set_shortcuts(sh)
        # app.quit()

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_screenshot_popup(self):
        """Test function ScreenshotPopup."""
        def fcn():
            pass
        app = QtWidgets.QApplication([])
        sc = ScreenshotPopup(fcn)
        sc._fcn_select_render()
        sc._fcn_resolution()
        sc.to_kwargs()
        sc._fcn_enable_bgcolor()
        # app.quit()

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_help_menu(self):
        """Test function HelpMenu."""
        pass


###############################################################################
###############################################################################
#                                guitools.py
###############################################################################
###############################################################################

class TestGuitools(object):
    """Test functions in guitools.py."""

    @staticmethod
    def _get_connect_function():
        def f1():
            pass
        return f1

    def test_slider2opacity(self):
        """Test function slider2opacity."""
        slider2opacity(-20.)
        slider2opacity(200.)
        slider2opacity(20.)

    def test_textline2color(self):
        """Test function textline2color."""
        textline2color("'green'")
        textline2color('green')
        textline2color('(.1, .1, .1)')
        textline2color('#ab4642')
        textline2color(None)

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_color2json(self):
        """Test function color2json."""
        app = QtWidgets.QApplication([])
        line = QtWidgets.QLineEdit()
        line.setText('green')
        color2json(line)

    def test_ndsubplot(self):
        """Test function ndsubplot."""
        ndsubplot(10, line=30)
        ndsubplot(10, force_col=5)
        ndsubplot(50)

    def test_combo(self):
        """Test function combo."""
        combo(['oki', 1, 2, 1, 'ok', 'oki'], [0, 1, 2, 3, 4, 5])

    def test_is_color(self):
        """Test function is_color."""
        is_color('green')
        is_color('bad_color')
        is_color("'green'", comefrom='textline')
        is_color('(.1, .1, .1)', comefrom='textline')

    def test_mouse_event_control(self):
        """Test class MouseEventControl."""
        class Modifier(object):
            def __init__(self):
                self.name = 'ctrl'

        class MouseEvent(object):
            def __init__(self):
                self.button = 1
                self.modifiers = [Modifier()]

        mec = MouseEventControl()
        me = MouseEvent()
        assert mec._is_left_click(me)
        assert mec._is_modifier(me, 'ctrl')
        assert not mec._is_modifier(me, 'alt')

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_disconnect_all(self):
        """Test function disconnect_all."""
        app = QtWidgets.QApplication([])
        f1 = self._get_connect_function()
        spin = QtWidgets.QDoubleSpinBox()
        spin.valueChanged.connect(f1)
        disconnect_all(spin)

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_extend_combo_list(self):
        """Test function extend_combo_list."""
        app = QtWidgets.QApplication([])
        f1 = self._get_connect_function()
        cbox = QtWidgets.QComboBox()
        cbox.currentIndexChanged.connect(f1)
        extend_combo_list(cbox, 'NewItem', f1)
        assert cbox.itemText(0) == 'NewItem'

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_get_combo_list_index(self):
        """Test function get_combo_list_index."""
        app = QtWidgets.QApplication([])
        cbox = QtWidgets.QComboBox()
        extend_combo_list(cbox, 'NewItem1')
        extend_combo_list(cbox, 'NewItem2')
        assert get_combo_list_index(cbox, 'NewItem2') == 1

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_safely_set_cbox(self):
        """Test function safely_set_cbox."""
        app = QtWidgets.QApplication([])
        f1 = self._get_connect_function()
        cbox = QtWidgets.QComboBox()
        cbox.currentIndexChanged.connect(f1)
        extend_combo_list(cbox, 'NewItem1', f1)
        extend_combo_list(cbox, 'NewItem2', f1)
        safely_set_cbox(cbox, 1, f1)
        assert int(cbox.currentIndex()) == 1

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_safely_set_spin(self):
        """Test function safely_set_spin."""
        app = QtWidgets.QApplication([])
        f1 = self._get_connect_function()
        spin = QtWidgets.QDoubleSpinBox()
        spin.valueChanged.connect(f1)
        safely_set_spin(spin, 2., [f1])
        assert float(spin.value()) == 2.

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_safely_set_slider(self):
        """Test function safely_set_slider."""
        app = QtWidgets.QApplication([])
        f1 = self._get_connect_function()
        slider = QtWidgets.QSlider()
        slider.valueChanged.connect(f1)
        safely_set_slider(slider, 2., [f1])
        assert float(slider.value()) == 2.

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_toggle_enable_tab(self):
        """Test function toggle_enable_tab."""
        app = QtWidgets.QApplication([])
        _translate = QtCore.QCoreApplication.translate
        tab = QtWidgets.QTabWidget()
        tab_2 = QtWidgets.QWidget()
        tab.addTab(tab_2, "")
        tab.setTabText(tab.indexOf(tab_2), _translate("MainWindow", "TabName"))
        toggle_enable_tab(tab, 'TabName', False)
        assert not tab.isTabEnabled(0)

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_get_screen_size(self):
        """Test function get_screen_size."""
        app = QtWidgets.QApplication([])
        get_screen_size(app)

    @pytest.mark.skip('Too much app creation => segmentation fault')
    def test_set_widget_size(self):
        """Test function set_widget_size."""
        app = QtWidgets.QApplication([])
        w = QtWidgets.QWidget()
        set_widget_size(app, w)


###############################################################################
###############################################################################
#                                memory.py
###############################################################################
###############################################################################


class TestMemory(object):
    """Test functions in memory.py."""

    def test_id(self):
        """Test function id."""
        a = b = np.arange(10)
        assert id(b) == id(a)

    def test_arrays_share_data(self):
        """Test function arrays_share_data."""
        a = b = np.arange(10)
        assert arrays_share_data(a, b)

    def test_code_timer(self):
        """Test function code_timer."""
        start = code_timer(verbose=False)
        code_timer(start, unit='ms')
        code_timer(start, unit='us')


###############################################################################
###############################################################################
#                                mesh.py
###############################################################################
###############################################################################


class TestMesh(object):
    """Test functions in mesh.py."""

    def _creation(self):
        """Create vertices, faces and normals."""
        # Define random
        self.vertices = np.array([[0., 1., 0.],
                                  [0., 2., 0.],
                                  [0., 3., 1.],
                                  [1., 4., 0.]])
        self.normals = np.array([[-1., 1., 2.],
                                 [-1., 1., 2.],
                                 [-2., -3., -1.],
                                 [-4., -5., -4.]])
        self.faces = np.array([[0, 1, 2], [0, 1, 3], [1, 2, 3]])
        self.template = 'TestTemplate.npz'

    def test_vispy_array(self):
        """Test vispy_array function."""
        mat = np.random.randint(0, 10, (10, 30))
        mat_convert = vispy_array(mat, np.float64)
        assert mat_convert.flags['C_CONTIGUOUS']
        assert mat_convert.dtype == np.float64

    def test_convert_meshdata(self):
        """Test convert_meshdata function."""
        from vispy.geometry import MeshData
        import vispy.visuals.transforms as vist
        # Force creation of vertices, faces and normals :
        self._creation()
        tup = (self.vertices, self.faces)
        # Compare (vertices + faces) Vs. MeshData :
        mesh1 = convert_meshdata(*tup)
        mesh2 = convert_meshdata(meshdata=MeshData(*tup))
        assert np.array_equal(mesh1[0], mesh2[0])
        assert np.array_equal(mesh1[1], mesh2[1])
        assert np.array_equal(mesh1[2], mesh2[2])
        # Invert normals :
        inv1 = convert_meshdata(*tup, invert_normals=True)[-1]
        assert np.array_equal(inv1, -mesh1[-1])
        # Create transformation :
        tr = vist.MatrixTransform()
        tr.rotate(90, (0, 0, 1))
        convert_meshdata(*tup, transform=tr)[-1]

    def test_volume_to_mesh(self):
        """Test function volume_to_mesh."""
        x = np.random.rand(10, 20, 30)
        volume_to_mesh(x)

    def test_add_brain_template(self):
        """Test add_brain_template function."""
        # Force creation of vertices, faces and normals :
        self._creation()
        tup = (self.vertices, self.faces, self.normals)
        # Get converted vertices, faces and normals :
        mesh1 = convert_meshdata(*tup)
        add_brain_template(self.template, *mesh1)

    def test_remove_brain_template(self):
        """Test remove_brain_template function."""
        # Force creation of vertices, faces and normals :
        self._creation()
        remove_brain_template(self.template)

    def test_mesh_edges(self):
        """Test function mesh_edges."""
        self._creation()
        mesh_edges(self.faces)

    def test_smoothing_matrix(self):
        """Test function smoothing_matrix."""
        self._creation()
        vertices = np.array([1, 3])
        smoothing_matrix(vertices, mesh_edges(self.faces))

###############################################################################
###############################################################################
#                                others.py
###############################################################################
###############################################################################


class TestOthers(object):
    """Test functions in others.py."""

    def test_get_dsf(self):
        """Test function get_dsf."""
        assert get_dsf(100, 1000.) == (10, 100.)
        assert get_dsf(100, None) == (1, 100.)

    def test_set_if_not_none(self):
        """Test function set_if_not_none."""
        a = 5.
        assert set_if_not_none(a, None) == 5.
        assert set_if_not_none(a, 10., False) == 5.
        assert set_if_not_none(a, 10.) == 10.

    def test_set_log_level(self):
        """Test function set_log_level."""
        levels = [True, False, 'warning', 'error', 'critical', 'debug', 'info',
                  None]
        for k in levels:
            set_log_level(k)

    def test_get_data_path(self):
        """Test function get_data_path."""
        assert isinstance(get_data_path(), str)

###############################################################################
###############################################################################
#                                physio.py
###############################################################################
###############################################################################


class TestPhysio(object):
    """Test functions in physio.py."""

    @staticmethod
    def _generate_eeg_dataset(data_type='eeg'):
        """Generate an EEG dataset to test re-referencing functions."""
        data = np.random.rand(4, 100)
        if data_type == 'eeg':
            data = np.random.rand(4, 100)
            channels = ['Cz', 'Pz', 'Fz', 'EOG']
        elif data_type == 'intra':
            channels = ['m1.132', 'm2.134', 'm3.45', 'i1.32']
        return data, channels, [False, False, False, True]

    @staticmethod
    def _generate_coordinates():
        """Generate random xyz coordinates."""
        return np.random.rand(50, 3)

    def test_find_non_eeg(self):
        """Test function find_non_eeg."""
        bool_vec = find_non_eeg(['cz', 'eog', 'emg'])
        assert np.array_equal(bool_vec, (False, True, True))

    def test_rereferencing(self):
        """Test function rereferencing."""
        data, channels, ignore = self._generate_eeg_dataset('eeg')
        data_r, chan_r, consider = rereferencing(data, channels, 1, ignore)
        assert chan_r == ['Cz-Pz', 'Pz', 'Fz-Pz', 'EOG']

    def test_bipolarization(self):
        """Test function bipolarization."""
        data, channels, ignore = self._generate_eeg_dataset('intra')
        data_r, chan_r, consider = bipolarization(data, channels, ignore)
        assert chan_r == ['m1', 'm2-m1', 'm3-m2', 'i1']

    def test_commonaverage(self):
        """Test function commonaverage."""
        data, channels, ignore = self._generate_eeg_dataset('eeg')
        data_r, chan_r, consider = commonaverage(data, channels, ignore)
        assert chan_r == ['Cz-m', 'Pz-m', 'Fz-m', 'EOG']

    def test_tal2mni(self):
        """Test function tal2mni."""
        xyz = self._generate_coordinates()
        tal2mni(xyz)

    def test_mni2tal(self):
        """Test function mni2tal."""
        xyz = self._generate_coordinates()
        mni2tal(xyz)

    def test_generate_eeg(self):
        """Test function generate_eeg."""
        generate_eeg(n_pts=1000)

###############################################################################
###############################################################################
#                                picture.py
###############################################################################
###############################################################################


class TestPicture(object):
    """Test functions in picture.py."""

    def _compare_shapes(self, im, shapes):
        im_shapes = [k.shape for k in im]
        assert np.array_equal(im_shapes, shapes)

    def test_piccrop(self):
        """Test function piccrop."""
        pic = np.array([[0., 0., 0., 0., 0.],
                        [0., 0., 1., 0., 0.],
                        [0., 1., 1., 1., 0.],
                        [0., 0., 1., 0., 0.],
                        [0., 0., 0., 0., 0.]])
        destination = np.array([[0., 1., 0.],
                                [1., 1., 1.],
                                [0., 1., 0.]])
        assert np.array_equal(piccrop(pic, margin=0), destination)

    def test_picresize(self):
        """Test function picresize."""
        shapes = [(10, 20), (30, 40), (50, 60)]
        im = [np.random.rand(*k) for k in shapes]
        s_0 = picresize(im)
        s_0_ex = picresize(im, extend=True)
        s_1 = picresize(im, axis=1)
        s_1_ex = picresize(im, axis=1, extend=True)
        self._compare_shapes(s_0, [(10, 20), (10, 13), (10, 12)])
        self._compare_shapes(s_1, [(10, 20), (15, 20), (16, 20)])
        self._compare_shapes(s_0_ex, [(50, 100), (50, 66), (50, 60)])
        self._compare_shapes(s_1_ex, [(30, 60), (45, 60), (50, 60)])


###############################################################################
###############################################################################
#                                sigproc.py
###############################################################################
###############################################################################


class TestSigproc(object):
    """Test functions in sigproc.py."""

    def test_normalize(self):
        """Test normalize function."""
        mat = np.random.rand(10, 20)
        mat_n = normalize(mat, -10., 14.)
        assert (mat_n.min() == -10.) and (mat_n.max() == 14.)

    def test_derivative(self):
        """Test function derivative."""
        x, window, sf = np.random.rand(2000), 10., 512.
        derivative(x, window, sf)

    def test_tkeo(self):
        """Test function tkeo."""
        x = np.random.rand(2000)
        tkeo(x)

    def test_zerocrossing(self):
        """Test function zerocrossing."""
        x = np.array([1., -10, -4, 2., 4., -7., -1., 5.])
        assert np.array_equal(zerocrossing(x), [1, 3, 5, 7])

    def test_power_of_ten(self):
        """Test function power_of_ten."""
        assert np.allclose(power_of_ten(-57.), (-57., 0))
        assert np.allclose(power_of_ten(1024.), (1.024, 3))
        assert np.allclose(power_of_ten(-14517.2), (-1.45172, 4))

    def test_averaging(self):
        """Test function averaging."""
        data = np.random.rand(57, 103, 154)
        # Test axis
        for x in [0, 1, 2, -1]:
            ts_out = averaging(data, 5, axis=x, overlap=.5)
            assert ts_out.shape[x] < data.shape[x]
        # Test window :
        window = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
        for w in window:
            averaging(data, 5, axis=-1, overlap=.5, window=w)

    def test_normalization(self):
        """Test function normalization."""
        data = np.random.rand(10, 20)
        # Test the different normalizations using a baseline or not :
        for norm, base in product(range(5), [None, (2, 7)]):
            normalization(data, -1, norm, base)

    def test_smoothing(self):
        """Test function smoothing."""
        # Test small vector :
        x_3 = np.array([0, 1, 2])
        assert np.array_equal(smoothing(x_3, n_window=1), x_3)
        # Test windows :
        x_n = np.arange(127)
        window = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
        for w in window:
            x_ns = smoothing(x_n, window=w)
            assert len(x_ns) == len(x_n)

    def test_smooth_3d(self):
        """Test function smooth_3d."""
        x = np.random.rand(10, 20, 30)
        smooth_3d(x)


###############################################################################
###############################################################################
#                                hypnoprocessing.py
###############################################################################
###############################################################################


class TestHypnoprocessing(object):
    """Test functions in hypnoprocessing.py."""

    def test_transient(self):
        """Test function transient."""
        data = np.array([0, 0, 0, 1, 1, 2, 2, 2, 3, 4, 4, 5])
        time = np.arange(len(data)) / 2.
        index = np.array([[0, 2], [3, 4], [5, 7], [8, 8], [9, 10], [11, 11]])
        tr, idx, stages = transient(data)
        assert np.array_equal(tr, [2, 4, 7, 8, 10])
        assert np.array_equal(index, idx)
        assert np.array_equal(stages, [0, 1, 2, 3, 4, 5])
        _, idx_time, _ = transient(data, time)
        assert np.array_equal(index / 2., idx_time)

    def test_sleepstats(self):
        """Test function sleepstats."""
        hypno = np.random.randint(-1, 3, (2000,))
        sleepstats(hypno, 100.)

###############################################################################
###############################################################################
#                                transform.py
###############################################################################
###############################################################################


class TestTransform(object):
    """Test functions in transform.py."""

    @staticmethod
    def _test_vpmean(mat, tr):
        """Test if the center of (x, y, z) is [0., 0., 0.]."""
        assert np.array_equal(tr.map(mat).mean(0), [0., 0., 0., 1.])

    @staticmethod
    def _test_vpdist(mat, tr, dist):
        """Test if Peak to Peak along (x, y, z) is equal to dist."""
        mat_ptp = np.round(np.ptp(tr.map(mat), axis=0))
        assert np.array_equal(mat_ptp, [float(dist)] * 3 + [0.])

    def test_vprescale(self):
        """Test function vprescale."""
        mat = np.arange(30).reshape(10, 3)
        dist = 100.
        self._test_vpdist(mat, vprescale(mat, dist=dist), dist)

    def test_vprecenter(self):
        """Test function vprecenter."""
        mat = np.arange(30).reshape(10, 3)
        self._test_vpmean(mat, vprecenter(mat))

    def test_vpnormalize(self):
        """Test function vpnormalize."""
        mat = np.arange(30).reshape(10, 3)
        dist = 5.
        tr = vpnormalize(mat, dist=dist)
        self._test_vpmean(mat, tr)
        self._test_vpdist(mat, tr, dist)

    def test_array_to_stt(self):
        """Test function array_to_stt."""
        scale = (4., 5., 3.)
        translate = (10., 25., 7.)
        mat = np.array([[scale[0], 0., 0., translate[0]],
                        [0., scale[1], 0., translate[1]],
                        [0., 0., scale[2], translate[2]],
                        [0., 0., 0., 1.]
                        ])
        assert np.array_equal(array_to_stt(mat).matrix, mat)
