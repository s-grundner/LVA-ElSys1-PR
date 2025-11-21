#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: USRP from CC1101
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
import math
from gnuradio import blocks
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
import threading



class usrp_send(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "USRP from CC1101", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("USRP from CC1101")
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
        self.samp_rate = samp_rate = 2e6
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
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=1,
                decimation=100,
                taps=[],
                fractional_bw=0)
        self.low_pass_filter_0 = filter.fir_filter_ccf(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                100e3,
                1000,
                window.WIN_HAMMING,
                6.76))
        self.blocks_head_0 = blocks.head(gr.sizeof_float*1, (1024*20))
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_float*1, '/home/simon/Dokumente/repos-jku/ElSys-PR/2_usrp_send/4-fsk-b3.gnc', False)
        self.blocks_file_sink_0.set_unbuffered(True)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf((samp_rate/(2*math.pi*fsk_deviation_Hz)))


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_head_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_head_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.low_pass_filter_0, 0))


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
        self.analog_quadrature_demod_cf_0.set_gain((self.samp_rate/(2*math.pi*self.fsk_deviation_Hz)))
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, 100e3, 1000, window.WIN_HAMMING, 6.76))
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0.set_bandwidth(self.samp_rate, 0)

    def get_gain_db(self):
        return self.gain_db

    def set_gain_db(self, gain_db):
        self.gain_db = gain_db
        self.uhd_usrp_source_0.set_gain(self.gain_db, 0)

    def get_fsk_deviation_Hz(self):
        return self.fsk_deviation_Hz

    def set_fsk_deviation_Hz(self, fsk_deviation_Hz):
        self.fsk_deviation_Hz = fsk_deviation_Hz
        self.analog_quadrature_demod_cf_0.set_gain((self.samp_rate/(2*math.pi*self.fsk_deviation_Hz)))

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
