#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Non Coherent FSK Receiver
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import sip
import threading



class usrp_send(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Non Coherent FSK Receiver", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Non Coherent FSK Receiver")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "usrp_send")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.f_xosc_Hz = f_xosc_Hz = 26e6
        self.dev_mantissa = dev_mantissa = 7
        self.dev_exp = dev_exp = 4
        self.samp_rate = samp_rate = 1e6
        self.gain_db = gain_db = 10
        self.fsk_deviation_Hz = fsk_deviation_Hz = (f_xosc_Hz / 2**17) * (8 + dev_mantissa) * 2**dev_exp
        self.f_center_Hz = f_center_Hz = 433.2e6
        self.bandwidth = bandwidth = 1e6

        ##################################################
        # Blocks
        ##################################################

        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_unknown_pps(uhd.time_spec(0))

        self.uhd_usrp_source_0.set_center_freq(f_center_Hz, 0)
        self.uhd_usrp_source_0.set_antenna("RX2", 0)
        self.uhd_usrp_source_0.set_bandwidth(samp_rate, 0)
        self.uhd_usrp_source_0.set_rx_agc(False, 0)
        self.uhd_usrp_source_0.set_gain(gain_db, 0)
        self.qtgui_sink_x_0_0 = qtgui.sink_c(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_0_win = sip.wrapinstance(self.qtgui_sink_x_0_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0_0.enable_rf_freq(False)

        self.top_layout.addWidget(self._qtgui_sink_x_0_0_win)
        self.qtgui_sink_x_0 = qtgui.sink_c(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(False)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_complex_to_mag_squared_0_0_0 = blocks.complex_to_mag_squared(1)
        self.blocks_complex_to_mag_squared_0_0 = blocks.complex_to_mag_squared(1)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)
        self.band_pass_filter_0_0 = filter.fir_filter_ccc(
            1,
            firdes.complex_band_pass(
                1,
                samp_rate,
                (-fsk_deviation_Hz/2-5e3),
                (-fsk_deviation_Hz/2+5e3),
                500,
                window.WIN_HAMMING,
                6.76))
        self.band_pass_filter_0 = filter.fir_filter_ccc(
            1,
            firdes.complex_band_pass(
                1,
                samp_rate,
                (18000-5e3),
                (18000+5e3),
                500,
                window.WIN_HAMMING,
                6.76))


        ##################################################
        # Connections
        ##################################################
        self.connect((self.band_pass_filter_0, 0), (self.blocks_complex_to_mag_squared_0_0, 0))
        self.connect((self.band_pass_filter_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.band_pass_filter_0_0, 0), (self.blocks_complex_to_mag_squared_0_0_0, 0))
        self.connect((self.band_pass_filter_0_0, 0), (self.qtgui_sink_x_0_0, 0))
        self.connect((self.blocks_char_to_float_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.blocks_complex_to_mag_squared_0_0_0, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.band_pass_filter_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.band_pass_filter_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "usrp_send")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_f_xosc_Hz(self):
        return self.f_xosc_Hz

    def set_f_xosc_Hz(self, f_xosc_Hz):
        self.f_xosc_Hz = f_xosc_Hz
        self.set_fsk_deviation_Hz((self.f_xosc_Hz / 2**17) * (8 + self.dev_mantissa) * 2**self.dev_exp)

    def get_dev_mantissa(self):
        return self.dev_mantissa

    def set_dev_mantissa(self, dev_mantissa):
        self.dev_mantissa = dev_mantissa
        self.set_fsk_deviation_Hz((self.f_xosc_Hz / 2**17) * (8 + self.dev_mantissa) * 2**self.dev_exp)

    def get_dev_exp(self):
        return self.dev_exp

    def set_dev_exp(self, dev_exp):
        self.dev_exp = dev_exp
        self.set_fsk_deviation_Hz((self.f_xosc_Hz / 2**17) * (8 + self.dev_mantissa) * 2**self.dev_exp)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.samp_rate, (18000-5e3), (18000+5e3), 500, window.WIN_HAMMING, 6.76))
        self.band_pass_filter_0_0.set_taps(firdes.complex_band_pass(1, self.samp_rate, (-self.fsk_deviation_Hz/2-5e3), (-self.fsk_deviation_Hz/2+5e3), 500, window.WIN_HAMMING, 6.76))
        self.qtgui_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0.set_bandwidth(self.samp_rate, 0)
        self.qtgui_sink_x_0_0.set_frequency_range(0, self.samp_rate)

    def get_gain_db(self):
        return self.gain_db

    def set_gain_db(self, gain_db):
        self.gain_db = gain_db
        self.uhd_usrp_source_0.set_gain(self.gain_db, 0)

    def get_fsk_deviation_Hz(self):
        return self.fsk_deviation_Hz

    def set_fsk_deviation_Hz(self, fsk_deviation_Hz):
        self.fsk_deviation_Hz = fsk_deviation_Hz
        self.band_pass_filter_0_0.set_taps(firdes.complex_band_pass(1, self.samp_rate, (-self.fsk_deviation_Hz/2-5e3), (-self.fsk_deviation_Hz/2+5e3), 500, window.WIN_HAMMING, 6.76))

    def get_f_center_Hz(self):
        return self.f_center_Hz

    def set_f_center_Hz(self, f_center_Hz):
        self.f_center_Hz = f_center_Hz
        self.uhd_usrp_source_0.set_center_freq(self.f_center_Hz, 0)

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth




def main(top_block_cls=usrp_send, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
