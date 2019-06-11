from scapy.all import *
import sys, os

PROTO_pcounter = 0xFD
TYPE_TCP = 0x6

class PCounter(Packet):
    name = "PCounter"
    fields_desc = [
        ByteField("pid", 0),
        IntField("count", 0)
    ]
    def mysummary(self):
        return self.sprintf("pid=%pid%, count=%count%")


bind_layers(IP, PCounter, proto=PROTO_pcounter)
bind_layers(PCounter, TCP, pid=TYPE_TCP)

