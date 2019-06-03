from scapy.all import *
import sys, os

TYPE_pcounter = 0x1212
TYPE_IPV4 = 0x800;

class PCounter(Packet):
    name = "PCounter"
    fields_desc = [
        ShortField("pid", 0),
        IntField("count", 0)
    ]
    def mysummary(self):
        return self.sprintf("pid=%pid%, count=%count%")

bind_layers(Ether, PCounter, type=TYPE_pcounter)
bind_layers(PCounter, IP, pid=TYPE_IPV4)
