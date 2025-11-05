import numpy as np
from pathlib import Path
import pytest
import tempfile
import time
from unittest.mock import MagicMock, call

from cmt_vna.vna import IP, PORT, DEFAULT_FLAG_THRESHOLDS, lin2dB, mlin
from cmt_vna.testing import DummyVNA


class TestDummyVNA:
    """Test suite for DummyVNA class to ensure it works as expected."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.switch_fn = MagicMock(return_value=True)
        self.vna = DummyVNA(switch_fn=self.switch_fn)

    def test_initialization(self):
        """Test DummyVNA initialization."""
        assert self.vna.vna_ip == IP
        assert self.vna.vna_port == PORT
        assert self.vna.save_dir == Path(".")
        assert self.vna.switch_fn is self.switch_fn
        assert self.vna.data == {}
        assert self.vna.stds_meta == {}

    def test_initialization_with_params(self):
        """Test DummyVNA initialization with custom parameters."""
        save_dir = Path("/tmp")
        vna = DummyVNA(
            ip="192.168.1.1", port=1234, timeout=5000, save_dir=save_dir
        )
        assert vna.vna_ip == "192.168.1.1"
        assert vna.vna_port == 1234
        assert vna.vna_timeout == 5000000  # converted to milliseconds
        assert vna.save_dir == save_dir
        assert vna.switch_fn is None  # No switch_fn by default

    def test_id_property(self):
        """Test the id property returns expected value."""
        assert self.vna.id == "DummyVNA"

    def test_frequency_properties(self):
        """Test frequency start/stop properties."""
        # Test initial state
        assert self.vna.fstart is None
        assert self.vna.fstop is None

        # Test setting values
        self.vna.fstart = 1e6
        assert self.vna.fstart == 1e6

        self.vna.fstop = 250e6
        assert self.vna.fstop == 250e6

        # Test setting same value doesn't change anything
        self.vna.fstart = 1e6  # Should not cause issues
        assert self.vna.fstart == 1e6

    def test_npoints_property(self):
        """Test npoints property."""
        assert self.vna.npoints is None

        self.vna.npoints = 1000
        assert self.vna.npoints == 1000

        # Test setting same value
        self.vna.npoints = 1000
        assert self.vna.npoints == 1000

    def test_ifbw_property(self):
        """Test ifbw property."""
        assert self.vna.ifbw is None

        self.vna.ifbw = 100
        assert self.vna.ifbw == 100

    def test_power_property(self):
        """Test power_dBm property."""
        assert self.vna.power_dBm is None

        self.vna.power_dBm = -10
        assert self.vna.power_dBm == -10

    def test_freqs_property(self):
        """Test freqs property calculation."""
        # Should return None when not properly configured
        assert self.vna.freqs is None

        # Configure frequency range
        self.vna.fstart = 1e6
        self.vna.fstop = 250e6
        self.vna.npoints = 1000

        freqs = self.vna.freqs
        assert isinstance(freqs, np.ndarray)
        assert len(freqs) == 1000
        assert freqs[0] == 1e6
        assert freqs[-1] == 250e6
        np.testing.assert_allclose(freqs, np.linspace(1e6, 250e6, 1000))

    def test_setup(self):
        """Test setup method."""
        freqs = self.vna.setup(
            fstart=1e6, fstop=250e6, npoints=1000, ifbw=100, power_dBm=-5
        )

        assert self.vna.fstart == 1e6
        assert self.vna.fstop == 250e6
        assert self.vna.npoints == 1000
        assert self.vna.ifbw == 100
        assert self.vna.power_dBm == -5
        assert isinstance(freqs, np.ndarray)
        assert len(freqs) == 1000

    def test_header_property(self):
        """Test header property returns correct metadata."""
        self.vna.setup(1e6, 250e6, 1000, 100, -5)

        header = self.vna.header
        assert header["fstart"] == 1e6
        assert header["fstop"] == 250e6
        assert header["npoints"] == 1000
        assert header["ifbw"] == 100
        assert header["power_dBm"] == -5
        assert isinstance(header["freqs"], np.ndarray)

    def test_wait_for_opc(self):
        """Test wait_for_opc method."""
        # Should complete immediately with no error
        self.vna.wait_for_opc()

        # Test with wait time
        start_time = time.time()
        self.vna.wait_for_opc(wait=0.1)
        elapsed = time.time() - start_time
        assert elapsed >= 0.1

        # Test with error
        with pytest.raises(TimeoutError):
            self.vna.wait_for_opc(err=True)

    def test_measure_s11(self):
        """Test S11 measurement."""
        self.vna.setup(1e6, 250e6, 1000, 100, -5)

        # Test normal measurement
        s11 = self.vna.measure_S11()
        assert isinstance(s11, np.ndarray)
        assert len(s11) == 1000
        assert s11.dtype == complex
        assert np.all(s11 == 0)  # DummyResource returns zeros

        # Test verbose measurement
        s11_verbose = self.vna.measure_S11(verbose=True)
        assert np.array_equal(s11, s11_verbose)

    def test_measure_osl_without_switch_fn(self, monkeypatch):
        """Test OSL measurement without switch_fn (manual mode)."""
        self.vna.switch_fn = None  # ensure no switch_fn is set
        self.vna.setup(1e6, 250e6, 1000, 100, -5)

        # Mock input() to simulate user pressing enter
        monkeypatch.setattr("builtins.input", lambda: "")
        # Call measure_OSL which should prompt for OSL standards
        osl = self.vna.measure_OSL()

        assert isinstance(osl, dict)
        assert "VNAO" in osl
        assert "VNAS" in osl
        assert "VNAL" in osl
        for std in osl.values():
            assert isinstance(std, np.ndarray)
            assert len(std) == 1000
            assert std.dtype == complex

    def test_measure_osl_with_switch_fn(self):
        """Test OSL measurement with switch_fn."""
        self.vna.setup(1e6, 250e6, 1000, 100, -5)

        osl = self.vna.measure_OSL()
        assert isinstance(osl, dict)
        assert set(osl.keys()) == {"VNAO", "VNAS", "VNAL"}
        for key, data in osl.items():
            assert isinstance(data, np.ndarray)
            assert len(data) == 1000
            assert data.dtype == complex
            assert np.all(data == 0)  # DummyResource returns zeros

        # Verify switch_fn was called correctly
        assert self.switch_fn.call_count == 3
        self.switch_fn.assert_has_calls(
            [call("VNAO"), call("VNAS"), call("VNAL")]
        )

    def test_measure_osl_switch_fn_failure_raises(self):
        """measure_OSL raises RuntimeError when switch_fn returns falsy."""
        self.vna.setup(1e6, 250e6, 1000, 100, -5)
        self.vna.switch_fn = MagicMock(return_value=False)
        with pytest.raises(RuntimeError, match="Failed to switch"):
            self.vna.measure_OSL()

    def test_add_osl(self, monkeypatch):
        """Test add_OSL method."""
        self.vna.setup(1e6, 250e6, 1000, 100, -5)

        monkeypatch.setattr("builtins.input", lambda: "")
        self.vna.add_OSL("test_std")

        assert "test_std" in self.vna.data
        assert "test_std" in self.vna.stds_meta
        assert self.vna.stds_meta["test_std"] == ["VNAO", "VNAS", "VNAL"]
        assert isinstance(self.vna.data["test_std"], np.ndarray)
        assert self.vna.data["test_std"].shape == (3, 1000)

    def test_measure_ant_without_switch_fn(self):
        """Test antenna measurement without switch_fn raises error."""
        self.vna.switch_fn = None  # ensure no switch_fn is set
        with pytest.raises(RuntimeError, match="No switch_fn set"):
            self.vna.measure_ant()

    def test_measure_ant_with_switch_fn(self):
        """Test antenna measurement with switch_fn."""
        self.vna.setup(1e6, 250e6, 1000, 100, -5)

        # Test with noise measurement
        s11 = self.vna.measure_ant(measure_noise=True)

        assert self.switch_fn.call_count == 3
        self.switch_fn.assert_has_calls(
            [call("VNAANT"), call("VNANOFF"), call("VNANON")]
        )

        assert "ant" in s11
        assert "load" in s11
        assert "noise" in s11
        assert isinstance(s11["ant"], np.ndarray)
        assert isinstance(s11["load"], np.ndarray)
        assert isinstance(s11["noise"], np.ndarray)

        # Test without noise measurement
        self.switch_fn.reset_mock()
        s11_no_noise = self.vna.measure_ant(
            measure_load=False, measure_noise=False
        )
        assert self.switch_fn.call_count == 1
        self.switch_fn.assert_has_calls([call("VNAANT")])

        assert "ant" in s11_no_noise
        assert "noise" not in s11_no_noise

    def test_measure_rec_without_switch_fn(self):
        """Test receiver measurement without switch_fn raises error."""
        self.vna.switch_fn = None  # ensure no switch_fn is set
        with pytest.raises(RuntimeError, match="No switch_fn set"):
            self.vna.measure_rec()

    def test_measure_rec_with_switch_fn(self):
        """Test receiver measurement with switch_fn."""
        self.vna.setup(1e6, 250e6, 1000, 100, -5)
        s11 = self.vna.measure_rec()
        self.switch_fn.assert_called_once_with("VNARF")
        assert "rec" in s11
        assert isinstance(s11["rec"], np.ndarray)

    def test_read_data(self):
        """Test read_data method."""
        self.vna.setup(1e6, 250e6, 1000, 100, -5)

        # Test single measurement
        self.vna.read_data(num_data=1)
        assert len(self.vna.data) == 1
        key = list(self.vna.data.keys())[0]
        assert key.endswith("_gamma")
        assert isinstance(self.vna.data[key], np.ndarray)

        # multiple measurements; may have same timestamp due to sec precision
        self.vna._clear_data()
        self.vna.read_data(num_data=3)

        # should have at least 1 measurement
        # (multiple calls may overwrite due to timestamp)
        assert len(self.vna.data) >= 1
        for key, value in self.vna.data.items():
            assert key.endswith("_gamma")
            assert isinstance(value, np.ndarray)

        # Test that the method actually does work with delays
        self.vna._clear_data()
        self.vna.read_data(num_data=1)
        time.sleep(1.1)  # Ensure different second
        self.vna.read_data(num_data=1)

        # Now we should have 2 measurements with different timestamps
        assert len(self.vna.data) == 2

    def test_write_data(self):
        """Test write_data method."""
        self.vna.setup(1e6, 250e6, 1000, 100, -5)

        # Add some test data manually to ensure we have known content
        self.vna.data["test1_gamma"] = np.array([1 + 1j, 2 + 2j])
        self.vna.data["test2_gamma"] = np.array([3 + 3j, 4 + 4j])

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Test writing to specific directory
            self.vna.write_data(outdir=tmppath)

            # Check data was cleared
            assert len(self.vna.data) == 0

            # Check file was created
            files = list(tmppath.glob("*_vna_data.npz"))
            assert len(files) == 1

            # Check file contents
            data = np.load(files[0])
            assert "freqs" in data
            assert "test1_gamma" in data
            assert "test2_gamma" in data

    def test_write_data_default_dir(self):
        """Test write_data with default save directory."""
        self.vna.setup(1e6, 250e6, 1000, 100, -5)
        self.vna.read_data(num_data=1)

        with tempfile.TemporaryDirectory() as tmpdir:
            self.vna.save_dir = Path(tmpdir)
            self.vna.write_data()

            files = list(Path(tmpdir).glob("*_vna_data.npz"))
            assert len(files) == 1

    def test_clear_data(self):
        """Test _clear_data method."""
        self.vna.data = {"test": np.array([1, 2, 3])}
        self.vna.stds_meta = {"test": ["VNAO"]}

        self.vna._clear_data()

        assert self.vna.data == {}
        assert self.vna.stds_meta == {}


class TestVNAEdgeCases:
    """Test edge cases and error conditions for VNA classes."""

    def test_frequency_array_with_missing_params(self):
        """Test freqs property when parameters are missing."""
        vna = DummyVNA()

        # Missing all parameters
        assert vna.freqs is None

        # Missing some parameters
        vna.fstart = 1e6
        assert vna.freqs is None

        vna.fstop = 250e6
        assert vna.freqs is None

        # All parameters set
        vna.npoints = 1000
        freqs = vna.freqs
        assert freqs is not None
        assert isinstance(freqs, np.ndarray)

    def test_measure_s11_with_uninitialized_vna(self):
        """Test S11 measurement without proper setup."""
        vna = DummyVNA()

        # Should still work but return zeros
        s11 = vna.measure_S11()
        assert isinstance(s11, np.ndarray)
        # Default npoints in DummyResource is 1000
        assert len(s11) == 1000

    def test_header_with_none_values(self):
        """Test header when some values are None."""
        vna = DummyVNA()
        header = vna.header

        assert header["fstart"] is None
        assert header["fstop"] is None
        assert header["npoints"] is None
        assert header["ifbw"] is None
        assert header["power_dBm"] is None
        assert header["freqs"] is None


class TestVNAIntegration:
    """Integration tests for VNA functionality."""

    def test_full_measurement_workflow(self, monkeypatch):
        """Test a complete measurement workflow."""
        vna = DummyVNA()

        # Setup measurement
        freqs = vna.setup(1e6, 250e6, 1000, 100, -5)
        assert len(freqs) == 1000

        # Add some test data manually to ensure predictable state
        vna.data["test1_gamma"] = np.array([1 + 1j] * 1000)
        vna.data["test2_gamma"] = np.array([2 + 2j] * 1000)
        initial_data_count = len(vna.data)

        # Add OSL measurements
        monkeypatch.setattr("builtins.input", lambda: "")
        vna.add_OSL("cal_std")

        # Should have initial data + OSL data
        assert len(vna.data) == initial_data_count + 1
        assert "cal_std" in vna.data

        # Write data and verify cleanup
        with tempfile.TemporaryDirectory() as tmpdir:
            vna.write_data(outdir=tmpdir)
            assert len(vna.data) == 0

            files = list(Path(tmpdir).glob("*.npz"))
            assert len(files) == 1


def _const_lin(db_value, n=16):
    """Build a constant complex S11 array with magnitude `10**(db/20)`."""
    return np.full(n, 10 ** (db_value / 20), dtype=complex)


class TestDbHelpers:
    def test_lin2dB_scalar(self):
        assert lin2dB(np.array([1.0])) == pytest.approx(0.0)
        assert lin2dB(np.array([0.1])) == pytest.approx(-20.0)

    def test_lin2dB_complex_uses_magnitude(self):
        # magnitude of 3+4j is 5 → 20*log10(5) ≈ 13.979
        assert lin2dB(np.array([3 + 4j])) == pytest.approx(13.9794, rel=1e-4)

    def test_mlin_matches_manual_mean(self):
        arr = np.array([1.0, 0.1])
        assert mlin(arr) == pytest.approx(np.mean([0.0, -20.0]))


class TestActiveFlag:
    def setup_method(self):
        self.vna = DummyVNA()
        # Open/short near 0 dB, load at -35 dB → all pass defaults.
        self.good_cal = {
            "VNAO": _const_lin(-1),
            "VNAS": _const_lin(-1),
            "VNAL": _const_lin(-35),
        }

    def test_rec_branch_pass(self):
        data = {"rec": _const_lin(-10)}
        flags = self.vna.activeflag(data, self.good_cal)
        assert flags == {"cal": True, "rec": True}

    def test_rec_branch_fail_above_upper(self):
        data = {"rec": _const_lin(-1)}  # above -5 dB upper bound
        flags = self.vna.activeflag(data, self.good_cal)
        assert flags["rec"] is False

    def test_ant_load_noise_branch(self):
        data = {
            "ant": _const_lin(-10),
            "load": _const_lin(-40),
            "noise": _const_lin(-40),
        }
        flags = self.vna.activeflag(data, self.good_cal)
        assert flags == {
            "cal": True,
            "ant": True,
            "load": True,
            "noise": True,
        }

    def test_optional_keys_missing_are_skipped(self):
        # Only "ant" present — no KeyError for missing load/noise.
        data = {"ant": _const_lin(-10)}
        flags = self.vna.activeflag(data, self.good_cal)
        assert flags == {"cal": True, "ant": True}

    def test_cal_fails_when_open_out_of_band(self):
        bad_cal = dict(self.good_cal, VNAO=_const_lin(-10))  # below -5 dB
        flags = self.vna.activeflag({"rec": _const_lin(-10)}, bad_cal)
        assert flags["cal"] is False
        assert flags["rec"] is True

    def test_cal_fails_when_load_above_upper(self):
        bad_cal = dict(self.good_cal, VNAL=_const_lin(-10))  # above -30 dB
        flags = self.vna.activeflag({"rec": _const_lin(-10)}, bad_cal)
        assert flags["cal"] is False

    def test_threshold_override(self):
        data = {"rec": _const_lin(-1)}
        # Override rec band to allow -1 dB → should now pass.
        flags = self.vna.activeflag(
            data, self.good_cal, thresholds={"rec": (None, 0)}
        )
        assert flags["rec"] is True

    def test_default_thresholds_shape(self):
        # Sanity check defaults weren't accidentally reshaped.
        for key in ("VNAO", "VNAS", "VNAL", "rec", "ant", "load", "noise"):
            low, high = DEFAULT_FLAG_THRESHOLDS[key]
            assert low is None or isinstance(low, (int, float))
            assert high is None or isinstance(high, (int, float))
